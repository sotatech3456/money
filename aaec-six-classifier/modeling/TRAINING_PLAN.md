# Training Plan

This project is now model-ready and supports multi-source weak supervision plus optional seq2seq distillation.

## Dataset Strategy

AAEC labels are not identical to the requested six rhetorical labels. Use AAEC as a source of argumentative essay sentences, then create a new six-label annotation layer.

Recommended minimum:

- 300 examples per label for first fine-tuning.
- 1000+ examples per label for stronger public-facing quality.
- A held-out test set with prompts/topics not used in training.

## Suggested Student Encoder

Start with:

```text
answerdotai/ModernBERT-base
```

Upgrade when quality matters more than cost:

```text
answerdotai/ModernBERT-large
```

## Suggested Teacher

Local baseline:

```text
google/flan-t5-base
```

Stronger teacher outputs usually require a stronger instruction model or API-backed generator.

## Label File Format

```jsonl
{"text":"Because public transport reduces congestion, it helps cities.","label":"cause_explanation"}
{"text":"For example, trains can move thousands of people per hour.","label":"example_elaboration"}
```

## Training Command

```bash
pip install -r requirements-ml.txt
python3 -m modeling.run_aaec_pipeline \
  --base-model answerdotai/ModernBERT-base \
  --teacher-model google/flan-t5-base \
  --output-dir models/six-class-essay-classifier \
  --epochs 3 \
  --batch-size 8
```

Manual student training after data already exists:

```bash
python3 -m modeling.train_transformer \
  --train-file data/processed/multisource-six-labels/train.jsonl \
  --validation-file data/processed/multisource-six-labels/validation.jsonl \
  --base-model answerdotai/ModernBERT-base \
  --output-dir models/six-class-essay-classifier
```

Run the app with the trained model:

```bash
MODEL_BACKEND=modernbert MODEL_PATH=models/six-class-essay-classifier python3 server.py
```

## Evaluation Targets

- Macro F1: important because label balance matters.
- Per-label recall: important for rare contrast/concession sentences.
- Confusion matrix: watch `cause_explanation` vs `evaluation_interpretation`, and `summary_conclusion` vs `cause_explanation`.
