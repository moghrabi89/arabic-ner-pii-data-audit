# Code Explanation

## Purpose

The repository implements a reproducible pre-training audit for the Arabic NER/PII assignment. The code deliberately separates two evidence levels:

1. Direct measurements from accessible dataset rows.
2. Claims documented by model cards when the underlying raw data cannot be inspected.

This prevents a model page from being treated as if it were a dataset.

## Execution map

The program follows this dependency chain:

Source qualification
→ WikiANN Arabic and English loading
→ declared Maqsam dataset access attempt
→ statistical profiling
→ random-sample review
→ label and PII coverage
→ quality and leakage checks
→ cross-dataset comparison
→ report generation
→ run manifest and closure status

## src/common.py

This file contains reusable statistical and text-analysis utilities.

### normalize_text

Normalizes Unicode to NFC and collapses repeated whitespace. It is used before duplicate and split-overlap comparisons so visually equivalent spacing does not create false differences.

### token_text

Reconstructs a readable sentence from the token list supplied by a token-classification dataset.

### script_ratios

Measures how much alphabetic content is Arabic-script versus Latin-script. This is useful for spotting code-switching or mixed-script examples that may change training behavior.

### length_stats

Calculates the main descriptive statistics for sample length:

- mean
- median
- standard deviation
- quartiles
- P95 and P99
- maximum
- skewness
- excess kurtosis
- IQR-based long-sample outliers

### normality

Uses several complementary checks instead of relying on one visual impression:

- D'Agostino K-squared test
- Shapiro-Wilk test
- Anderson-Darling statistic

Shapiro-Wilk is capped at a deterministic sample of 5,000 observations because very large samples make the test both computationally unnecessary and hypersensitive.

The decision rule uses alpha = 0.05. Rejecting Normality is reported as a property of the data, not as an error to be corrected.

### plot_lengths

Creates two figures:

- histogram/density with a fitted Normal curve
- Normal Q-Q plot

The Q-Q plot makes tail deviations and skewness visible even when a histogram looks approximately bell-shaped.

### bio_errors

Checks basic BIO transition consistency. An I-type tag is suspicious if it is not preceded by a B- or I-tag of the same entity type.

## src/wikiann.py

### analyze_wikiann

This is the core WikiANN audit. It loads one language configuration at a time and performs the same workflow for Arabic and English.

For every split it measures:

- row count
- token-length statistics
- Normality
- exact duplicate rows
- BIO label frequencies

Across all splits it additionally measures:

- O-token dominance
- semantic entity counts from spans
- annotation-length mismatches
- BIO transition anomalies
- Unicode replacement characters
- Arabic/Latin script mixing
- exact sentence overlap between train, validation and test

The function also draws 10 deterministic random training examples using seed 42. Deterministic sampling means anyone rerunning the repository receives the same examples.

## src/sources.py

### qualify_sources

Uses the Hugging Face API to classify and verify the supplied resources. This is the provenance gate.

It checks:

- unimelb-nlp/wikiann as a dataset
- Maqsam/ArabicPIIRedaction as the training dataset declared by the MutazYoune model card
- MutazYoune/Arabic-NER-PII as a model
- contriqx-Hub/arabic-pii-guardrail as a model

Reachability, revision SHA, gating/private status and pipeline metadata are recorded when available.

### analyze_declared_dataset

Attempts to load Maqsam/ArabicPIIRedaction directly.

If it is accessible, the function detects likely text/token/label columns and runs the same basic EDA: lengths, Normality, duplicate rows, labels and 10 random examples.

If it is not accessible, the function does not invent results. It writes an evidence record with status NOT_DIRECTLY_ACCESSIBLE and the access error.

## src/report.py

### build_comparison

Creates a compact CSV matrix comparing directly measured datasets and access states.

### build_report

Generates the final Markdown report from the machine-readable analysis outputs. The report is therefore derived from the same values produced by the code, reducing the risk of manual copy/paste errors.

The report directly answers the four assignment questions and also adds:

- provenance distinctions
- cross-split leakage checks
- training-readiness assessment
- future modeling recommendations

## src/main.py

This is the end-to-end orchestrator.

It runs:

1. source qualification
2. WikiANN Arabic audit
3. WikiANN English audit
4. Maqsam access/audit
5. final report generation
6. closure manifest

The final manifest reports PASS or PASS_WITH_EVIDENCE_BOUNDARIES. An inaccessible optional training dataset does not cause the entire assignment to fail, because the limitation itself is a verified finding.

## tests/test_common.py

This file provides deterministic unit tests for the core helper contract. The current tests verify:

- whitespace/Unicode normalization behavior
- a valid BIO sequence produces zero transition errors
- an orphan I-tag is detected
- the canonical WikiANN label mapping remains stable

These tests are intentionally lightweight: the full dataset audit remains the integration/E2E gate, while this suite catches regressions in reusable helper behavior before the expensive analysis begins.

## Dependency reproducibility

The top-level analysis dependencies are now pinned to the exact versions from the verified clean run:

- datasets 4.8.5
- huggingface_hub 1.33.0
- pandas 3.1.1
- numpy 2.4.6
- scipy 1.17.1
- matplotlib 3.11.2
- pyarrow 26.0.1

This removes the earlier version-range drift risk for the principal analysis stack.

## GitHub Actions workflow

The workflow uses Python 3.11 and runs the project through explicit quality gates:

1. install the exact top-level dependency set
2. compile all Python modules as a syntax gate
3. run the deterministic unit-test suite
4. execute the full end-to-end dataset audit
5. upload the reproducibility artifact
6. commit generated results, figures and report back to the repository

The workflow also uses a concurrency group for the main branch so overlapping audit runs are serialized and an older in-progress run cannot become the canonical closure by accident.

## Final verified execution

The repaired repository was revalidated on the current implementation state.

- GitHub Actions run: #8
- Run ID: 42243655615
- Validated head SHA: 1f1d3328310d7f493307639d6309b872e96754e2
- Generated-evidence commit: 48ddde9f17bd9c1e98e4bc8a5edcc8035a59b6fd
- Artifact ID: 13515953129
- Artifact SHA-256: 347f67fd5e59e624e5f6c601afd2e1a15d23c3a957df5aaac653d0b4ead3991c
- Workflow conclusion: SUCCESS

The generated `run_manifest.json` reports `PASS_WITH_EVIDENCE_BOUNDARIES`, and its stored report character count matches the generated final report.

## Reproducibility

The random seed is fixed at 42. The combination of exact top-level dependencies, syntax compilation, unit tests, full E2E execution, generated evidence commit, and artifact digest provides the final reproducibility/readback chain for this delivery.
