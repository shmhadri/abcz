from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LocustSummary:
    requests: int
    failures: int
    failure_rate: float
    requests_per_second: float
    avg_response_ms: float
    p50_response_ms: float
    p95_response_ms: float
    p99_response_ms: float
    max_response_ms: float
    slowest_name: str
    slowest_p95_ms: float


def _float(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key) or 0)
    except ValueError:
        return 0.0


def _int(row: dict[str, str], key: str) -> int:
    try:
        return int(float(row.get(key) or 0))
    except ValueError:
        return 0


def summarize_stats_csv(path: str | Path) -> LocustSummary:
    rows = list(csv.DictReader(Path(path).open(newline="", encoding="utf-8")))
    if not rows:
        raise ValueError("Locust stats CSV is empty.")

    aggregate = next((row for row in rows if row.get("Name") == "Aggregated"), rows[-1])
    endpoint_rows = [row for row in rows if row.get("Name") != "Aggregated"]
    slowest = max(endpoint_rows or [aggregate], key=lambda row: _float(row, "95%"))

    requests = _int(aggregate, "Request Count")
    failures = _int(aggregate, "Failure Count")
    failure_rate = (failures / requests) * 100 if requests else 0
    return LocustSummary(
        requests=requests,
        failures=failures,
        failure_rate=round(failure_rate, 2),
        requests_per_second=round(_float(aggregate, "Requests/s"), 2),
        avg_response_ms=round(_float(aggregate, "Average Response Time"), 2),
        p50_response_ms=round(_float(aggregate, "50%"), 2),
        p95_response_ms=round(_float(aggregate, "95%"), 2),
        p99_response_ms=round(_float(aggregate, "99%"), 2),
        max_response_ms=round(_float(aggregate, "Max Response Time"), 2),
        slowest_name=slowest.get("Name") or "",
        slowest_p95_ms=round(_float(slowest, "95%"), 2),
    )


def format_summary(summary: LocustSummary) -> str:
    return "\n".join([
        f"requests={summary.requests}",
        f"failures={summary.failures}",
        f"failure_rate={summary.failure_rate}%",
        f"requests_per_second={summary.requests_per_second}",
        f"avg_response_ms={summary.avg_response_ms}",
        f"p50_response_ms={summary.p50_response_ms}",
        f"p95_response_ms={summary.p95_response_ms}",
        f"p99_response_ms={summary.p99_response_ms}",
        f"max_response_ms={summary.max_response_ms}",
        f"slowest_name={summary.slowest_name}",
        f"slowest_p95_ms={summary.slowest_p95_ms}",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a Locust *_stats.csv file.")
    parser.add_argument("stats_csv", help="Path to a Locust stats CSV file.")
    args = parser.parse_args()
    print(format_summary(summarize_stats_csv(args.stats_csv)))


if __name__ == "__main__":
    main()
