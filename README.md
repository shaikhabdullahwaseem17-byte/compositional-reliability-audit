# Compositional Reliability Audit

**Subtitle:** Testing an Atom-Product Law for Exact Success on Structured Tasks  
**Researcher:** Shaikh Abdullah Waseem  
**Release date:** 25 October 2026

## Overview

This repository contains the reproducibility materials for an empirical audit of a proposed compositional reliability law. The study asks whether a model-specific reliability estimate derived from isolated operations can predict exact success on more complex tasks built from parallel, sequential, conditional, and nested-conditional structures.

The candidate atom-product law combines estimated success probabilities for individual operations. Its predictive performance is compared with simpler and structure-aware baselines on 192 composition trials across two model aliases (`Model_A` and `Model_B`). The release includes a cleaned analysis workbook, the selected frozen predictions, analysis scripts, result tables, integrity checks, and run logs. The research-paper PDF and DOCX are intentionally not included in this repository package.

## Main result

The atom-product law did **not** consistently outperform the stronger baseline predictors in this experiment. Its Brier score was **0.134732**, compared with **0.123897** for the structure-specific baseline, **0.122706** for the operation-count baseline, and **0.125725** for the graph-corrected baseline. The task-cluster bootstrap interval for the difference from the structure-specific baseline included zero. The results therefore do not validate the proposed law as a general predictive rule.

The study also found substantial differences between the two model aliases and a concentration of `FILTER_CHAR` errors among `Model_B` composition failures. These are descriptive findings from this task bank, not evidence that the same pattern must occur in other models or tasks. A pooled score close to the observed overall success rate masked opposing model-specific prediction errors.

## Repository contents

- `C.R.O._C.R.A._raw_analysis_sheet.xlsx` — cleaned workbook used for analysis. Four personal dashboard sign-in timestamps were redacted; research-relevant trial/oracle values were preserved. This is not a byte-identical copy of the original workbook.
- `C.R.O._Frozen_Predictions_workbook_matching.csv` — selected 192-row primary prediction freeze.
- `C.R.O._Frozen_Predictions_workbook_matching.sha256.txt` — hash and freeze-sidecar record for that CSV.
- `C.R.O._analyze_compositional_reliability_v2.py` — primary analysis pipeline.
- `C.R.O._independent_audit_v2.py` — separate task-oracle reconstruction and strict-scoring audit.
- `C.R.O._calibration_only_baseline.py` — exploratory calibration-only comparator.
- `C.R.O._sensitivity_and_lenient.py` — labelled post-hoc sensitivity diagnostics, including the A0045 and embedded-JSON checks.
- `C.R.O._requirements.txt` — Python dependencies.
- `C.R.O._*.csv`, `C.R.O._*.json`, and `C.R.O._*.txt` — aggregate result tables, row-level audit output, integrity records, and archived run logs. See `C.R.O._reproducibility_README.txt` for a detailed file-by-file guide and commands.
- `C.R.O._SHA256SUMS.txt` — file-integrity checksums for the release files.

## Reproducing the analysis

Use Python 3 and run commands from the directory containing these files. Install dependencies:

```bash
python -m pip install -r C.R.O._requirements.txt
```

Run the primary analysis using the selected frozen predictions (do not regenerate the freeze):

```bash
python C.R.O._analyze_compositional_reliability_v2.py C.R.O._C.R.A._raw_analysis_sheet.xlsx --phase analyze --predictions C.R.O._Frozen_Predictions_workbook_matching.csv --outdir C.R.O._analysis_output
```

Run the independent scoring/oracle audit:

```bash
python C.R.O._independent_audit_v2.py C.R.O._C.R.A._raw_analysis_sheet.xlsx --outdir C.R.O._independent_audit_outputs
```

Run the exploratory calibration-only comparator after the primary analysis:

```bash
python C.R.O._calibration_only_baseline.py --analysis-dir C.R.O._analysis_output --predictions C.R.O._Frozen_Predictions_workbook_matching.csv --outdir C.R.O._calibration_only_results
```

Run the explicitly post-hoc sensitivity diagnostics:

```bash
python C.R.O._sensitivity_and_lenient.py C.R.O._C.R.A._raw_analysis_sheet.xlsx --predictions C.R.O._Frozen_Predictions_workbook_matching.csv --outdir C.R.O._sensitivity_outputs
```

The primary analysis and independent audit are separate checks, but they do not guarantee that every possible error has been eliminated. The sensitivity analysis is exploratory and must not be substituted for the strict primary result.

## Limitations and provenance notes

1. **No successful validation claim:** the candidate law did not beat the stronger baselines consistently. This is a bounded empirical audit, not proof that every multiplicative reliability model is invalid.
2. **Model identity:** the workbook uses `Model_A` and `Model_B` aliases. Exact model/version provenance—particularly for `Model_B`—is not sufficiently secure to attribute results to a uniquely verified commercial model version.
3. **Freeze chronology:** the selected freeze reproduces against the current workbook calibration data, but the timing of the freeze relative to composition responses cannot be independently verified from row-level timestamps. Do not describe this as fully verified prospective preregistration.
4. **Calibration anomaly:** row `A0045` contains a response apparently copied from an unrelated operation. It is preserved in the primary analysis; the sensitivity script separately explores its effect. It has not been silently corrected.
5. **Task-bank scope:** the study uses 12 task families. The composition rows were distinct from calibration operation rows, but the broader task-family bank was reused. Generalization beyond these tasks remains unestablished.
6. **Historical freeze:** an alternate historical prediction file differed on 84 of 192 predictions. It is excluded from the release and was not used as the selected primary freeze. The detailed reproducibility note records its hash for audit context.
7. **Sharing implications:** the workbook contains prompts, model responses, oracle logic, and task-family designs. Publishing it makes these materials available for copying and inspection. Review all files and applicable model-provider terms before making the repository public.

## AI assistance and researcher contributions

The central research question and overall direction originated with the researcher. The researcher conducted the prompt runs, collected and recorded responses, maintained the experimental notes in the analysis workbook, carried out the calibration and composition phases, and performed the prediction-freezing procedure and associated recordkeeping. ChatGPT assisted with refining the presentation of the research question, discussing methodological choices, developing and reviewing analytical code, cross-checking calculations and results, and improving the written presentation. A separate scoring implementation was used to cross-check oracle reconstruction and strict scoring. The researcher remains responsible for the final methods, interpretations, and conclusions. AI assistance does not guarantee correctness.

## Citation

If you use or discuss this release, please cite it as:

> Waseem, S. A. (2026). *Compositional Reliability Audit: Testing an Atom-Product Law for Exact Success on Structured Tasks* [Research data and analysis code]. GitHub repository (URL to be added after publication).

After publishing, replace the placeholder with the repository URL. If a version is archived with a DOI, add the DOI and cite that version.

## Licensing

- **Code:** MIT License, in `LICENSE`.
- **Researcher-authored README and documentation:** CC BY 4.0, as described in `CONTENT_LICENSE.md`.
- **Workbook, raw model outputs, prompts, and other empirical materials:** no blanket reuse license is asserted here. Their reuse may be affected by applicable model-provider terms and other rights. Do not assume the MIT license or documentation license automatically covers those materials.

## Contact

Use the researcher's preferred public contact method, if intentionally provided in the repository profile. Avoid adding private contact details to a public repository unless you explicitly want them public.
