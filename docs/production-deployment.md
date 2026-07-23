# Production deployment safety

## Immutable candidates

The main build publishes commit-specific frontend and backend tags. Candidate
preparation combines those tags with their registry digests and records them
in a root-only `release-manifest.env` alongside:

- the full release commit SHA;
- the workflow run ID that first created the candidate;
- the source archive SHA-256;
- the tracked-file checksum manifest SHA-256; and
- the UTC creation time.

Rerunning candidate preparation for the same commit validates the existing
manifest, every tracked source file, the immutable image references, and the
rendered Compose images. Matching candidates are reused; mismatches fail
without overwriting either candidate.

The `PRODUCTION_DEPLOY_ENABLED` repository variable must remain unset or false
until candidate evidence has been reviewed. Candidate preparation never runs
`docker compose pull`, `docker compose up`, or a traffic switch.

## Production configuration boundary

The production Compose contract currently requires exactly two secret-bearing
files:

- a root `.env` for PostgreSQL and MinIO Compose interpolation; and
- `backend/.env` for the backend container.

Candidate preparation copies only those two files with mode `0600`. It does not
copy the active repository, its uncommitted source files, or any data volume.
Secret values must never be logged or committed.

The active server currently stores these files under the dirty
`/opt/PastExamWeb_PHY` checkout. Moving them to an independent, root-only
configuration directory (for example `/opt/pastexam-config`) and updating the
activation procedure to reference that directory is a blocker before a
production traffic switch. Candidate preparation may be validated before that
migration, but production activation must not proceed while it depends on the
active checkout for configuration.
