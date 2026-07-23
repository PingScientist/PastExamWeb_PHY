#!/usr/bin/env bash

set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose_file="$repository_root/docker/docker-compose.acceptance.yml"
env_file="${ACCEPTANCE_ENV_FILE:-$repository_root/docker/acceptance.env.example}"

if [ ! -f "$env_file" ]; then
  echo "Acceptance environment file not found: $env_file" >&2
  exit 1
fi

project_name="$(
  sed -n 's/^COMPOSE_PROJECT_NAME=//p' "$env_file" |
    tail -n 1
)"

case "$project_name" in
  pastexam-acceptance-*) ;;
  *)
    echo "Refusing non-acceptance Compose project: $project_name" >&2
    exit 1
    ;;
esac

compose=(
  docker compose
  --project-name "$project_name"
  --env-file "$env_file"
  --file "$compose_file"
)

postgres_user="$(
  sed -n 's/^POSTGRES_USER=//p' "$env_file" |
    tail -n 1
)"
empty_database="$(
  sed -n 's/^POSTGRES_DB=//p' "$env_file" |
    tail -n 1
)"
upgrade_database="$(
  sed -n 's/^ACCEPTANCE_UPGRADE_DB=//p' "$env_file" |
    tail -n 1
)"
test_database="$(
  sed -n 's/^ACCEPTANCE_TEST_DB=//p' "$env_file" |
    tail -n 1
)"
http_port="$(
  sed -n 's/^ACCEPTANCE_HTTP_PORT=//p' "$env_file" |
    tail -n 1
)"

for required_value in \
  "$postgres_user" \
  "$empty_database" \
  "$upgrade_database" \
  "$test_database" \
  "$http_port"
do
  if [ -z "$required_value" ]; then
    echo "Acceptance environment is missing a required value." >&2
    exit 1
  fi
done

"${compose[@]}" config --quiet
"${compose[@]}" up -d --build --wait db redis minio

echo "Validating empty database migration to head..."
"${compose[@]}" run --rm migrate
"${compose[@]}" run --rm migrate alembic current
"${compose[@]}" run --rm migrate

echo "Validating migration path from 3a7e9c1d5b42 to head..."
"${compose[@]}" exec -T db sh -eu -c '
  database_name="$1"
  if ! psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc \
    "SELECT 1 FROM pg_database WHERE datname = '\''$database_name'\''" |
    grep -Fxq 1
  then
    createdb -U "$POSTGRES_USER" "$database_name"
  fi
' sh "$upgrade_database"
"${compose[@]}" run --rm \
  -e "DB_NAME=$upgrade_database" \
  migrate alembic upgrade 3a7e9c1d5b42
"${compose[@]}" run --rm \
  -e "DB_NAME=$upgrade_database" \
  migrate alembic current
"${compose[@]}" run --rm \
  -e "DB_NAME=$upgrade_database" \
  migrate alembic upgrade head
"${compose[@]}" run --rm \
  -e "DB_NAME=$upgrade_database" \
  migrate alembic current
"${compose[@]}" run --rm \
  -e "DB_NAME=$upgrade_database" \
  migrate alembic upgrade head

echo "Running backend tests against a third isolated database..."
"${compose[@]}" exec -T db sh -eu -c '
  database_name="$1"
  if ! psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc \
    "SELECT 1 FROM pg_database WHERE datname = '\''$database_name'\''" |
    grep -Fxq 1
  then
    createdb -U "$POSTGRES_USER" "$database_name"
  fi
' sh "$test_database"
"${compose[@]}" run --rm \
  -e "DB_NAME=$test_database" \
  migrate alembic upgrade head
"${compose[@]}" run --rm \
  -e "DB_NAME=$test_database" \
  migrate python -m app.scripts.seed_db
"${compose[@]}" --profile tests run --rm backend-tests

"${compose[@]}" up -d --build --wait backend frontend nginx

curl --fail --silent --show-error \
  "http://127.0.0.1:$http_port/api/health"
curl --fail --silent --show-error \
  "http://127.0.0.1:$http_port/" >/dev/null

"${compose[@]}" exec -T redis redis-cli ping |
  grep -Fxq PONG
"${compose[@]}" exec -T minio mc ready local

"${compose[@]}" ps
echo "Acceptance validation completed for $project_name."
