# React Native and Expo test adapter

Open this reference for React Native or Expo submissions after the common mobile evidence matrix selects the required evidence class.

## Preferred layers

- Jest: TypeScript/JavaScript logic, reducers, validation, mappers, and state transitions.
- React Native Testing Library: component rendering, interaction, state, accessibility semantics, and error presentation that do not require a real native runtime.
- Maestro: canonical Android/iOS regression user journeys when the project has adopted Maestro.
- Playwright: Expo Web product journeys only; it does not replace Android/iOS evidence.
- mobile runtime verification harness: exploration, reproduction, device-only verification, logs/network/component-tree inspection, profiling, and evidence collection.

## Expo-specific boundaries

Require a development or release-equivalent build rather than Expo Go when the claim involves custom native modules, app-specific native profiling, native configuration, or release behavior. The absence of committed `ios/`/`android/` directories in an Expo CNG project does not remove the platform evidence requirement.

Record package manager, Expo/React Native version evidence, build identity, app/runtime environment, target device, and canonical project commands. Do not add packages, invoke EAS build/submit, or publish updates merely to complete the gate.

## Cross-platform completion

For a feature claimed on both mobile platforms:

- shared Jest/RNTL evidence may cover shared semantics
- Android Maestro/runtime evidence covers Android only
- iOS Maestro/runtime evidence covers iOS only
- platform-specific deviations must remain inside the approved parity record
- unavailable macOS/iOS infrastructure produces `unknown` or `blocked`, not an inferred pass
