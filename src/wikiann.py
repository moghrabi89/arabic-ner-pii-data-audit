from __future__ import annotations
from collections import Counter

import numpy as np
import pandas as pd
from datasets import load_dataset

from .common import (
    FIGURES, RESULTS, SEED, WIKIANN_LABELS, bio_errors, dump_json,
    length_stats, normalize_text, normality, plot_lengths, script_ratios, token_text,
)

def analyze_wikiann(lang: str):
    ds = load_dataset("unimelb-nlp/wikiann", lang)
    split_stats = {}
    split_sets = {}
    all_lengths = []
    all_texts = []
    all_tags = []
    span_types = Counter()
    annotation_mismatch = 0
    bio_problem_count = 0
    mixed_script = 0
    arabic_present = 0
    latin_present = 0
    replacement_chars = 0
    redirect_like_prefix = 0

    for split, part in ds.items():
        lengths = []
        texts = []
        tags_here = []
        for row in part:
            tokens = list(row["tokens"])
            tags = list(row["ner_tags"])
            langs = list(row["langs"])
            text = token_text(tokens)
            lengths.append(len(tokens))
            texts.append(text)
            tags_here.extend(int(x) for x in tags)
            all_tags.extend(int(x) for x in tags)
            for span in row.get("spans", []) or []:
                typ = str(span).split(":", 1)[0].strip()
                if typ:
                    span_types[typ] += 1
            if not (len(tokens) == len(tags) == len(langs)):
                annotation_mismatch += 1
            bio_problem_count += bio_errors(tags)
            ar, lat = script_ratios(text)
            if ar > 0:
                arabic_present += 1
            if lat > 0:
                latin_present += 1
            if ar > 0.05 and lat > 0.05:
                mixed_script += 1
            if "\ufffd" in text:
                replacement_chars += 1
            if lang == "ar" and text.startswith("تحويل "):
                redirect_like_prefix += 1
            if lang == "en" and (text.lower().startswith("redirect ") or text.startswith("#REDIRECT")):
                redirect_like_prefix += 1

        all_lengths.extend(lengths)
        all_texts.extend(texts)
        normed = [normalize_text(x) for x in texts]
        split_sets[split] = set(normed)
        labels = Counter(WIKIANN_LABELS.get(x, str(x)) for x in tags_here)
        split_stats[split] = {
            "rows": len(part),
            "length": length_stats(lengths),
            "normality": normality(lengths),
            "exact_duplicate_rows": len(normed) - len(set(normed)),
            "exact_duplicate_pct": (len(normed) - len(set(normed))) / max(1, len(normed)) * 100,
            "label_counts": dict(labels),
        }

    leakage = {}
    names = list(split_sets)
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            overlap = split_sets[left] & split_sets[right]
            leakage[left + "__" + right] = {
                "exact_sentence_overlap": len(overlap),
                "pct_of_smaller_unique_split": len(overlap) / max(1, min(len(split_sets[left]), len(split_sets[right]))) * 100,
            }

    label_counts = Counter(WIKIANN_LABELS.get(x, str(x)) for x in all_tags)
    total_tokens = sum(label_counts.values())
    combined_normed = [normalize_text(x) for x in all_texts]

    rng = np.random.default_rng(SEED)
    sample_split = "train" if "train" in ds else names[0]
    ids = rng.choice(len(ds[sample_split]), size=min(10, len(ds[sample_split])), replace=False)
    samples = []
    for idx in ids:
        row = ds[sample_split][int(idx)]
        samples.append({
            "index": int(idx),
            "text": token_text(row["tokens"]),
            "tokens": list(row["tokens"]),
            "labels": [WIKIANN_LABELS.get(int(x), str(x)) for x in row["ner_tags"]],
            "spans": list(row.get("spans", []) or []),
        })

    result = {
        "dataset": "unimelb-nlp/wikiann",
        "language": lang,
        "source_status": "DIRECTLY_MEASURED",
        "splits": split_stats,
        "combined": {
            "rows": len(all_texts),
            "length": length_stats(all_lengths),
            "normality": normality(all_lengths),
            "label_counts": dict(label_counts),
            "semantic_entity_counts_from_spans": dict(span_types),
            "O_token_pct": label_counts.get("O", 0) / max(1, total_tokens) * 100,
            "entity_token_pct": (total_tokens - label_counts.get("O", 0)) / max(1, total_tokens) * 100,
            "exact_duplicate_rows": len(combined_normed) - len(set(combined_normed)),
            "annotation_length_mismatches": annotation_mismatch,
            "bio_transition_errors": bio_problem_count,
            "replacement_character_rows": replacement_chars,
            "redirect_like_prefix_rows": redirect_like_prefix,
            "redirect_like_prefix_pct": redirect_like_prefix / max(1, len(all_texts)) * 100,
            "samples_with_arabic_letters_pct": arabic_present / max(1, len(all_texts)) * 100,
            "samples_with_latin_letters_pct": latin_present / max(1, len(all_texts)) * 100,
            "mixed_arabic_latin_script_pct": mixed_script / max(1, len(all_texts)) * 100,
        },
        "cross_split_exact_overlap": leakage,
        "random_samples": samples,
        "figures": plot_lengths(all_lengths, "wikiann_" + lang, "WikiANN " + lang),
        "semantic_classes": ["PER", "ORG", "LOC"],
        "pii_coverage": {
            "person_name": "YES — PER",
            "organization": "YES — ORG",
            "geographic_location": "YES — LOC",
            "home_address": "NO dedicated class",
            "phone_number": "NO",
            "email": "NO",
            "structured_id": "NO",
            "iban": "NO",
            "credit_card": "NO",
            "social_media": "NO",
        },
    }
    dump_json(RESULTS / ("wikiann_" + lang + "_analysis.json"), result)
    pd.DataFrame(samples).to_csv(RESULTS / ("wikiann_" + lang + "_random_samples.csv"), index=False)
    return result
