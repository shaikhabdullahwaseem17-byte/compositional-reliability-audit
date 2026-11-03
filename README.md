# Compositional Reliability Audit

**Full title:** *Compositional Reliability Audit: Testing an Atom-Product Law for Exact Success on Structured Tasks*  
**Researcher:** Shaikh Abdullah Waseem  
**Release date:** 25 October 2026

## Overview

This repository publishes selected analysis code, the primary prediction freeze, aggregate results, and verification records for a black-box empirical audit of whether reliability estimates from isolated operations predict exact success on composed tasks.

The study evaluates parallel, sequential, conditional, and nested-conditional task structures across two endpoint aliases, `Model_A` and `Model_B`.

## Main finding

Across 192 composition predictions, the atom-product law had a Brier score of **0.134732**. The structure-specific baseline scored **0.123897**, the operation-count baseline **0.122706**, and the graph-corrected baseline **0.125725**. Lower Brier scores are better. The atom-product law therefore did not outperform these comparators in the pooled primary comparison. The task-family-clustered uncertainty interval for its Brier-score difference from the structure-specific baseline includes zero.

This is a bounded result for the tested task bank. It does not establish that every multiplicative reliability model is invalid.

## Repository contents

- **[Essential Data & Prediction Freeze](Essential%20Data%20%26%20Prediction%20Freeze/README.md):** selected 192-row prediction file and SHA-256 sidecar.
- **[Analysis Code](Analysis%20Code/):** primary analysis pipeline, independent oracle/scoring audit, calibration-only comparator, post-hoc sensitivity diagnostics, and dependency list.
- **[Results & Verification](Results%20%26%20Verification/README.md):** aggregate result tables, uncertainty intervals, and release-integrity records.
- **[SHA256SUMS.txt](SHA256SUMS.txt):** SHA-256 checksums for the listed public files. The manifest does not hash itself.

## Data availability and reproduction

The analyzed workbook, `C.R.A._raw_analysis_sheet`, is intentionally **not included** in this public repository. It is maintained separately by the researcher and contains prompts, raw model responses, oracle data, and task-bank designs. The analysis scripts require an authorized local copy with the expected `Trial_Data` and `Gold_Oracle` sheets; the independent audit also requires `Task_Bank`.

The published prediction freeze can be inspected and its checksum verified without the workbook. Full scoring and oracle reconstruction cannot be reproduced from this repository alone.

Install the dependencies from the repository root:

```bash
python -m pip install -r "Analysis Code/C.R.A._requirements.txt"
```

Run the primary analysis using the separately held workbook and the published freeze (do not regenerate the historical freeze):

```bash
python "Analysis Code/C.R.A._analyze_compositional_reliability_v2.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --phase analyze --predictions "Essential Data & Prediction Freeze/C.R.A._Frozen_Predictions_workbook_matching.csv" --outdir analysis_output
```

Run the independent oracle/scoring audit:

```bash
python "Analysis Code/C.R.A._independent_audit_v2.py" "PATH/TO/YOUR_LOCAL_ANALYZED_WORKBOOK.xlsx" --outdir independent_audit_outputs
```

The calibration-only comparator and post-hoc sensitivity diagnostics are optional secondary analyses. Their exact commands and interpretation limits are documented in [Results & Verification/REPRODUCING.md](Results%20%26%20Verification/REPRODUCING.md).

## Baselines and model fitting

The graph-corrected comparator is a **logistic-regression analysis baseline**, fitted within leave-one-task-family-out cross-validation. Its inputs are the frozen atom-product probability (on the logit scale), active-node count, graph structure, and endpoint alias. Each held-out task family is excluded from fitting its corresponding prediction. This is ordinary statistical model fitting for a comparator; it is **not** a separately trained foundation model, a new AI system, or a model intended for deployment.

The structure-specific, operation-count, and global baselines are empirical rate predictors calculated from the non-held-out composition families. The calibration-only pooled-operation comparator uses calibration rows only and is labelled exploratory/post-audit in the study documentation.

## Limitations and provenance

1. The source workbook is maintained separately and is not part of this public release. Consequently, the full pipeline cannot be rerun from the repository alone.
2. The endpoint names `Model_A` and `Model_B` are aliases. The reported configurations were Gemini 3 at Medium thinking depth for Model A and GPT-6 at Fast mode for Model B, based on the researcher's account. Exact per-response provider/version metadata was not retained for every run.
3. The workbook does not contain complete row-level run timestamps and exact-version metadata. The freeze checksum establishes file identity, not the chronology of freezing or prospective preregistration.
4. Calibration record `A0045` has a documented response anomaly. It remains in the primary analysis; a separate post-hoc sensitivity analysis is provided.
5. The study covers 12 task families. Generalization beyond this task bank has not been established.
6. The primary result does not validate the candidate atom-product law; its pooled Brier score is worse than the structure-specific and operation-count baselines.

## Researcher and AI-assistance statement

The researcher designed and conducted the experiment, ran and recorded the prompt trials, maintained the research workbook and annotations, managed calibration and composition phases, handled the prediction-freezing process, and is responsible for the analysis decisions, interpretation, and conclusions.

ChatGPT was used as an assistance tool for methodological discussion, code drafting and review, checking calculations, and editorial refinement. The researcher reviewed and takes responsibility for the released code, results, and written claims. AI assistance is disclosed here and should not be interpreted as independent validation of the study.

## Citation

Waseem, S. A. (2026). *Compositional Reliability Audit: Testing an Atom-Product Law for Exact Success on Structured Tasks*.

## Licensing

- Python analysis code: MIT License ([LICENSE](LICENSE)).
- Researcher-authored documentation: CC BY 4.0 ([CONTENT_LICENSE.md](CONTENT_LICENSE.md)).
- Empirical result tables and the prediction freeze are not granted a blanket reuse license by either notice. See [CONTENT_LICENSE.md](CONTENT_LICENSE.md) and [Supporting Release Scope](Results%20%26%20Verification/Supporting%20Release%20Scope.md).

