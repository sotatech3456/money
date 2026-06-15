from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from datasets import load_dataset


WORD_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stream a large unlabeled corpus and save roughly a target number of tokens as JSONL."
    )
    parser.add_argument("--dataset", default="HuggingFaceFW/fineweb-edu")
    parser.add_argument("--subset", default="sample-10BT")
    parser.add_argument("--split", default="train")
    parser.add_argument("--output-file", default="data/processed/unlabeled/fineweb_100m_tokens.jsonl")
    parser.add_argument("--target-tokens", type=int, default=100_000_000)
    parser.add_argument("--min-chars", type=int, default=300)
    parser.add_argument("--max-docs", type=int, default=0)
    parser.add_argument("--field", default="text")
    return parser.parse_args()


def rough_token_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def main() -> None:
    args = parse_args()
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset(
        args.dataset,
        None if args.subset in {"", "none", "null"} else args.subset,
        split=args.split,
        streaming=True,
    )

    saved_docs = 0
    saved_tokens = 0
    seen_docs = 0

    with output_path.open("w", encoding="utf-8") as file:
        for row in dataset:
            seen_docs += 1
            text = str(row.get(args.field, "")).strip()
            if len(text) < args.min_chars:
                continue
            tokens = rough_token_count(text)
            if tokens == 0:
                continue

            payload = {
                "text": text,
                "source_dataset": args.dataset,
                "source_subset": args.subset,
                "rough_tokens": tokens,
            }
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")
            saved_docs += 1
            saved_tokens += tokens

            if saved_docs % 1000 == 0:
                progress = saved_tokens / max(1, args.target_tokens)
                print(
                    f"saved_docs={saved_docs} seen_docs={seen_docs} "
                    f"saved_tokens={saved_tokens} progress={progress:.4%}"
                )

            if saved_tokens >= args.target_tokens:
                break
            if args.max_docs > 0 and saved_docs >= args.max_docs:
                break

    print(
        f"Completed import: saved_docs={saved_docs} saved_tokens={saved_tokens} "
        f"target_tokens={args.target_tokens} output={output_path}"
    )


if __name__ == "__main__":
    main()

