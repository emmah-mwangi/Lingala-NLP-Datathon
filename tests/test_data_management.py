"""
test_data_management.py — Tests for data_quality, ingest_batch and reconcile.

Run from the repository root:
    python -m pytest tests/test_data_management.py -v

These tests use synthetic fixture rows (not real Lingala contributions).
They verify structural and logic behaviour only.
"""
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import data_quality
import ingest_batch
import reconcile

# ── Shared fixture helpers ────────────────────────────────────────────────────

CONTRIB_COLS = [
    "record_id", "language", "text", "label",
    "source_dataset", "source_version", "source_record_id", "source_url",
    "source_method", "licence_or_permission",
    "contributor_code", "reviewer_code", "review_status",
    "group_id", "split",
]


def _make_row(**overrides) -> dict:
    base = {
        "record_id": "T07-001",
        "language": "ln",
        "text": "Tala mbula lelo.",
        "label": "weather_query",
        "source_dataset": "team07_lingala_v1",
        "source_version": "1.0",
        "source_record_id": "T07-001",
        "source_url": "not_applicable",
        "source_method": "original_human",
        "licence_or_permission": "team_permission",
        "contributor_code": "T07-V1",
        "reviewer_code": "T07-A",
        "review_status": "independently_reviewed",
        "group_id": "T07-001",
        "split": "test",
    }
    base.update(overrides)
    return base


def _csv(rows: list[dict], tmp_path: Path, name: str = "test.csv") -> Path:
    p = tmp_path / name
    pd.DataFrame(rows, columns=CONTRIB_COLS).to_csv(p, index=False)
    return p


# ── data_quality tests ────────────────────────────────────────────────────────

class TestDataQuality:
    def test_clean_record_no_issues(self, tmp_path):
        p = _csv([_make_row()], tmp_path)
        result = data_quality.check(str(p))
        assert result["counts"] == {}, f"Unexpected flags: {result['issues']}"

    def test_invalid_label_flagged(self, tmp_path):
        p = _csv([_make_row(label="not_a_label")], tmp_path)
        result = data_quality.check(str(p))
        assert "invalid_label" in result["counts"]

    def test_empty_text_flagged(self, tmp_path):
        p = _csv([_make_row(text="")], tmp_path)
        result = data_quality.check(str(p))
        assert "empty_field" in result["counts"]

    def test_duplicate_id_flagged(self, tmp_path):
        rows = [_make_row(record_id="T07-001", text="Tala mbula lelo."),
                _make_row(record_id="T07-001", text="Mbula ekoya.")]
        p = _csv(rows, tmp_path)
        result = data_quality.check(str(p))
        assert "duplicate_id" in result["counts"]

    def test_exact_duplicate_text_flagged(self, tmp_path):
        rows = [_make_row(record_id="T07-001", text="Tala mbula lelo."),
                _make_row(record_id="T07-002", text="Tala mbula lelo.")]
        p = _csv(rows, tmp_path)
        result = data_quality.check(str(p))
        assert "exact_duplicate_text" in result["counts"]

    def test_near_duplicate_flagged(self, tmp_path):
        rows = [_make_row(record_id="T07-001", text="Tala mbula lelo."),
                _make_row(record_id="T07-002", text="Tala mbula leloo.")]
        p = _csv(rows, tmp_path)
        result = data_quality.check(str(p), near_dup_threshold=0.85)
        assert "near_duplicate_text" in result["counts"]

    def test_pii_phone_flagged(self, tmp_path):
        p = _csv([_make_row(text="Bela ngai na 0712345678.")], tmp_path)
        result = data_quality.check(str(p))
        assert "pii_pattern" in result["counts"]

    def test_unrecognised_author_flagged(self, tmp_path):
        p = _csv([_make_row(contributor_code="UNKNOWN")], tmp_path)
        result = data_quality.check(str(p))
        assert "unrecognised_author" in result["counts"]

    def test_missing_file_returns_load_error(self):
        result = data_quality.check("data/does_not_exist.csv")
        assert "load_error" in result["counts"]

    def test_no_auto_deletion(self, tmp_path):
        """Flagged records must remain in the source file — checker never deletes."""
        p = _csv([_make_row(label="bad_label")], tmp_path)
        data_quality.check(str(p))
        df = pd.read_csv(p, dtype=str)
        assert len(df) == 1  # record still present


# ── ingest_batch tests ────────────────────────────────────────────────────────

BATCH_COLS = [
    "record_id", "language", "text", "label",
    "source_dataset", "source_version", "source_record_id", "source_url",
    "source_method", "licence_or_permission",
    "contributor_code", "reviewer_code", "review_status",
    "group_id", "split",
]


def _batch_csv(rows: list[dict], tmp_path: Path) -> Path:
    p = tmp_path / "batch.csv"
    pd.DataFrame(rows, columns=BATCH_COLS).to_csv(p, index=False)
    return p


class TestIngestBatch:
    def _run(self, rows, tmp_path, existing=None):
        """Helper: run ingest with isolated contribution.csv and record_log.csv."""
        contrib = tmp_path / "contribution.csv"
        log_dir = tmp_path / "private" / "source_log"
        log_dir.mkdir(parents=True)
        log = log_dir / "record_log.csv"

        if existing:
            pd.DataFrame(existing, columns=CONTRIB_COLS).to_csv(contrib, index=False)
        else:
            pd.DataFrame(columns=CONTRIB_COLS).to_csv(contrib, index=False)

        pd.DataFrame(columns=[
            "record_id", "contributor_code", "source_type", "batch",
            "date_received", "assigned_label", "review_status",
            "correction_status", "approval_status", "notes",
        ]).to_csv(log, index=False)

        batch = _batch_csv(rows, tmp_path)

        # Patch module-level paths
        orig_contrib = ingest_batch.CONTRIBUTION_CSV
        orig_log = ingest_batch.RECORD_LOG_CSV
        orig_review = ingest_batch.REVIEW_DIR
        ingest_batch.CONTRIBUTION_CSV = contrib
        ingest_batch.RECORD_LOG_CSV = log
        ingest_batch.REVIEW_DIR = tmp_path / "review"
        try:
            result = ingest_batch.ingest(str(batch), "batch-01", "2026-11-05")
        finally:
            ingest_batch.CONTRIBUTION_CSV = orig_contrib
            ingest_batch.RECORD_LOG_CSV = orig_log
            ingest_batch.REVIEW_DIR = orig_review

        return result, contrib, log

    def test_clean_row_accepted(self, tmp_path):
        result, contrib, _ = self._run([_make_row(record_id="")], tmp_path)
        assert result["accepted"] == 1
        assert result["flagged"] == 0
        df = pd.read_csv(contrib, dtype=str)
        assert len(df) == 1

    def test_id_assigned_when_blank(self, tmp_path):
        result, contrib, _ = self._run([_make_row(record_id="")], tmp_path)
        df = pd.read_csv(contrib, dtype=str)
        assert df.iloc[0]["record_id"].startswith("T07-")

    def test_invalid_label_flagged_not_written(self, tmp_path):
        result, contrib, _ = self._run([_make_row(record_id="", label="bad")], tmp_path)
        assert result["flagged"] == 1
        assert result["accepted"] == 0
        df = pd.read_csv(contrib, dtype=str)
        assert len(df) == 0

    def test_exact_duplicate_existing_flagged(self, tmp_path):
        existing = [_make_row(record_id="T07-001", text="Tala mbula lelo.")]
        incoming = [_make_row(record_id="", text="Tala mbula lelo.")]
        result, contrib, _ = self._run(incoming, tmp_path, existing=existing)
        assert result["flagged"] == 1
        df = pd.read_csv(contrib, dtype=str)
        assert len(df) == 1  # only the original

    def test_log_updated_on_accept(self, tmp_path):
        result, _, log = self._run([_make_row(record_id="")], tmp_path)
        log_df = pd.read_csv(log, dtype=str)
        assert len(log_df) == 1
        assert log_df.iloc[0]["batch"] == "batch-01"

    def test_dry_run_writes_nothing(self, tmp_path):
        contrib = tmp_path / "contribution.csv"
        pd.DataFrame(columns=CONTRIB_COLS).to_csv(contrib, index=False)
        batch = _batch_csv([_make_row(record_id="")], tmp_path)

        orig_contrib = ingest_batch.CONTRIBUTION_CSV
        ingest_batch.CONTRIBUTION_CSV = contrib
        try:
            ingest_batch.ingest(str(batch), "batch-01", "2026-11-05", dry_run=True)
        finally:
            ingest_batch.CONTRIBUTION_CSV = orig_contrib

        df = pd.read_csv(contrib, dtype=str)
        assert len(df) == 0  # nothing written

    def test_pii_in_text_flagged(self, tmp_path):
        result, _, _ = self._run([_make_row(record_id="", text="Bela ngai na 0712345678.")], tmp_path)
        assert result["flagged"] == 1


# ── reconcile tests ───────────────────────────────────────────────────────────

LOG_COLS = [
    "record_id", "contributor_code", "source_type", "batch",
    "date_received", "assigned_label", "review_status",
    "correction_status", "approval_status", "notes",
]


def _log_row(record_id="T07-001", approval="approved") -> dict:
    return {
        "record_id": record_id,
        "contributor_code": "T07-V1",
        "source_type": "original_human",
        "batch": "batch-01",
        "date_received": "2026-11-05",
        "assigned_label": "weather_query",
        "review_status": "independently_reviewed",
        "correction_status": "none",
        "approval_status": approval,
        "notes": "",
    }


class TestReconcile:
    def _run(self, contrib_rows, log_rows, tmp_path):
        contrib_path = tmp_path / "contribution.csv"
        log_path = tmp_path / "record_log.csv"
        pd.DataFrame(contrib_rows, columns=CONTRIB_COLS).to_csv(contrib_path, index=False)
        pd.DataFrame(log_rows, columns=LOG_COLS).to_csv(log_path, index=False)
        return reconcile.reconcile(str(contrib_path), str(log_path))

    def test_shortfall_reported(self, tmp_path):
        report = self._run([_make_row()], [_log_row()], tmp_path)
        assert "SHORTFALL" in report

    def test_in_csv_not_log_detected(self, tmp_path):
        report = self._run([_make_row(record_id="T07-001")], [], tmp_path)
        assert "T07-001" in report
        assert "missing from Record Log" in report

    def test_in_log_not_csv_detected(self, tmp_path):
        report = self._run([], [_log_row("T07-999")], tmp_path)
        assert "T07-999" in report
        assert "missing from CSV" in report

    def test_unapproved_flagged(self, tmp_path):
        report = self._run([_make_row()], [_log_row(approval="pending")], tmp_path)
        assert "not yet approved" in report

    def test_clean_dataset_passes(self, tmp_path):
        report = self._run([_make_row()], [_log_row()], tmp_path)
        assert "All CSV records have a Record Log entry" in report
        assert "All logged records are approved" in report
