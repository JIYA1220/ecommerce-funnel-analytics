# Reproduce one phase with one command (PowerShell).
#
#   powershell -ExecutionPolicy Bypass -File scripts\reproduce.ps1 -Phase 2
#   powershell -ExecutionPolicy Bypass -File scripts\reproduce.ps1 -Phase 2 -DryRunOnly
#
# Run from the repo root with the virtual environment active and GOOGLE_CLOUD_PROJECT set.
# -DryRunOnly prints how many bytes each BigQuery query would scan and runs nothing.
# Phase 0 smoke test, 1 data profile, 2 funnel and retention, 3 Power BI files,
# 4 BA pack numbers and diagrams, 5 A/B test (needs ab_test\data\cookie_cats.csv).
param(
    [Parameter(Mandatory = $true)][ValidateSet('0', '1', '2', '3', '4', '5')][string]$Phase,
    [switch]$DryRunOnly
)
$ErrorActionPreference = 'Stop'

function Invoke-Query([string]$File, [double]$MaxGb = 1.0) {
    $a = @('-m', 'scripts.run_query', $File, '--max-gb', $MaxGb)
    if ($DryRunOnly) { $a += '--dry-run-only' }
    python @a
    if ($LASTEXITCODE -ne 0) { throw "query failed: $File" }
}

function Invoke-Module([string]$Name) {
    python -m $Name
    if ($LASTEXITCODE -ne 0) { throw "script failed: $Name" }
}

switch ($Phase) {
    '0' { Invoke-Query 'sql/00_smoke_test.sql' }
    '1' {
        foreach ($f in Get-ChildItem sql -File | Where-Object { $_.Name -match '^0[1-6]_.*\.sql$' } | Sort-Object Name) { Invoke-Query "sql/$($f.Name)" }
    }
    '2' {
        Invoke-Module 'scripts.setup_dataset'
        # The two table builds scan about 1.1 to 1.2 GB each (approved one-time exception to the 1 GB cap).
        Invoke-Query 'sql/10_build_events_slim.sql' 1.5
        Invoke-Query 'sql/11_build_item_events.sql' 1.5
        foreach ($f in Get-ChildItem sql -File | Where-Object { $_.Name -match '^(1[23]|2[0-9])[a-z]?_.*\.sql$' } | Sort-Object Name) {
            Invoke-Query "sql/$($f.Name)"
        }
    }
    '3' {
        Invoke-Query 'sql/30_daily_kpis.sql'
        Invoke-Query 'sql/31_product_table.sql'
        Invoke-Module 'scripts.export_powerbi'
        Invoke-Module 'scripts.expected_values'
    }
    '4' {
        Invoke-Module 'scripts.ba_numbers'
        Invoke-Module 'scripts.make_drawio'
    }
    '5' { Invoke-Module 'scripts.ab_analysis' }
}
Write-Output "Phase $Phase done."
