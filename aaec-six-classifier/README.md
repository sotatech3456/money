# AAEC Six-Class Essay Classifier MVP

English-only MVP for classifying essay sentences into six rhetorical roles inspired by AAEC-style argument analysis.

## Labels

| Label | Japanese | Meaning |
| --- | --- | --- |
| `cause_explanation` | 理由 | Cause / Explanation |
| `example_elaboration` | 具体例 | Example / Elaboration |
| `contrast_concession` | 反論 | Contrast / Concession |
| `background_circumstance` | 背景 | Background / Circumstance |
| `summary_conclusion` | 結論 | Summary / Conclusion |
| `evaluation_interpretation` | 解釈 | Evaluation / Interpretation |

## Run

```bash
cd /Users/sotanakano/class/programing/money/aaec-six-classifier
python3 server.py
```

Open:

```text
http://127.0.0.1:8008
```

## API

```bash
curl -sS http://127.0.0.1:8008/api/classify \
  -H 'content-type: application/json' \
  -d '{"text":"Although the policy is expensive, it can reduce pollution. For example, cities with better transit often have cleaner air. Therefore, governments should invest in public transport."}'
```

## Current Model

This MVP ships with a deterministic rule-based classifier so the service runs without installing ML dependencies or downloading model weights.

The model boundary is intentionally isolated in:

```text
app/classifier.py
```

Replace `RuleBasedClassifier` with a fine-tuned `roberta-base`, `microsoft/deberta-v3-base`, or `microsoft/deberta-v3-large` classifier when labeled training data is ready.

## ModernBERT Student + Seq2Seq Teacher

The project now supports a two-stage pipeline:

1. An optional encoder-decoder teacher step that distills pseudo-labels and rationales.
2. A ModernBERT encoder student that learns the final six-way classifier.

This is the closest practical version of a DeepSeek-style process for this task: teacher-generated supervision, then a smaller encoder optimized for classification.

Install ML dependencies:

```bash
pip install -r requirements-ml.txt
```

Automatically download/import multiple datasets, build a merged weak corpus, and fine-tune a ModernBERT student:

```bash
python3 -m modeling.run_aaec_pipeline \
  --base-model answerdotai/ModernBERT-base \
  --output-dir models/six-class-essay-classifier \
  --epochs 3 \
  --batch-size 8
```

Add the seq2seq teacher stage:

```bash
python3 -m modeling.run_aaec_pipeline \
  --base-model answerdotai/ModernBERT-base \
  --teacher-model google/flan-t5-base \
  --output-dir models/six-class-essay-classifier \
  --epochs 3 \
  --batch-size 8
```

For stronger local teacher quality, use a better instruction-tuned seq2seq model. The included `flan-t5-base` path is mainly a reproducible local baseline.

Fine-tune manually from existing JSONL files:

```bash
python3 -m modeling.train_transformer \
  --train-file data/processed/multisource-six-labels/train.jsonl \
  --validation-file data/processed/multisource-six-labels/validation.jsonl \
  --base-model answerdotai/ModernBERT-base \
  --output-dir models/six-class-essay-classifier
```

Run the API with the transformer model:

```bash
MODEL_BACKEND=modernbert MODEL_PATH=models/six-class-essay-classifier python3 server.py
```

## Training Material

The merged corpus builder currently supports:

- `AAEC / AAE2`
- `AbstRCT`
- `ArgMicro`
- `PERSUADE` as an optional large CSV import

Default merged outputs:

```text
data/processed/multisource-six-labels/train.jsonl
data/processed/multisource-six-labels/validation.jsonl
```

If you have PERSUADE locally:

```bash
python3 -m modeling.run_aaec_pipeline \
  --include-persuade \
  --persuade-train-csv /absolute/path/to/persuade_train.csv
```

Note: these datasets do not natively use your exact six labels. The pipeline creates weak/pseudo labels from the original argument annotations, then optionally distills them through a seq2seq teacher before training ModernBERT.

## Large Unlabeled Import

For large-scale continued pretraining or teacher-label generation, the repo can stream and save large unlabeled corpora.

Import roughly 100 million tokens from FineWeb-Edu:

```bash
.venv/bin/python -m modeling.import_large_unlabeled_corpus \
  --dataset HuggingFaceFW/fineweb-edu \
  --subset sample-10BT \
  --output-file data/processed/unlabeled/fineweb_100m_tokens.jsonl \
  --target-tokens 100000000
```

Check token inventory:

```bash
.venv/bin/python -m modeling.token_inventory \
  data/processed/multisource-six-labels/train.jsonl \
  data/processed/multisource-six-labels/validation.jsonl \
  data/processed/unlabeled/fineweb_100m_tokens.jsonl
```

Run the hand-labeled long-form benchmark:

```bash
.venv/bin/python -m modeling.evaluate_benchmark \
  --model-path models/six-class-essay-classifier \
  --input-file modeling/long_form_benchmark.jsonl
```

Rebuild the balanced benchmark and dump model errors for review:

```bash
.venv/bin/python -m modeling.build_curated_benchmark
.venv/bin/python -m modeling.dump_predictions \
  --model-path models/six-class-essay-classifier \
  --input-file modeling/long_form_benchmark.jsonl \
  --output-file reports/long_form_prediction_errors.csv
```

The benchmark is intentionally balanced across the six labels. Do not use it as
training data; use it to identify systematic failures, then add separate
training examples for the labels the model misses.

## Production Path

1. Import AAEC, AbstRCT, ArgMicro, and PERSUADE.
2. Distill better labels with a stronger teacher model than `flan-t5-base`.
3. Fine-tune `answerdotai/ModernBERT-base` or `answerdotai/ModernBERT-large`.
4. Add a hand-labeled gold set for `contrast_concession` and `evaluation_interpretation`.
5. Keep the current `/api/classify` response shape and swap models safely.
