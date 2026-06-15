from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from app.classifier import LABEL_KEYS


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: str | Path) -> list[dict]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def oversample_minimum(rows: list[dict], minimum: int) -> list[dict]:
    if minimum <= 0:
        return rows

    by_label: dict[str, list[dict]] = {label: [] for label in LABEL_KEYS}
    for row in rows:
        by_label[row["label"]].append(row)

    balanced = list(rows)
    for label, label_rows in by_label.items():
        if not label_rows:
            print(f"Warning: no training rows for label {label}; cannot oversample it.")
            continue
        needed = minimum - len(label_rows)
        for index in range(max(0, needed)):
            source = dict(label_rows[index % len(label_rows)])
            source["source"] = f"{source['source']}+oversampled"
            balanced.append(source)
    return balanced


def print_label_counts(rows: list[dict], title: str) -> None:
    counts = Counter(row["label"] for row in rows)
    print(title)
    for label in LABEL_KEYS:
        print(f"  {label}: {counts[label]}")

