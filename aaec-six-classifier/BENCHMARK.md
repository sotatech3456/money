# Benchmark Report

Date: 2026-06-15

## Current Run: Hand-Labeled Long-Form Benchmark

Command:

```bash
.venv/bin/python -m modeling.evaluate_benchmark \
  --model-path models/six-class-essay-classifier \
  --input-file modeling/long_form_benchmark.jsonl
```

Dataset:

- `modeling/long_form_benchmark.jsonl`
- 18 benchmark rows
- 3 examples per label

Results:

| Metric | Score |
| --- | ---: |
| Accuracy | 0.5000 |
| Macro F1 | 0.4500 |

Per-label F1:

| Label | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| `cause_explanation` | 0.2500 | 1.0000 | 0.4000 |
| `example_elaboration` | 1.0000 | 1.0000 | 1.0000 |
| `contrast_concession` | 0.0000 | 0.0000 | 0.0000 |
| `background_circumstance` | 0.0000 | 0.0000 | 0.0000 |
| `summary_conclusion` | 1.0000 | 0.6667 | 0.8000 |
| `evaluation_interpretation` | 1.0000 | 0.3333 | 0.5000 |

Unit tests:

```bash
python3 -m unittest
```

Result: 3 tests passed.

## Readout

The current model is usable as a prototype, but it is not ready as a reliable public classifier.

The strongest class is `example_elaboration`. `summary_conclusion` is also promising. The main failure is that `contrast_concession` and `background_circumstance` are not being recovered at all on the hand-labeled benchmark. The model also overpredicts `cause_explanation`, which explains the high recall but low precision for that label.

## Next Step

Do not train a larger model first. The highest-impact next move is to improve the gold benchmark and add targeted examples for the weak labels.

Recommended next actions:

1. Expand `modeling/long_form_benchmark.jsonl` from 18 rows to at least 120 rows.
2. Add at least 25 hand-checked examples each for:
   - `contrast_concession`
   - `background_circumstance`
   - `evaluation_interpretation`
3. Add a prediction dump script that writes text, gold label, predicted label, and confidence to a CSV for fast error review.
4. Retrain only after the benchmark exposes stable failure patterns.
5. Use the benchmark as the gate before replacing the model in the web app.

Target before public demo:

- Macro F1: 0.75 or higher on a hand-labeled benchmark
- No label below 0.60 F1
- At least 30 benchmark examples per label

## Current Run: Multi-Source Validation Set

Command:

```bash
.venv/bin/python -m modeling.evaluate_benchmark \
  --model-path models/six-class-essay-classifier \
  --input-file data/processed/multisource-six-labels/validation.jsonl
```

Dataset:

- `data/processed/multisource-six-labels/validation.jsonl`
- 3,596 validation rows
- Weak/pseudo labels from the multi-source corpus

Results:

| Metric | Score |
| --- | ---: |
| Accuracy | 0.6577 |
| Macro F1 | 0.4862 |
| Weighted F1 | 0.5579 |

Per-label F1:

| Label | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| `cause_explanation` | 2,289 | 0.6709 | 0.9681 | 0.7926 |
| `example_elaboration` | 4 | 0.5714 | 1.0000 | 0.7273 |
| `contrast_concession` | 170 | 0.0000 | 0.0000 | 0.0000 |
| `background_circumstance` | 48 | 0.9200 | 0.9583 | 0.9388 |
| `summary_conclusion` | 173 | 0.4576 | 0.3121 | 0.3711 |
| `evaluation_interpretation` | 912 | 0.3814 | 0.0493 | 0.0874 |

Readout:

The validation accuracy is 65.77%, but this is inflated by label imbalance. `cause_explanation` is 63.7% of the validation set, and the model heavily favors that class. Macro F1 is the better headline metric right now: 48.62%.

The next improvement target is not "run it a million times." Repeated deterministic evaluation will return the same accuracy. The useful version of that request is to expand the benchmark, inspect wrong predictions, and retrain against the labels the model currently misses.
