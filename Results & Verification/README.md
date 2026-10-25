# Section C — Results and Verification

This directory contains the machine-readable result tables and audit records supporting the study. These files supplement the research materials in **Essential Data & Prediction Freeze** and **Analysis Code**.

## Primary result tables

- `predictor_metrics_by_model.csv` — Brier score, log loss, mean predicted probability, observed rate, and calibration gap for the atom-product law and comparator baselines.
- `composition_component_metrics.csv` — schema validity, node sequence, step-value, final-value, and exact-success metrics.
- `task_cluster_bootstrap_brier_diff.csv` — task-family-cluster bootstrap comparison between the product law and structure-specific baseline.
- `task_cluster_bootstrap_success_ci.csv` — cluster-bootstrap intervals for exact success by model and graph structure.
- `calibration_only_baseline_metrics.csv` and `calibration_only_baseline_bootstrap.csv` — calibration-only comparator and its uncertainty.
- `embedded_json_metrics.csv` — post-hoc diagnostic distinguishing strict-format success from recoverable embedded JSON.
- `integrity_checks.json` and `release_verification.json` — row-count, run-ID, freeze-hash, and release checks.

## Main result, stated conservatively

Across 192 composition predictions, the atom-product law had Brier score **0.134732**. The structure-specific baseline scored **0.123897**, the operation-count baseline **0.122706**, and the graph-corrected cross-validation baseline **0.125725**. Lower Brier scores are better, so the candidate law did not outperform these stronger baselines in the pooled primary comparison.

The task-cluster bootstrap interval for the product-law minus structure-specific-baseline Brier difference spans zero. This does not establish a reliable advantage for either predictor. The findings do not prove that all multiplicative reliability laws are invalid.

## Integrity and interpretation notes

- The freeze hash identifies the published prediction file; it does not establish prospective preregistration or prove when model outputs were generated.
- Model labels are retained as `Model_A` and `Model_B`; do not infer exact provider/version provenance from these labels.
- The embedded-JSON analysis is post hoc and must not replace the strict exact-success primary metric.
- The workbook included in the repository is the safety-cleaned analyzed workbook, with four personal dashboard sign-in timestamps redacted. The redactions did not alter trial or oracle values.
- Scripts and outputs should be interpreted alongside the limitations documented in the top-level README.

All values in these tables are analysis outputs, not claims that the candidate law was validated.

## Row-level diagnostics

Publication boundaries for row-level materials are documented in [Row-Level Audit/](Row-Level%20Audit/README.md). Full response-heavy row-level exports and machine-specific logs are intentionally not duplicated; use the analyzed workbook and scoring scripts when detailed inspection is necessary.
