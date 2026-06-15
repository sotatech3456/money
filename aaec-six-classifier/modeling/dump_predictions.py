from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.classifier import LABEL_KEYS
from modeling.common import read_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dump model predictions for benchmark error review.")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--input-file", default="modeling/long_form_benchmark.jsonl")
    parser.add_argument("--output-file", default="reports/prediction_errors.csv")
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--include-correct", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.input_file)

    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    model = AutoModelForSequenceClassification.from_pretrained(args.model_path)
    model.eval()

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "article",
        "gold_label",
        "predicted_label",
        "confidence",
        "correct",
        "text",
    ]

    written = 0
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        with torch.no_grad():
            for row in rows:
                encoded = tokenizer(
                    row["text"],
                    padding=True,
                    truncation=True,
                    max_length=args.max_length,
                    return_tensors="pt",
                )
                probabilities = torch.softmax(model(**encoded).logits, dim=-1).cpu().numpy()[0]
                predicted_index = int(np.argmax(probabilities))
                predicted_label = LABEL_KEYS[predicted_index]
                correct = predicted_label == row["label"]

                if correct and not args.include_correct:
                    continue

                writer.writerow(
                    {
                        "article": row.get("article", ""),
                        "gold_label": row["label"],
                        "predicted_label": predicted_label,
                        "confidence": f"{probabilities[predicted_index]:.4f}",
                        "correct": str(correct).lower(),
                        "text": row["text"],
                    }
                )
                written += 1

    print(f"wrote {written} rows to {output_path}")


if __name__ == "__main__":
    main()
