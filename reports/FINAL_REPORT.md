# Arabic NER and PII Dataset Audit — Final Technical Report

**Execution mode:** reproducible evidence-backed audit

**Random seed:** 42

## Executive conclusion

The three supplied Hugging Face links are not three equivalent datasets. WikiANN is a directly analyzable multilingual NER dataset. MutazYoune/Arabic-NER-PII is a token-classification model whose model card declares Maqsam/ArabicPIIRedaction as its training dataset. contriqx-Hub/arabic-pii-guardrail is a binary PII-sharing-intent classifier rather than a token-boundary NER dataset.

Accordingly, this report separates directly measured dataset facts from model-card claims. No statistic is presented as measured unless the underlying examples were accessible to the execution.

## 1. Source qualification and provenance

| Resource supplied or resolved | Type | Direct EDA status | Role in this assignment |
|---|---|---|---|
| unimelb-nlp/wikiann | Dataset | DIRECTLY_MEASURED | Arabic and English NER analysis |
| MutazYoune/Arabic-NER-PII | Model | MODEL_ONLY | Points to a declared Arabic PII training dataset |
| Maqsam/ArabicPIIRedaction | Declared training dataset | NOT_DIRECTLY_ACCESSIBLE | Analyzed only if direct access succeeds |
| contriqx-Hub/arabic-pii-guardrail | Model | MODEL_ONLY | Taxonomy and intent-classifier context, not raw NER examples |

**Maqsam access evidence:** DatasetNotFoundError: Dataset 'Maqsam/ArabicPIIRedaction' doesn't exist on the Hub or cannot be accessed.

## 2. Sentence-length distributions and Normality

Length is measured primarily as the number of dataset tokens per sample. Normality is evaluated using a histogram with a fitted Normal density, a Normal Q-Q plot, D'Agostino K-squared, Shapiro-Wilk on a deterministic sample capped at 5,000 rows, and Anderson-Darling.

| Dataset | Rows | Mean | Median | P95 | Max | Skew | D'Agostino p | Shapiro p | Decision at alpha 0.05 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| WikiANN Arabic | 40000 | 6.446 | 5.000 | 12.000 | 63 | 3.879 | 0.000000 | 0.000000 | **REJECT_NORMALITY** |
| WikiANN English | 40000 | 8.031 | 6.000 | 19.000 | 439 | 13.394 | 0.000000 | 0.000000 | **REJECT_NORMALITY** |
| Maqsam/ArabicPIIRedaction | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | **NOT DIRECTLY MEASURABLE** |

A rejected Normality test is a finding, not an error that should be artificially corrected. NLP sentence lengths are discrete and commonly right-skewed. The practical implication is to design batching and truncation around the actual tail of the distribution.

Generated figures:

- figures/wikiann_ar_length_distribution.png
- figures/wikiann_ar_qq_plot.png
- figures/wikiann_en_length_distribution.png
- figures/wikiann_en_qq_plot.png

## 3. Ten deterministic random samples and qualitative sanity review

The following examples come from the training split using random seed 42. They are preserved in CSV form so that the same review can be reproduced.

### WikiANN Arabic — 10 random samples

| # | Text | Entities / spans |
|---:|---|---|
| 1 | وانتقلت إلى مومباي وقدمت العديد من العروض هناك . | LOC: مومباي |
| 2 | تحويل فاندرهوف ( كولومبيا البريطانية ) | LOC: فاندرهوف ( كولومبيا البريطانية ) |
| 3 | تحويل ابن حزم الأندلسي | PER: ابن حزم الأندلسي |
| 4 | كتلته تعادل 2,7 كتلة شمسية ونصف قطره 3 نصف قطر شمسي . | ORG: كتلة شمسية, ORG: نصف قطر شمسي |
| 5 | تحويل ابن البناء المراكشي | PER: ابن البناء المراكشي |
| 6 | تحويل مقاطعة تشيبيوا ( مينيسوتا ) | LOC: مقاطعة تشيبيوا ( مينيسوتا ) |
| 7 | تحويل وسائل تواصل اجتماعي | ORG: وسائل تواصل اجتماعي |
| 8 | تحويل رقم يو إن | ORG: رقم يو إن |
| 9 | تحويل روكلاند ( مقاطعة مانيتووك ) | LOC: روكلاند ( مقاطعة مانيتووك ) |
| 10 | مثّل منتخب كوستاريكا لكرة القدم . | ORG: منتخب كوستاريكا لكرة القدم |

### WikiANN English — 10 random samples

| # | Text | Entities / spans |
|---:|---|---|
| 1 | `` I Want to Hold Your Hand '' / `` Twist and Shout '' / `` Hey Jude '' | ORG: I Want to Hold Your Hand, ORG: Twist and Shout, ORG: Hey Jude |
| 2 | Max Ochs , Takoma Records guitarist | PER: Max Ochs, ORG: Takoma Records |
| 3 | Pharmaceutical Society of Northern Ireland | ORG: Pharmaceutical Society of Northern Ireland |
| 4 | Kyle Orton 2005 , 2007 , 2008 | PER: Kyle Orton |
| 5 | North Pacific Coast Railroad ( defunct ) | ORG: North Pacific Coast Railroad |
| 6 | ' '' Wisconsin '' ' | LOC: Wisconsin |
| 7 | They were married in 1943 and had five children , and he lived in West Hartford , CT , for the rest of his life . | ORG: West Hartford , CT |
| 8 | She is married to journalist Don Van Natta , Jr . ; they have two children . | PER: Don Van Natta , Jr . |
| 9 | Dabel Brothers Productions | ORG: Dabel Brothers Productions |
| 10 | '' Look of Love '' | ORG: Look of Love |

### Maqsam/ArabicPIIRedaction

Ten random training rows cannot be truthfully printed because the underlying rows were not directly accessible in this run. Model-card examples are not substituted for random dataset samples.

Qualitative interpretation: WikiANN is Wikipedia-derived NER material, not conversational PII text. Short fragments, title-like snippets and Wikipedia artifacts can therefore appear even when the annotation is structurally valid. This domain difference matters for a future model intended for chats, forms or personal-data redaction.

## 4. Labels and PII coverage

### WikiANN Arabic BIO label distribution

| Label | Count | Percent |
|---|---:|---:|
| O | 105516 | 40.926% |
| I-ORG | 39303 | 15.244% |
| I-LOC | 36811 | 14.278% |
| I-PER | 31165 | 12.088% |
| B-LOC | 15415 | 5.979% |
| B-PER | 15204 | 5.897% |
| B-ORG | 14408 | 5.588% |

### WikiANN English BIO label distribution

| Label | Count | Percent |
|---|---:|---:|
| O | 163071 | 50.760% |
| I-ORG | 46471 | 14.465% |
| I-PER | 29698 | 9.244% |
| I-LOC | 25981 | 8.087% |
| B-ORG | 18844 | 5.866% |
| B-LOC | 18836 | 5.863% |
| B-PER | 18355 | 5.714% |

WikiANN has seven BIO labels but only three semantic entity classes: **PER, ORG and LOC**.

| PII or entity category | WikiANN |
|---|---|
| Person name | Yes — PER |
| Organization | Yes — ORG |
| Geographic location | Yes — LOC |
| Home or street address | No dedicated class |
| Phone number | No |
| Email | No |
| National or structured identifier | No |
| IBAN | No |
| Credit card | No |
| Social-media handle | No |

### MutazYoune/Arabic-NER-PII model-card schema

The model card documents 11 BIO labels: O plus B- and I- variants for five coarse entity types: CONTACT, NETWORK, IDENTIFIER, NUMERIC_ID and PII. CONTACT groups email and telephone-like information, while the generic PII class is broader than a clean person-name taxonomy. These are documented claims unless independently confirmed from the raw training rows.

### contriqx-Hub/arabic-pii-guardrail task and taxonomy

The card describes PHONE, EMAIL, SOCIAL_MEDIA, IBAN, ADDRESS, URL, CREDIT_CARD, CRYPTO_ADDRESS, OFF_PLATFORM_ATTEMPT and NAME contexts, but the model output itself is binary PII versus NOT_PII. It classifies intent to share PII after an entity has already been extracted; it is not a token-level NER training corpus from the supplied link.

## 5. Weird or risky findings that can affect model training

### Directly measured WikiANN findings

- Arabic O-token share: **40.926%**.
- English O-token share: **50.760%**.
- Arabic exact duplicate rows across all splits combined: **6985**.
- English exact duplicate rows across all splits combined: **1145**.
- Arabic annotation-length mismatches: **0**.
- English annotation-length mismatches: **0**.
- Arabic BIO transition anomalies: **0**.
- English BIO transition anomalies: **0**.
- Arabic long-length IQR outliers: **2342 (5.855%)**.
- English long-length IQR outliers: **3402 (8.505%)**.
- Arabic rows containing both Arabic and Latin-script letters: **4.513%**.

### Cross-split exact-overlap audit

| Pair | Arabic overlap | English overlap |
|---|---:|---:|
| test__train | 1454 | 226 |
| validation__test | 911 | 139 |
| validation__train | 1387 | 257 |

Any non-zero exact train-validation-test overlap is an evaluation-leakage warning and should be resolved before final model benchmarking.

### Structural training risks

1. **PII coverage gap:** WikiANN cannot train a comprehensive PII detector because it lacks dedicated phone, email, address, identifier and financial classes.
2. **Domain mismatch:** Wikipedia NER text differs materially from messages, support chats, forms and redaction workloads.
3. **Silver-standard annotation risk:** WikiANN is automatically derived and should not be assumed to have gold-label quality in every language.
4. **Non-entity dominance:** high O-token prevalence can make raw token accuracy misleading; use entity-level precision, recall and F1 by class.
5. **Declared synthetic and regex bias:** the MutazYoune model card says its training set combines 10,000 original and 10,000 LLM-augmented sentences with regex-based annotation. If confirmed, template repetition and boundary bias should be audited before training.
6. **Guardrail task mismatch:** its model card reports a false-positive rate of 28.8% and weaker mixed-language F1 of 0.782. These are intent-classification characteristics, not NER boundary metrics.

## 6. Training-readiness assessment

| Resource | Status for future Arabic token-level NER/PII training | Why |
|---|---|---|
| WikiANN Arabic | **LIMITED / USEFUL AUXILIARY** | Good PER/ORG/LOC Arabic NER signal, but incomplete PII taxonomy and Wikipedia domain mismatch. |
| WikiANN English | **AUXILIARY / MULTILINGUAL CONTROL** | Useful for English comparison and multilingual experiments, not the core Arabic PII corpus. |
| Maqsam/ArabicPIIRedaction | **UNVERIFIED / ACCESS-BLOCKED** | The model card is promising, but the raw rows were not directly auditable in this execution. |
| arabic-pii-guardrail | **NOT A DIRECT NER DATASET** | Useful later as a second-stage sharing-intent signal or taxonomy reference, not as supplied token-boundary training data. |

## 7. Recommended modeling direction after this assignment

For the later NER phase, define a canonical fine-grained PII schema, deduplicate before splitting, preserve character/token span boundaries, create clean train/validation/test partitions, and evaluate entity-level F1 per class. WikiANN can supplement PER/ORG/LOC recognition, but a dedicated Arabic PII corpus is needed for phone, email, address, ID and financial entities.

## 8. Reproducibility manifest

- results/source_qualification.json
- results/wikiann_ar_analysis.json
- results/wikiann_en_analysis.json
- results/maqsam_arabic_pii_redaction_analysis.json
- results/wikiann_ar_random_samples.csv
- results/wikiann_en_random_samples.csv
- results/dataset_comparison.csv
- figures/ length histograms and Q-Q plots

## Final answer to the four requested points

1. **Length distributions and Normality:** measured, plotted and statistically tested for every directly accessible dataset configuration.
2. **Ten random sentences:** produced reproducibly for Arabic and English WikiANN, plus the declared Maqsam dataset only if the underlying rows are accessible.
3. **Labels and PII:** WikiANN has three semantic NER classes and lacks most major PII classes; the supplied model pages describe richer PII concepts but are not equivalent raw datasets.
4. **Training-impact notes:** class dominance, duplicates, split leakage, outliers, BIO consistency, script mixing, domain mismatch, annotation provenance and inaccessible-data boundaries are explicitly audited.
