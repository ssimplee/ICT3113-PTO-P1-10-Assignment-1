"""Run and audit the formal golden-set accuracy test through POST /tickets.

The default invocation is validation-only. Sending golden tickets requires both
--confirm-formal-run and a committed prediction record whose status is FROZEN.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CATEGORIES = (
    "Credit reporting",
    "Debt collection",
    "Mortgage",
    "Credit card",
    "Bank account or service",
    "Consumer loan",
    "Money transfer or service",
)
ERROR_BUCKET = "__ERROR__"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_golden(path: Path, expected_count: int = 175) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"row", "narrative", "label"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"Golden CSV must contain {sorted(required)}; found {reader.fieldnames}")
        tickets = []
        for line_number, item in enumerate(reader, start=2):
            try:
                row_id = int(item["row"])
            except (TypeError, ValueError) as error:
                raise ValueError(f"Line {line_number}: row must be an integer") from error
            narrative = (item["narrative"] or "").strip()
            label = (item["label"] or "").strip()
            if not 10000 <= row_id <= 10999:
                raise ValueError(f"Line {line_number}: row {row_id} is outside Group 10 range")
            if not narrative:
                raise ValueError(f"Line {line_number}: narrative is empty")
            if label not in CATEGORIES:
                raise ValueError(f"Line {line_number}: unsupported label {label!r}")
            tickets.append({"row": row_id, "narrative": narrative, "label": label})
    if len(tickets) != expected_count:
        raise ValueError(f"Expected {expected_count} golden tickets; found {len(tickets)}")
    row_ids = [ticket["row"] for ticket in tickets]
    if len(row_ids) != len(set(row_ids)):
        duplicates = sorted(row for row, count in Counter(row_ids).items() if count > 1)
        raise ValueError(f"Duplicate golden row IDs: {duplicates}")
    return tickets


def git(*args: str, cwd: Path, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True,
        text=not binary,
    )
    return result.stdout


def repo_relative(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"{path} must be inside repository {repo}") from error


def verify_frozen_inputs(repo: Path, prediction_path: Path, golden_path: Path,
                         prediction_commit: str) -> str:
    resolved = str(git("rev-parse", f"{prediction_commit}^{{commit}}", cwd=repo)).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", resolved):
        raise ValueError("Unable to resolve prediction commit to a full Git SHA")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", resolved, "HEAD"], cwd=repo
    )
    if ancestor.returncode != 0:
        raise ValueError("Prediction commit is not an ancestor of the current HEAD")

    for path in (prediction_path, golden_path):
        relative = repo_relative(path, repo)
        try:
            committed_blob = str(git("rev-parse", f"{resolved}:{relative}", cwd=repo)).strip()
        except subprocess.CalledProcessError as error:
            raise ValueError(f"{relative} is not present in prediction commit {resolved}") from error
        if not path.is_file():
            raise ValueError(f"{relative} does not exist in the working tree")
        current_blob = str(git("hash-object", "--path", relative, str(path), cwd=repo)).strip()
        if current_blob != committed_blob:
            raise ValueError(f"{relative} differs from the frozen copy in {resolved}")

    frozen_text = prediction_path.read_text(encoding="utf-8")
    if not re.search(r"(?im)^\*\*Status:\*\*\s*FROZEN\s*$", frozen_text):
        raise ValueError("Prediction record must contain '**Status:** FROZEN' before a formal run")
    return resolved


def request_json(method: str, url: str, timeout: float,
                 body: dict[str, object] | None = None) -> tuple[int, dict[str, str], object]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(url, method=method, data=data,
                      headers={"Content-Type": "application/json"})
    try:
        response = urlopen(request, timeout=timeout)
    except HTTPError as error:
        response = error
    with response:
        raw = response.read()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"unparseable_body": raw.decode("utf-8", errors="replace")}
        return response.status, dict(response.headers.items()), payload


def read_completed(path: Path) -> dict[int, dict[str, object]]:
    if not path.exists():
        return {}
    completed = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        row_id = int(record["row"])
        if row_id in completed:
            raise ValueError(f"Duplicate row {row_id} in {path} at line {line_number}")
        completed[row_id] = record
    return completed


def summarise(records: list[dict[str, object]], expected_total: int) -> dict[str, object]:
    successful = [record for record in records if record.get("status") == 201]
    correct = sum(bool(record.get("correct")) for record in successful)
    errors = expected_total - len(successful)
    by_category: dict[str, dict[str, object]] = {}
    for category in CATEGORIES:
        category_records = [r for r in records if r.get("expected") == category]
        category_correct = sum(bool(r.get("correct")) for r in category_records)
        by_category[category] = {
            "total": len(category_records),
            "correct": category_correct,
            "errors": sum(r.get("status") != 201 for r in category_records),
            "accuracy": category_correct / len(category_records) if category_records else None,
        }
    elapsed = sorted(float(r["client_elapsed_ms"]) for r in successful)
    return {
        "expected_tickets": expected_total,
        "records": len(records),
        "successful_classifications": len(successful),
        "errors": errors,
        "correct": correct,
        "overall_accuracy": correct / expected_total if expected_total else None,
        "valid_classification_accuracy": correct / len(successful) if successful else None,
        "client_latency_ms": {
            "min": min(elapsed) if elapsed else None,
            "median": percentile(elapsed, 50),
            "p95": percentile(elapsed, 95),
            "max": max(elapsed) if elapsed else None,
        },
        "per_category": by_category,
    }


def percentile(values: list[float], percent: int) -> float | None:
    if not values:
        return None
    rank = max(1, (percent * len(values) + 99) // 100)
    return values[rank - 1]


def write_outputs(output_dir: Path, records: list[dict[str, object]],
                  expected_total: int) -> dict[str, object]:
    ordered = sorted(records, key=lambda record: int(record["row"]))
    summary = summarise(ordered, expected_total)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    fields = (
        "row", "expected", "predicted", "correct", "status", "model",
        "request_id", "client_elapsed_ms", "ticket_id", "error",
    )
    with (output_dir / "predictions.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(ordered)

    with (output_dir / "per_category.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(("category", "total", "correct", "errors", "accuracy"))
        for category in CATEGORIES:
            values = summary["per_category"][category]
            writer.writerow((category, values["total"], values["correct"],
                             values["errors"], values["accuracy"]))

    matrix: dict[str, Counter[str]] = defaultdict(Counter)
    for record in ordered:
        predicted = str(record.get("predicted") or ERROR_BUCKET)
        matrix[str(record["expected"])][predicted] += 1
    columns = (*CATEGORIES, ERROR_BUCKET)
    with (output_dir / "confusion_matrix.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(("actual\\predicted", *columns))
        for actual in CATEGORIES:
            writer.writerow((actual, *(matrix[actual][predicted] for predicted in columns)))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden", type=Path,
                        default=Path("golden-set/golden_tickets_175_baseline.csv"))
    parser.add_argument("--prediction-record", type=Path,
                        default=Path("predictions/prediction_record.md"))
    parser.add_argument("--prediction-commit",
                        help="Commit containing the frozen prediction record and golden CSV")
    parser.add_argument("--model-tag", required=True,
                        help="Exact expected Ollama tag returned by POST /tickets")
    parser.add_argument("--model-digest", required=True,
                        help="Full sha256 digest recorded after pulling the exact tag")
    parser.add_argument("--url", default="http://127.0.0.1:18000")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--allow-nonempty-database", action="store_true")
    parser.add_argument("--confirm-formal-run", action="store_true",
                        help="Actually submit the 175 golden tickets")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    golden_path = (repo / args.golden).resolve() if not args.golden.is_absolute() else args.golden
    prediction_path = ((repo / args.prediction_record).resolve()
                       if not args.prediction_record.is_absolute() else args.prediction_record)
    output_dir = ((repo / args.output_dir).resolve()
                  if not args.output_dir.is_absolute() else args.output_dir)
    tickets = load_golden(golden_path)

    if not re.fullmatch(r"sha256:[0-9a-f]{64}", args.model_digest):
        raise ValueError("--model-digest must be a full value in sha256:<64 lowercase hex> form")

    print(f"Validated {len(tickets)} unique Group 10 golden tickets.")
    print(f"Golden SHA-256: {sha256_file(golden_path)}")
    if not args.confirm_formal_run:
        print("Validation only: no ticket was submitted. Add --confirm-formal-run after freeze gates pass.")
        return 0
    if not args.prediction_commit:
        raise ValueError("--prediction-commit is required for a formal run")
    frozen_commit = verify_frozen_inputs(
        repo, prediction_path, golden_path, args.prediction_commit
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "raw_predictions.jsonl"
    existing_files = [path for path in output_dir.iterdir() if path.is_file()]
    if existing_files and not args.resume:
        raise ValueError(f"Output directory is not empty: {output_dir}; use a new directory or --resume")
    completed = read_completed(raw_path) if args.resume else {}

    try:
        stats_status, _, stats = request_json("GET", args.url.rstrip("/") + "/stats", args.timeout)
    except URLError as error:
        raise RuntimeError(f"Cannot reach service at {args.url}: {error}") from error
    if stats_status != 200 or not isinstance(stats, dict):
        raise RuntimeError(f"Service preflight failed with status {stats_status}: {stats}")
    if int(stats.get("total", -1)) != 0 and not (args.allow_nonempty_database or args.resume):
        raise RuntimeError(
            f"Service database contains {stats.get('total')} tickets. Use an isolated empty Compose "
            "project for a formal run; override only with --allow-nonempty-database."
        )

    manifest_path = output_dir / "manifest.json"
    if args.resume:
        if not manifest_path.exists():
            raise ValueError("Cannot resume without manifest.json")
        old_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if old_manifest["golden_sha256"] != sha256_file(golden_path):
            raise ValueError("Golden CSV changed since this run started")
        if old_manifest["model_tag"] != args.model_tag or old_manifest["model_digest"] != args.model_digest:
            raise ValueError("Model tag or digest differs from the existing run manifest")
        manifest = old_manifest
    else:
        manifest = {
            "run_started_at": utc_now(),
            "git_head": str(git("rev-parse", "HEAD", cwd=repo)).strip(),
            "prediction_commit": frozen_commit,
            "golden_path": repo_relative(golden_path, repo),
            "golden_sha256": sha256_file(golden_path),
            "prediction_record_path": repo_relative(prediction_path, repo),
            "model_tag": args.model_tag,
            "model_digest": args.model_digest,
            "service_url": args.url,
            "timeout_seconds": args.timeout,
            "database_total_at_start": stats.get("total"),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with raw_path.open("a", encoding="utf-8", buffering=1) as raw:
        for index, ticket in enumerate(tickets, start=1):
            row_id = int(ticket["row"])
            if row_id in completed:
                continue
            started = time.perf_counter()
            status = 0
            headers: dict[str, str] = {}
            payload: object = {}
            error_text = None
            try:
                status, headers, payload = request_json(
                    "POST", args.url.rstrip("/") + "/tickets", args.timeout,
                    {"narrative": ticket["narrative"]},
                )
            except (URLError, TimeoutError) as error:
                error_text = f"{type(error).__name__}: {error}"
            elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
            body = payload if isinstance(payload, dict) else {}
            model = body.get("model")
            predicted = body.get("category") if status == 201 else None
            if status == 201 and model != args.model_tag:
                raise RuntimeError(
                    f"Service returned model {model!r}, expected {args.model_tag!r}. "
                    "Stop and recreate the service with the intended OLLAMA_MODEL."
                )
            record = {
                "sequence": index,
                "row": row_id,
                "expected": ticket["label"],
                "predicted": predicted,
                "correct": predicted == ticket["label"] if status == 201 else False,
                "status": status,
                "model": model,
                "request_id": headers.get("X-Request-ID") or headers.get("X-Request-Id"),
                "client_elapsed_ms": elapsed_ms,
                "ticket_id": body.get("id"),
                "error": error_text or body.get("error"),
                "recorded_at": utc_now(),
            }
            raw.write(json.dumps(record, ensure_ascii=False) + "\n")
            completed[row_id] = record
            print(f"[{index:03}/{len(tickets)}] row={row_id} status={status} "
                  f"predicted={predicted!r} expected={ticket['label']!r}")

    records = list(completed.values())
    summary = write_outputs(output_dir, records, len(tickets))
    manifest["run_finished_at"] = utc_now()
    manifest["records_written"] = len(records)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["errors"] == 0 and len(records) == len(tickets) else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
