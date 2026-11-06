"""Create the (free) Sandbox dataset `funnel` used for derived tables. Safe to rerun.

Usage: python -m scripts.setup_dataset
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    from google.cloud import bigquery

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        print("Set GOOGLE_CLOUD_PROJECT first.", file=sys.stderr)
        return 1
    client = bigquery.Client(project=project)
    ds = bigquery.Dataset(f"{project}.funnel")
    ds.location = "US"  # the public GA4 sample lives in the US multi-region
    ds.description = "Derived tables for ecommerce-funnel-analytics (built from the public GA4 sample)"
    client.create_dataset(ds, exists_ok=True)
    print(f"Dataset ready: {project}.funnel (US)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
