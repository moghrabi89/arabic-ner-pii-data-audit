# Arabic NER and PII Dataset Audit — Final Technical Report

**Execution mode:** reproducible evidence-backed audit

**Random seed:** 42

## Executive conclusion

The three supplied Hugging Face links are not three equivalent datasets. WikiANN is a directly analyzable multilingual NER dataset. MutazYoune/Arabic-NER-PII is a token-classification model whose model card declares Maqsam/ArabicPIIRedaction as its training dataset. contriqx-Hub/arabic-pii-guardrail is a binary PII-sharing-intent classifier rather than a token-boundary NER dataset.

Accordingly, this report separates directly measured dataset facts from model-card claims. No statistic is presented as measured unless the underlying examples were accessible to the execution.

## المنهجية المتبعة

اعتمد التحليل على منهجية تحقق متدرجة تبدأ بتثبيت هوية كل مصدر ومرجعيته قبل استخدامه، مع الفصل بين البيانات التي أمكن قياسها مباشرة والمعلومات الواردة في صفحات النماذج فقط. بعد ذلك نُفذت فحوص جودة متعددة تشمل سلامة البنية، التكرار، تداخل مجموعات التدريب والتحقق والاختبار، الاتساق في الوسوم، والقيم الشاذة. وفي المرحلة الأخيرة أُعيدت قراءة النتائج ومقارنتها بالمخرجات الآلية قبل إغلاق التحليل، لضمان أن الأرقام والاستنتاجات الواردة في التقرير مدعومة بأدلة قابلة للتحقق وإعادة الإنتاج.

## 1. Source qualification and provenance

| Resource supplied or resolved | Type | Direct EDA status | Role in this assignment |
|---|---|---|---|
| unimelb-nlp/wikiann | Dataset | DIRECTLY_MEASURED | Arabic and English NER analysis |
| MutazYoune/Arabic-NER-PII | Model | MODEL_ONLY | Points to a declared Arabic PII training dataset |
| Maqsam/ArabicPIIRedaction as dataset namespace | Declared by model card | NOT_DIRECTLY_ACCESSIBLE | No public dataset rows were returned by the Hub dataset API |
| Maqsam/ArabicPIIRedaction public Space | Competition Space | REACHABLE | Public repo files: .gitattributes, Dockerfile, README.md — no raw corpus file is exposed in the Space repository |
| contriqx-Hub/arabic-pii-guardrail | Model | MODEL_ONLY | Taxonomy and intent-classifier context, not raw NER examples |

**Maqsam access evidence:** DatasetNotFoundError: Dataset 'Maqsam/ArabicPIIRedaction' doesn't exist on the Hub or cannot be accessed.
**Space verification:** the public Maqsam/ArabicPIIRedaction Space is reachable, but its repository contains only .gitattributes, Dockerfile, README.md; therefore it is not a substitute for the missing raw training corpus.

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

**Manual sample-quality findings:** the deterministic Arabic sample includes cases such as كتلة شمسية and نصف قطر شمسي labeled ORG, and وسائل تواصل اجتماعي labeled ORG; the English sample includes West Hartford, CT labeled ORG and song titles labeled ORG. These are semantically questionable labels and are concrete evidence of silver-standard annotation noise rather than merely a theoretical risk.

A second Arabic-specific artifact is very large: **20191 of 40000 rows (50.477%) begin with تحويل**. This strongly indicates Wikipedia redirect/title-style material and means the Arabic subset is not representative of ordinary natural prose.

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

At the semantic entity-start level, WikiANN is comparatively balanced: Arabic LOC/ORG/PER counts are {'LOC': 15415, 'ORG': 14408, 'PER': 15204} (max/min ratio 1.070), and English counts are {'ORG': 18844, 'LOC': 18836, 'PER': 18355} (max/min ratio 1.027). The bigger imbalance concern is therefore O versus entity tokens and domain/annotation quality, not severe PER/ORG/LOC scarcity.

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
- Arabic exact duplicate rows across all splits combined: **6985 (17.462%)**.
- English exact duplicate rows across all splits combined: **1145 (2.863%)**.
- Arabic annotation-length mismatches: **0**.
- English annotation-length mismatches: **0**.
- Arabic BIO transition anomalies: **0**.
- English BIO transition anomalies: **0**.
- Arabic long-length IQR outliers: **2342 (5.855%)**.
- English long-length IQR outliers: **3402 (8.505%)**.
- Arabic rows containing both Arabic and Latin-script letters: **4.513%**.
- Arabic redirect-like rows beginning with تحويل: **20191 (50.477%)**.

### Cross-split exact-overlap audit

| Pair | Arabic overlap | Arabic % of smaller unique split | English overlap | English % of smaller unique split |
|---|---:|---:|---:|---:|
| test__train | 1454 | 15.645% | 226 | 2.286% |
| validation__test | 911 | 9.802% | 139 | 1.406% |
| validation__train | 1387 | 14.884% | 257 | 2.599% |

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
| WikiANN Arabic | **LIMITED / USEFUL AUXILIARY** | Good PER/ORG/LOC signal, but incomplete PII taxonomy, high exact duplication/split overlap, 50% redirect-like rows, questionable silver labels and Wikipedia domain mismatch. |
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


---

# Arabic NER Dataset Audit — CV18-NER & ANERCorp Extension

This extension applies the same reproducible audit pipeline used for WikiANN to Elyadata/CV18-NER and asas-ai/ANERCorp, then compares all three Arabic NER sources.

## Executive conclusion

**All three length distributions reject Normality. This does not make them unusable for model training.** Sentence lengths in NLP are discrete and commonly right-skewed; practical suitability depends on the observed tail, label coverage, duplicates/leakage, annotation quality, domain fit, and reproducibility together.

**CV18-NER is the strongest of the three for broad fine-grained Arabic NER coverage.** It exposes 20 observed Wojood-style entity types and has a compact length profile (mean about 7 tokens, maximum 25). However, it has severe class imbalance, the expected UNIT type is absent, CURR/LAW/PERCENT are extremely rare, exact duplicates are material, cross-split exact overlap reaches several percent, and basic BIO anomalies are present.

**ANERCorp is useful for longer natural/news-style Arabic prose and has very low train/test exact overlap.** Its limitations are a heavy length tail, very high O-token share, only four semantic classes, and measurable BIO inconsistencies.

**WikiANN remains auxiliary only** because of its redirect/title artifacts, high duplication, material split overlap, narrow PER/ORG/LOC taxonomy, and observed silver-label noise.

None of the three datasets contains the full dedicated PII taxonomy needed for phone, email, street address, structured ID, IBAN, credit card, and social identifiers.

## 1. Source qualification and evidence boundaries

| Resource | Measurement mode | Evidence boundary |
|---|---|---|
| WikiANN Arabic | Direct dataset rows | Wikipedia-derived silver-standard NER; prior audit established redirect, duplication, leakage and label-noise issues. |
| CV18-NER | Direct raw train/dev/test annotation files | Hugging Face viewer currently fails CSV parsing; the audit reads raw rows directly and preserves embedded commas by splitting each physical row only once. Audio duration is outside this text-analysis scope. |
| ANERCorp | Direct word/tag rows plus documented reconstruction | Hugging Face exposes a token stream. Sentence boundaries are reconstructed after one-or-more period tokens according to the standardized CAMeL release documentation. |

## 2. Length distributions and Normality

| Dataset | Samples/sentences | Mean | Median | P95 | Max | Skew | Decision | IQR long outliers |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| WikiANN Arabic | 40000 | 6.446 | 5.000 | 12.000 | 63 | 3.879 | REJECT_NORMALITY | 2342 (5.855%) |
| CV18-NER | 11707 | 7.070 | 6.000 | 13.000 | 25 | 1.077 | REJECT_NORMALITY | 614 (5.245%) |
| ANERCorp | 5110 | 29.376 | 25.000 | 67.000 | 530 | 3.988 | REJECT_NORMALITY | 203 (3.973%) |

### Interpretation

- CV18-NER is the least skewed and most compact source (skew 1.08, maximum 25 tokens). It is statistically non-Normal, but its tail is easy to manage with ordinary batching/padding.
- ANERCorp provides much longer sentence diversity (P95 67.0, maximum 530), so truncation/bucketing policy matters.
- WikiANN Arabic is short, but its main weakness is not shortness alone: the prior audit found extensive redirect-style material and contamination.

## 3. Ten deterministic random samples

### CV18-NER — 10 training samples (seed 42)

| # | Text | Tagged tokens |
|---:|---|---|
| 1 | " كارول تدرس الإسبانية ." | B-PERS:كارول, B-LANGUAGE:الإسبانية |
| 2 | "وقال الفضل بن سهل " | B-PERS:الفضل, I-PERS:بن, I-PERS:سهل |
| 3 | "كم يوما في الأسبوع ؟" | B-DATE:يوما, B-DATE:الأسبوع |
| 4 | "أوافقك الرأي أن الممثل موهوب جدا ." | B-OCC:الممثل |
| 5 | " سامي يعيش حياة رائعة ." | B-PERS:سامي |
| 6 | "جعل هذا سامي يشعر بالسعادة ." | B-PERS:سامي |
| 7 | "كذبت عاد المرسلين " | B-NORP:المرسلين |
| 8 | "نسيت عنوان توم ." | B-PERS:توم |
| 9 | "وصدق أبو عثمان " | B-PERS:أبو, I-PERS:عثمان |
| 10 | "في اليوم التالي " | B-DATE:اليوم, I-DATE:التالي |

### ANERCorp — 10 reconstructed training sentences (seed 42)

| # | Text | Tagged tokens |
|---:|---|---|
| 1 | وقال رافاران في اول حديث مهم له في مجال الشؤون الخارجية أمام الجمعية الوطنية ، انه ما من شك في ان العراق خطر محتمل على الشرق الأوسط ، ولكن ينبغي لاي عمل عسكري ان ينفذ بتأييد دولي واسع النطاق . | B-PERS:رافاران, B-LOC:العراق, B-LOC:الشرق, I-LOC:الأوسط |
| 2 | وكان افراد المجموعة يحملون سكاكين صغيرة والمشارط . | No tagged entity in sample |
| 3 | أدت هذه الظعائن المتبادلة ، إلى قطع العلاقة بين الطرفين نهائيا عام 1645 م . | No tagged entity in sample |
| 4 | والهجوم هو الأول من نوعه منذ إقرار وقف العمليات الحربية بين حزب الله وإسرائيل قبل تسعة أيام . | B-ORG:حزب, I-ORG:الله, B-LOC:وإسرائيل |
| 5 | إنقرض منذ حوالي 35 ، 000 إلى 10 ، 000 سنة مضت . | No tagged entity in sample |
| 6 | تبلغ ذكور الأسود النضج الجنسي بحلول عامها الثالث ، وتصبح قادرة على الإستيلاء على زمرة خاصة لها بحلول عامها الرابع أو الخامس وتبدأ بالشيوخ عندما تبلغ العام الثامن ، مما يترك في هذا الوقت فرصة ضئيلة لأشبالها بالنضوج ، ل... | No tagged entity in sample |
| 7 | ولخص محفوظ رؤيته للابداع ولمستقبل الآدب في حتفال نظمته وزارة الثقافة المصرية بمناسبة مرور عشر سنوات على فوزه بجائزة نوبل ولم يتمكن من حضوره بسبب الاصابة الناتجة عن محاولة اغتياله . | B-PERS:محفوظ, B-MISC:نوبل |
| 8 | -- تخرج من جامعة القرويين بفاس . | B-MISC:جامعة, I-MISC:القرويين, B-LOC:بفاس |
| 9 | وأفاد مصدر حكومي مطلع على اخبار عائلة الزعيم الكوري الشمالي ان كيم كوك هي " السيدة الاولى في كوريا الشمالية من الناحية الفعلية " وسترافق الزعيم الكوري الشمالي في كل تنقلاته . | B-PERS:كيم, I-PERS:كوك, B-LOC:كوريا, I-LOC:الشمالية |
| 10 | واعلن متحدث باسم منظمة الدول المصدرة للنفط اوبك امس الثلاثاء ان اوبك لا تعتزم حاليا عقد " اجتماع طاريء " قبل اجتماعها المقرر في 14 ديسمبر المقبل وذلك بالرغم من تراجع الاسعار في الاونة الاخيرة . | B-ORG:منظمة, I-ORG:الدول, I-ORG:المصدرة, I-ORG:للنفط, B-ORG:اوبك, B-ORG:اوبك |

CV18 samples are short spoken/transcribed Arabic utterances with fine-grained labels. ANERCorp samples are longer natural/news-style prose. Full untruncated samples are preserved in the generated CSV files.

## 4. Labels, class balance and PII coverage

### CV18-NER semantic entity-start distribution

| Entity class | Starts | Share of entity starts |
|---|---:|---:|
| PERS | 6606 | 44.569% |
| NORP | 1749 | 11.800% |
| DATE | 1542 | 10.403% |
| GPE | 1058 | 7.138% |
| OCC | 831 | 5.607% |
| TIME | 686 | 4.628% |
| CARDINAL | 546 | 3.684% |
| ORDINAL | 468 | 3.157% |
| LANGUAGE | 445 | 3.002% |
| LOC | 265 | 1.788% |
| ORG | 242 | 1.633% |
| FAC | 143 | 0.965% |
| EVENT | 92 | 0.621% |
| MONEY | 52 | 0.351% |
| PRODUCT | 32 | 0.216% |
| QUANTITY | 29 | 0.196% |
| WEBSITE | 26 | 0.175% |
| LAW | 4 | 0.027% |
| PERCENT | 4 | 0.027% |
| CURR | 2 | 0.013% |

CV18 expected schema types: 21. Observed semantic types: 20. Missing expected type: UNIT. Rare entity-start types (10 or fewer): LAW=4, PERCENT=4, CURR=2. Entity-start max/min ratio: 3303.0.

### ANERCorp semantic entity-start distribution

| Entity class | Starts | Share of entity starts |
|---|---:|---:|
| LOC | 4444 | 39.778% |
| PERS | 3579 | 32.035% |
| ORG | 2026 | 18.135% |
| MISC | 1123 | 10.052% |

ANERCorp entity-start max/min ratio: 3.96. O tokens account for 88.971% of tokens.

| PII need | WikiANN | CV18-NER | ANERCorp |
|---|---|---|---|
| Person name | Yes | Yes | Yes |
| Organization | Yes | Yes | Yes |
| Geographic location | Yes | Yes | Yes |
| Date/time | No dedicated class | Yes | No dedicated class |
| Phone | No | No | No |
| Email | No | No | No |
| Street/home address | No | No dedicated class | No |
| Structured/National ID | No | No | No |
| IBAN | No | No | No |
| Credit card | No | No | No |
| Social-media handle | No | No | No |

## 5. Training-impact and quality findings

| Check | WikiANN Arabic | CV18-NER | ANERCorp |
|---|---:|---:|---:|
| Exact duplicates | 6985 (17.462%) | 883 (7.542%) | 253 (4.951%) |
| O-token share | 40.926% | 77.712% | 88.971% |
| Basic BIO-transition anomalies | 0 | 70 | 113 |

### CV18-NER cross-split exact overlap

| Split pair | Exact overlap | % of smaller unique split |
|---|---:|---:|
| test__train | 95 | 4.114% |
| validation__test | 38 | 1.726% |
| validation__train | 138 | 6.267% |

### ANERCorp cross-split exact overlap

| Split pair | Exact overlap | % of smaller unique split |
|---|---:|---:|
| train__test | 1 | 0.108% |

### Annotation-consistency evidence

CV18-NER contains 70 basic BIO-transition anomalies. Representative anomaly examples are preserved in results/cv18_ner_analysis.json.

ANERCorp contains 113 basic BIO-transition anomalies. Representative anomaly examples are preserved in results/anercorp_analysis.json.

## 6. Training-readiness decision

| Dataset | Readiness | Best use | Main caveat |
|---|---|---|---|
| CV18-NER | **PROMISING WITH CLEANUP** | Fine-grained Arabic NER, especially speech/transcript-style text | Severe class imbalance, UNIT absent, rare classes, duplicates/overlap, BIO anomalies, CC BY-NC non-commercial license |
| ANERCorp | **USEFUL AUXILIARY WITH CLEANUP** | General Arabic NER on longer natural/news prose | Narrow four-class taxonomy, high O share, long tail, BIO inconsistencies, older news domain |
| WikiANN Arabic | **LIMITED AUXILIARY** | Additional PER/ORG/LOC signal | Redirect artifacts, high duplicates, split leakage and silver-label noise |

If the goal is general Arabic NER, CV18-NER is the most attractive new source for label breadth and ANERCorp is a useful complementary source for longer prose. Both should be cleaned and re-split before final benchmarking.

If the goal is comprehensive Arabic PII detection, none of these three is sufficient alone. A dedicated Arabic PII corpus is still required.

## 7. Licensing and reuse boundary

- CV18-NER: CC BY-NC 4.0. Commercial reuse is restricted by the non-commercial condition.
- ANERCorp: CC BY-SA 4.0. Attribution and share-alike obligations apply to adapted material.

## 8. Reproducibility outputs

- results/cv18_ner_analysis.json
- results/cv18_ner_random_samples.csv
- results/anercorp_analysis.json
- results/anercorp_random_samples.csv
- results/dataset_comparison_extended.csv
- figures/cv18_ner_length_distribution.png
- figures/cv18_ner_qq_plot.png
- figures/anercorp_length_distribution.png
- figures/anercorp_qq_plot.png

## Final answer to the extension request

The same pipeline has now been applied to both additional Hugging Face datasets. CV18-NER is substantially richer in entity taxonomy and has the cleanest/most compact length profile of the analyzed Arabic sources, but it requires class-balancing and annotation/split cleanup. ANERCorp provides much longer natural Arabic text with very low cross-split exact overlap, but it is a narrower and noisier four-class NER corpus. Neither dataset follows a Normal length distribution, and neither alone solves the broader PII-label coverage requirement.
