from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from app.classifier import LABEL_KEYS
from modeling.common import oversample_minimum, print_label_counts, write_jsonl
from modeling.prepare_aaec_six_labels import convert_document as convert_aaec_document
from modeling.prepare_aaec_six_labels import read_split as read_aaec_split


ABSTRCT_URL = "https://gitlab.com/tomaye/abstrct/-/archive/master/abstrct-master.zip"
ARGMICRO_URL = "https://github.com/peldszus/arg-microtexts/archive/refs/heads/master.zip"
PERSUADE_TRAIN_URL = "https://drive.google.com/uc?export=download&id=13phHyDzIsb0MHyJr6q-B-qIa9P2tM135"
PERSUADE_TRAIN_FILE_ID = "13phHyDzIsb0MHyJr6q-B-qIa9P2tM135"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a larger weakly labeled six-class corpus from multiple argument-mining datasets."
    )
    parser.add_argument("--output-dir", default="data/processed/multisource-six-labels")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--min-train-per-label", type=int, default=500)
    parser.add_argument("--include-aaec", action="store_true", default=True)
    parser.add_argument("--include-abstrct", action="store_true", default=True)
    parser.add_argument("--include-argmicro", action="store_true", default=True)
    parser.add_argument("--include-persuade", action="store_true")
    parser.add_argument("--persuade-train-csv", default="")
    parser.add_argument("--download-persuade", action="store_true")
    return parser.parse_args()


def ensure_download(url: str, zip_path: Path) -> None:
    if zip_path.exists():
        return
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url}")
    with urllib.request.urlopen(url) as response, zip_path.open("wb") as file:
        shutil.copyfileobj(response, file)


def ensure_gdrive_download(file_id: str, target_path: Path) -> None:
    if target_path.exists():
        return
    target_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            ".venv/bin/python",
            "-m",
            "gdown",
            "--id",
            file_id,
            "--output",
            str(target_path),
            "--fuzzy",
        ],
        check=True,
    )


def ensure_extracted(zip_path: Path, output_dir: Path, expected_dir: Path) -> None:
    if expected_dir.exists():
        return
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(output_dir)


def build_aaec_rows(raw_dir: Path) -> dict[str, list[dict]]:
    corpus_dir = raw_dir / "ArgumentAnnotatedEssays-2.0"
    brat_dir = corpus_dir / "brat-project-final"
    split_by_id = read_aaec_split(corpus_dir)
    rows_by_split = {"train": [], "validation": []}
    for ann_path in sorted(brat_dir.glob("essay*.ann")):
        split = split_by_id.get(ann_path.stem, "train")
        rows_by_split[split].extend(convert_aaec_document(ann_path, split, False))
    for split in rows_by_split:
        for row in rows_by_split[split]:
            row["dataset"] = "aaec"
    return rows_by_split


def parse_brat_components(ann_path: Path) -> list[tuple[str, int, int, str]]:
    components = []
    for line in ann_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("T"):
            continue
        ann_id, meta, text = line.split("\t", 2)
        parts = meta.split()
        label = parts[0]
        start = int(parts[1])
        end = int(parts[-1])
        components.append((label, start, end, " ".join(text.split())))
    return sorted(components, key=lambda item: (item[1], item[2]))


def weak_label_from_text(text: str, base_label: str) -> str:
    lower = text.lower().strip()
    first = " ".join(lower.split()[:6])
    if first.startswith(("for example", "for instance", "such as", "to illustrate")):
        return "example_elaboration"
    if first.startswith(("however", "although", "on the other hand", "despite")):
        return "contrast_concession"
    if first.startswith(("in conclusion", "overall", "to conclude", "to sum up")):
        return "summary_conclusion"
    if first.startswith(("in recent years", "historically", "currently", "today", "during")):
        return "background_circumstance"
    return base_label


def build_abstrct_rows(raw_dir: Path) -> dict[str, list[dict]]:
    zip_path = raw_dir / "abstrct-master.zip"
    corpus_root = raw_dir / "abstrct-master"
    ensure_download(ABSTRCT_URL, zip_path)
    ensure_extracted(zip_path, raw_dir, corpus_root)

    split_dirs = {
        "train": [
            corpus_root / "AbstRCT_corpus/data/train/neoplasm_train",
        ],
        "validation": [
            corpus_root / "AbstRCT_corpus/data/dev/neoplasm_dev",
            corpus_root / "AbstRCT_corpus/data/test/neoplasm_test",
            corpus_root / "AbstRCT_corpus/data/test/glaucoma_test",
            corpus_root / "AbstRCT_corpus/data/test/mixed_test",
        ],
    }
    rows_by_split = {"train": [], "validation": []}
    for split, directories in split_dirs.items():
        for directory in directories:
            for ann_path in sorted(directory.glob("*.ann")):
                for component_label, start, end, text in parse_brat_components(ann_path):
                    base_label = "evaluation_interpretation" if component_label.lower() == "claim" else "cause_explanation"
                    label = weak_label_from_text(text, base_label)
                    rows_by_split[split].append(
                        {
                            "text": text,
                            "label": label,
                            "source": "abstrct_weak",
                            "dataset": "abstrct",
                            "aaec_component": component_label,
                            "essay_id": ann_path.stem,
                            "split": split,
                            "span": [start, end],
                        }
                    )
    return rows_by_split


def build_argmicro_rows(raw_dir: Path) -> dict[str, list[dict]]:
    zip_path = raw_dir / "arg-microtexts-master.zip"
    corpus_root = raw_dir / "arg-microtexts-master"
    ensure_download(ARGMICRO_URL, zip_path)
    ensure_extracted(zip_path, raw_dir, corpus_root)

    rows_by_split = {"train": [], "validation": []}
    en_dir = corpus_root / "corpus/en"
    text_files = sorted(en_dir.glob("*.txt"))
    cutoff = max(1, int(len(text_files) * 0.8))
    for index, txt_path in enumerate(text_files):
        split = "train" if index < cutoff else "validation"
        text = txt_path.read_text(encoding="utf-8")
        root = ElementTree.parse(txt_path.with_suffix(".xml")).getroot()
        adu_type = {adu.attrib["id"]: adu.attrib.get("type", "pro") for adu in root.findall("adu")}
        edges_by_src: dict[str, list[str]] = {}
        for edge in root.findall("edge"):
            edges_by_src.setdefault(edge.attrib["src"], []).append(edge.attrib["type"])

        start_pos = 0
        for edu in root.findall("edu"):
            edu_text = (edu.text or "").strip()
            if not edu_text:
                continue
            start = text.find(edu_text, start_pos)
            end = start + len(edu_text) if start >= 0 else start_pos + len(edu_text)
            start_pos = max(end, start_pos)

            linked_adu = edu.attrib.get("id", "").replace("e", "a", 1)
            adu_label = adu_type.get(linked_adu, "pro")
            outgoing = edges_by_src.get(linked_adu, [])
            if "reb" in outgoing or adu_label == "opp":
                label = "contrast_concession"
            elif "exa" in outgoing or edu_text.lower().startswith(("for example", "for instance")):
                label = "example_elaboration"
            elif edu_text.lower().startswith(("in conclusion", "overall", "therefore")):
                label = "summary_conclusion"
            else:
                label = weak_label_from_text(edu_text, "cause_explanation" if adu_label == "pro" else "contrast_concession")

            rows_by_split[split].append(
                {
                    "text": " ".join(edu_text.split()),
                    "label": label,
                    "source": "argmicro_weak",
                    "dataset": "argmicro",
                    "aaec_component": adu_label,
                    "essay_id": txt_path.stem,
                    "split": split,
                    "span": [start, end],
                }
            )
    return rows_by_split


def read_persuade_csv(csv_path: Path) -> dict[str, list[dict]]:
    mapping = {
        "Lead": "background_circumstance",
        "Position": "evaluation_interpretation",
        "Claim": "evaluation_interpretation",
        "Counterclaim": "contrast_concession",
        "Rebuttal": "contrast_concession",
        "Evidence": "example_elaboration",
        "Concluding Summary": "summary_conclusion",
    }
    rows_by_split = {"train": [], "validation": []}
    with csv_path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            discourse_type = row.get("discourse_type", "").strip()
            if discourse_type not in mapping:
                continue
            split = "validation" if row.get("competition_set", "").lower() == "test" else "train"
            rows_by_split[split].append(
                {
                    "text": " ".join(row.get("discourse_text", "").split()),
                    "label": mapping[discourse_type],
                    "source": "persuade_human",
                    "dataset": "persuade",
                    "aaec_component": discourse_type,
                    "essay_id": row.get("essay_id_comp", ""),
                    "split": split,
                    "span": [
                        int(row.get("discourse_start", "0") or 0),
                        int(row.get("discourse_end", "0") or 0),
                    ],
                }
            )
    return rows_by_split


def maybe_download_persuade(raw_dir: Path) -> Path | None:
    csv_path = raw_dir / "persuade_train.csv"
    try:
        ensure_gdrive_download(PERSUADE_TRAIN_FILE_ID, csv_path)
        return csv_path
    except Exception as exc:
        print(f"Skipping automatic PERSUADE download: {exc}")
        return None


def merge_rows(*datasets: dict[str, list[dict]]) -> dict[str, list[dict]]:
    merged = {"train": [], "validation": []}
    for dataset in datasets:
        for split in merged:
            merged[split].extend(dataset.get(split, []))
    return merged


def main() -> None:
    args = parse_args()
    raw_dir = Path(args.raw_dir)
    output_dir = Path(args.output_dir)

    sources = []
    if args.include_aaec:
        sources.append(build_aaec_rows(raw_dir))
    if args.include_abstrct:
        sources.append(build_abstrct_rows(raw_dir))
    if args.include_argmicro:
        sources.append(build_argmicro_rows(raw_dir))
    if args.include_persuade:
        csv_path = Path(args.persuade_train_csv) if args.persuade_train_csv else None
        if csv_path and csv_path.exists():
            sources.append(read_persuade_csv(csv_path))
        elif args.download_persuade:
            downloaded = maybe_download_persuade(raw_dir)
            if downloaded and downloaded.exists():
                sources.append(read_persuade_csv(downloaded))
        else:
            print("Skipping PERSUADE: provide --persuade-train-csv or add --download-persuade.")

    rows_by_split = merge_rows(*sources)
    if args.min_train_per_label:
        rows_by_split["train"] = oversample_minimum(rows_by_split["train"], args.min_train_per_label)

    for split, rows in rows_by_split.items():
        path = output_dir / f"{split}.jsonl"
        write_jsonl(path, rows)
        print(f"Wrote {len(rows)} rows to {path}")
        print_label_counts(rows, f"{split} label counts:")


if __name__ == "__main__":
    main()
