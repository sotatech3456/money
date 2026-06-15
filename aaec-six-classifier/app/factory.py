from __future__ import annotations

import os

from app.classifier import RuleBasedClassifier
from app.transformer_classifier import TransformerClassifier


def create_classifier():
    backend = os.getenv("MODEL_BACKEND", "rule").strip().lower()
    if backend in {"rule", "rules", "rule_based"}:
        return RuleBasedClassifier()
    if backend in {"bert", "transformer", "deberta", "roberta", "modernbert"}:
        model_path = os.getenv("MODEL_PATH", "models/six-class-essay-classifier")
        return TransformerClassifier(model_path)
    raise ValueError(f"Unknown MODEL_BACKEND: {backend}")
