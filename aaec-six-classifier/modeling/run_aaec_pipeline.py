from __future__ import annotations

import argparse
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a multi-source weak corpus, optionally distill with a seq2seq teacher, and fine-tune an encoder.")
    parser.add_argument("--base-model", default="answerdotai/ModernBERT-base")
    parser.add_argument("--output-dir", default="models/six-class-essay-classifier")
    parser.add_argument("--epochs", default="3")
    parser.add_argument("--batch-size", default="8")
    parser.add_argument("--min-train-per-label", default="500")
    parser.add_argument("--teacher-model", default="")
    parser.add_argument("--teacher-limit", default="0")
    parser.add_argument("--include-persuade", action="store_true")
    parser.add_argument("--persuade-train-csv", default="")
    parser.add_argument("--download-persuade", action="store_true")
    parser.add_argument("--include-non-argument-background", action="store_true")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-distill", action="store_true")
    parser.add_argument("--skip-train", action="store_true")
    return parser.parse_args()


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    args = parse_args()

    if not args.skip_download:
        run([sys.executable, "-m", "modeling.download_aaec"])

    prepare_command = [
        sys.executable,
        "-m",
        "modeling.build_multisource_corpus",
        "--min-train-per-label",
        args.min_train_per_label,
    ]
    if args.include_persuade:
        prepare_command.append("--include-persuade")
    if args.persuade_train_csv:
        prepare_command.extend(["--persuade-train-csv", args.persuade_train_csv])
    if args.download_persuade:
        prepare_command.append("--download-persuade")
    run(prepare_command)

    train_file = "data/processed/multisource-six-labels/train.jsonl"
    validation_file = "data/processed/multisource-six-labels/validation.jsonl"

    if args.teacher_model and not args.skip_distill:
        distilled_train = "data/processed/multisource-six-labels/train.distilled.jsonl"
        run(
            [
                sys.executable,
                "-m",
                "modeling.distill_with_seq2seq_teacher",
                "--input-file",
                train_file,
                "--output-file",
                distilled_train,
                "--teacher-model",
                args.teacher_model,
                "--limit",
                args.teacher_limit,
                "--overwrite-labels",
            ]
        )
        train_file = distilled_train

    if not args.skip_train:
        run(
            [
                sys.executable,
                "-m",
                "modeling.train_transformer",
                "--train-file",
                train_file,
                "--validation-file",
                validation_file,
                "--base-model",
                args.base_model,
                "--output-dir",
                args.output_dir,
                "--epochs",
                args.epochs,
                "--batch-size",
                args.batch_size,
            ]
        )


if __name__ == "__main__":
    main()
