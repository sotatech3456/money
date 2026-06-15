# Multi-Source Training Pipeline

This folder builds a larger weakly supervised corpus for the six-label classifier and supports a teacher-student pipeline:

- Seq2seq teacher: optional label distillation
- ModernBERT student: final classifier

## One Command

```bash
python3 -m modeling.run_aaec_pipeline \
  --base-model answerdotai/ModernBERT-base \
  --output-dir models/six-class-essay-classifier \
  --epochs 3 \
  --batch-size 8
```

With teacher distillation:

```bash
python3 -m modeling.run_aaec_pipeline \
  --base-model answerdotai/ModernBERT-base \
  --teacher-model google/flan-t5-base \
  --output-dir models/six-class-essay-classifier \
  --epochs 3 \
  --batch-size 8
```

## What It Does

1. Downloads AAEC v2 from TU Darmstadt.
2. Downloads and parses additional public argument-mining datasets.
3. Converts source labels into weak six-label examples.
4. Writes:

```text
data/processed/multisource-six-labels/train.jsonl
data/processed/multisource-six-labels/validation.jsonl
```

5. Optionally distills labels with a seq2seq teacher.
6. Fine-tunes a Hugging Face sequence-classification model.

## Supported Sources

- AAEC / AAE2
- AbstRCT
- ArgMicro
- PERSUADE, if provided as a local CSV or direct Google Drive download is available

## Large Unlabeled Corpus

Use `modeling.import_large_unlabeled_corpus` to stream large general English corpora into JSONL.

Example:

```bash
.venv/bin/python -m modeling.import_large_unlabeled_corpus \
  --dataset HuggingFaceFW/fineweb-edu \
  --subset sample-10BT \
  --output-file data/processed/unlabeled/fineweb_100m_tokens.jsonl \
  --target-tokens 100000000
```

Track total token volume:

```bash
.venv/bin/python -m modeling.token_inventory \
  data/processed/multisource-six-labels/train.jsonl \
  data/processed/unlabeled/fineweb_100m_tokens.jsonl
```

Evaluate on the included long-form benchmark:

```bash
.venv/bin/python -m modeling.evaluate_benchmark \
  --model-path models/six-class-essay-classifier
```

## Why This Is DeepSeek-Inspired, Not DeepSeek Architecture

DeepSeek’s public reasoning pipeline relies heavily on teacher-generated supervision and distillation into smaller deployable models. This repo now follows that pattern conceptually:

- teacher model generates labels and rationales
- student encoder learns the final classification task

It is not implementing DeepSeek-V3 or DeepSeek-R1 architecture directly.

## Why It Is Weak Supervision

AAEC does not directly contain these six labels:

- `cause_explanation`
- `example_elaboration`
- `contrast_concession`
- `background_circumstance`
- `summary_conclusion`
- `evaluation_interpretation`

AAEC contains argument-mining labels such as `MajorClaim`, `Claim`, `Premise`, plus `supports` and `attacks` relations. The conversion script creates practical pseudo-labels from those annotations. This is enough to bootstrap a BERT-style classifier, but real public quality still needs manual correction and additional examples, especially for `example_elaboration`.

## Run The App With The Trained Model

```bash
MODEL_BACKEND=transformer MODEL_PATH=models/six-class-essay-classifier python3 server.py
```
