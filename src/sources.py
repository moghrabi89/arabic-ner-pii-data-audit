from __future__ import annotations
from collections import Counter

import numpy as np
import pandas as pd
from datasets import DatasetDict, load_dataset
from huggingface_hub import HfApi

from .common import RESULTS, SEED, dump_json, length_stats, normalize_text, normality, plot_lengths, token_text

MODEL_CARD_CLAIMS = {
    "MutazYoune/Arabic-NER-PII": {
        "source_type": "model",
        "task": "token-classification / NER",
        "declared_training_dataset": "Maqsam/ArabicPIIRedaction",
        "declared_size": "20,000 sentences (10k original + 10k LLM-augmented)",
        "declared_annotation": "BIO tagging scheme with regex pattern matching",
        "declared_labels": "11 total: O + B-/I- for CONTACT, NETWORK, IDENTIFIER, NUMERIC_ID, PII",
        "declared_entities": ["CONTACT", "NETWORK", "IDENTIFIER", "NUMERIC_ID", "PII"],
    },
    "contriqx-Hub/arabic-pii-guardrail": {
        "source_type": "model",
        "task": "binary PII-sharing intent classification, not token-level NER",
        "declared_training_dataset": None,
        "declared_size": "41,427 samples across 9 original entity types + 2,500 NAME samples",
        "declared_languages": ["Arabic", "English", "Mixed/code-switched", "Arabizi"],
        "entity_types": [
            "PHONE", "EMAIL", "SOCIAL_MEDIA", "IBAN", "ADDRESS", "URL",
            "CREDIT_CARD", "CRYPTO_ADDRESS", "OFF_PLATFORM_ATTEMPT", "NAME"
        ],
        "output_labels": ["PII", "NOT_PII"],
        "benchmark_claims": {
            "macro_f1": 0.865,
            "accuracy": 0.866,
            "false_positive_rate": 0.288,
            "false_negative_rate": 0.031,
            "mixed_language_f1": 0.782,
            "false_positive_traps_f1": 0.415,
            "context_flip_pairs_f1": 0.637,
        },
    },
}

def qualify_sources():
    api = HfApi()
    checks = [
        ("unimelb-nlp/wikiann", "dataset"),
        ("Maqsam/ArabicPIIRedaction", "dataset"),
        ("MutazYoune/Arabic-NER-PII", "model"),
        ("contriqx-Hub/arabic-pii-guardrail", "model"),
    ]
    out = {
        "checked_utc": pd.Timestamp.utcnow().isoformat(),
        "sources": {},
        "model_card_claims": MODEL_CARD_CLAIMS,
    }
    for repo_id, kind in checks:
        try:
            info = api.dataset_info(repo_id) if kind == "dataset" else api.model_info(repo_id)
            out["sources"][repo_id] = {
                "kind": kind,
                "reachable": True,
                "id": info.id,
                "sha": info.sha,
                "private": getattr(info, "private", None),
                "gated": getattr(info, "gated", None),
                "pipeline_tag": getattr(info, "pipeline_tag", None),
            }
        except Exception as exc:
            out["sources"][repo_id] = {
                "kind": kind,
                "reachable": False,
                "error": type(exc).__name__ + ": " + str(exc)[:600],
            }
    try:
        space = api.space_info("Maqsam/ArabicPIIRedaction")
        space_files = api.list_repo_files("Maqsam/ArabicPIIRedaction", repo_type="space")
        out["sources"]["Maqsam/ArabicPIIRedaction_space"] = {
            "kind": "space",
            "reachable": True,
            "id": space.id,
            "sha": space.sha,
            "private": getattr(space, "private", None),
            "gated": getattr(space, "gated", None),
            "files": space_files,
        }
    except Exception as exc:
        out["sources"]["Maqsam/ArabicPIIRedaction_space"] = {
            "kind": "space",
            "reachable": False,
            "error": type(exc).__name__ + ": " + str(exc)[:600],
        }

    dump_json(RESULTS / "source_qualification.json", out)
    return out

def _columns(part):
    cols = list(part.column_names)
    def choose(options):
        return next((x for x in options if x in cols), None)
    return {
        "text": choose(["text", "sentence", "content", "context", "raw_text"]),
        "tokens": choose(["tokens", "words", "word_tokens"]),
        "labels": choose(["ner_tags", "tags", "labels", "label", "bio_tags", "annotations"]),
    }

def _label_map(feature):
    try:
        if hasattr(feature, "feature") and hasattr(feature.feature, "names"):
            return {i: n for i, n in enumerate(feature.feature.names)}
        if hasattr(feature, "names"):
            return {i: n for i, n in enumerate(feature.names)}
    except Exception:
        return None
    return None

def analyze_declared_dataset(repo_id="Maqsam/ArabicPIIRedaction"):
    slug = "maqsam_arabic_pii_redaction"
    result = {"dataset": repo_id, "source_status": "UNKNOWN", "access_error": None}
    try:
        ds = load_dataset(repo_id)
    except Exception as exc:
        result["source_status"] = "NOT_DIRECTLY_ACCESSIBLE"
        result["access_error"] = type(exc).__name__ + ": " + str(exc)[:1000]
        dump_json(RESULTS / (slug + "_analysis.json"), result)
        return result

    if not isinstance(ds, DatasetDict):
        ds = DatasetDict({"train": ds})
    first = "train" if "train" in ds else next(iter(ds))
    cols = _columns(ds[first])
    label_map = _label_map(ds[first].features[cols["labels"]]) if cols["labels"] else None
    result["source_status"] = "DIRECTLY_MEASURED"
    result["schema"] = {name: str(part.features) for name, part in ds.items()}
    result["detected_columns"] = cols

    all_lengths = []
    all_texts = []
    labels = Counter()
    splits = {}
    for split, part in ds.items():
        lengths = []
        texts = []
        for row in part:
            if cols["tokens"] and isinstance(row.get(cols["tokens"]), (list, tuple)):
                toks = list(row[cols["tokens"]])
                text = token_text(toks)
                length = len(toks)
            elif cols["text"] and isinstance(row.get(cols["text"]), str):
                text = normalize_text(row[cols["text"]])
                length = len(text.split())
            else:
                text = normalize_text(str(row))
                length = len(text.split())
            lengths.append(length)
            texts.append(text)
            if cols["labels"]:
                raw = row.get(cols["labels"])
                vals = raw if isinstance(raw, (list, tuple)) else [raw]
                for lab in vals:
                    if isinstance(lab, (int, np.integer)) and label_map:
                        labels[label_map.get(int(lab), str(lab))] += 1
                    else:
                        labels[str(lab)] += 1
        all_lengths.extend(lengths)
        all_texts.extend(texts)
        splits[split] = {
            "rows": len(part),
            "length": length_stats(lengths),
            "normality": normality(lengths),
            "exact_duplicate_rows": len(texts) - len(set(map(normalize_text, texts))),
        }

    rng = np.random.default_rng(SEED)
    part = ds[first]
    ids = rng.choice(len(part), size=min(10, len(part)), replace=False)
    samples = []
    for idx in ids:
        row = part[int(idx)]
        if cols["tokens"] and isinstance(row.get(cols["tokens"]), (list, tuple)):
            text = token_text(row[cols["tokens"]])
        elif cols["text"] and isinstance(row.get(cols["text"]), str):
            text = normalize_text(row[cols["text"]])
        else:
            text = normalize_text(str(row))
        samples.append({"index": int(idx), "text": text})

    result["splits"] = splits
    result["combined"] = {
        "rows": len(all_texts),
        "length": length_stats(all_lengths),
        "normality": normality(all_lengths),
        "label_counts": dict(labels),
        "exact_duplicate_rows": len(all_texts) - len(set(map(normalize_text, all_texts))),
    }
    result["random_samples"] = samples
    result["figures"] = plot_lengths(all_lengths, slug, repo_id)
    dump_json(RESULTS / (slug + "_analysis.json"), result)
    pd.DataFrame(samples).to_csv(RESULTS / (slug + "_random_samples.csv"), index=False)
    return result
