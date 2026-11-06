from __future__ import annotations

import pandas as pd

from .common import REPORTS, RESULTS


def fmt(value, digits=3):
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return format(value, "." + str(digits) + "f")
    return str(value)


def escape_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def sample_table(title, samples):
    lines = ["### " + title, "", "| # | Text | Entities / spans |", "|---:|---|---|"]
    for i, sample in enumerate(samples, 1):
        spans = ", ".join(str(x) for x in sample.get("spans", []))
        lines.append("| " + str(i) + " | " + escape_cell(sample.get("text", "")) + " | " + escape_cell(spans) + " |")
    return "\n".join(lines)


def label_table(title, counts):
    total = sum(counts.values())
    lines = ["### " + title, "", "| Label | Count | Percent |", "|---|---:|---:|"]
    for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        pct = count / max(1, total) * 100
        lines.append("| " + escape_cell(label) + " | " + str(count) + " | " + f"{pct:.3f}" + "% |")
    return "\n".join(lines)


def build_comparison(ar, en, maqsam):
    rows = []
    for name, data in [("WikiANN Arabic", ar), ("WikiANN English", en)]:
        c = data["combined"]
        rows.append({
            "source": name,
            "status": data["source_status"],
            "rows": c["rows"],
            "mean_tokens": c["length"]["mean"],
            "median_tokens": c["length"]["median"],
            "p95_tokens": c["length"]["p95"],
            "max_tokens": c["length"]["max"],
            "normality": c["normality"]["decision_alpha_0_05"],
            "exact_duplicate_rows": c["exact_duplicate_rows"],
            "O_token_pct": c["O_token_pct"],
            "bio_transition_errors": c["bio_transition_errors"],
        })
    if maqsam.get("source_status") == "DIRECTLY_MEASURED":
        c = maqsam["combined"]
        rows.append({
            "source": "Maqsam/ArabicPIIRedaction",
            "status": maqsam["source_status"],
            "rows": c["rows"],
            "mean_tokens": c["length"]["mean"],
            "median_tokens": c["length"]["median"],
            "p95_tokens": c["length"]["p95"],
            "max_tokens": c["length"]["max"],
            "normality": c["normality"]["decision_alpha_0_05"],
            "exact_duplicate_rows": c["exact_duplicate_rows"],
            "O_token_pct": None,
            "bio_transition_errors": None,
        })
    else:
        rows.append({
            "source": "Maqsam/ArabicPIIRedaction",
            "status": maqsam.get("source_status"),
            "rows": None,
            "mean_tokens": None,
            "median_tokens": None,
            "p95_tokens": None,
            "max_tokens": None,
            "normality": "NOT DIRECTLY MEASURABLE",
            "exact_duplicate_rows": None,
            "O_token_pct": None,
            "bio_transition_errors": None,
        })
    frame = pd.DataFrame(rows)
    frame.to_csv(RESULTS / "dataset_comparison.csv", index=False)
    return frame


def build_report(source_q, ar, en, maqsam):
    build_comparison(ar, en, maqsam)
    ac = ar["combined"]
    ec = en["combined"]
    maqsam_direct = maqsam.get("source_status") == "DIRECTLY_MEASURED"
    space_info = source_q.get("sources", {}).get("Maqsam/ArabicPIIRedaction_space", {})
    space_files = ", ".join(space_info.get("files", [])) if space_info.get("reachable") else "unavailable"
    ar_entities = ac.get("semantic_entity_counts_from_spans", {})
    en_entities = ec.get("semantic_entity_counts_from_spans", {})
    ar_entity_balance = max(ar_entities.values()) / min(ar_entities.values()) if ar_entities else None
    en_entity_balance = max(en_entities.values()) / min(en_entities.values()) if en_entities else None

    lines = [
        "# Arabic NER and PII Dataset Audit — Final Technical Report",
        "",
        "**Execution mode:** reproducible evidence-backed audit",
        "",
        "**Random seed:** 42",
        "",
        "## Executive conclusion",
        "",
        "The three supplied Hugging Face links are not three equivalent datasets. WikiANN is a directly analyzable multilingual NER dataset. MutazYoune/Arabic-NER-PII is a token-classification model whose model card declares Maqsam/ArabicPIIRedaction as its training dataset. contriqx-Hub/arabic-pii-guardrail is a binary PII-sharing-intent classifier rather than a token-boundary NER dataset.",
        "",
        "Accordingly, this report separates directly measured dataset facts from model-card claims. No statistic is presented as measured unless the underlying examples were accessible to the execution.",
        "",
        "## المنهجية المتبعة",
        "",
        "اعتمد التحليل على منهجية تحقق متدرجة تبدأ بتثبيت هوية كل مصدر ومرجعيته قبل استخدامه، مع الفصل بين البيانات التي أمكن قياسها مباشرة والمعلومات الواردة في صفحات النماذج فقط. بعد ذلك نُفذت فحوص جودة متعددة تشمل سلامة البنية، التكرار، تداخل مجموعات التدريب والتحقق والاختبار، الاتساق في الوسوم، والقيم الشاذة. وفي المرحلة الأخيرة أُعيدت قراءة النتائج ومقارنتها بالمخرجات الآلية قبل إغلاق التحليل، لضمان أن الأرقام والاستنتاجات الواردة في التقرير مدعومة بأدلة قابلة للتحقق وإعادة الإنتاج.",
        "",
        "## 1. Source qualification and provenance",
        "",
        "| Resource supplied or resolved | Type | Direct EDA status | Role in this assignment |",
        "|---|---|---|---|",
        "| unimelb-nlp/wikiann | Dataset | DIRECTLY_MEASURED | Arabic and English NER analysis |",
        "| MutazYoune/Arabic-NER-PII | Model | MODEL_ONLY | Points to a declared Arabic PII training dataset |",
        "| Maqsam/ArabicPIIRedaction as dataset namespace | Declared by model card | " + escape_cell(maqsam.get("source_status")) + " | No public dataset rows were returned by the Hub dataset API |",
        "| Maqsam/ArabicPIIRedaction public Space | Competition Space | REACHABLE | Public repo files: " + escape_cell(space_files) + " — no raw corpus file is exposed in the Space repository |",
        "| contriqx-Hub/arabic-pii-guardrail | Model | MODEL_ONLY | Taxonomy and intent-classifier context, not raw NER examples |",
        "",
    ]
    if maqsam.get("access_error"):
        lines.extend([
            "**Maqsam access evidence:** " + escape_cell(maqsam["access_error"]),
            "**Space verification:** the public Maqsam/ArabicPIIRedaction Space is reachable, but its repository contains only " + escape_cell(space_files) + "; therefore it is not a substitute for the missing raw training corpus.",
            "",
        ])

    lines.extend([
        "## 2. Sentence-length distributions and Normality",
        "",
        "Length is measured primarily as the number of dataset tokens per sample. Normality is evaluated using a histogram with a fitted Normal density, a Normal Q-Q plot, D'Agostino K-squared, Shapiro-Wilk on a deterministic sample capped at 5,000 rows, and Anderson-Darling.",
        "",
        "| Dataset | Rows | Mean | Median | P95 | Max | Skew | D'Agostino p | Shapiro p | Decision at alpha 0.05 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        "| WikiANN Arabic | " + str(ac["rows"]) + " | " + fmt(ac["length"]["mean"]) + " | " + fmt(ac["length"]["median"]) + " | " + fmt(ac["length"]["p95"]) + " | " + str(ac["length"]["max"]) + " | " + fmt(ac["length"]["skew"]) + " | " + fmt(ac["normality"]["dagostino_p"], 6) + " | " + fmt(ac["normality"]["shapiro_p"], 6) + " | **" + ac["normality"]["decision_alpha_0_05"] + "** |",
        "| WikiANN English | " + str(ec["rows"]) + " | " + fmt(ec["length"]["mean"]) + " | " + fmt(ec["length"]["median"]) + " | " + fmt(ec["length"]["p95"]) + " | " + str(ec["length"]["max"]) + " | " + fmt(ec["length"]["skew"]) + " | " + fmt(ec["normality"]["dagostino_p"], 6) + " | " + fmt(ec["normality"]["shapiro_p"], 6) + " | **" + ec["normality"]["decision_alpha_0_05"] + "** |",
    ])
    if maqsam_direct:
        mc = maqsam["combined"]
        lines.append("| Maqsam/ArabicPIIRedaction | " + str(mc["rows"]) + " | " + fmt(mc["length"]["mean"]) + " | " + fmt(mc["length"]["median"]) + " | " + fmt(mc["length"]["p95"]) + " | " + str(mc["length"]["max"]) + " | " + fmt(mc["length"]["skew"]) + " | " + fmt(mc["normality"]["dagostino_p"], 6) + " | " + fmt(mc["normality"]["shapiro_p"], 6) + " | **" + mc["normality"]["decision_alpha_0_05"] + "** |")
    else:
        lines.append("| Maqsam/ArabicPIIRedaction | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | **NOT DIRECTLY MEASURABLE** |")

    lines.extend([
        "",
        "A rejected Normality test is a finding, not an error that should be artificially corrected. NLP sentence lengths are discrete and commonly right-skewed. The practical implication is to design batching and truncation around the actual tail of the distribution.",
        "",
        "Generated figures:",
        "",
        "- figures/wikiann_ar_length_distribution.png",
        "- figures/wikiann_ar_qq_plot.png",
        "- figures/wikiann_en_length_distribution.png",
        "- figures/wikiann_en_qq_plot.png",
        "",
        "## 3. Ten deterministic random samples and qualitative sanity review",
        "",
        "The following examples come from the training split using random seed 42. They are preserved in CSV form so that the same review can be reproduced.",
        "",
        sample_table("WikiANN Arabic — 10 random samples", ar["random_samples"]),
        "",
        sample_table("WikiANN English — 10 random samples", en["random_samples"]),
        "",
    ])
    if maqsam_direct:
        lines.extend([
            sample_table("Maqsam/ArabicPIIRedaction — 10 random samples", maqsam["random_samples"]),
            "",
        ])
    else:
        lines.extend([
            "### Maqsam/ArabicPIIRedaction",
            "",
            "Ten random training rows cannot be truthfully printed because the underlying rows were not directly accessible in this run. Model-card examples are not substituted for random dataset samples.",
            "",
        ])

    lines.extend([
        "Qualitative interpretation: WikiANN is Wikipedia-derived NER material, not conversational PII text. Short fragments, title-like snippets and Wikipedia artifacts can therefore appear even when the annotation is structurally valid. This domain difference matters for a future model intended for chats, forms or personal-data redaction.",
        "",
        "**Manual sample-quality findings:** the deterministic Arabic sample includes cases such as كتلة شمسية and نصف قطر شمسي labeled ORG, and وسائل تواصل اجتماعي labeled ORG; the English sample includes West Hartford, CT labeled ORG and song titles labeled ORG. These are semantically questionable labels and are concrete evidence of silver-standard annotation noise rather than merely a theoretical risk.",
        "",
        "A second Arabic-specific artifact is very large: **" + str(ac.get("redirect_like_prefix_rows", 0)) + " of " + str(ac["rows"]) + " rows (" + fmt(ac.get("redirect_like_prefix_pct", 0.0)) + "%) begin with تحويل**. This strongly indicates Wikipedia redirect/title-style material and means the Arabic subset is not representative of ordinary natural prose.",
        "",
        "## 4. Labels and PII coverage",
        "",
        label_table("WikiANN Arabic BIO label distribution", ac["label_counts"]),
        "",
        label_table("WikiANN English BIO label distribution", ec["label_counts"]),
        "",
        "WikiANN has seven BIO labels but only three semantic entity classes: **PER, ORG and LOC**.",
        "",
        "At the semantic entity-start level, WikiANN is comparatively balanced: Arabic LOC/ORG/PER counts are " + str(ar_entities) + " (max/min ratio " + fmt(ar_entity_balance) + "), and English counts are " + str(en_entities) + " (max/min ratio " + fmt(en_entity_balance) + "). The bigger imbalance concern is therefore O versus entity tokens and domain/annotation quality, not severe PER/ORG/LOC scarcity.",
        "",
        "| PII or entity category | WikiANN |",
        "|---|---|",
        "| Person name | Yes — PER |",
        "| Organization | Yes — ORG |",
        "| Geographic location | Yes — LOC |",
        "| Home or street address | No dedicated class |",
        "| Phone number | No |",
        "| Email | No |",
        "| National or structured identifier | No |",
        "| IBAN | No |",
        "| Credit card | No |",
        "| Social-media handle | No |",
        "",
        "### MutazYoune/Arabic-NER-PII model-card schema",
        "",
        "The model card documents 11 BIO labels: O plus B- and I- variants for five coarse entity types: CONTACT, NETWORK, IDENTIFIER, NUMERIC_ID and PII. CONTACT groups email and telephone-like information, while the generic PII class is broader than a clean person-name taxonomy. These are documented claims unless independently confirmed from the raw training rows.",
        "",
        "### contriqx-Hub/arabic-pii-guardrail task and taxonomy",
        "",
        "The card describes PHONE, EMAIL, SOCIAL_MEDIA, IBAN, ADDRESS, URL, CREDIT_CARD, CRYPTO_ADDRESS, OFF_PLATFORM_ATTEMPT and NAME contexts, but the model output itself is binary PII versus NOT_PII. It classifies intent to share PII after an entity has already been extracted; it is not a token-level NER training corpus from the supplied link.",
        "",
        "## 5. Weird or risky findings that can affect model training",
        "",
        "### Directly measured WikiANN findings",
        "",
        "- Arabic O-token share: **" + fmt(ac["O_token_pct"]) + "%**.",
        "- English O-token share: **" + fmt(ec["O_token_pct"]) + "%**.",
        "- Arabic exact duplicate rows across all splits combined: **" + str(ac["exact_duplicate_rows"]) + " (" + fmt(ac["exact_duplicate_rows"] / ac["rows"] * 100) + "%)**.",
        "- English exact duplicate rows across all splits combined: **" + str(ec["exact_duplicate_rows"]) + " (" + fmt(ec["exact_duplicate_rows"] / ec["rows"] * 100) + "%)**.",
        "- Arabic annotation-length mismatches: **" + str(ac["annotation_length_mismatches"]) + "**.",
        "- English annotation-length mismatches: **" + str(ec["annotation_length_mismatches"]) + "**.",
        "- Arabic BIO transition anomalies: **" + str(ac["bio_transition_errors"]) + "**.",
        "- English BIO transition anomalies: **" + str(ec["bio_transition_errors"]) + "**.",
        "- Arabic long-length IQR outliers: **" + str(ac["length"]["iqr_outlier_count"]) + " (" + fmt(ac["length"]["iqr_outlier_pct"]) + "%)**.",
        "- English long-length IQR outliers: **" + str(ec["length"]["iqr_outlier_count"]) + " (" + fmt(ec["length"]["iqr_outlier_pct"]) + "%)**.",
        "- Arabic rows containing both Arabic and Latin-script letters: **" + fmt(ac["mixed_arabic_latin_script_pct"]) + "%**.",
        "- Arabic redirect-like rows beginning with تحويل: **" + str(ac.get("redirect_like_prefix_rows", 0)) + " (" + fmt(ac.get("redirect_like_prefix_pct", 0.0)) + "%)**.",
        "",
        "### Cross-split exact-overlap audit",
        "",
        "| Pair | Arabic overlap | Arabic % of smaller unique split | English overlap | English % of smaller unique split |",
        "|---|---:|---:|---:|---:|",
    ])
    pairs = sorted(set(ar["cross_split_exact_overlap"]) | set(en["cross_split_exact_overlap"]))
    for pair in pairs:
        arow = ar["cross_split_exact_overlap"].get(pair, {})
        erow = en["cross_split_exact_overlap"].get(pair, {})
        av = arow.get("exact_sentence_overlap", 0)
        ev = erow.get("exact_sentence_overlap", 0)
        ap = arow.get("pct_of_smaller_unique_split", 0.0)
        ep = erow.get("pct_of_smaller_unique_split", 0.0)
        lines.append("| " + pair + " | " + str(av) + " | " + fmt(ap) + "% | " + str(ev) + " | " + fmt(ep) + "% |")

    lines.extend([
        "",
        "Any non-zero exact train-validation-test overlap is an evaluation-leakage warning and should be resolved before final model benchmarking.",
        "",
        "### Structural training risks",
        "",
        "1. **PII coverage gap:** WikiANN cannot train a comprehensive PII detector because it lacks dedicated phone, email, address, identifier and financial classes.",
        "2. **Domain mismatch:** Wikipedia NER text differs materially from messages, support chats, forms and redaction workloads.",
        "3. **Silver-standard annotation risk:** WikiANN is automatically derived and should not be assumed to have gold-label quality in every language.",
        "4. **Non-entity dominance:** high O-token prevalence can make raw token accuracy misleading; use entity-level precision, recall and F1 by class.",
        "5. **Declared synthetic and regex bias:** the MutazYoune model card says its training set combines 10,000 original and 10,000 LLM-augmented sentences with regex-based annotation. If confirmed, template repetition and boundary bias should be audited before training.",
        "6. **Guardrail task mismatch:** its model card reports a false-positive rate of 28.8% and weaker mixed-language F1 of 0.782. These are intent-classification characteristics, not NER boundary metrics.",
        "",
        "## 6. Training-readiness assessment",
        "",
        "| Resource | Status for future Arabic token-level NER/PII training | Why |",
        "|---|---|---|",
        "| WikiANN Arabic | **LIMITED / USEFUL AUXILIARY** | Good PER/ORG/LOC signal, but incomplete PII taxonomy, high exact duplication/split overlap, 50% redirect-like rows, questionable silver labels and Wikipedia domain mismatch. |",
        "| WikiANN English | **AUXILIARY / MULTILINGUAL CONTROL** | Useful for English comparison and multilingual experiments, not the core Arabic PII corpus. |",
        "| Maqsam/ArabicPIIRedaction | **" + ("READY_WITH_AUDIT" if maqsam_direct else "UNVERIFIED / ACCESS-BLOCKED") + "** | " + ("Rows were directly measured; inspect generated findings before use." if maqsam_direct else "The model card is promising, but the raw rows were not directly auditable in this execution.") + " |",
        "| arabic-pii-guardrail | **NOT A DIRECT NER DATASET** | Useful later as a second-stage sharing-intent signal or taxonomy reference, not as supplied token-boundary training data. |",
        "",
        "## 7. Recommended modeling direction after this assignment",
        "",
        "For the later NER phase, define a canonical fine-grained PII schema, deduplicate before splitting, preserve character/token span boundaries, create clean train/validation/test partitions, and evaluate entity-level F1 per class. WikiANN can supplement PER/ORG/LOC recognition, but a dedicated Arabic PII corpus is needed for phone, email, address, ID and financial entities.",
        "",
        "## 8. Reproducibility manifest",
        "",
        "- results/source_qualification.json",
        "- results/wikiann_ar_analysis.json",
        "- results/wikiann_en_analysis.json",
        "- results/maqsam_arabic_pii_redaction_analysis.json",
        "- results/wikiann_ar_random_samples.csv",
        "- results/wikiann_en_random_samples.csv",
        "- results/dataset_comparison.csv",
        "- figures/ length histograms and Q-Q plots",
        "",
        "## Final answer to the four requested points",
        "",
        "1. **Length distributions and Normality:** measured, plotted and statistically tested for every directly accessible dataset configuration.",
        "2. **Ten random sentences:** produced reproducibly for Arabic and English WikiANN, plus the declared Maqsam dataset only if the underlying rows are accessible.",
        "3. **Labels and PII:** WikiANN has three semantic NER classes and lacks most major PII classes; the supplied model pages describe richer PII concepts but are not equivalent raw datasets.",
        "4. **Training-impact notes:** class dominance, duplicates, split leakage, outliers, BIO consistency, script mixing, domain mismatch, annotation provenance and inaccessible-data boundaries are explicitly audited.",
        "",
    ])

    report = "\n".join(lines)
    path = REPORTS / "FINAL_REPORT.md"
    path.write_text(report, encoding="utf-8")
    return report
