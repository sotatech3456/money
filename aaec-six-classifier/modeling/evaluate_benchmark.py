from __future__ import annotations

import argparse
from collections import Counter

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

from app.classifier import LABEL_KEYS
from modeling.common import read_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a sequence classifier on a JSONL benchmark.")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--input-file", default="modeling/long_form_benchmark.jsonl")
    parser.add_argument("--max-length", type=int, default=256)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.input_file)
    texts = [row["text"] for row in rows]
    y_true = [LABEL_KEYS.index(row["label"]) for row in rows]

    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    model = AutoModelForSequenceClassification.from_pretrained(args.model_path)
    model.eval()

    preds = []
    batch_size = 32
    with torch.no_grad():
        for index in range(0, len(texts), batch_size):
            batch = texts[index : index + batch_size]
            encoded = tokenizer(batch, padding=True, truncation=True, max_length=args.max_length, return_tensors="pt")
            logits = model(**encoded).logits
            preds.extend(np.argmax(torch.softmax(logits, dim=-1).cpu().numpy(), axis=-1).tolist())

    accuracy = accuracy_score(y_true, preds)
    macro_f1 = f1_score(y_true, preds, average="macro")
    print(f"rows={len(rows)}")
    print(f"accuracy={accuracy:.4f}")
    print(f"macro_f1={macro_f1:.4f}")
    print("label_counts=" + str(dict(Counter(row["label"] for row in rows))))
    print(classification_report(y_true, preds, target_names=LABEL_KEYS, zero_division=0, digits=4))


if __name__ == "__main__":
    main()

