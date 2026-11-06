import pytest

from scripts import check_secrets
from scripts import run_query as rq


@pytest.mark.parametrize(
    "n,expected",
    [(0, "0 B"), (1023, "1023 B"), (1024, "1.00 KB"), (1536, "1.50 KB"),
     (1024**2, "1.00 MB"), (1024**3, "1.00 GB"), (5 * 1024**3, "5.00 GB")],
)
def test_format_bytes(n, expected):
    assert rq.format_bytes(n) == expected


def test_format_bytes_negative():
    with pytest.raises(ValueError):
        rq.format_bytes(-1)


def test_read_sql(tmp_path):
    f = tmp_path / "q.sql"
    f.write_text("  SELECT 1  \n", encoding="utf-8")
    assert rq.read_sql(f) == "SELECT 1"


def test_read_sql_empty(tmp_path):
    f = tmp_path / "q.sql"
    f.write_text("   \n", encoding="utf-8")
    with pytest.raises(ValueError):
        rq.read_sql(f)


def test_result_path(tmp_path):
    assert rq.result_path("sql/02_funnel.sql", tmp_path) == tmp_path / "02_funnel.csv"
    assert rq.result_path("sql/a.sql", tmp_path, name="x") == tmp_path / "x.csv"


def test_check_budget():
    rq.check_budget(100, 100)  # equal is allowed
    with pytest.raises(rq.QueryTooBigError):
        rq.check_budget(101, 100)


def test_log_and_total(tmp_path):
    log = tmp_path / "log.csv"
    assert rq.total_logged_bytes(log) == 0
    base = {"timestamp_utc": "t", "query": "q", "rows": 1}
    rq.append_log(log, dict(base, dry_run_bytes=10, billed_bytes=10485760, status="ok"))
    rq.append_log(log, dict(base, dry_run_bytes=99, billed_bytes=0, status="blocked"))
    rq.append_log(log, dict(base, dry_run_bytes=5, billed_bytes=10485760, status="ok"))
    assert rq.total_logged_bytes(log) == 2 * 10485760
    assert log.read_text().count("timestamp_utc") == 1  # one header


def test_main_requires_project(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    with pytest.raises(SystemExit):
        rq.main(["sql/x.sql"])


def test_scan_text_detects_patterns():
    assert "private key block" in check_secrets.scan_text("-----BEGIN " + "PRIVATE KEY-----")
    assert "service account json" in check_secrets.scan_text('{"type": "service' + '_account"}')
    assert check_secrets.scan_text("SELECT COUNT(*) FROM events") == []


def test_forbidden_names():
    assert check_secrets.is_forbidden_name("a/.env")
    assert check_secrets.is_forbidden_name("application_default_credentials.json")
    assert not check_secrets.is_forbidden_name(".env.example")
    assert not check_secrets.is_forbidden_name("README.md")
