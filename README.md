# Compositional Reliability Audit

**Full title:** *Compositional Reliability Audit: Testing an Atom-Product Law for Exact Success on Structured Tasks* 
**Researcher:** Shaikh Abdullah Waseem  
**Release date:** 25 October 2026

## Overview

This repository contains selected code, prediction-freeze metadata, aggregate results, and integrity records for a black-box empirical audit of whether reliability estimates from isolated operations predict exact success on composed tasks. Or simply, whether an AI can solve smaller pieces of puzzles with the exact success rate as when those pieces combine together for the complete artifact.

The study evaluates parallel, sequential, conditional, and nested-conditional structures across two model aliases, `Model_A` and `Model_B`.

## Main result

The atom-product law did not consistently outperform stronger baselines in the 192 composition predictions. Its Brier score (a suitable metric) was **0.134732**, compared with **0.123897** for the structure-specific baseline, **0.122706** for the operation-count baseline, and **0.125725** for the graph-corrected baseline. The task-cluster uncertainty interval for the product-law minus structure-specific-baseline Brier difference includes zero. These findings do **not** prove that every multiplicative reliability model is invalid.

## Repository map

- **[Essential Data & Prediction Freeze](Essential%20Data%20%26%20Prediction%20Freeze/README.md):** selected 192-row prediction file and its SHA-256 sidecar. The analyzed workbook is intentionally not published.
- **[Analysis Code](Analysis%20Code/):** primary pipeline, independent oracle/scoring audit, exploratory calibration-only comparator, post-hoc sensitivity script, and dependency file.
- **[Results & Verification](Results%20%26%20Verification/README.md):** aggregate tables, model-by-structure results, bootstrap uncertainty, and integrity records.
- **[SHA256SUMS.txt](SHA256SUMS.txt):** checksums for the listed public release files; the manifest intentionally does not hash itself.

## Data availability and reproduction

The source workbook `C.R.A._raw_analysis_sheet` is **not included**, as intended by the researcher. It contains the original prompts, model responses, oracle values, and task-bank designs. To rerun the analysis scripts, the researcher must provide their own authorized link of the analyzed workbook matching the expected `Trial_Data`, `Gold_Oracle`, and (for the independent audit) `Task_Bank` sheets. The selected freeze included here can be used without regenerating it. Contact Researcher at helloquvanti@gmail.com. 

Install dependencies from the repository root:

```bash
python -m pip install -r "Analysis Code/C.R.A._requirements.txt"
```

Using a private local workbook path, run the primary analysis (do not regenerate the freeze):

```bash
python "Analysis Code/C.R.A._analyze_compositional_reliability_v2.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --phase analyze --predictions "Essential Data & Prediction Freeze/C.R.A._Frozen_Predictions_workbook_matching.csv" --outdir analysis_output
```

Then run the independent audit:

```bash
python "Analysis Code/C.R.A._independent_audit_v2.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --outdir independent_audit_outputs
```

The calibration-only comparator requires the primary analysis output; the sensitivity script is post-hoc and should not replace the primary result. Exact commands and interpretation guardrails are documented in [Results & Verification/REPRODUCING.md](Results%20%26%20Verification/REPRODUCING.md).

## Limitations and provenance

1. The public repository does not include the raw/analyzed workbook, because it contains prompts, model outputs, oracle logic, and task-bank designs. Therefore users cannot rerun the complete pipeline from only this repository.
2. Model endpoints are reported as `Model_A` and `Model_B`. Model A was Gemini 3 at Medium thinking depth; Model B was GPT-6 Luna at Fast mode. These settings are based on the researcher's account of the configurations used.
3.  The workbook lacks row-level run timestamps and exact-version metadata, so freeze chronology and prospective preregistration cannot be independently established.
4.   Calibration record `A0045` has a documented response anomaly; it is preserved in the primary analysis, with a separate post-hoc sensitivity check.
5. The dataset includes 12 task families. Generalization beyond this task bank is unestablished.
6. The result does **not** validate the candidate law; the primary Brier score is **worse** than the structure-specific and operation-count baselines.

## AI assistance

ChatGPT assisted with methodological discussion, planning, code development/review, cross-checking calculations. The researcher conducted the experiment and remains responsible for the direction, methods, comments, interpretations, conclusions and presentation. AI assistance does not guarantee perfection 

## Citation

Waseem, S. A. (2026). *Compositional Reliability Audit: Testing an Atom-Product Law for Exact Success on Structured Tasks* 

## Licensing

- Python code: MIT License (`LICENSE`).
- Researcher-authored documentation: CC BY 4.0 (`CONTENT_LICENSE.md`).
- Empirical result tables and the prediction freeze are not granted a blanket reuse license by these code/documentation licenses; see the limits described in the result documentation.


[Last updated: 10/26/2026]
