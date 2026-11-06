"""Run a .sql file on BigQuery with a dry-run size check, save CSV, log bytes.

Usage (PowerShell):
    python -m scripts.run_query sql/00_smoke_test.sql
    python -m scripts.run_query sql/01_profile.sql --max-gb 0.5
    python -m scripts.run_query sql/01_profile.sql --dry-run-only
    python -m scripts.run_query --total

The project id comes from --project or the GOOGLE_CLOUD_PROJECT env var.
Credentials come from `gcloud auth application-default login` (never in the repo).
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

GB = 1024**3
DEFAULT_MAX_GB = 1.0
DEFAULT_DATASET = "funnel"
RESULTS_DIR = Path("results")
LOG_NAME = "_bytes_log.csv"
LOG_FIELDS = ["timestamp_utc", "query", "dry_run_bytes", "billed_bytes", "rows", "status"]


class QueryTooBigError(RuntimeError):
    """Raised when a dry run says the query would scan more than the budget."""


def format_bytes(n: int) -> str:
    """Human readable size, e.g. 1536 -> '1.50 KB'."""
    if n < 0:
        raise ValueError("bytes cannot be negative")
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{int(size)} B" if unit == "B" else f"{size:.2f} {unit}"
        size /= 1024
    raise AssertionError("unreachable")


def read_sql(path: Path) -> str:
    """Read a SQL file and refuse empty files."""
    text = Path(path).read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"SQL file is empty: {path}")
    return text


def result_path(sql_path: Path, results_dir: Path = RESULTS_DIR, name: str | None = None) -> Path:
    """results/<name>.csv, where name defaults to the SQL file stem."""
    return Path(results_dir) / f"{name or Path(sql_path).stem}.csv"


def check_budget(dry_run_bytes: int, max_bytes: int) -> None:
    """Raise if the dry run exceeds the budget."""
    if dry_run_bytes > max_bytes:
        raise QueryTooBigError(
            f"Query would scan {format_bytes(dry_run_bytes)}, "
            f"over the limit of {format_bytes(max_bytes)}. Ask before raising --max-gb."
        )


def append_log(log_path: Path, row: dict) -> None:
    """Append one row to the bytes log, writing the header if the file is new."""
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    new = not log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new:
            writer.writeheader()
        writer.writerow(row)


def total_logged_bytes(log_path: Path) -> int:
    """Sum of billed bytes over all successful runs in the log (0 if no log)."""
    log_path = Path(log_path)
    if not log_path.exists():
        return 0
    with log_path.open(newline="", encoding="utf-8") as f:
        return sum(
            int(r["billed_bytes"] or 0) for r in csv.DictReader(f) if r["status"] == "ok"
        )


def should_save_csv(statement_type: str | None) -> bool:
    """Only SELECT results are saved as CSV. DDL such as CREATE TABLE has no result set."""
    return (statement_type or "SELECT") == "SELECT"


def run(sql_path: Path, project: str, max_gb: float, dry_run_only: bool, name: str | None,
        dataset: str = DEFAULT_DATASET) -> int:
    from google.cloud import bigquery  # imported here so helpers test without the SDK
    from google.cloud.exceptions import NotFound

    client = bigquery.Client(project=project)
    default_dataset = None
    if dataset:
        try:
            client.get_dataset(f"{project}.{dataset}")
            default_dataset = f"{project}.{dataset}"
        except NotFound:
            pass  # run scripts.setup_dataset first if the SQL uses unqualified table names
    sql = read_sql(sql_path)
    max_bytes = int(max_gb * GB)
    log_path = RESULTS_DIR / LOG_NAME
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    dry = client.query(sql, job_config=bigquery.QueryJobConfig(
        dry_run=True, use_query_cache=False, default_dataset=default_dataset))
    est = int(dry.total_bytes_processed or 0)
    print(f"[dry run] {sql_path}: will scan {format_bytes(est)} ({est} bytes)")
    try:
        check_budget(est, max_bytes)
    except QueryTooBigError as exc:
        append_log(log_path, {"timestamp_utc": ts, "query": str(sql_path), "dry_run_bytes": est,
                      "billed_bytes": 0, "rows": 0, "status": "blocked"})
        print(f"[blocked] {exc}", file=sys.stderr)
        return 2
    if dry_run_only:
        return 0

    job = client.query(sql, job_config=bigquery.QueryJobConfig(
        maximum_bytes_billed=max_bytes, default_dataset=default_dataset))
    result = job.result()
    out = result_path(sql_path, RESULTS_DIR, name)
    if should_save_csv(job.statement_type):
        df = result.to_dataframe()
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
    else:
        df = []
        out = f"(no CSV, {job.statement_type})"
    billed = int(job.total_bytes_billed or 0)
    processed = int(job.total_bytes_processed or 0)
    append_log(log_path, {"timestamp_utc": ts, "query": str(sql_path), "dry_run_bytes": est,
                  "billed_bytes": billed, "rows": len(df), "status": "ok"})
    print(f"[done] {len(df)} rows -> {out} | processed {format_bytes(processed)}, "
          f"billed {format_bytes(billed)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sql", nargs="?", type=Path, help="path to a .sql file")
    p.add_argument("--project", default=os.environ.get("GOOGLE_CLOUD_PROJECT"))
    p.add_argument("--max-gb", type=float, default=DEFAULT_MAX_GB, help="scan limit in GB (default 1)")
    p.add_argument("--dataset", default=DEFAULT_DATASET,
                   help="default dataset for unqualified table names (default: funnel)")
    p.add_argument("--dry-run-only", action="store_true")
    p.add_argument("--name", help="output name (default: SQL file stem)")
    p.add_argument("--total", action="store_true", help="print total bytes logged and exit")
    args = p.parse_args(argv)

    if args.total:
        t = total_logged_bytes(RESULTS_DIR / LOG_NAME)
        print(f"Total billed bytes logged: {t} ({format_bytes(t)})")
        return 0
    if not args.sql:
        p.error("sql file is required")
    if not args.project:
        p.error("set --project or the GOOGLE_CLOUD_PROJECT environment variable")
    return run(args.sql, args.project, args.max_gb, args.dry_run_only, args.name, args.dataset)


if __name__ == "__main__":
    raise SystemExit(main())
