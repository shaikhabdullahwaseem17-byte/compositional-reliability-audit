# Section C — Results and Verification

This directory contains aggregate result tables and selected audit records supporting the study. The source workbook is intentionally excluded from the public repository.

## Result files

- `predictor_metrics_by_model.csv` — Brier score, log loss, mean prediction, observed rate, and calibration gap for the candidate law and comparator baselines.
- `outcomes_and_scores_by_model_structure.csv` — exact-success rates and proper scores by model alias and graph structure.
- `family_level_outcomes.csv` — task-family by model/structure outcome summaries.
- `calibration_by_operation.csv` — operation-level calibration estimates used by the candidate law.
- `composition_component_metrics.csv` and `composition_filter_node_metrics.csv` — strict schema/component performance and aggregate FILTER_CHAR diagnostics.
- `task_cluster_bootstrap_brier_diff.csv` and `task_cluster_bootstrap_success_ci.csv` — task-cluster uncertainty intervals.
- `calibration_only_baseline_metrics.csv` and `calibration_only_baseline_bootstrap.csv` — exploratory calibration-only comparator and uncertainty results.
- `embedded_json_metrics.csv` — post-hoc diagnostic, separate from the strict primary metric.
- `integrity_checks.json` — source-data/freeze integrity checks performed on the researcher-held workbook.
- `release_verification.json` — public-release scope and exclusions.
- `REPRODUCING.md` — data availability, run instructions, and cautions.
- `Supporting Release Scope.md` — explanation of publication boundaries.

## Primary result

Across 192 composition predictions, the atom-product law had Brier score **0.134732**. The structure-specific baseline scored **0.123897**, the operation-count baseline **0.122706**, and the graph-corrected baseline **0.125725**. Lower is better, so the atom-product law did not outperform these stronger baselines in the pooled primary comparison. The task-cluster bootstrap interval includes zero.

The results are a bounded empirical audit, not proof that all multiplicative reliability laws are invalid. The embedded-JSON recovery diagnostic is post hoc and does not replace strict exact success.

## Integrity and provenance notes

- The selected freeze has 192 rows and is accompanied by its SHA-256 sidecar.
- The source workbook is not present in this public repository. The integrity JSON summarizes checks previously performed on the researcher-held analyzed data.
- Exact provider/version provenance for the model aliases is incomplete; no unique commercial version should be inferred.
- The workbook lacks row-level timestamp/model-version metadata, so freeze chronology cannot be independently established.
- Calibration record A0045 is an identified anomaly and is retained in the primary analysis; post-hoc sensitivity is separately labelled.
