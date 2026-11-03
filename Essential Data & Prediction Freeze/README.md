# Essential Data and Prediction Freeze

This folder contains the selected 192-row prediction freeze used for the primary analysis and its SHA-256 sidecar.

- `C.R.A._Frozen_Predictions_workbook_matching.csv` — archived predictions for the 192 composition runs.
- `C.R.A._Frozen_Predictions_workbook_matching.sha256.txt` — archived digest and stated freeze timestamp.

The private analyzed workbook is not stored in this repository. The primary analysis recomputes calibration-derived estimates from that workbook and checks the published prediction file row by row. The alternate historical freeze is not part of this release and must not be substituted.

A matching checksum confirms file identity. It does not, by itself, prove when the predictions were frozen relative to composition collection.
