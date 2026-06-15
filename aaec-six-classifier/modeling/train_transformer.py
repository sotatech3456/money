from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from datasets import load_dataset
from sklearn.metrics import accuracy_score, f1_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

from app.classifier import LABEL_KEYS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fine-tune a BERT-style six-class essay classifier.")
    parser.add_argument("--train-file", required=True, help="JSONL with fields: text, label")
    parser.add_argument("--validation-file", required=True, help="JSONL with fields: text, label")
    parser.add_argument("--base-model", default="answerdotai/ModernBERT-base")
    parser.add_argument("--output-dir", default="models/six-class-essay-classifier")
    parser.add_argument("--epochs", type=float, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--max-length", type=int, default=256)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    label2id = {label: index for index, label in enumerate(LABEL_KEYS)}
    id2label = {index: label for label, index in label2id.items()}

    dataset = load_dataset(
        "json",
        data_files={"train": args.train_file, "validation": args.validation_file},
    )

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=args.max_length)

    def encode_label(example):
        if example["label"] not in label2id:
            raise ValueError(f"Unknown label: {example['label']}")
        example["labels"] = label2id[example["label"]]
        return example

    tokenized = dataset.map(encode_label).map(tokenize, batched=True)
    removable_columns = [
        column
        for column in tokenized["train"].column_names
        if column not in {"input_ids", "attention_mask", "labels"}
    ]
    tokenized = tokenized.remove_columns(removable_columns)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        num_labels=len(LABEL_KEYS),
        id2label=id2label,
        label2id=label2id,
    )

    def compute_metrics(eval_prediction):
        logits, labels = eval_prediction
        predictions = np.argmax(logits, axis=-1)
        return {
            "accuracy": accuracy_score(labels, predictions),
            "macro_f1": f1_score(labels, predictions, average="macro"),
        }

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics,
    )
    trainer.train()

    output_dir = Path(args.output_dir)
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Saved classifier to {output_dir}")


if __name__ == "__main__":
    main()
