from __future__ import annotations
import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
REPORTS = ROOT / "reports"
for p in (RESULTS, FIGURES, REPORTS):
    p.mkdir(parents=True, exist_ok=True)

WIKIANN_LABELS = {
    0: "O", 1: "B-PER", 2: "I-PER", 3: "B-ORG",
    4: "I-ORG", 5: "B-LOC", 6: "I-LOC"
}

def dump_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()

def token_text(tokens) -> str:
    return normalize_text(" ".join(str(x) for x in tokens))

def script_ratios(text: str) -> tuple[float, float]:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0, 0.0
    ar = sum(("\u0600" <= c <= "\u06FF") or ("\u0750" <= c <= "\u077F") or ("\u08A0" <= c <= "\u08FF") for c in letters)
    lat = sum(("A" <= c <= "Z") or ("a" <= c <= "z") for c in letters)
    return ar / len(letters), lat / len(letters)

def length_stats(values: list[int]) -> dict[str, Any]:
    a = np.asarray(values, dtype=float)
    q1, q3 = np.percentile(a, [25, 75])
    threshold = q3 + 1.5 * (q3 - q1)
    return {
        "n": int(len(a)),
        "mean": float(np.mean(a)),
        "median": float(np.median(a)),
        "std": float(np.std(a, ddof=1)),
        "min": int(np.min(a)),
        "p25": float(q1),
        "p75": float(q3),
        "p95": float(np.percentile(a, 95)),
        "p99": float(np.percentile(a, 99)),
        "max": int(np.max(a)),
        "skew": float(stats.skew(a, bias=False)),
        "excess_kurtosis": float(stats.kurtosis(a, fisher=True, bias=False)),
        "iqr_outlier_threshold": float(threshold),
        "iqr_outlier_count": int(np.sum(a > threshold)),
        "iqr_outlier_pct": float(np.mean(a > threshold) * 100),
    }

def normality(values: list[int]) -> dict[str, Any]:
    a = np.asarray(values, dtype=float)
    rng = np.random.default_rng(SEED)
    sample = a if len(a) <= 5000 else rng.choice(a, size=5000, replace=False)
    k2, kp = stats.normaltest(a)
    sw, sp = stats.shapiro(sample)
    ad = stats.anderson(a, dist="norm")
    reject = kp < 0.05 or sp < 0.05
    return {
        "dagostino_k2": float(k2),
        "dagostino_p": float(kp),
        "shapiro_w": float(sw),
        "shapiro_p": float(sp),
        "shapiro_n": int(len(sample)),
        "anderson_statistic": float(ad.statistic),
        "anderson_critical_values": [float(x) for x in ad.critical_values],
        "decision_alpha_0_05": "REJECT_NORMALITY" if reject else "DO_NOT_REJECT_NORMALITY",
    }

def plot_lengths(values: list[int], slug: str, title: str) -> list[str]:
    a = np.asarray(values, dtype=float)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(a, bins="auto", density=True, alpha=0.75)
    mu, sigma = np.mean(a), np.std(a, ddof=1)
    if sigma > 0:
        x = np.linspace(max(0, np.min(a)), np.max(a), 300)
        ax.plot(x, stats.norm.pdf(x, mu, sigma), linewidth=2, label="Normal fit")
        ax.legend()
    ax.set_title(title + " — token-length distribution")
    ax.set_xlabel("Tokens per sample")
    ax.set_ylabel("Density")
    fig.tight_layout()
    p1 = FIGURES / (slug + "_length_distribution.png")
    fig.savefig(p1, dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 6))
    stats.probplot(a, dist="norm", plot=ax)
    ax.set_title(title + " — Normal Q-Q plot")
    fig.tight_layout()
    p2 = FIGURES / (slug + "_qq_plot.png")
    fig.savefig(p2, dpi=180)
    plt.close(fig)
    return [str(p1.relative_to(ROOT)), str(p2.relative_to(ROOT))]

def bio_errors(tags) -> int:
    mapped = [WIKIANN_LABELS.get(int(t), str(t)) for t in tags]
    prev = "O"
    errors = 0
    for tag in mapped:
        if tag.startswith("I-"):
            typ = tag[2:]
            if prev not in ("B-" + typ, "I-" + typ):
                errors += 1
        prev = tag
    return errors


def bio_errors_labels(tags) -> int:
    """Count invalid BIO I-tag transitions for string labels."""
    prev = "O"
    errors = 0
    for raw in tags:
        tag = str(raw)
        if tag.startswith("I-"):
            typ = tag[2:]
            if prev not in ("B-" + typ, "I-" + typ):
                errors += 1
        prev = tag
    return errors


def semantic_class_counts(label_counts: dict[str, int]) -> dict[str, int]:
    """Collapse BIO label counts to semantic classes using entity starts."""
    out: dict[str, int] = {}
    for label, count in label_counts.items():
        if label.startswith("B-"):
            cls = label[2:]
            out[cls] = out.get(cls, 0) + int(count)
    return out
