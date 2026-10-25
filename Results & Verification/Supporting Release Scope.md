# Supporting Release — Scope and Safety

This repository separates the analyzed data/freeze, executable analysis code, and results/verification so a reader can navigate the study without duplicating files.

## Publicly included supporting materials

- Primary analysis code, independent oracle/scoring audit code, calibration-only comparator code, and dependency list in [Analysis Code](../Analysis%20Code/).
- The selected 192-row frozen prediction file and its SHA-256 sidecar in [Essential Data & Prediction Freeze](../Essential%20Data%20%26%20Prediction%20Freeze/).
- Aggregate predictive metrics, calibration tables, task-cluster uncertainty intervals, component metrics, integrity checks, and release-verification metadata in [Results & Verification](../Results%20%26%20Verification/).
- Curated row-level diagnostic summaries in [Row-Level Audit](../Results%20%26%20Verification/Row-Level%20Audit/).

## Materials intentionally not copied into another duplicate folder

The analyzed workbook and primary freeze are already included in the repository's data section. This avoids maintaining duplicate copies that could drift apart. The alternate historical freeze, old workbook versions, report PDF/DOCX, ZIP packages, local machine paths, and unredacted personal sign-in timestamps are not included as extra copies.

## Raw-response and operational-data caution

The workbook contains prompts, model responses, task-bank designs, and oracle information. These materials can expose the exact evaluation tasks and make them easier to copy or reproduce. The curated row-level failure inventory includes response prefixes and is therefore a deliberate disclosure of some task-level material. Do not add full raw-response dumps, credentials, private account data, or unreviewed machine logs to a public repository.

## Reproduction and limits

Use the selected freeze as published; do not regenerate it and then describe it as the original freeze. SHA-256 checks verify byte identity only. The missing row-level timestamps and exact model-version provenance limit chronology/source verification. The results do not validate the atom-product law: the primary pooled Brier score was worse than the operation-count and structure-specific baselines, and uncertainty intervals included zero.

## Release completeness statement

The repository includes the principal data/freeze, analysis scripts, aggregate result tables, integrity checks, and selected row-level diagnostics. It is not a byte-for-byte mirror of the local release folder: local run logs, environment-specific outputs, duplicate data files, and the nonessential PDF README are not copied wholesale. This is intentional to avoid publishing redundant, machine-specific, or raw-response-heavy artifacts without additional review.
