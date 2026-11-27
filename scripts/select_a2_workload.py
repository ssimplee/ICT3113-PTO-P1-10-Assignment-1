"""Select the fixed Assignment 2 speed-test tickets from Group 10's rows outside the golden set."""

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workload-tickets/ict3113_tickets.csv"
GOLDEN = ROOT / "golden-set/golden_tickets_175_baseline.csv"
OUTPUT = ROOT / "jmeter/a2-workload"
SEED = 3113
WORKLOAD_TICKETS = 90
LONG_EVERY = 4  # every fourth workload ticket is a long one


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def words(row):
    return len(row["narrative"].split())


def write(name, rows):
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["row", "words", "length", "narrative"])
        for kind, row in rows:
            writer.writerow([row["row"], words(row), kind, row["narrative"]])


def main():
    csv.field_size_limit(10**9)
    golden = {row["row"] for row in read(GOLDEN)}
    pool = [row for row in read(SOURCE) if 10000 <= int(row["row"]) <= 10999 and row["row"] not in golden]
    assert len(pool) == 825
    for row in pool:
        # Git stores these files with LF endings, so the narrative must not depend on CRLF.
        row["narrative"] = row["narrative"].replace("\r\n", "\n")
    counts = sorted(words(row) for row in pool)
    p25, p75, p90 = (counts[int(q * (len(counts) - 1))] for q in (0.25, 0.75, 0.90))
    typical = [row for row in pool if p25 <= words(row) <= p75]
    long = [row for row in pool if words(row) >= p90]
    rng = random.Random(SEED)
    rng.shuffle(typical)
    rng.shuffle(long)
    workload = [("long", long.pop()) if position % LONG_EVERY == 0 else ("typical", typical.pop())
                for position in range(1, WORKLOAD_TICKETS + 1)]
    OUTPUT.mkdir(exist_ok=True)
    write("workload.csv", workload)
    write("warmup.csv", [("typical", typical.pop()) for _ in range(3)])
    write("s-timing.csv", [("typical", typical.pop()) for _ in range(3)])
    print(f"typical = {p25}-{p75} words, long = {p90} words or more")
    print(f"workload: {len(workload)} tickets, {sum(kind == 'long' for kind, _ in workload)} long")


if __name__ == "__main__":
    main()
