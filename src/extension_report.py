from __future__ import annotations

import pandas as pd

from .common import REPORTS, RESULTS


def _fmt(value, digits=3):
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return format(value, "." + str(digits) + "f")
    return str(value)


def build_extension_report(wiki_ar, cv18, anercorp):
    rows = []
    for name, data in [
        ("WikiANN Arabic", wiki_ar),
        ("CV18-NER", cv18),
        ("ANERCorp", anercorp),
    ]:
        if data.get("source_status", "").startswith("BLOCKED"):
            rows.append({"dataset": name, "status": data.get("source_status")})
            continue
        c = data["combined"]
        rows.append({
            "dataset": name,
            "status": data.get("source_status"),
            "rows_or_sentences": c.get("rows"),
            "mean_tokens": c["length"]["mean"],
            "median_tokens": c["length"]["median"],
            "p95_tokens": c["length"]["p95"],
            "max_tokens": c["length"]["max"],
            "skew": c["length"]["skew"],
            "normality": c["normality"]["decision_alpha_0_05"],
            "exact_duplicates": c.get("exact_duplicate_rows"),
            "O_token_pct": c.get("O_token_pct"),
            "semantic_classes": ",".join(c.get("semantic_classes", [])),
        })
    pd.DataFrame(rows).to_csv(RESULTS / "dataset_comparison_extended.csv", index=False)

    lines = [
        "# Arabic NER Dataset Audit — Extension Report",
        "",
        "This extension applies the same evidence-backed pipeline to Elyadata/CV18-NER and asas-ai/ANERCorp, then compares them with the previously audited Arabic WikiANN subset.",
        "",
        "## Methodological note",
        "",
        "Normality is measured because it was explicitly requested, but a non-Normal sentence-length distribution is not by itself a reason to reject a dataset for model training. Training suitability is judged from the observed length tail, label coverage, duplicates/leakage, annotation quality, domain fit, and reproducibility together.",
        "",
        "## Comparison",
        "",
        "| Dataset | Samples/sentences | Mean tokens | Median | P95 | Max | Skew | Normality | Exact duplicates | O-token % |",
        "|---|---:|---:|---:|---:|---:|---:|---|---:|---:|",
    ]
    for name, data in [("WikiANN Arabic", wiki_ar), ("CV18-NER", cv18), ("ANERCorp", anercorp)]:
        if data.get("source_status", "").startswith("BLOCKED"):
            lines.append("| " + name + " | BLOCKED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |")
            continue
        c = data["combined"]
        lines.append(
            "| " + name + " | " + str(c.get("rows")) + " | " + _fmt(c["length"]["mean"]) +
            " | " + _fmt(c["length"]["median"]) + " | " + _fmt(c["length"]["p95"]) +
            " | " + str(c["length"]["max"]) + " | " + _fmt(c["length"]["skew"]) +
            " | " + c["normality"]["decision_alpha_0_05"] +
            " | " + str(c.get("exact_duplicate_rows", "N/A")) +
            " | " + _fmt(c.get("O_token_pct")) + " |"
        )

    lines += [
        "",
        "## CV18-NER evidence boundary",
        "",
        cv18.get("loader_note", "N/A"),
        "",
        "The audit evaluates the text/NER annotation field only. The source dataset is speech-oriented, but audio-duration analysis is outside the requested text-length pipeline.",
        "",
        "## ANERCorp evidence boundary",
        "",
        anercorp.get("boundary_method", "N/A"),
        "",
        "The Hugging Face representation is token-level. Sentence-length statistics therefore refer to sentences reconstructed using the documented period-boundary rule, not native sentence rows from the Hugging Face parquet.",
        "",
        "## Label coverage",
        "",
        "- CV18-NER semantic classes: " + ", ".join(cv18.get("combined", {}).get("semantic_classes", [])) + ".",
        "- ANERCorp semantic classes: " + ", ".join(anercorp.get("combined", {}).get("semantic_classes", [])) + ".",
        "",
        "## Reproducibility outputs",
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
    ]
    report = "\n".join(lines)
    (REPORTS / "EXTENSION_REPORT.md").write_text(report, encoding="utf-8")
    return report
