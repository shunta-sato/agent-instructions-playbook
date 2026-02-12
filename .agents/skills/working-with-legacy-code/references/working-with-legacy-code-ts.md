# Working with legacy code (TypeScript examples)

These examples mirror the “Create seams” guidance in the main reference and focus on
deterministic seams for nondeterminism and I/O.

## 3.1 Example: seam for retry backoff (TypeScript)

```ts
type BackoffFn = (attempt: number) => number;

class RetryPolicy {
  constructor(private readonly backoffMs: BackoffFn) {}

  delayFor(attempt: number): number {
    return this.backoffMs(attempt);
  }
}

// production: exponential backoff with cap
const prodPolicy = new RetryPolicy((attempt) =>
  Math.min(1000, 25 * 2 ** attempt),
);

// test: deterministic, fast
const testPolicy = new RetryPolicy(() => 0);
```

## 3.2 Example: seam for external I/O (TypeScript)

```ts
type FetchJson = (url: string) => Promise<{ total: number }>;

class MetricsClient {
  constructor(private readonly fetchJson: FetchJson) {}

  async totalUsers(): Promise<number> {
    const result = await this.fetchJson("/metrics/users");
    return result.total;
  }
}

// production: real fetch wrapper
const prodClient = new MetricsClient(async (url) => {
  const response = await fetch(url);
  return response.json();
});

// test: deterministic stub
const testClient = new MetricsClient(async () => ({ total: 42 }));
```
