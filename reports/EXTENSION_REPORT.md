# Arabic NER Dataset Audit — Extension Report

This extension applies the same evidence-backed pipeline to Elyadata/CV18-NER and asas-ai/ANERCorp, then compares them with the previously audited Arabic WikiANN subset.

## Methodological note

Normality is measured because it was explicitly requested, but a non-Normal sentence-length distribution is not by itself a reason to reject a dataset for model training. Training suitability is judged from the observed length tail, label coverage, duplicates/leakage, annotation quality, domain fit, and reproducibility together.

## Comparison

| Dataset | Samples/sentences | Mean tokens | Median | P95 | Max | Skew | Normality | Exact duplicates | O-token % |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| WikiANN Arabic | 40000 | 6.446 | 5.000 | 12.000 | 63 | 3.879 | REJECT_NORMALITY | 6985 | 40.926 |
| CV18-NER | 11707 | 7.070 | 6.000 | 13.000 | 25 | 1.077 | REJECT_NORMALITY | 883 | 77.712 |
| ANERCorp | 5110 | 29.376 | 25.000 | 67.000 | 530 | 3.988 | REJECT_NORMALITY | 253 | 88.971 |

## CV18-NER evidence boundary

Hugging Face viewer currently reports CSV ParserError; the audit reads the raw annotation files directly and splits each physical row on the first delimiter so embedded commas remain part of the annotation text.

The audit evaluates the text/NER annotation field only. The source dataset is speech-oriented, but audio-duration analysis is outside the requested text-length pipeline.

## ANERCorp evidence boundary

Hugging Face rows are token-level word/tag pairs. Sentences are reconstructed after one-or-more period tokens, matching the CAMeL Lab split documentation.

The Hugging Face representation is token-level. Sentence-length statistics therefore refer to sentences reconstructed using the documented period-boundary rule, not native sentence rows from the Hugging Face parquet.

## Label coverage

- CV18-NER semantic classes: CARDINAL, CURR, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, OCC, ORDINAL, ORG, PERCENT, PERS, PRODUCT, QUANTITY, TIME, WEBSITE.
- ANERCorp semantic classes: LOC, MISC, ORG, PERS.

## Reproducibility outputs

- results/cv18_ner_analysis.json
- results/cv18_ner_random_samples.csv
- results/anercorp_analysis.json
- results/anercorp_random_samples.csv
- results/dataset_comparison_extended.csv
- figures/cv18_ner_length_distribution.png
- figures/cv18_ner_qq_plot.png
- figures/anercorp_length_distribution.png
- figures/anercorp_qq_plot.png
