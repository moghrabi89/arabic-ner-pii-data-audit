from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from datasets import load_dataset
from huggingface_hub import HfApi, hf_hub_download

from .common import (
    RESULTS, SEED, bio_errors_labels, dump_json, length_stats, normalize_text,
    normality, plot_lengths, script_ratios, semantic_class_counts, token_text,
)

INLINE_NER = re.compile(r"<([^<>]+?)\s+((?:B|I)-[A-Za-z0-9_]+)>")

def _cross_split_overlap(split_sets):
    names = list(split_sets)
    out = {}
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            overlap = split_sets[left] & split_sets[right]
            out[left + "__" + right] = {
                "exact_sentence_overlap": len(overlap),
                "pct_of_smaller_unique_split": len(overlap) / max(
                    1, min(len(split_sets[left]), len(split_sets[right]))
                ) * 100,
            }
    return out

def _sample_records(records, n=10):
    if not records:
        return []
    rng = np.random.default_rng(SEED)
    ids = rng.choice(len(records), size=min(n, len(records)), replace=False)
    return [records[int(i)] for i in ids]

def _pii_coverage(classes):
    cls = {str(x).upper() for x in classes}
    return {
        "person_name": bool(cls & {"PER", "PERS", "PERSON"}),
        "organization": bool(cls & {"ORG", "ORGANIZATION"}),
        "geographic_location": bool(cls & {"LOC", "GPE", "LOCATION", "FAC"}),
        "home_address": bool(cls & {"ADDRESS", "STREET_ADDRESS"}),
        "phone_number": bool(cls & {"PHONE", "TELEPHONE"}),
        "email": "EMAIL" in cls,
        "structured_id": bool(cls & {"ID", "IDENTIFIER", "NATIONAL_ID"}),
        "iban": "IBAN" in cls,
        "credit_card": bool(cls & {"CARD", "CREDIT_CARD"}),
        "social_media": bool(cls & {"SOCIAL_MEDIA", "HANDLE", "USERNAME"}),
        "date_or_time": bool(cls & {"DATE", "TIME"}),
    }

def _parse_inline_annotation(raw):
    raw = normalize_text(str(raw).replace('""', '"'))
    tokens, tags = [], []
    pos = 0
    parse_errors = 0
    for match in INLINE_NER.finditer(raw):
        before = raw[pos:match.start()].strip()
        if before:
            plain = before.split()
            tokens.extend(plain)
            tags.extend(["O"] * len(plain))
        entity_text = match.group(1).strip()
        label = match.group(2).strip()
        entity_tokens = entity_text.split()
        if entity_tokens:
            tokens.append(entity_tokens[0])
            tags.append(label)
            if len(entity_tokens) > 1:
                typ = label[2:] if "-" in label else label
                continuation = "I-" + typ
                tokens.extend(entity_tokens[1:])
                tags.extend([continuation] * (len(entity_tokens) - 1))
        pos = match.end()
    tail = raw[pos:].strip()
    if tail:
        plain = tail.split()
        tokens.extend(plain)
        tags.extend(["O"] * len(plain))
    if "<" in raw or ">" in raw:
        consumed = INLINE_NER.sub("", raw)
        if "<" in consumed or ">" in consumed:
            parse_errors += 1
    return tokens, tags, parse_errors

def _infer_split(name):
    s = name.lower()
    if "train" in s:
        return "train"
    if "valid" in s or "dev" in s:
        return "validation"
    if "test" in s:
        return "test"
    return Path(name).stem

def analyze_cv18_ner():
    repo_id = "Elyadata/CV18-NER"
    api = HfApi()
    files = api.list_repo_files(repo_id, repo_type="dataset")
    ann_files = [
        f for f in files
        if f.lower().endswith((".csv", ".tsv", ".txt"))
        and not f.lower().endswith((".md",))
    ]
    result = {
        "dataset": repo_id,
        "source_status": "DIRECTLY_MEASURED_RAW_ANNOTATIONS",
        "loader_note": (
            "Hugging Face viewer currently reports CSV ParserError; audit reads raw "
            "annotation files directly and splits each physical row on the first delimiter."
        ),
        "repo_files": files,
        "annotation_files": ann_files,
    }
    split_records = {}
    malformed_rows = 0
    annotation_parse_errors = 0
    for filename in ann_files:
        split = _infer_split(filename)
        path = hf_hub_download(repo_id, filename=filename, repo_type="dataset")
        rows = []
        with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
            for line_no, line in enumerate(handle, 1):
                raw_line = line.rstrip("\r\n")
                if not raw_line.strip():
                    continue
                delim = "\t" if "\t" in raw_line and "," not in raw_line.split("\t", 1)[0] else ","
                if delim not in raw_line:
                    malformed_rows += 1
                    continue
                left, right = raw_line.split(delim, 1)
                if line_no == 1 and "file" in left.lower() and "sentence" in right.lower():
                    continue
                tokens, tags, err = _parse_inline_annotation(right)
                annotation_parse_errors += err
                if not tokens or len(tokens) != len(tags):
                    malformed_rows += 1
                    continue
                rows.append({
                    "file_name": left.strip().strip('"'),
                    "text": token_text(tokens),
                    "tokens": tokens,
                    "labels": tags,
                    "raw_annotation": right.strip(),
                })
        split_records.setdefault(split, []).extend(rows)

    if not split_records:
        result["source_status"] = "BLOCKED_NO_ANNOTATION_FILES"
        dump_json(RESULTS / "cv18_ner_analysis.json", result)
        return result

    all_records = [r for rows in split_records.values() for r in rows]
    all_lengths = [len(r["tokens"]) for r in all_records]
    all_tags = [tag for r in all_records for tag in r["labels"]]
    label_counts = Counter(all_tags)
    semantic = semantic_class_counts(dict(label_counts))
    split_sets, split_stats = {}, {}
    bio_errors = 0
    mixed = 0
    replacements = 0
    for split, rows in split_records.items():
        texts = [normalize_text(r["text"]) for r in rows]
        split_sets[split] = set(texts)
        lengths = [len(r["tokens"]) for r in rows]
        tags = [t for r in rows for t in r["labels"]]
        bio = sum(bio_errors_labels(r["labels"]) for r in rows)
        bio_errors += bio
        for text in texts:
            ar, lat = script_ratios(text)
            if ar > 0.05 and lat > 0.05:
                mixed += 1
            if "\ufffd" in text:
                replacements += 1
        split_stats[split] = {
            "rows": len(rows),
            "length": length_stats(lengths),
            "normality": normality(lengths),
            "exact_duplicate_rows": len(texts) - len(set(texts)),
            "label_counts": dict(Counter(tags)),
            "bio_transition_errors": bio,
        }

    total_tokens = len(all_tags)
    samples_from = split_records.get("train") or next(iter(split_records.values()))
    samples = _sample_records(samples_from)
    combined_texts = [normalize_text(r["text"]) for r in all_records]
    result.update({
        "splits": split_stats,
        "combined": {
            "rows": len(all_records),
            "length": length_stats(all_lengths),
            "normality": normality(all_lengths),
            "label_counts": dict(label_counts),
            "semantic_entity_start_counts": semantic,
            "semantic_classes": sorted(semantic),
            "O_token_pct": label_counts.get("O", 0) / max(1, total_tokens) * 100,
            "exact_duplicate_rows": len(combined_texts) - len(set(combined_texts)),
            "annotation_parse_errors": annotation_parse_errors,
            "malformed_physical_rows": malformed_rows,
            "bio_transition_errors": bio_errors,
            "replacement_character_rows": replacements,
            "mixed_arabic_latin_script_pct": mixed / max(1, len(all_records)) * 100,
        },
        "cross_split_exact_overlap": _cross_split_overlap(split_sets),
        "random_samples": samples,
        "figures": plot_lengths(all_lengths, "cv18_ner", "CV18-NER annotated text"),
        "pii_coverage": _pii_coverage(semantic),
        "scope_note": "Text/NER annotations audited; audio-duration distribution is outside the requested text-length pipeline.",
    })
    dump_json(RESULTS / "cv18_ner_analysis.json", result)
    pd.DataFrame([
        {"file_name": r["file_name"], "text": r["text"], "labels": " ".join(r["labels"])}
        for r in samples
    ]).to_csv(RESULTS / "cv18_ner_random_samples.csv", index=False)
    return result

def _reconstruct_anercorp(rows):
    sentences = []
    tokens, tags = [], []
    for row in rows:
        word = str(row["word"])
        tag = str(row["tag"])
        tokens.append(word)
        tags.append(tag)
        if re.fullmatch(r"\.+", word):
            sentences.append({"text": token_text(tokens), "tokens": tokens, "labels": tags})
            tokens, tags = [], []
    if tokens:
        sentences.append({"text": token_text(tokens), "tokens": tokens, "labels": tags})
    return sentences

def analyze_anercorp():
    repo_id = "asas-ai/ANERCorp"
    ds = load_dataset(repo_id)
    split_records = {split: _reconstruct_anercorp(part) for split, part in ds.items()}
    all_records = [r for rows in split_records.values() for r in rows]
    all_lengths = [len(r["tokens"]) for r in all_records]
    all_tags = [tag for r in all_records for tag in r["labels"]]
    label_counts = Counter(all_tags)
    semantic = semantic_class_counts(dict(label_counts))
    split_sets, split_stats = {}, {}
    bio_total = 0
    mixed = 0
    for split, rows in split_records.items():
        texts = [normalize_text(r["text"]) for r in rows]
        split_sets[split] = set(texts)
        lengths = [len(r["tokens"]) for r in rows]
        tags = [t for r in rows for t in r["labels"]]
        bio = sum(bio_errors_labels(r["labels"]) for r in rows)
        bio_total += bio
        for text in texts:
            ar, lat = script_ratios(text)
            if ar > 0.05 and lat > 0.05:
                mixed += 1
        split_stats[split] = {
            "token_rows": len(ds[split]),
            "reconstructed_sentences": len(rows),
            "length": length_stats(lengths),
            "normality": normality(lengths),
            "exact_duplicate_rows": len(texts) - len(set(texts)),
            "label_counts": dict(Counter(tags)),
            "bio_transition_errors": bio,
        }

    total_tokens = len(all_tags)
    samples_from = split_records.get("train") or next(iter(split_records.values()))
    samples = _sample_records(samples_from)
    combined_texts = [normalize_text(r["text"]) for r in all_records]
    result = {
        "dataset": repo_id,
        "source_status": "DIRECTLY_MEASURED_WITH_CANONICAL_SENTENCE_RECONSTRUCTION",
        "boundary_method": (
            "Hugging Face rows are token-level word/tag pairs. Sentences are reconstructed "
            "after one-or-more period tokens, matching the CAMeL Lab split documentation."
        ),
        "native_token_rows": {split: len(part) for split, part in ds.items()},
        "splits": split_stats,
        "combined": {
            "rows": len(all_records),
            "token_rows": sum(len(part) for part in ds.values()),
            "length": length_stats(all_lengths),
            "normality": normality(all_lengths),
            "label_counts": dict(label_counts),
            "semantic_entity_start_counts": semantic,
            "semantic_classes": sorted(semantic),
            "O_token_pct": label_counts.get("O", 0) / max(1, total_tokens) * 100,
            "exact_duplicate_rows": len(combined_texts) - len(set(combined_texts)),
            "bio_transition_errors": bio_total,
            "mixed_arabic_latin_script_pct": mixed / max(1, len(all_records)) * 100,
        },
        "cross_split_exact_overlap": _cross_split_overlap(split_sets),
        "random_samples": samples,
        "figures": plot_lengths(all_lengths, "anercorp", "ANERCorp reconstructed sentences"),
        "pii_coverage": _pii_coverage(semantic),
    }
    dump_json(RESULTS / "anercorp_analysis.json", result)
    pd.DataFrame([
        {"text": r["text"], "labels": " ".join(r["labels"])}
        for r in samples
    ]).to_csv(RESULTS / "anercorp_random_samples.csv", index=False)
    return result
