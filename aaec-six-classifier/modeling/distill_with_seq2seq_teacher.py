from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from app.classifier import LABEL_KEYS
from modeling.common import read_jsonl, write_jsonl


JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


PROMPT_TEMPLATE = """You are labeling one English sentence for rhetorical role classification.
Choose exactly one label from this closed set:
- cause_explanation
- example_elaboration
- contrast_concession
- background_circumstance
- summary_conclusion
- evaluation_interpretation

Return valid JSON with keys:
- label
- rationale

Sentence:
{sentence}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Use a seq2seq teacher model to distill pseudo-labels and rationales for six-class argument mining."
    )
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--teacher-model", default="google/flan-t5-base")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--overwrite-labels", action="store_true")
    return parser.parse_args()


def extract_json(text: str) -> dict | None:
    match = JSON_RE.search(text)
    if not match:
        return None


def normalize_label(text: str) -> str:
    normalized = text.strip().lower().replace("-", "_").replace("/", "_").replace(" ", "_")
    aliases = {
        "cause": "cause_explanation",
        "explanation": "cause_explanation",
        "cause_explanation": "cause_explanation",
        "example": "example_elaboration",
        "elaboration": "example_elaboration",
        "example_elaboration": "example_elaboration",
        "contrast": "contrast_concession",
        "concession": "contrast_concession",
        "contrast_concession": "contrast_concession",
        "background": "background_circumstance",
        "circumstance": "background_circumstance",
        "background_circumstance": "background_circumstance",
        "summary": "summary_conclusion",
        "conclusion": "summary_conclusion",
        "summary_conclusion": "summary_conclusion",
        "evaluation": "evaluation_interpretation",
        "interpretation": "evaluation_interpretation",
        "description_interpretation": "evaluation_interpretation",
        "evaluation_interpretation": "evaluation_interpretation",
    }
    return aliases.get(normalized, "")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def main() -> None:
    args = parse_args()
    try:
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError("Install ML dependencies before distillation.") from exc

    rows = read_jsonl(args.input_file)
    if args.limit > 0:
        rows = rows[: args.limit]

    tokenizer = AutoTokenizer.from_pretrained(args.teacher_model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.teacher_model)
    model.eval()

    distilled_rows = []
    for index, row in enumerate(rows, start=1):
        prompt = PROMPT_TEMPLATE.format(sentence=row["text"])
        encoded = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            generated = model.generate(
                **encoded,
                max_new_tokens=96,
                do_sample=False,
            )
        decoded = tokenizer.decode(generated[0], skip_special_tokens=True)
        payload = extract_json(decoded) or {}
        teacher_label = normalize_label(str(payload.get("label", ""))) or normalize_label(decoded)
        if teacher_label not in LABEL_KEYS:
            teacher_label = row["label"]
        result = dict(row)
        result["teacher_model"] = args.teacher_model
        result["teacher_label"] = teacher_label
        result["teacher_rationale"] = str(payload.get("rationale", "")).strip()
        result["distillation_raw_output"] = decoded
        if args.overwrite_labels:
            result["label"] = teacher_label
        distilled_rows.append(result)
        if index % 100 == 0:
            print(f"Distilled {index} rows")

    write_jsonl(Path(args.output_file), distilled_rows)
    print(f"Wrote distilled rows to {args.output_file}")


if __name__ == "__main__":
    main()
