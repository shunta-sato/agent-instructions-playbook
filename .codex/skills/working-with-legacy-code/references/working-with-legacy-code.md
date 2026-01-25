# Working with legacy code: practical workflow

This document is a reference for changing code when tests are weak (or missing). It fixes the **order of operations** so changes stay safe.

The goal is not to build an ideal structure immediately. The goal is to **make change safe first**, then separate responsibilities and boundaries as pressure increases.

## 1. Prepare for the fight (rollback + repeatability)

Before changing behavior, ensure at least:

- **Rollback is possible**: the code is under version control (do not commit secrets).
- **Repeatability exists**: at least one step is automated (build / format / static analysis / test).
- **Fast feedback exists**: even one automated test is enough to start.

Note: do not start with a big rewrite. First, create the smallest automated route, then proceed.

## 2. Rough safety-net tests (characterization)

If unit tests are hard to write right now, first lock the current behavior at a coarse, entrypoint-near granularity.

- Call an entry point (handler / node / service / public API).
- Assert inputs/outputs or key observable effects.
- Prioritize “one test that runs” over perfect coverage.
- Example: one happy-path test + two representative branches.

If exact matching is difficult, strengthen in this order:

1) Start by asserting only **observable points** (state transitions, counts, categories).
2) Once stable, increase strictness only where needed.

## 3. Create seams (places you can substitute behavior)

When you find nondeterminism (random/time/UUID/I/O/concurrency), do not rely only on direct edits. Create a seam that lets tests substitute behavior.

Common targets:

- random
- clock/time
- UUID generation
- external I/O (HTTP/DB/FS)

### 3.1 Example: function injection (C++)

```cpp
using NextIndexFn = std::function<size_t(size_t)>;

class QuizCore {
 public:
  explicit QuizCore(NextIndexFn next_index) : next_index_(std::move(next_index)) {}

  size_t Next(size_t n) { return next_index_(n); }

 private:
  NextIndexFn next_index_;
};

// production
QuizCore core([](size_t n) { return static_cast<size_t>(std::rand()) % n; });

// test
QuizCore core_test([](size_t) { return 4; });
```

### 3.2 Example: TimeProvider

```cpp
class Clock {
 public:
  virtual ~Clock() = default;
  virtual std::chrono::system_clock::time_point Now() const = 0;
};

class SystemClock final : public Clock {
 public:
  std::chrono::system_clock::time_point Now() const override { return std::chrono::system_clock::now(); }
};

class FakeClock final : public Clock {
 public:
  explicit FakeClock(std::chrono::system_clock::time_point now) : now_(now) {}
  std::chrono::system_clock::time_point Now() const override { return now_; }
  void Set(std::chrono::system_clock::time_point now) { now_ = now; }

 private:
  std::chrono::system_clock::time_point now_;
};
```

## 4. Keep the outside thin, make the inside deterministic (Humble Object direction)

Move hard-to-test things (frameworks, SDKs, I/O) to a thin outer layer.
Make the inside deterministic: “input → output” is predictable.

- Outside: adaptation and connection only.
- Inside: rules and state transitions (core).

The goal is not “remove the outside”, but “make the outside thin”.

## 5. For spec changes: test → implement → tidy

Once you have a safety net and seams, switch to normal TDD:

Test List → one item at a time (Red/Green/Refactor).

- If the Test List grows too much, split the requirements.
- Move one item at a time; keep the safety net green.

## 6. Decide: Extract or Sprout

There are two main strategies for improving legacy code:

- **Extract**: protect existing behavior with tests, then extract gradually.
- **Sprout**: avoid touching legacy code heavily; add new, tested code and connect it.

Rule of thumb:

- If you can build a safety net → Extract is often viable.
- If touching legacy code is too risky → proceed with Sprout.

Record which you chose and why (e.g., in `docs/PLAN.md` or the review notes).

## 7. Separate facts from derived information

As requirements grow, direct state updates tend to drift out of consistency.

- Facts: what happened, when it happened (history, start/end times).
- Derived info: scores, trends, averages (computed from facts).

This separation helps you evolve metrics and computations safely.

## 8. Refine boundaries at the end

After the core grows, separate “volatile details” (SDK/DB/HTTP) from “stable policy” (core).

- When in doubt, invoke `$architecture-boundaries` and decide dependency direction + DTO/IF.

## 9. Minimal checklist

Before starting:

- [ ] At least one safety-net test exists to lock current behavior.
- [ ] A seam exists (or you have a plan) for nondeterminism (random/time/I/O).

Before submitting:

- [ ] Safety net + added tests are all green.
- [ ] Intent of seams and boundaries is readable (comments at coupling points).
- [ ] You can explain what you fixed as “unchanged”, and what you intentionally substituted.
