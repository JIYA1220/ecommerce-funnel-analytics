# E-commerce Funnel and Retention Analytics

Work in progress. Funnel, retention and segmentation analysis of the Google Merchandise Store GA4 sample dataset (BigQuery), a business analyst pack, and an A/B test analysis.

Status: Phases 0 to 3 prepared (scaffolding, data profile and quality, funnel, retention and segment analysis in `docs/FINDINGS.md`, Power BI data and build guide in `powerbi/`). The dashboard itself is built by hand. Phase 4 BA pack is in `ba/`. A/B test comes later; every number in this repo will come from a saved query or script output in `results/`.

## Setup (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
gcloud auth application-default login
$env:GOOGLE_CLOUD_PROJECT = "<your-sandbox-project-id>"
python -m scripts.run_query sql/00_smoke_test.sql
python -m pytest -q
```

Every query does a dry run first, prints the bytes it will scan, and is blocked above 1 GB by default. Bytes are logged in `results/_bytes_log.csv`; `python -m scripts.run_query --total` prints the running total.
