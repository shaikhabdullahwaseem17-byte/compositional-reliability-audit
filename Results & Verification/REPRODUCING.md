# Reproduction Instructions and Data Availability

## Required private input

The analyzed workbook is intentionally excluded from this repository. Keep it in the researcher's private storage. The primary pipeline and release-table builder require `Trial_Data` and `Gold_Oracle`; the independent audit also requires `Task_Bank`.

The published freeze is the selected workbook-matching file. Its SHA-256 is:

`0272c0f14e5a32ec366314ca68272034a355032bf6d32a58080dd4bbc1514a21`

An alternate historical freeze exists outside the selected release. Do not substitute it. The primary analysis now reconstructs calibration-derived predictions from the supplied workbook and rejects a freeze whose row-level estimates do not match.

## Install and run

Run from the repository root:

```bash
python -m pip install -r "Analysis Code/C.R.A._requirements.txt"
```

Run the primary analysis first:

```bash
python "Analysis Code/C.R.A._analyze_compositional_reliability_v2.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --phase analyze --predictions "Essential Data & Prediction Freeze/C.R.A._Frozen_Predictions_workbook_matching.csv" --outdir analysis_output
```

Run the independent oracle/scoring audit:

```bash
python "Analysis Code/C.R.A._independent_audit_v2.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --outdir independent_audit_outputs
```

Regenerate the aggregate result tables (this writes derived tables only; it does not copy the workbook or raw responses):

```bash
python "Analysis Code/C.R.A._build_release_tables.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --predictions "Essential Data & Prediction Freeze/C.R.A._Frozen_Predictions_workbook_matching.csv" --outdir "Results & Verification"
```

Run the optional secondary analyses:

```bash
python "Analysis Code/C.R.A._calibration_only_baseline.py" --analysis-dir analysis_output --predictions "Essential Data & Prediction Freeze/C.R.A._Frozen_Predictions_workbook_matching.csv" --outdir calibration_only_results

python "Analysis Code/C.R.A._sensitivity_and_lenient.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --predictions "Essential Data & Prediction Freeze/C.R.A._Frozen_Predictions_workbook_matching.csv" --outdir sensitivity_outputs
```

The calibration-only comparator is exploratory. The A0045 restoration and embedded-JSON extraction are post-hoc diagnostics; neither replaces the strict, as-frozen primary analysis. Do not run `--phase freeze` to recreate the historical freeze.

## Verified primary outputs

Using the selected freeze and the analyzed workbook, the primary pipeline returns 336 scored rows, including 192 composition rows and 94 exact composition successes. The atom-product Brier score is 0.134732; structure-specific, operation-count, global, and graph-corrected scores are 0.123897, 0.122706, 0.123551, and 0.125725 respectively.

The 5,000-replicate task-family bootstrap uses seed 20261023. It gives a mean Brier difference (product minus structure-specific) of 0.010834, with percentile interval [-0.017275, 0.035369]. The interval includes zero. The optional calibration-only comparator and 100,000-replicate bootstrap are produced by its own script.

## What can be reproduced from this repository alone

The published prediction freeze and aggregate tables can be inspected without the workbook. Full scoring, oracle reconstruction, and regeneration of derived result tables require the researcher's private workbook. The workbook is not included in the public repository.

## Interpretation and provenance

The study covers 12 task families; generalization beyond this task bank has not been established. `Model_A` and `Model_B` are endpoint aliases. The reported configurations are based on the researcher's account; exact per-response provider/version metadata was not retained for every run. The workbook lacks row-level run timestamps and exact-model-version columns, so freeze chronology cannot be independently established from the workbook. The prediction sidecar records a timestamp and file hash, but a hash proves file identity, not prospective timing or preregistration.

Calibration record `A0045` is retained as recorded in the primary analysis. Its response anomaly is addressed only in a clearly labelled post-hoc sensitivity analysis.
