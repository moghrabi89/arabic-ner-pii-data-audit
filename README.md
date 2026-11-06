# Arabic NER & PII Dataset Audit

A reproducible audit of the Hugging Face resources supplied for an Arabic NER/PII assignment.

## Assignment questions
1. Plot sentence/text length distributions and test whether they are normally distributed.
2. Print 10 deterministic random samples from each analyzable dataset/language and inspect their quality.
3. Count labels/entity classes and assess coverage of important PII categories.
4. Identify data-quality issues that can affect model training.

## Source qualification
The supplied URLs are not equivalent:
- `unimelb-nlp/wikiann` is a dataset. The audit analyzes Arabic and English subsets.
- `MutazYoune/Arabic-NER-PII` is a token-classification model. Its model card names `Maqsam/ArabicPIIRedaction` as the training dataset; the workflow attempts direct access and records whether it is actually retrievable.
- `contriqx-Hub/arabic-pii-guardrail` is an intent-classification model, not a token-level NER dataset. Its training-data claims are kept separate from directly measured dataset facts.

## Reproducibility
The GitHub Actions workflow installs an exact top-level dependency set captured from the last successful reproducible run, loads accessible Hugging Face datasets, runs the audit, writes figures/tables/JSON/Markdown, and commits generated outputs back to the repository.

## Evidence rule
Model-card claims are reported as **documented claims** unless the underlying training data is accessible and independently measured. Unavailable evidence remains **UNKNOWN / NOT DIRECTLY VERIFIABLE**.

## Structure
- `src/main.py` — end-to-end orchestrator.
- `src/common.py` — shared statistics, plotting, normalization, and BIO checks.
- `src/wikiann.py` — WikiANN Arabic/English audit.
- `src/sources.py` — Hugging Face source qualification and declared-dataset access checks.
- `src/report.py` — evidence-linked report generation.
- `tests/` — lightweight deterministic unit tests for core helpers.
- `results/` — generated machine-readable outputs.
- `figures/` — generated plots.
- `reports/FINAL_REPORT.md` — generated technical report.
- `docs/CODE_EXPLANATION.md` — code walkthrough.
- `.github/workflows/run-analysis.yml` — reproducible execution.

Seed: `42`.


## Canonical citation

WikiANN / PAN-X is used here as the directly measured multilingual NER corpus. For academic work, cite the dataset card and its referenced original publication rather than treating this repository as the dataset source.
