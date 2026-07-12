# Architecture map

Use this map as a starting point and verify it against the current tree.

- `frontend/`: Vue 3 + Vite application using PrimeVue, PrimeFlex/Tailwind utilities, Axios, Vue Router, Vitest, and Playwright.
- `frontend/src/views/`: route-level screens. `frontend/src/components/`: reusable UI. `frontend/src/composables/` and `utils/`: shared state and behavior.
- `frontend/src/api/` and `frontend/src/utils/http.js`: client/server contract and HTTP behavior.
- `frontend/src/style.css`: global variables, themes, typography, sizing, and shared visual rules. Check this and neighboring UI before creating new tokens.
- `backend/`: Python 3.12 FastAPI application using SQLModel, Alembic, PostgreSQL/asyncpg, Redis/ARQ, and MinIO.
- `backend/app/api/services/`: route/domain handlers. `backend/app/models/`: persisted and API models. `backend/app/utils/`: shared auth, storage, and supporting boundaries.
- `backend/alembic/` or current migration directory: persisted schema history. Locate the configured script location before generating or editing migrations.
- Root and package workflows define CI expectations; they are not the default validation target for every local change.

For cross-layer changes, trace: view/component → API client → FastAPI route/service → schema/model → database/storage → focused tests. Confirm naming, optionality, timestamps, permissions, status codes, and error shapes at both ends.
