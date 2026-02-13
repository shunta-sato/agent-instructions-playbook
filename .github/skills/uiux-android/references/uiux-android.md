# Android UI/UX adapter reference

Use this reference with `$uiux-android` after `$uiux-core`.

## Allowed file edits

- `ui_contract.yaml`: `platform_overrides.android`
- `auto_review.json`: append Android-specific checks with `id` prefixed by `android.`

## Suggested Android overrides/checks

- Touch target sizing guidance in dp (e.g., 48dp minimum target intent).
- Navigation pattern consistency with Android conventions (top app bar, back behavior, tabs/bottom nav).
- TalkBack semantics coverage for interactive controls.
- Dynamic content/state announcements where needed for assistive tech.

## Example check IDs

- `android.accessibility.min_touch_target_dp`
- `android.navigation.back_behavior_consistency`
- `android.a11y.talkback_label_coverage`
