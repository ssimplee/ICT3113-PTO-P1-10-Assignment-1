"""Reproduce narrative-length statistics for the frozen Golden Set."""

from __future__ import annotations

import csv
import math
import statistics
from collections import Counter
from pathlib import Path


SOURCE = Path("golden-set/golden_tickets_175_baseline.csv")


def nearest_rank(values: list[int], quantile: float) -> int:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(quantile * len(ordered)) - 1)]


def describe(values: list[int]) -> dict[str, float | int]:
    return {
        "min": min(values),
        "mean": round(statistics.mean(values), 1),
        "p50": statistics.median(values),
        "p75": nearest_rank(values, 0.75),
        "p90": nearest_rank(values, 0.90),
        "p95": nearest_rank(values, 0.95),
        "p99": nearest_rank(values, 0.99),
        "max": max(values),
    }


def main() -> None:
    with SOURCE.open(encoding="utf-8-sig", newline="") as source_file:
        rows = list(csv.DictReader(source_file))

    narratives = [row["narrative"] for row in rows]
    row_ids = [row["row"] for row in rows]
    print(f"tickets={len(rows)}")
    print(f"blank_narratives={sum(not value.strip() for value in narratives)}")
    print(f"duplicate_row_ids={len(row_ids) - len(set(row_ids))}")
    print(f"characters={describe([len(value) for value in narratives])}")
    print(f"words={describe([len(value.split()) for value in narratives])}")
    print(f"labels={dict(sorted(Counter(row['label'] for row in rows).items()))}")


if __name__ == "__main__":
    main()
