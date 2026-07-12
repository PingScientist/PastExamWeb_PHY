# Backend, API, and database guide

## Boundaries and contracts

- Locate the existing route/service/model/auth/storage pattern and extend it consistently.
- Validate inputs at the API boundary and enforce authorization, ownership, and business invariants server-side in reusable boundaries.
- Keep status codes and error bodies predictable. Prefer additive, backward-compatible response changes; update every in-repo client for intentional contract changes.
- Avoid leaking sensitive fields, internal exceptions, resource existence, credentials, or storage paths.

## Persistence

- Before changing a model, assess existing rows, nullability, server/application defaults, uniqueness, indexes, foreign keys, cascade behavior, timestamps, and serialization.
- Add an Alembic migration for persisted schema changes. Do not edit applied history. Make upgrade order safe and downgrade practical when the project supports it.
- Keep related writes atomic and rollback-safe. Bound list queries, prevent N+1 access, and consider concurrency/idempotency for retryable actions.
- Keep PDF binaries out of Git and relational rows; store metadata in the database and binaries in the configured object/local development storage.

## Proportionate checks

- Pure helper/schema logic: focused unit test and Ruff on affected paths.
- Route/service behavior: focused API tests including authorization and failure cases.
- Model/migration/query changes: focused tests plus migration/schema checks against an available disposable database.
- Auth, storage, worker, or shared infrastructure: broaden to integration tests when services and credentials are available; otherwise state the unverified boundary.
