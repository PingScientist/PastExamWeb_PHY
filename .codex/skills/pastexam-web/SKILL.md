---
name: pastexam-web
description: Implement and review PastExamWeb_PHY full-stack changes efficiently across its Vue/PrimeVue frontend and FastAPI/SQLModel backend. Use for repository architecture discovery, UI/UX integration, API or database work, risk-based testing, browser/screenshot validation, workspace protection, and commit preparation in PastExamWeb_PHY.
---

# PastExamWeb Full-Stack Workflow

## Orient narrowly

1. Read the repository `AGENTS.md` and inspect `git status`.
2. Identify the entry point and owning module with `rg` or targeted file listings.
3. Trace only the relevant imports, API calls, models, migrations, shared tokens, and tests. Expand scope when a dependency or contract requires it; never use an arbitrary file-count ceiling.
4. Read [architecture.md](references/architecture.md) when ownership or cross-layer impact is unclear.

## Deliver a coherent change

- Define the requested behavior and the affected contract before editing.
- Follow existing patterns first. Preserve unrelated user changes and avoid opportunistic cleanup.
- Complete all legitimately affected layers together: UI state, API client, route/service, schema/model, migration, authorization, and focused tests as applicable.
- For frontend work, read [frontend.md](references/frontend.md). Use the optional local `ui-ux-pro-max` Skill only for advisory UI searches; keep PastExamWeb's established tokens and interaction language authoritative.
- For API, persistence, authorization, or storage work, read [backend.md](references/backend.md).

## Validate by risk

Read [validation-and-git.md](references/validation-and-git.md), select the lowest sufficient validation level, and escalate only from evidence or risk. Never loop on an unchanged failure.

For browser or screenshot checks, allow one initial attempt and one targeted retry after a concrete correction. After the second failure for the same scenario, stop browser work, record the blocker, and use cheaper evidence where it remains meaningful.

## Finish cleanly

- Review the full and staged diffs for contract gaps, inconsistent UI, secrets, debug code, unrelated formatting, and generated artifacts.
- State exactly which checks ran and which were omitted with reasons.
- Commit only when requested, using a focused Conventional Commit. Do not push or merge without explicit instruction.
