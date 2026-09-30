import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "accuracy"))
from run_accuracy import CATEGORIES, load_golden, percentile, summarise, write_outputs


class AccuracyRunnerTests(unittest.TestCase):
    def make_csv(self, rows):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "golden.csv"
        with path.open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=("row", "narrative", "label"))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_load_golden_validates_scope_labels_and_duplicates(self):
        path = self.make_csv([
            {"row": 10001, "narrative": "One", "label": CATEGORIES[0]},
            {"row": 10002, "narrative": "Two", "label": CATEGORIES[1]},
        ])
        self.assertEqual(len(load_golden(path, expected_count=2)), 2)

        duplicate = self.make_csv([
            {"row": 10001, "narrative": "One", "label": CATEGORIES[0]},
            {"row": 10001, "narrative": "Two", "label": CATEGORIES[1]},
        ])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            load_golden(duplicate, expected_count=2)

    def test_summary_uses_all_tickets_as_accuracy_denominator(self):
        records = [
            {"row": 10001, "expected": CATEGORIES[0], "predicted": CATEGORIES[0],
             "correct": True, "status": 201, "client_elapsed_ms": 100},
            {"row": 10002, "expected": CATEGORIES[1], "predicted": CATEGORIES[0],
             "correct": False, "status": 201, "client_elapsed_ms": 200},
            {"row": 10003, "expected": CATEGORIES[1], "predicted": None,
             "correct": False, "status": 502, "client_elapsed_ms": 50},
        ]
        summary = summarise(records, expected_total=3)
        self.assertEqual(summary["successful_classifications"], 2)
        self.assertEqual(summary["errors"], 1)
        self.assertAlmostEqual(summary["overall_accuracy"], 1 / 3)
        self.assertAlmostEqual(summary["valid_classification_accuracy"], 1 / 2)
        self.assertEqual(percentile([100, 200], 95), 200)

    def test_output_files_are_auditable(self):
        records = [
            {"row": 10001, "expected": CATEGORIES[0], "predicted": CATEGORIES[0],
             "correct": True, "status": 201, "model": "test:tag", "request_id": "r1",
             "client_elapsed_ms": 100, "ticket_id": 1, "error": None},
        ]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            write_outputs(output, records, expected_total=1)
            self.assertTrue((output / "predictions.csv").exists())
            self.assertTrue((output / "per_category.csv").exists())
            self.assertTrue((output / "confusion_matrix.csv").exists())
            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["correct"], 1)


if __name__ == "__main__":
    unittest.main()
