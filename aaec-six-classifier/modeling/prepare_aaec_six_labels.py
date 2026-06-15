from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

from app.classifier import LABEL_KEYS
from modeling.common import oversample_minimum, write_jsonl


SHELL_PREFIX_RE = re.compile(
    r"^(on the other hand|however|therefore|hence|for example|for instance|in conclusion|to conclude|overall)[, ]+",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Component:
    ann_id: str
    aaec_label: str
    start: int
    end: int
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert AAEC BRAT annotations into weak six-label JSONL for transformer fine-tuning."
    )
    parser.add_argument("--corpus-dir", default="data/raw/ArgumentAnnotatedEssays-2.0")
    parser.add_argument("--output-dir", default="data/processed/aaec-six-labels")
    parser.add_argument("--include-non-argument-background", action="store_true")
    parser.add_argument(
        "--min-train-per-label",
        type=int,
        default=0,
        help="Duplicate train examples until every label has at least this many rows.",
    )
    return parser.parse_args()


def read_split(corpus_dir: Path) -> dict[str, str]:
    split_path = corpus_dir / "train-test-split.csv"
    result: dict[str, str] = {}
    with split_path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            result[row["ID"]] = "validation" if row["SET"].upper() == "TEST" else "train"
    return result


def parse_ann(path: Path) -> tuple[dict[str, Component], dict[str, str], dict[str, list[str]]]:
    components: dict[str, Component] = {}
    stances: dict[str, str] = {}
    outgoing_relations: dict[str, list[str]] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        if line.startswith("T"):
            ann_id, meta, text = line.split("\t", 2)
            parts = meta.split()
            aaec_label = parts[0]
            start = int(parts[1])
            end = int(parts[-1])
            components[ann_id] = Component(ann_id, aaec_label, start, end, clean_text(text))
        elif line.startswith("A"):
            _ann_id, attr, target, value = line.split()
            if attr == "Stance":
                stances[target] = value
        elif line.startswith("R"):
            _ann_id, relation, arg1, _arg2 = line.split()[:4]
            source = arg1.split(":", 1)[1]
            outgoing_relations.setdefault(source, []).append(relation)

    return components, stances, outgoing_relations


def clean_text(text: str) -> str:
    return " ".join(SHELL_PREFIX_RE.sub("", text.strip()).split())


def weak_six_label(component: Component, stance: str | None, outgoing_relations: list[str]) -> str:
    text = component.text.lower()
    first_words = " ".join(text.split()[:5])

    if component.aaec_label == "MajorClaim":
        return "summary_conclusion"

    if any(relation == "attacks" for relation in outgoing_relations) or stance == "Against":
        return "contrast_concession"

    if first_words.startswith(("for example", "for instance", "take ", "such as")) or " for instance" in text:
        return "example_elaboration"

    if first_words.startswith(("during ", "when ", "today ", "currently ", "in recent years", "historically ")):
        return "background_circumstance"

    if component.aaec_label == "Premise":
        return "cause_explanation"

    if component.aaec_label == "Claim":
        return "evaluation_interpretation"

    return "background_circumstance"


def non_argument_backgrounds(text: str, components: list[Component], min_words: int = 8) -> list[str]:
    spans = sorted((component.start, component.end) for component in components)
    gaps: list[tuple[int, int]] = []
    cursor = 0
    for start, end in spans:
        if start > cursor:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < len(text):
        gaps.append((cursor, len(text)))

    examples: list[str] = []
    for start, end in gaps:
        chunk = clean_text(text[start:end])
        if len(chunk.split()) >= min_words:
            examples.append(chunk)
    return examples


def convert_document(ann_path: Path, split: str, include_non_argument_background: bool) -> list[dict]:
    text_path = ann_path.with_suffix(".txt")
    full_text = text_path.read_text(encoding="utf-8") if text_path.exists() else ""
    components, stances, outgoing_relations = parse_ann(ann_path)

    rows: list[dict] = []
    for component in sorted(components.values(), key=lambda item: (item.start, item.end)):
        label = weak_six_label(component, stances.get(component.ann_id), outgoing_relations.get(component.ann_id, []))
        rows.append(
            {
                "text": component.text,
                "label": label,
                "source": "aaec_weak",
                "aaec_component": component.aaec_label,
                "essay_id": ann_path.stem,
                "split": split,
                "span": [component.start, component.end],
            }
        )

    if include_non_argument_background and full_text:
        for background in non_argument_backgrounds(full_text, list(components.values())):
            rows.append(
                {
                    "text": background,
                    "label": "background_circumstance",
                    "source": "aaec_non_argument_gap",
                    "aaec_component": "NonArgument",
                    "essay_id": ann_path.stem,
                    "split": split,
                    "span": None,
                }
            )
    return rows

def main() -> None:
    args = parse_args()
    corpus_dir = Path(args.corpus_dir)
    brat_dir = corpus_dir / "brat-project-final"
    output_dir = Path(args.output_dir)
    split_by_id = read_split(corpus_dir)

    rows_by_split = {"train": [], "validation": []}
    for ann_path in sorted(brat_dir.glob("essay*.ann")):
        split = split_by_id.get(ann_path.stem, "train")
        rows_by_split[split].extend(convert_document(ann_path, split, args.include_non_argument_background))

    if args.min_train_per_label:
        from collections import Counter

        before = Counter(row["label"] for row in rows_by_split["train"])
        rows_by_split["train"] = oversample_minimum(rows_by_split["train"], args.min_train_per_label)
        after = Counter(row["label"] for row in rows_by_split["train"])
        print("Train balancing:")
        for label in LABEL_KEYS:
            print(f"  {label}: {before[label]} -> {after[label]}")

    for split, rows in rows_by_split.items():
        path = output_dir / f"{split}.jsonl"
        write_jsonl(path, rows)
        print(f"Wrote {len(rows)} rows to {path}")

    label_counts = {label: 0 for label in LABEL_KEYS}
    for rows in rows_by_split.values():
        for row in rows:
            label_counts[row["label"]] += 1
    print("Label counts:")
    for label, count in label_counts.items():
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
