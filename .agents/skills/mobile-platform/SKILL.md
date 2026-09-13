---
name: mobile-platform
description: "Resolve missing mobile toolchain, native/platform capability, lifecycle, or cross-platform behavior facts."
---

# Mobile platform context

Establish only the facts needed by the change: native Android/iOS, Flutter, React
Native/Expo, build and SDK versions, package manager, runtime permissions, native
modules, deep links, lifecycle, or supported device classes.

`scripts/inspect_mobile_project.py --root PATH --markdown` is an optional read-only
collector for an unfamiliar project. Confirm actual commands and platform capabilities;
installed packages or configuration files alone are not runtime proof. It does not
install dependencies, alter signing, or approve production device/account access.

Define shared product semantics separately from platform-native presentation. A
permission, background-mode or native dependency change needs its affected platform
facts even when the visible UI change is small. Use current platform documentation
for version-sensitive behavior. Record material platform differences and test limits
in the existing task instead of creating parallel specifications.
