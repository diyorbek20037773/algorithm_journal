"""Concurrent-user load test against a running instance.

The client's terms of reference (§10) require the site to serve 200 users at
once without failing. This script is how that claim is checked rather than
asserted: it opens N concurrent virtual users, each of which reads pages the
way a visitor does — home, archive, an article, a search, a PDF — with a short
pause between clicks, for a fixed duration, and reports throughput, latency
percentiles and the error rate.

Run it against the production-mode gunicorn, never against `runserver`::

    python scripts/loadtest.py --base http://localhost:8020 --users 200 --seconds 60

Exit status is non-zero when the error rate exceeds --max-error-rate or the
p95 latency exceeds --max-p95-ms, so it can gate a deployment.
"""

from __future__ import annotations

import argparse
import asyncio
import random
import statistics
import sys
import time
from collections import Counter

import httpx

#: A reader's session, weighted towards the pages readers actually open.
PATHS: list[tuple[str, int]] = [
    ("/en/", 5),
    ("/uz/", 2),
    ("/ru/", 2),
    ("/en/issues/", 3),
    ("/en/issues/1/3/", 3),
    ("/en/article/14/", 6),
    ("/en/article/9/", 4),
    ("/en/article/3/", 3),
    ("/en/search/?q=inflation", 2),
    ("/en/search/?q=trade", 2),
    ("/en/about/editorial-board/", 2),
    ("/en/about/publication-ethics/", 1),
    ("/en/statistics/", 1),
    ("/article/14/pdf/", 2),
    ("/oai/?verb=Identify", 1),
    ("/api/v1/articles/", 1),
]


def _pick() -> str:
    paths = [p for p, w in PATHS for _ in range(w)]
    return random.choice(paths)


async def _user(
    client: httpx.AsyncClient,
    base: str,
    deadline: float,
    think: float,
    latencies: list[float],
    statuses: Counter,
    errors: list[str],
) -> None:
    while time.monotonic() < deadline:
        path = _pick()
        start = time.perf_counter()
        try:
            response = await client.get(base + path)
            elapsed = (time.perf_counter() - start) * 1000
            latencies.append(elapsed)
            statuses[response.status_code] += 1
            if response.status_code >= 500:
                errors.append(f"{response.status_code} {path}")
        except httpx.HTTPError as exc:
            latencies.append((time.perf_counter() - start) * 1000)
            statuses["exc"] += 1
            errors.append(f"{type(exc).__name__} {path}")
        await asyncio.sleep(random.uniform(0, think))


async def run(base: str, users: int, seconds: int, think: float) -> dict:
    latencies: list[float] = []
    statuses: Counter = Counter()
    errors: list[str] = []
    limits = httpx.Limits(max_connections=users + 10, max_keepalive_connections=users)
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(limits=limits, timeout=timeout, follow_redirects=True) as client:
        deadline = time.monotonic() + seconds
        # Ramp users in over the first few seconds so the server is not hit by
        # N simultaneous first requests, which no real audience produces.
        tasks = []
        for index in range(users):
            tasks.append(
                asyncio.create_task(
                    _user(client, base, deadline, think, latencies, statuses, errors)
                )
            )
            if index % 20 == 19:
                await asyncio.sleep(0.25)
        await asyncio.gather(*tasks)

    total = len(latencies)
    failed = sum(v for k, v in statuses.items() if k == "exc" or (isinstance(k, int) and k >= 500))
    latencies.sort()

    def pct(p: float) -> float:
        if not latencies:
            return 0.0
        return latencies[min(len(latencies) - 1, int(len(latencies) * p))]

    return {
        "users": users,
        "seconds": seconds,
        "requests": total,
        "rps": round(total / seconds, 1),
        "error_rate": round(failed / total * 100, 2) if total else 0.0,
        "p50_ms": round(pct(0.50)),
        "p95_ms": round(pct(0.95)),
        "p99_ms": round(pct(0.99)),
        "max_ms": round(latencies[-1]) if latencies else 0,
        "mean_ms": round(statistics.mean(latencies)) if latencies else 0,
        "statuses": dict(sorted(statuses.items(), key=lambda kv: str(kv[0]))),
        "sample_errors": errors[:8],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://localhost:8020")
    parser.add_argument("--users", type=int, default=200)
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--think", type=float, default=3.0, help="max pause between clicks, s")
    parser.add_argument("--max-error-rate", type=float, default=1.0, help="percent")
    parser.add_argument("--max-p95-ms", type=int, default=3000)
    args = parser.parse_args()

    result = asyncio.run(run(args.base.rstrip("/"), args.users, args.seconds, args.think))

    print(f"\n{args.users} concurrent users for {args.seconds}s against {args.base}")
    print(f"  requests     {result['requests']}  ({result['rps']} req/s)")
    print(f"  error rate   {result['error_rate']}%")
    print(
        f"  latency ms   p50={result['p50_ms']}  p95={result['p95_ms']}  "
        f"p99={result['p99_ms']}  max={result['max_ms']}  mean={result['mean_ms']}"
    )
    print(f"  statuses     {result['statuses']}")
    for line in result["sample_errors"]:
        print(f"  error        {line}")

    ok = result["error_rate"] <= args.max_error_rate and result["p95_ms"] <= args.max_p95_ms
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
