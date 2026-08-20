# React Native and Expo project detection

Open this reference when repository evidence suggests React Native or Expo, or when the requested stack is React Native/Expo but the repository shape is not yet confirmed.

## Evidence hierarchy

Prefer repository evidence over the request text:

1. `package.json` dependency and script names
2. `app.json`, `app.config.js`, or `app.config.ts` presence
3. `eas.json` and `.eas/workflows/`
4. committed `ios/` and `android/` projects
5. `.maestro/`, Jest/RNTL, Playwright, and runtime-tool configuration
6. executable toolchain and device evidence

Do not execute dynamic Expo config during read-only inspection. Record the config path, then use a project-approved Expo command later if evaluated public configuration is required.

## Classifications

- `react-native-expo`: both React Native and Expo are confirmed.
- `react-native-bare-or-brownfield`: React Native is confirmed without Expo.
- `expo-cng`: Expo is confirmed while generated native directories are not committed. Their absence is not evidence that iOS or Android is unsupported.
- `committed-native-projects`: Expo is confirmed and both native project directories are present.
- `bare-or-brownfield`: native projects are present but the Expo/CNG ownership model is not confirmed.

Record Expo Go, development build, preview/release build, and EAS paths separately. Expo Go is not sufficient evidence for custom native modules, app-specific native profiling, or release behavior.

## First files and commands

Inspect, without reading credential values:

- `package.json` and the selected lockfile
- Expo app config path
- `eas.json` and workflow paths
- project `AGENTS.md` and canonical command documentation
- `.maestro/` and test configuration
- native directories when committed

Prefer repository scripts and the pinned package manager. Do not invent `npx`, EAS, build, submission, or package-add commands when the project already defines a wrapper.

## Route outputs

Record:

- framework and native-project model
- Node/package-manager policy
- Expo SDK and React Native version evidence
- Expo Router, development-build, updates, and EAS surfaces
- Jest/RNTL, Maestro, Playwright, and runtime-harness evidence
- Android/iOS host and device readiness
- cloud/auth/native/performance/release routes
- unknowns and blockers
