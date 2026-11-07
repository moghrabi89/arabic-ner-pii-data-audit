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
