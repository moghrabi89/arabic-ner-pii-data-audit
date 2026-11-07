from __future__ import annotations

import json
from pathlib import Path

from .common import FIGURES, REPORTS, RESULTS, ROOT, SEED, dump_json
from .report import build_report
from .sources import analyze_declared_dataset, qualify_sources
from .wikiann import analyze_wikiann
from .additional_datasets import analyze_cv18_ner, analyze_anercorp
from .extension_report import build_extension_report


def main():
    source_q = qualify_sources()
    wiki_ar = analyze_wikiann("ar")
    wiki_en = analyze_wikiann("en")
    maqsam = analyze_declared_dataset("Maqsam/ArabicPIIRedaction")
    cv18 = analyze_cv18_ner()
    anercorp = analyze_anercorp()
    report = build_report(source_q, wiki_ar, wiki_en, maqsam)
    extension_report = build_extension_report(wiki_ar, cv18, anercorp)
    integrated_report = report + "\n\n---\n\n" + extension_report
    (REPORTS / "FINAL_REPORT.md").write_text(integrated_report, encoding="utf-8")

    generated = []
    for parent in (RESULTS, FIGURES, REPORTS):
        for path in parent.rglob("*"):
            if path.is_file():
                generated.append(str(path.relative_to(ROOT)))

    status = "PASS"
    evidence_boundaries = []
    if maqsam.get("source_status") != "DIRECTLY_MEASURED":
        status = "PASS_WITH_EVIDENCE_BOUNDARIES"
        evidence_boundaries.append(
            "Maqsam/ArabicPIIRedaction could not be directly measured; its model-card claims remain documented claims."
        )
    evidence_boundaries.append(
        "contriqx-Hub/arabic-pii-guardrail is a model link without a directly supplied raw training dataset."
    )

    manifest = {
        "seed": SEED,
        "status": status,
        "evidence_boundaries": evidence_boundaries,
        "generated_files": sorted(generated),
        "report_character_count": len(integrated_report),
        "base_report_character_count": len(report),
        "extension_report_character_count": len(extension_report),
        "extension_datasets": {
            "Elyadata/CV18-NER": cv18.get("source_status"),
            "asas-ai/ANERCorp": anercorp.get("source_status"),
        },
    }
    dump_json(RESULTS / "run_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
