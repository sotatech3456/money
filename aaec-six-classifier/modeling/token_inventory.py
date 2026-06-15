from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


WORD_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate token inventory for JSONL corpora.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--field", default="text")
    return parser.parse_args()


def estimate_tokens(text: str) -> int:
    return len(WORD_RE.findall(text))


def main() -> None:
    args = parse_args()
    total_tokens = 0
    total_rows = 0
    for raw_path in args.paths:
        path = Path(raw_path)
        rows = 0
        chars = 0
        tokens = 0
        label_counts = Counter()
        with path.open(encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                row = json.loads(line)
                text = str(row.get(args.field, ""))
                rows += 1
                chars += len(text)
                tokens += estimate_tokens(text)
                if "label" in row:
                    label_counts[str(row["label"])] += 1
        total_rows += rows
        total_tokens += tokens
        print(f"path={path}")
        print(f"  rows={rows}")
        print(f"  chars={chars}")
        print(f"  rough_tokens={tokens}")
        if label_counts:
            print("  labels=" + json.dumps(dict(label_counts), ensure_ascii=False))
    print(f"TOTAL rows={total_rows} rough_tokens={total_tokens}")


if __name__ == "__main__":
    main()

