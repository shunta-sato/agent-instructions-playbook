# Concurrency core reference

Use this document to decide **if** concurrency is needed, **how** to structure it, and **how** to verify it.

## Decision guide (compact)

**Work type**
- CPU-bound → prefer worker pools with bounded queues.
- I/O-bound → async/await or limited worker threads; watch external backpressure.
- Mixed → split phases (I/O stage → CPU stage) with separate queues.

**Required guarantees**
- Ordering → single-threaded stage or ordered queue.
- Latency → short critical sections; avoid blocking on shared locks.
- Throughput → parallelize independent units; cap concurrency.
- Bounded memory → bounded queues; backpressure or drop policy.

## Pattern catalog (language-agnostic)

Use the patterns below. Each entry lists **When it fits / What to watch / Minimal skeleton**.

### Immutable
- **When it fits:** shared read-mostly data; configuration snapshots.
- **What to watch:** avoid hidden mutation; copy cost.
- **Minimal skeleton:** create immutable value once; share by reference; replace wholesale on change.

### Producer–Consumer (Queue)
- **When it fits:** decouple input rate from processing rate.
- **What to watch:** unbounded growth; define backpressure/drop policy.
- **Minimal skeleton:** producer pushes to bounded queue; consumer loop pulls and processes.

### Worker Thread (Thread Pool / Executor)
- **When it fits:** parallelizable work items; CPU-bound tasks.
- **What to watch:** oversubscription; shared-state contention.
- **Minimal skeleton:** submit tasks to executor; limit pool size; join on shutdown.

### Guarded Suspension (Condition Variable / Await)
- **When it fits:** wait until state becomes ready (queue not empty, data available).
- **What to watch:** spurious wakeups; always re-check condition.
- **Minimal skeleton:** lock → while condition not met: wait → proceed.

### Balking (Skip if Not Needed)
- **When it fits:** avoid redundant work if state already satisfied.
- **What to watch:** missed updates; define “already done” clearly.
- **Minimal skeleton:** if state already satisfied → return; else perform.

### Read–Write Lock
- **When it fits:** many reads, few writes; allow parallel readers.
- **What to watch:** writer starvation; lock upgrades.
- **Minimal skeleton:** read lock for reads; write lock for mutation.

### Thread-Per-Message (Bounded)
- **When it fits:** short, bursty, isolated tasks; only with strict caps.
- **What to watch:** resource exhaustion; context-switch cost.
- **Minimal skeleton:** spawn thread for task with strict concurrency cap; join/cleanup.

### Future / Promise
- **When it fits:** async result delivery; pipeline stages.
- **What to watch:** cancellation propagation; blocking waits.
- **Minimal skeleton:** start task → return future → await/get with timeout.

### Two-Phase Termination (Graceful Shutdown)
- **When it fits:** background workers that must stop cleanly.
- **What to watch:** “stop accepting” vs “drain” ordering.
- **Minimal skeleton:** signal stop → stop accepting → drain queue → join workers.

### Active Object (Message-Based Async Object)
- **When it fits:** shared object accessed by many threads; serialize access.
- **What to watch:** queue growth; long-running handlers.
- **Minimal skeleton:** public methods enqueue messages; dedicated thread processes messages sequentially.

## Concurrency Plan template (mandatory)

Copy this into your response and fill it in.

### Concurrency Plan
- **Goal (NFR tie-in):**
- **Model (what runs concurrently; what does not):**
- **Ownership & shared state map:**
- **Synchronization strategy:**
- **Shutdown/cancellation strategy:**
- **Error propagation strategy:**
- **Observability (logs/metrics/traces):**
- **Verification (tests + tooling):**

### Risks & mitigations (summary)
- Risk:
- Mitigation:
