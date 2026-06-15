from __future__ import annotations

from pathlib import Path

from app.classifier import (
    LABEL_BY_KEY,
    LABEL_KEYS,
    build_text_response,
    label_payload,
    split_sentences,
)


class TransformerClassifier:
    """BERT-style sentence classifier backed by Hugging Face Transformers.

    The model directory must contain a sequence-classification model fine-tuned
    for the six labels in app.classifier.LABEL_KEYS.
    """

    def __init__(self, model_path: str | Path, max_length: int = 256):
        self.model_path = str(model_path)
        self.max_length = max_length
        self.model_name = f"transformer:{self.model_path}"

        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "Transformer backend requires ML dependencies. Install them with "
                "`pip install -r requirements-ml.txt`."
            ) from exc

        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        self.model.eval()

        config = self.model.config
        self.id2label = self._normalize_id2label(getattr(config, "id2label", None))

    def classify_text(self, text: str) -> dict:
        text = text.strip()
        if not text:
            return {"ok": False, "error": "empty_text", "message": "Text is required."}

        sentences = split_sentences(text)
        if not sentences:
            return {"ok": False, "error": "no_sentences", "message": "No sentences found."}

        results = self.classify_sentences(sentences)
        return build_text_response(self.model_name, text, results)

    def classify_sentences(self, sentences: list[str]) -> list[dict]:
        encoded = self.tokenizer(
            sentences,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )

        with self.torch.no_grad():
            logits = self.model(**encoded).logits
            probabilities = self.torch.softmax(logits, dim=-1)

        results = []
        for index, sentence in enumerate(sentences):
            row = probabilities[index].tolist()
            scores = {self.id2label[i]: row[i] for i in range(len(row))}
            best_key = max(scores, key=scores.get)
            sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
            margin = sorted_scores[0][1] - sorted_scores[1][1] if len(sorted_scores) > 1 else sorted_scores[0][1]

            results.append(
                {
                    "index": index,
                    "text": sentence,
                    "label": label_payload(LABEL_BY_KEY[best_key]),
                    "confidence": round(sorted_scores[0][1], 4),
                    "margin": round(margin, 4),
                    "scores": {key: round(value, 4) for key, value in scores.items()},
                }
            )
        return results

    def _normalize_id2label(self, id2label: dict | None) -> dict[int, str]:
        if not id2label:
            return {index: label for index, label in enumerate(LABEL_KEYS)}

        normalized: dict[int, str] = {}
        for raw_index, raw_label in id2label.items():
            index = int(raw_index)
            label = str(raw_label)
            if label.startswith("LABEL_"):
                normalized[index] = LABEL_KEYS[index]
            else:
                normalized[index] = label

        unknown = set(normalized.values()) - set(LABEL_KEYS)
        if unknown:
            raise ValueError(f"Model labels do not match this app: {sorted(unknown)}")
        return normalized

