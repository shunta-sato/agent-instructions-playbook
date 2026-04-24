# UIUX platform adapter reference

Use this reference with `uiux-core` when a UIUX task targets Web, iOS, and/or Android.

## Shared adapter rules

- Do not create new UIUX Pack artifact names.
- Update `ui_contract.yaml` only under the matching `platform_overrides.<platform>` key.
- Add platform-specific checks to `auto_review.json` with ids prefixed by `web.`, `ios.`, or `android.`.
- Keep core checks in place; platform checks only add constraints or verification detail.

## Web

Apply when `ui_contract.yaml` includes `web` in `platforms`, or when browser UI flows/components/navigation are in scope.

Suggested overrides/checks:
- Keyboard-only navigation coverage, including tab order and actionable focus.
- ARIA role/name/value patterns for interactive components.
- CSS px target size guidance for pointer/touch targets.
- Focus visibility and focus management after dynamic updates.

Example check ids:
- `web.keyboard.navigation_flow`
- `web.aria.role_name_value_coverage`
- `web.accessibility.min_target_size_css_px`

## iOS

Apply when `ui_contract.yaml` includes `ios` in `platforms`, or when iOS UI flows/components/navigation are in scope.

Suggested overrides/checks:
- Dynamic Type support and text scaling behavior.
- System color usage for contrast and theme adaptability.
- VoiceOver naming/traits for controls and key content.
- Navigation/title/back affordance consistency with iOS patterns.

Example check ids:
- `ios.typography.dynamic_type_support`
- `ios.color.system_color_usage`
- `ios.a11y.voiceover_label_coverage`

## Android

Apply when `ui_contract.yaml` includes `android` in `platforms`, or when Android UI flows/components/navigation are in scope.

Suggested overrides/checks:
- Touch target sizing guidance in dp, such as 48dp minimum target intent.
- Navigation pattern consistency with Android conventions, including top app bar, back behavior, tabs, and bottom navigation.
- TalkBack semantics coverage for interactive controls.
- Dynamic content/state announcements where needed for assistive technology.

Example check ids:
- `android.accessibility.min_touch_target_dp`
- `android.navigation.back_behavior_consistency`
- `android.a11y.talkback_label_coverage`
