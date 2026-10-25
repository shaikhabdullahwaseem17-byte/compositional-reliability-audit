# Reproduction Instructions and Data Availability

## Required private input

The analyzed workbook is intentionally not in this public repository. To rerun the scripts, supply an authorized local workbook matching the study's analyzed version. The primary pipeline expects `Trial_Data` and `Gold_Oracle`; the independent oracle audit also uses `Task_Bank`. Do not upload the workbook as part of this public release.

## Install and run

From the repository root:

```bash
python -m pip install -r "Analysis Code/C.R.A._requirements.txt"
```

Use the selected published predictions; do not run `--phase freeze` to recreate the original freeze.

```bash
python "Analysis Code/C.R.A._analyze_compositional_reliability_v2.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --phase analyze --predictions "Essential Data & Prediction Freeze/Frozen_Predictions_workbook_matching.csv" --outdir analysis_output

python "Analysis Code/C.R.A._independent_audit_v2.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --outdir independent_audit_outputs

python "Analysis Code/C.R.A._calibration_only_baseline.py" --analysis-dir analysis_output --predictions "Essential Data & Prediction Freeze/Frozen_Predictions_workbook_matching.csv" --outdir calibration_only_results

python "Analysis Code/C.R.A._sensitivity_and_lenient.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --predictions "Essential Data & Prediction Freeze/Frozen_Predictions_workbook_matching.csv" --outdir sensitivity_outputs
```

The calibration-only comparator is exploratory, and the sensitivity script is post-hoc. Neither replaces the as-frozen primary analysis. The A0045 sensitivity record should not be silently substituted into the primary data.

## What can be reproduced from this repository alone

The CSV/JSON aggregate tables can be inspected without the workbook. Full scoring/oracle reconstruction cannot be run from this repository alone because raw trial rows, raw responses, oracle logic, and task-bank definitions are deliberately not publicly mirrored. A researcher with the authorized private workbook can execute the scripts and compare outputs with the published summaries.

## Interpretation guardrails

The atom-product law did not consistently beat the stronger comparison baselines. The study does not establish a universal rejection of multiplicative reliability models. The task bank uses 12 families; external generalization is unestablished. `Model_A`/`Model_B` are aliases, not verified exact provider/version identities. Checksum equality confirms bytes, not chronology or preregistration.
