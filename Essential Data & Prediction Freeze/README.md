# Essential Data & Prediction Freeze

This folder contains the selected 192-row primary prediction freeze and its companion SHA-256 sidecar.

- `Frozen_Predictions_workbook_matching.csv` — selected primary predictions used for scoring.
- `Frozen_Predictions_workbook_matching.sha256.txt` — freeze metadata and SHA-256 of the CSV.

**The analyzed workbook is intentionally not included.** It contains prompts, raw model responses, oracle data, and task-bank designs. Do not replace the selected freeze with a newly generated one and call it the original. A checksum proves file identity, not when the predictions were frozen.
