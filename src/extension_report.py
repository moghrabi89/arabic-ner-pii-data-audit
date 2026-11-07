from __future__ import annotations

import pandas as pd

from .common import REPORTS, RESULTS


def _fmt(value, digits=3):
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return format(value, "." + str(digits) + "f")
    return str(value)


def _pct(count, total):
    return count / max(1, total) * 100


def _sample_entities(sample):
    pairs = []
    for token, label in zip(sample.get("tokens", []), sample.get("labels", [])):
        if str(label) != "O":
            pairs.append(str(label) + ":" + str(token))
    return ", ".join(pairs) if pairs else "No tagged entity in sample"


def _sample_table(title, samples):
    lines = ["### " + title, "", "| # | Text | Tagged tokens |", "|---:|---|---|"]
    for i, sample in enumerate(samples, 1):
        text = str(sample.get("text", "")).replace("|", "\\|").replace("\n", " ")
        if len(text) > 220:
            text = text[:217] + "..."
        entities = _sample_entities(sample).replace("|", "\\|")
        if len(entities) > 180:
            entities = entities[:177] + "..."
        lines.append("| " + str(i) + " | " + text + " | " + entities + " |")
    return "\n".join(lines)


def _semantic_table(title, data):
    counts = data["combined"].get("semantic_entity_start_counts", {})
    total = sum(counts.values())
    lines = ["### " + title, "", "| Entity class | Starts | Share of entity starts |", "|---|---:|---:|"]
    for name, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append("| " + name + " | " + str(count) + " | " + _fmt(_pct(count, total)) + "% |")
    return "\n".join(lines)


def _overlap_table(data):
    overlap = data.get("cross_split_exact_overlap", {})
    lines = ["| Split pair | Exact overlap | % of smaller unique split |", "|---|---:|---:|"]
    if not overlap:
        lines.append("| N/A | 0 | 0.000% |")
        return lines
    for pair, row in sorted(overlap.items()):
        lines.append(
            "| " + pair + " | " + str(row.get("exact_sentence_overlap", 0)) +
            " | " + _fmt(row.get("pct_of_smaller_unique_split", 0.0)) + "% |"
        )
    return lines


def build_extension_report(wiki_ar, cv18, anercorp):
    rows = []
    for name, data in [("WikiANN Arabic", wiki_ar), ("CV18-NER", cv18), ("ANERCorp", anercorp)]:
        c = data["combined"]
        rows.append({
            "dataset": name,
            "status": data.get("source_status"),
            "samples_or_sentences": c.get("rows"),
            "mean_tokens": c["length"]["mean"],
            "median_tokens": c["length"]["median"],
            "p95_tokens": c["length"]["p95"],
            "max_tokens": c["length"]["max"],
            "skew": c["length"]["skew"],
            "normality": c["normality"]["decision_alpha_0_05"],
            "exact_duplicates": c.get("exact_duplicate_rows"),
            "exact_duplicate_pct": c.get(
                "exact_duplicate_pct",
                c.get("exact_duplicate_rows", 0) / max(1, c.get("rows", 1)) * 100,
            ),
            "O_token_pct": c.get("O_token_pct"),
            "semantic_classes": ",".join(c.get("semantic_classes", [])),
        })
    pd.DataFrame(rows).to_csv(RESULTS / "dataset_comparison_extended.csv", index=False)

    wc = wiki_ar["combined"]
    cc = cv18["combined"]
    ac = anercorp["combined"]

    lines = [
        "# Arabic NER Dataset Audit — CV18-NER & ANERCorp Extension",
        "",
        "This extension applies the same reproducible audit pipeline used for WikiANN to Elyadata/CV18-NER and asas-ai/ANERCorp, then compares all three Arabic NER sources.",
        "",
        "## Executive conclusion",
        "",
        "**All three length distributions reject Normality. This does not make them unusable for model training.** Sentence lengths in NLP are discrete and commonly right-skewed; practical suitability depends on the observed tail, label coverage, duplicates/leakage, annotation quality, domain fit, and reproducibility together.",
        "",
        "**CV18-NER is the strongest of the three for broad fine-grained Arabic NER coverage.** It exposes 20 observed Wojood-style entity types and has a compact length profile (mean about 7 tokens, maximum 25). However, it has severe class imbalance, the expected UNIT type is absent, CURR/LAW/PERCENT are extremely rare, exact duplicates are material, cross-split exact overlap reaches several percent, and basic BIO anomalies are present.",
        "",
        "**ANERCorp is useful for longer natural/news-style Arabic prose and has very low train/test exact overlap.** Its limitations are a heavy length tail, very high O-token share, only four semantic classes, and measurable BIO inconsistencies.",
        "",
        "**WikiANN remains auxiliary only** because of its redirect/title artifacts, high duplication, material split overlap, narrow PER/ORG/LOC taxonomy, and observed silver-label noise.",
        "",
        "None of the three datasets contains the full dedicated PII taxonomy needed for phone, email, street address, structured ID, IBAN, credit card, and social identifiers.",
        "",
        "## 1. Source qualification and evidence boundaries",
        "",
        "| Resource | Measurement mode | Evidence boundary |",
        "|---|---|---|",
        "| WikiANN Arabic | Direct dataset rows | Wikipedia-derived silver-standard NER; prior audit established redirect, duplication, leakage and label-noise issues. |",
        "| CV18-NER | Direct raw train/dev/test annotation files | Hugging Face viewer currently fails CSV parsing; the audit reads raw rows directly and preserves embedded commas by splitting each physical row only once. Audio duration is outside this text-analysis scope. |",
        "| ANERCorp | Direct word/tag rows plus documented reconstruction | Hugging Face exposes a token stream. Sentence boundaries are reconstructed after one-or-more period tokens according to the standardized CAMeL release documentation. |",
        "",
        "## 2. Length distributions and Normality",
        "",
        "| Dataset | Samples/sentences | Mean | Median | P95 | Max | Skew | Decision | IQR long outliers |",
        "|---|---:|---:|---:|---:|---:|---:|---|---:|",
        "| WikiANN Arabic | " + str(wc["rows"]) + " | " + _fmt(wc["length"]["mean"]) + " | " + _fmt(wc["length"]["median"]) + " | " + _fmt(wc["length"]["p95"]) + " | " + str(wc["length"]["max"]) + " | " + _fmt(wc["length"]["skew"]) + " | " + wc["normality"]["decision_alpha_0_05"] + " | " + str(wc["length"]["iqr_outlier_count"]) + " (" + _fmt(wc["length"]["iqr_outlier_pct"]) + "%) |",
        "| CV18-NER | " + str(cc["rows"]) + " | " + _fmt(cc["length"]["mean"]) + " | " + _fmt(cc["length"]["median"]) + " | " + _fmt(cc["length"]["p95"]) + " | " + str(cc["length"]["max"]) + " | " + _fmt(cc["length"]["skew"]) + " | " + cc["normality"]["decision_alpha_0_05"] + " | " + str(cc["length"]["iqr_outlier_count"]) + " (" + _fmt(cc["length"]["iqr_outlier_pct"]) + "%) |",
        "| ANERCorp | " + str(ac["rows"]) + " | " + _fmt(ac["length"]["mean"]) + " | " + _fmt(ac["length"]["median"]) + " | " + _fmt(ac["length"]["p95"]) + " | " + str(ac["length"]["max"]) + " | " + _fmt(ac["length"]["skew"]) + " | " + ac["normality"]["decision_alpha_0_05"] + " | " + str(ac["length"]["iqr_outlier_count"]) + " (" + _fmt(ac["length"]["iqr_outlier_pct"]) + "%) |",
        "",
        "### Interpretation",
        "",
        "- CV18-NER is the least skewed and most compact source (skew " + _fmt(cc["length"]["skew"], 2) + ", maximum " + str(cc["length"]["max"]) + " tokens). It is statistically non-Normal, but its tail is easy to manage with ordinary batching/padding.",
        "- ANERCorp provides much longer sentence diversity (P95 " + _fmt(ac["length"]["p95"], 1) + ", maximum " + str(ac["length"]["max"]) + "), so truncation/bucketing policy matters.",
        "- WikiANN Arabic is short, but its main weakness is not shortness alone: the prior audit found extensive redirect-style material and contamination.",
        "",
        "## 3. Ten deterministic random samples",
        "",
        _sample_table("CV18-NER — 10 training samples (seed 42)", cv18.get("random_samples", [])),
        "",
        _sample_table("ANERCorp — 10 reconstructed training sentences (seed 42)", anercorp.get("random_samples", [])),
        "",
        "CV18 samples are short spoken/transcribed Arabic utterances with fine-grained labels. ANERCorp samples are longer natural/news-style prose. Full untruncated samples are preserved in the generated CSV files.",
        "",
        "## 4. Labels, class balance and PII coverage",
        "",
        _semantic_table("CV18-NER semantic entity-start distribution", cv18),
        "",
        "CV18 expected schema types: " + str(len(cc.get("expected_wojood_schema_types", []))) + ". Observed semantic types: " + str(len(cc.get("observed_semantic_types_any_bio", []))) + ". Missing expected type: " + ", ".join(cc.get("missing_expected_types", [])) + ". Rare entity-start types (10 or fewer): " + ", ".join(k + "=" + str(v) for k, v in cc.get("rare_entity_start_types_le_10", {}).items()) + ". Entity-start max/min ratio: " + _fmt(cc.get("entity_start_max_min_ratio"), 1) + ".",
        "",
        _semantic_table("ANERCorp semantic entity-start distribution", anercorp),
        "",
        "ANERCorp entity-start max/min ratio: " + _fmt(ac.get("entity_start_max_min_ratio"), 2) + ". O tokens account for " + _fmt(ac.get("O_token_pct")) + "% of tokens.",
        "",
        "| PII need | WikiANN | CV18-NER | ANERCorp |",
        "|---|---|---|---|",
        "| Person name | Yes | Yes | Yes |",
        "| Organization | Yes | Yes | Yes |",
        "| Geographic location | Yes | Yes | Yes |",
        "| Date/time | No dedicated class | Yes | No dedicated class |",
        "| Phone | No | No | No |",
        "| Email | No | No | No |",
        "| Street/home address | No | No dedicated class | No |",
        "| Structured/National ID | No | No | No |",
        "| IBAN | No | No | No |",
        "| Credit card | No | No | No |",
        "| Social-media handle | No | No | No |",
        "",
        "## 5. Training-impact and quality findings",
        "",
        "| Check | WikiANN Arabic | CV18-NER | ANERCorp |",
        "|---|---:|---:|---:|",
        "| Exact duplicates | " + str(wc["exact_duplicate_rows"]) + " (" + _fmt(_pct(wc["exact_duplicate_rows"], wc["rows"])) + "%) | " + str(cc["exact_duplicate_rows"]) + " (" + _fmt(cc.get("exact_duplicate_pct")) + "%) | " + str(ac["exact_duplicate_rows"]) + " (" + _fmt(ac.get("exact_duplicate_pct")) + "%) |",
        "| O-token share | " + _fmt(wc["O_token_pct"]) + "% | " + _fmt(cc["O_token_pct"]) + "% | " + _fmt(ac["O_token_pct"]) + "% |",
        "| Basic BIO-transition anomalies | " + str(wc.get("bio_transition_errors", 0)) + " | " + str(cc.get("bio_transition_errors", 0)) + " | " + str(ac.get("bio_transition_errors", 0)) + " |",
        "",
        "### CV18-NER cross-split exact overlap",
        "",
    ] + _overlap_table(cv18) + [
        "",
        "### ANERCorp cross-split exact overlap",
        "",
    ] + _overlap_table(anercorp) + [
        "",
        "### Annotation-consistency evidence",
        "",
        "CV18-NER contains " + str(cc.get("bio_transition_errors", 0)) + " basic BIO-transition anomalies. Representative anomaly examples are preserved in results/cv18_ner_analysis.json.",
        "",
        "ANERCorp contains " + str(ac.get("bio_transition_errors", 0)) + " basic BIO-transition anomalies. Representative anomaly examples are preserved in results/anercorp_analysis.json.",
        "",
        "## 6. Training-readiness decision",
        "",
        "| Dataset | Readiness | Best use | Main caveat |",
        "|---|---|---|---|",
        "| CV18-NER | **PROMISING WITH CLEANUP** | Fine-grained Arabic NER, especially speech/transcript-style text | Severe class imbalance, UNIT absent, rare classes, duplicates/overlap, BIO anomalies, CC BY-NC non-commercial license |",
        "| ANERCorp | **USEFUL AUXILIARY WITH CLEANUP** | General Arabic NER on longer natural/news prose | Narrow four-class taxonomy, high O share, long tail, BIO inconsistencies, older news domain |",
        "| WikiANN Arabic | **LIMITED AUXILIARY** | Additional PER/ORG/LOC signal | Redirect artifacts, high duplicates, split leakage and silver-label noise |",
        "",
        "If the goal is general Arabic NER, CV18-NER is the most attractive new source for label breadth and ANERCorp is a useful complementary source for longer prose. Both should be cleaned and re-split before final benchmarking.",
        "",
        "If the goal is comprehensive Arabic PII detection, none of these three is sufficient alone. A dedicated Arabic PII corpus is still required.",
        "",
        "## 7. Licensing and reuse boundary",
        "",
        "- CV18-NER: CC BY-NC 4.0. Commercial reuse is restricted by the non-commercial condition.",
        "- ANERCorp: CC BY-SA 4.0. Attribution and share-alike obligations apply to adapted material.",
        "",
        "## 8. Reproducibility outputs",
        "",
        "- results/cv18_ner_analysis.json",
        "- results/cv18_ner_random_samples.csv",
        "- results/anercorp_analysis.json",
        "- results/anercorp_random_samples.csv",
        "- results/dataset_comparison_extended.csv",
        "- figures/cv18_ner_length_distribution.png",
        "- figures/cv18_ner_qq_plot.png",
        "- figures/anercorp_length_distribution.png",
        "- figures/anercorp_qq_plot.png",
        "",
        "## Final answer to the extension request",
        "",
        "The same pipeline has now been applied to both additional Hugging Face datasets. CV18-NER is substantially richer in entity taxonomy and has the cleanest/most compact length profile of the analyzed Arabic sources, but it requires class-balancing and annotation/split cleanup. ANERCorp provides much longer natural Arabic text with very low cross-split exact overlap, but it is a narrower and noisier four-class NER corpus. Neither dataset follows a Normal length distribution, and neither alone solves the broader PII-label coverage requirement.",
        "",
    ]

    report = "\n".join(lines)
    (REPORTS / "EXTENSION_REPORT.md").write_text(report, encoding="utf-8")
    return report
