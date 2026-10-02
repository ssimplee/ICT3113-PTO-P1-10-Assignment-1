#!/usr/bin/env python3
"""Validate the human-label audit workbook without third-party dependencies."""

from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
CATEGORIES = (
    "Bank account or service",
    "Consumer loan",
    "Credit card",
    "Credit reporting",
    "Debt collection",
    "Money transfer or service",
    "Mortgage",
)


def normalize_newlines(value: str) -> str:
    """Treat CSV CRLF and Excel LF line breaks as the same narrative text."""
    return value.replace("\r\n", "\n").replace("\r", "\n")


def column_index(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference)
    if letters is None:
        raise ValueError(f"Invalid cell reference: {reference}")
    result = 0
    for character in letters.group(0):
        result = result * 26 + ord(character) - ord("A") + 1
    return result - 1


def read_sheet(archive: zipfile.ZipFile, path: str, shared: list[str]) -> list[list[str]]:
    root = ET.fromstring(archive.read(path))
    rows: list[list[str]] = []
    for row in root.findall(f".//{NS}row"):
        values: dict[int, str] = {}
        for cell in row.findall(f"{NS}c"):
            index = column_index(cell.attrib["r"])
            value_node = cell.find(f"{NS}v")
            if cell.attrib.get("t") == "s" and value_node is not None:
                value = shared[int(value_node.text or "0")]
            elif cell.attrib.get("t") == "inlineStr":
                value = "".join(node.text or "" for node in cell.iter(f"{NS}t"))
            else:
                value = value_node.text if value_node is not None and value_node.text else ""
            values[index] = value
        width = max(values, default=-1) + 1
        rows.append([values.get(index, "") for index in range(width)])
    return rows


def records(rows: list[list[str]], expected_headers: list[str]) -> list[dict[str, str]]:
    if not rows or rows[0][: len(expected_headers)] != expected_headers:
        raise ValueError(f"Unexpected headers: {rows[0] if rows else 'empty sheet'}")
    return [dict(zip(expected_headers, row + [""] * (len(expected_headers) - len(row))))
            for row in rows[1:]]


def load_workbook(path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, str], dict[str, int]]:
    with zipfile.ZipFile(path) as archive:
        shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        shared = ["".join(node.text or "" for node in item.iter(f"{NS}t"))
                  for item in shared_root.findall(f"{NS}si")]
        golden_rows = read_sheet(archive, "xl/worksheets/sheet1.xml", shared)
        audit_rows = read_sheet(archive, "xl/worksheets/sheet2.xml", shared)
        summary_rows = read_sheet(archive, "xl/worksheets/sheet3.xml", shared)

    golden = records(golden_rows, ["row", "narrative", "label"])
    audit = records(audit_rows, [
        "row", "narrative", "member3_label", "thaedeus_label",
        "final_golden_label", "resolution", "adjudication_reason",
    ])
    summary_metrics = {row[0]: row[1] for row in summary_rows[1:] if len(row) > 1 and row[0]}
    summary_categories = {
        row[3]: int(row[4]) for row in summary_rows[1:]
        if len(row) > 4 and row[3] in CATEGORIES
    }
    return golden, audit, summary_metrics, summary_categories


def validate(workbook_path: Path, csv_path: Path) -> dict[str, object]:
    golden, audit, summary_metrics, summary_categories = load_workbook(workbook_path)
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        csv_rows = list(csv.DictReader(handle))

    errors: list[str] = []
    if len(golden) != 175 or len(audit) != 175 or len(csv_rows) != 175:
        errors.append(f"Expected 175 rows; workbook golden={len(golden)}, audit={len(audit)}, csv={len(csv_rows)}")

    for name, rows in (("workbook golden", golden), ("audit", audit), ("CSV", csv_rows)):
        identifiers = [row["row"] for row in rows]
        if len(identifiers) != len(set(identifiers)):
            errors.append(f"{name} contains duplicate row identifiers")

    csv_by_row = {row["row"]: row for row in csv_rows}
    audit_by_row = {row["row"]: row for row in audit}
    workbook_by_row = {row["row"]: row for row in golden}
    if set(csv_by_row) != set(audit_by_row) or set(csv_by_row) != set(workbook_by_row):
        errors.append("Workbook and CSV row-identifier sets differ")

    agreements = 0
    disagreements = 0
    for row_id, csv_row in csv_by_row.items():
        audit_row = audit_by_row.get(row_id)
        workbook_row = workbook_by_row.get(row_id)
        if audit_row is None or workbook_row is None:
            continue
        for field in ("narrative", "label"):
            workbook_field = "final_golden_label" if field == "label" else field
            csv_value = normalize_newlines(csv_row[field]) if field == "narrative" else csv_row[field]
            workbook_value = normalize_newlines(workbook_row[field]) if field == "narrative" else workbook_row[field]
            audit_value = normalize_newlines(audit_row[workbook_field]) if field == "narrative" else audit_row[workbook_field]
            if csv_value != workbook_value:
                errors.append(f"Row {row_id}: CSV and Golden_Set_175 differ in {field}")
            if csv_value != audit_value:
                errors.append(f"Row {row_id}: CSV and Audit_Trail differ in {field}")

        left = audit_row["member3_label"]
        right = audit_row["thaedeus_label"]
        final = audit_row["final_golden_label"]
        invalid = [label for label in (left, right, final) if label not in CATEGORIES]
        if invalid:
            errors.append(f"Row {row_id}: missing or unsupported labels {invalid}")
        if not audit_row["adjudication_reason"].strip():
            errors.append(f"Row {row_id}: missing adjudication reason")
        if left == right:
            agreements += 1
            if final != left or audit_row["resolution"] != "Initial annotator agreement":
                errors.append(f"Row {row_id}: inconsistent agreement resolution")
        else:
            disagreements += 1
            if audit_row["resolution"] != "Adjudicated after discussion":
                errors.append(f"Row {row_id}: inconsistent disagreement resolution")

    labels_a = Counter(row["member3_label"] for row in audit)
    labels_b = Counter(row["thaedeus_label"] for row in audit)
    final_counts = Counter(row["final_golden_label"] for row in audit)
    total = len(audit)
    observed = agreements / total if total else 0.0
    expected = sum(labels_a[label] * labels_b[label] for label in CATEGORIES) / (total * total) if total else 0.0
    kappa = (observed - expected) / (1 - expected) if expected != 1 else 1.0

    expected_summary = {
        "Total golden tickets": str(total),
        "Initial agreements": str(agreements),
        "Adjudicated disagreements": str(disagreements),
        "Missing final labels": str(sum(not row["final_golden_label"] for row in audit)),
    }
    if summary_metrics != expected_summary:
        errors.append(f"Summary metrics differ: workbook={summary_metrics}, calculated={expected_summary}")
    if summary_categories != dict(final_counts):
        errors.append(f"Summary category counts differ: workbook={summary_categories}, calculated={dict(final_counts)}")

    report: dict[str, object] = {
        "tickets": total,
        "agreements": agreements,
        "disagreements": disagreements,
        "raw_agreement": observed,
        "expected_agreement": expected,
        "cohens_kappa": kappa,
        "annotator_a_counts": dict(sorted(labels_a.items())),
        "annotator_b_counts": dict(sorted(labels_b.items())),
        "final_counts": dict(sorted(final_counts.items())),
        "errors": errors,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=Path("golden-set/golden_tickets_175_baseline_audit_trail.xlsx"))
    parser.add_argument("--golden-csv", type=Path, default=Path("golden-set/golden_tickets_175_baseline.csv"))
    args = parser.parse_args()
    report = validate(args.workbook, args.golden_csv)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
