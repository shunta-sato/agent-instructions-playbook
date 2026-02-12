# Working with legacy code (C++ examples)

These examples mirror the “Create seams” guidance in the main reference and focus on
deterministic seams for nondeterminism and I/O.

## 3.1 Example: seam for retry backoff (C++)

```cpp
#include <algorithm>
#include <functional>

using BackoffMsFn = std::function<int(int attempt)>;

class RetryPolicy {
 public:
  explicit RetryPolicy(BackoffMsFn backoff_ms) : backoff_ms_(std::move(backoff_ms)) {}

  int DelayFor(int attempt) const { return backoff_ms_(attempt); }

 private:
  BackoffMsFn backoff_ms_;
};

// production: exponential backoff with cap
RetryPolicy prod_policy([](int attempt) {
  const int base_ms = 25;
  const int max_ms = 1000;
  return std::min(max_ms, base_ms * (1 << attempt));
});

// test: deterministic, fast
RetryPolicy test_policy([](int) { return 0; });
```

## 3.2 Example: seam for time (C++)

```cpp
#include <chrono>

class Clock {
 public:
  virtual ~Clock() = default;
  virtual std::chrono::system_clock::time_point Now() const = 0;
};

class SystemClock final : public Clock {
 public:
  std::chrono::system_clock::time_point Now() const override {
    return std::chrono::system_clock::now();
  }
};

class FixedClock final : public Clock {
 public:
  explicit FixedClock(std::chrono::system_clock::time_point now) : now_(now) {}
  std::chrono::system_clock::time_point Now() const override { return now_; }
  void Set(std::chrono::system_clock::time_point now) { now_ = now; }

 private:
  std::chrono::system_clock::time_point now_;
};
```
