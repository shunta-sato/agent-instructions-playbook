# Android concurrency reference

Use this to decide between coroutines, WorkManager, or services, and to respect platform restrictions.

## Decision guide

- **UI work:** main thread only. Keep work short; offload CPU or I/O.
- **In-app async work:** Kotlin coroutines with proper dispatchers (`Dispatchers.Default` for CPU, `Dispatchers.IO` for I/O).
- **Deferrable, guaranteed background work:** WorkManager.
- **User-visible ongoing work:** Foreground service (with notification and platform restrictions).

## OS constraints (explicit)

- **Background service limitations (Android 8+):** background services are restricted; use WorkManager or foreground services.
- **Foreground service background-start restrictions (Android 12+):** starting a foreground service from the background is limited; follow allowed exemptions.
- **WorkManager long-running work:** runs as a foreground service under the hood when needed.

## Practical rules

- Do **not** treat Service as a generic background thread.
- Prefer **WorkManager** for deferrable/guaranteed work.
- Use **Foreground service** only when user-visible and allowed; always show a notification.

## Short examples

### Coroutine dispatcher usage and cancellation

```kotlin
viewModelScope.launch(Dispatchers.IO) {
  ensureActive()
  val result = repository.fetch()
  withContext(Dispatchers.Main) { render(result) }
}
```

### WorkManager long-running worker (skeleton)

```kotlin
class SyncWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
  override suspend fun doWork(): Result {
    return try {
      sync()
      Result.success()
    } catch (e: Exception) {
      Result.retry()
    }
  }
}
```

### Foreground service start constraints (notes)

```text
- Start only when user-visible and permitted by OS state.
- Provide a foreground notification immediately.
- Stop service when work completes or user dismisses.
```
