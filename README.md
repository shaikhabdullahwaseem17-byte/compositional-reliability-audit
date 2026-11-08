# Compositional Reliability Audit

**Full title:** *Can Isolated-Operation Reliability Predict Compositional Task Success? An Empirical Audit of the Candidate Atom-Product Law*  
**Researcher:** Shaikh Abdullah Waseem  
**Study date:** 25 October 2026

## Overview

This repository publishes selected analysis code, the selected 192-row prediction freeze, aggregate results, and verification records for a black-box empirical audit of whether reliability estimates from isolated operations predict exact success on composed tasks. Or In simpler words, whether an AI can solve pieces of a puzzle with the same success rate as when those pieces are combined in one, big puzzle.

The study covers parallel, sequential, conditional, and nested-conditional task structures across two endpoint aliases, `Model_A` and `Model_B`. Model_A being Gemini 3 flash at medium thinking level and Model_B being GPT-6 Luna. 

## Main result

Across 192 composition predictions, the atom-product law had Brier score **0.134732**. The structure-specific baseline scored **0.123897**, the operation-count baseline **0.122706**, and the graph-corrected baseline **0.125725**. Lower scores are better. The candidate law therefore did not outperform these comparators in the pooled primary point estimates. The task-family bootstrap interval for its difference from the structure-specific baseline includes zero.

This is a bounded result for the tested task bank. It does not establish that every multiplicative reliability model is invalid.

## Repository contents

- **[Essential Data & Prediction Freeze](Essential%20Data%20%26%20Prediction%20Freeze/README.md):** selected prediction file and SHA-256 sidecar.
- **[Analysis Code](Analysis%20Code/):** primary analysis, independent oracle/scoring audit, aggregate-table builder, calibration-only comparator, post-hoc sensitivity diagnostics, and dependencies.
- **[Results & Verification](Results%20%26%20Verification/README.md):** aggregate tables, uncertainty intervals, and integrity records.
- **[SHA256SUMS.txt](SHA256SUMS.txt):** checksums for listed public files; the manifest does not hash itself.

## Data and reproduction

The analyzed workbook is maintained separately by the researcher and is intentionally not included in this public repository. It contains prompts, raw model responses, oracle data, and task-bank details. The workbook is a private input to the scripts, not a repository dependency for inspecting the published freeze and tables.

A researcher with an authorized local copy can reproduce the analysis and regenerate aggregate tables. Follow the run order and commands in [Results & Verification/REPRODUCING.md](Results%20%26%20Verification/REPRODUCING.md). The primary script checks the archived freeze against calibration-derived probabilities row by row; an alternate historical freeze is not interchangeable.

## Baselines

The graph-corrected comparator is a logistic-regression analysis baseline fitted within leave-one-task-family-out cross-validation. It uses the logit of the frozen atom-product probability, active-node count, graph structure, and endpoint alias. It is a statistical comparison model—not a separately trained foundation model, a new AI system, or a deployment model.

The structure-specific, operation-count, and global comparators are empirical rate predictors calculated without the held-out task family. The calibration-only pooled-operation comparator uses calibration data only and is labelled exploratory/post-audit.

## Limitations and provenance

1. The source workbook is excluded from the public repository. Full execution requires the researcher's separate authorized copy.
2. `Model_A` and `Model_B` are endpoint aliases. The reported configurations are based on the researcher's account; exact per-response provider/version metadata was not retained for every run.
3. The workbook lacks row-level timestamps and exact-model-version metadata. The prediction sidecar records a freeze timestamp and hash, but the hash verifies file identity, not prospective timing or preregistration.
4. Calibration record `A0045` has a documented response anomaly. It remains in the primary analysis; a separate post-hoc sensitivity analysis is provided.
5. The study covers 12 task families. Generalization beyond this task bank has not been established.
6. The candidate atom-product law did not outperform the retrospective baselines in pooled primary point estimates; the uncertainty interval includes zero.

## Researcher and AI-assistance statement

The researcher designed and conducted the experiment, ran and recorded the prompt trials, maintained the research workbook and annotations, managed calibration and composition phases, handled prediction freezing, and is responsible for the analysis decisions, interpretation, and conclusions.

ChatGPT assisted with methodological discussion, code drafting and review, calculation checks, and editorial refinement. The researcher reviewed and takes responsibility for the released code, results, and written claims. AI assistance is disclosed here and should not be interpreted as independent validation.

## Citation

Waseem, S. A. (2026). *Can Isolated-Operation Reliability Predict Compositional Task Success? An Empirical Audit of the Candidate Atom-Product Law*.

## Licensing

- Python analysis code: MIT License ([LICENSE](LICENSE)).
- Researcher-authored documentation: CC BY 4.0 ([CONTENT_LICENSE.md](CONTENT_LICENSE.md)).
- Empirical result tables and prediction freeze are not granted a blanket reuse license by either notice. See [CONTENT_LICENSE.md](CONTENT_LICENSE.md) and [Supporting Release Scope](Results%20%26%20Verification/Supporting%20Release%20Scope.md).



## Enquiries & Feedback:
Would be much appreciated
Contact at helloquvanti@gmail.com



[Last updated: November/08/2026]
