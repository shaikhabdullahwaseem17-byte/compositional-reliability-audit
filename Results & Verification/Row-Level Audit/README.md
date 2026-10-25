# Row-Level Audit — Publication Scope

This folder is an index for the row-level audit boundary, not a dump of raw model responses.

## What is intentionally not published here

The release does not duplicate full row-level response excerpts, the detailed filter-node audit, or row-by-row scoring exports in this folder. Those artifacts are redundant with the analyzed workbook and can reveal exact task inputs, task-bank structure, and model response text. The public repository already documents aggregate diagnostics; this folder therefore avoids adding a second, less-controlled raw-data copy.

## Where to verify the results

- [Section C results and verification](../README.md) — aggregate predictive metrics, calibration tables, uncertainty intervals, component metrics, and integrity checks.
- [Analysis Code](../../Analysis%20Code/) — primary scoring pipeline and independent oracle/scoring audit.
- [Essential Data & Prediction Freeze](../../Essential%20Data%20%26%20Prediction%20Freeze/) — selected prediction freeze and its hash sidecar.

## Interpretation cautions

- `Model_A` and `Model_B` are study aliases; exact provider/version provenance is not fully established.
- The primary outcome is strict exact task success. Post-hoc embedded-JSON recovery is a separate diagnostic and does not replace the primary outcome.
- Row-level prompts, raw responses, and oracle data should be accessed through the analyzed workbook already provided in the data section, not duplicated into additional response-heavy CSVs.
- The public repository is not a byte-for-byte mirror of the local working folder. Machine-specific run logs, duplicate workbook/freeze files, alternate historical freezes, and report-building artifacts are intentionally excluded.
