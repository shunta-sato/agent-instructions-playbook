# iOS UI/UX adapter reference

Use this reference with `$uiux-ios` after `$uiux-core`.

## Allowed file edits

- `ui_contract.yaml`: `platform_overrides.ios`
- `auto_review.json`: append iOS-specific checks with `id` prefixed by `ios.`

## Suggested iOS overrides/checks

- Dynamic Type support and text scaling behavior.
- System color usage for contrast/theme adaptability.
- VoiceOver naming/traits for controls and key content.
- Navigation/title/back affordance consistency with iOS patterns.

## Example check IDs

- `ios.typography.dynamic_type_support`
- `ios.color.system_color_usage`
- `ios.a11y.voiceover_label_coverage`
