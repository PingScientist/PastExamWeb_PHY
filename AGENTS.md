# Repository Working Rules

- Minimize token usage.
- Do not scan the whole repository.
- Inspect only files relevant to the current task.
- Propose a minimal plan before editing.
- Avoid unrelated refactors.
- Do not run full test suites unless explicitly asked.
- Keep explanations concise.
- Do not commit PDF files to Git.
- Store PDF metadata in the database.
- Store PDF binaries in MinIO, S3-compatible storage, or local development storage.
- Centralize authentication and role checks.

## Budgeted autonomy mode

When the user asks for a focused fix but the exact file is uncertain:

1. Do a small responsibility check before editing.
2. Inspect at most 6 relevant files unless the user allows more.
3. Modify at most 2 files unless the user allows more.
4. Prefer the smallest safe frontend/backend scope.
5. Do not run browser automation, full builds, installs, or Docker rebuilds unless explicitly requested.
6. If more scope is needed, stop and explain why.
7. Do not claim visual verification unless it was actually performed.

For token-sensitive UI fixes:

1. Prefer code-level diff review and manual user verification.
2. Do not use browser/viewport testing unless explicitly requested.
3. Do not run Playwright, screenshot checks, or full builds unless explicitly requested.
4. Do not expand a small UI fix into a full responsive redesign.
5. If the environment has service, Docker, pnpm, permission, or 502 issues, stop after reporting the blocker unless the user explicitly asks to debug it.
