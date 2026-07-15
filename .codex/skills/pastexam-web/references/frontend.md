# Frontend execution guide

## Consistency first

- Inspect the closest comparable screen and `frontend/src/style.css` before designing.
- Reuse CSS variables, PrimeVue components, layout rhythm, typography, theme behavior, icons, dialogs, toasts, loading, empty, error, and permission states.
- Treat `ui-ux-pro-max` recommendations as a checklist or search index, not permission to replace the site's visual identity.

## Implementation

- Keep route-level orchestration in views and reusable behavior in components/composables when it has a clear boundary.
- Keep server state, derived state, and local interaction state distinguishable. Handle stale requests and loading/error transitions where relevant.
- Use semantic HTML, labels, keyboard operation, visible focus, accessible names, sufficient contrast, reduced-motion support, and responsive layouts without horizontal overflow.
- Keep action labels and resulting feedback consistent. Provide useful empty and failure recovery states.
- Update API clients and mocks/fixtures together when contracts change. Do not duplicate server authorization rules as a security boundary.

## Proportionate checks

- Style/copy/local template: diff review plus targeted lint or component test when available.
- State or interaction: focused Vitest test and targeted lint.
- Shared token/router/API-client/build configuration: affected tests and build/type/lint checks as justified.
- Use Playwright or screenshots for visually consequential or end-to-end behavior, not for documentation or isolated logic changes. Apply the two-attempt ceiling.
