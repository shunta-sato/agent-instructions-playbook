# Working with legacy code (Python examples)

These examples mirror the “Create seams” guidance in the main reference and focus on
deterministic seams for nondeterminism and I/O.

## 3.1 Example: seam for external I/O (Python)

```py
from dataclasses import dataclass


@dataclass(frozen=True)
class ExchangeRate:
    from_currency: str
    to_currency: str
    rate: float


class RatesClient:
    def fetch(self, from_currency: str, to_currency: str) -> ExchangeRate:
        raise NotImplementedError


class LiveRatesClient(RatesClient):
    def fetch(self, from_currency: str, to_currency: str) -> ExchangeRate:
        # real HTTP call omitted
        return ExchangeRate(from_currency, to_currency, 1.12)


class StubRatesClient(RatesClient):
    def __init__(self, rate: float) -> None:
        self._rate = rate

    def fetch(self, from_currency: str, to_currency: str) -> ExchangeRate:
        return ExchangeRate(from_currency, to_currency, self._rate)
```

## 3.2 Example: seam for time (Python)

```py
from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        raise NotImplementedError


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(tz=timezone.utc)


class FixedClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def set(self, now: datetime) -> None:
        self._now = now
```
