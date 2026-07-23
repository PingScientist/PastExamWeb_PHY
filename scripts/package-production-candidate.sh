#!/usr/bin/env bash

set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
release_sha="${RELEASE_SHA:?Set RELEASE_SHA}"
output_archive="${OUTPUT_ARCHIVE:?Set OUTPUT_ARCHIVE}"

if command -v sha256sum >/dev/null 2>&1; then
  checksum_command=(sha256sum)
elif command -v shasum >/dev/null 2>&1; then
  checksum_command=(shasum -a 256)
else
  echo "A SHA-256 checksum utility is required." >&2
  exit 1
fi

if [[ ! "$release_sha" =~ ^[0-9a-f]{40}$ ]]; then
  echo "RELEASE_SHA must be a full lowercase Git commit SHA." >&2
  exit 1
fi

if [ "$(git -C "$repository_root" rev-parse HEAD)" != "$release_sha" ]; then
  echo "The checked-out commit does not match RELEASE_SHA." >&2
  exit 1
fi

if [ -n "$(git -C "$repository_root" status --porcelain)" ]; then
  echo "Refusing to package a dirty candidate checkout." >&2
  exit 1
fi

temporary_root="$(mktemp -d)"
trap 'rm -rf "$temporary_root"' EXIT

metadata_root="$temporary_root/metadata"
install -d -m 700 "$metadata_root"

printf '%s\n' "$release_sha" >"$metadata_root/.release-source-sha"

(
  cd "$repository_root"
  while IFS= read -r -d '' tracked_file; do
    "${checksum_command[@]}" "$tracked_file"
  done < <(git ls-files -z)
) >"$metadata_root/.release-files.sha256"

git -C "$repository_root" archive \
  --format=tar \
  --output="$temporary_root/candidate.tar" \
  "$release_sha"

tar \
  --append \
  --file="$temporary_root/candidate.tar" \
  --directory="$metadata_root" \
  .release-source-sha \
  .release-files.sha256

install -d -m 700 "$(dirname "$output_archive")"
gzip -n -9 -c "$temporary_root/candidate.tar" >"$output_archive"
chmod 600 "$output_archive"

echo "Candidate archive created for $release_sha."
