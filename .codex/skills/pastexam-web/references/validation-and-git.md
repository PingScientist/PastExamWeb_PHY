# Validation and Git workflow

## Choose a level

1. **Localized, low risk:** review the diff and run the narrowest applicable syntax, lint, type, or unit target.
2. **Behavioral or cross-layer:** run focused frontend/backend tests and contract-relevant lint/build checks. Add or update tests for changed behavior.
3. **High risk or release:** run broader suites, builds, migrations, Docker integration, or E2E for shared infrastructure, auth/data critical paths, release changes, or an explicit user request.

Instruction, documentation, and Skill-only changes normally require structure/frontmatter validation, static scans, and diff review—not application builds or E2E.

## Failure and retry rules

- Read the first failure and distinguish product defect, test defect, missing dependency/service, permission issue, and environmental flake.
- Make one evidence-based correction before retrying. Never rerun the same failing command unchanged merely hoping it passes.
- Browser/screenshot scenario: initial attempt + one targeted retry maximum. Stop after a repeated blocker and report the URL/scenario, observed error, attempts, and alternative evidence.
- Stop when relevant checks pass with low residual risk, or when further checks need unavailable infrastructure/credentials or cost more than the change warrants.

## Commit safely

1. Inspect `git status`, `git diff --check`, and the full diff.
2. Stage explicit task-owned paths only.
3. Inspect `git diff --cached` and confirm no secrets, user changes, PDFs, caches, or unrelated formatting.
4. Use one focused Conventional Commit unless separable outcomes genuinely require more.
5. Do not push, merge, amend unrelated work, or bypass hooks without explicit instruction.
