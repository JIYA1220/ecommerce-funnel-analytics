-- Phase 0 smoke test: row count for a single day (2020-11-01).
SELECT COUNT(*) AS events_on_2020_11_01
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_20201101`
