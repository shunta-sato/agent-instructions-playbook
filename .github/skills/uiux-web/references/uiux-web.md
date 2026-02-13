# Web UI/UX adapter reference

Use this reference with `$uiux-web` after `$uiux-core`.

## Allowed file edits

- `ui_contract.yaml`: `platform_overrides.web`
- `auto_review.json`: append web-specific checks with `id` prefixed by `web.`

## Suggested web overrides/checks

- Keyboard-only navigation coverage (tab order, actionable focus).
- ARIA role/name/value patterns for interactive components.
- CSS px target size guidance for pointer/touch targets.
- Focus visibility and focus management after dynamic updates.

## Example check IDs

- `web.keyboard.navigation_flow`
- `web.aria.role_name_value_coverage`
- `web.accessibility.min_target_size_css_px`
