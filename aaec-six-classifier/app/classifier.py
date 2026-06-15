from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Label:
    key: str
    display: str
    japanese: str
    description: str
    keywords: tuple[str, ...]
    base_score: float = 0.03


LABELS: tuple[Label, ...] = (
    Label(
        key="cause_explanation",
        display="Cause / Explanation",
        japanese="理由",
        description="Reasons, causes, evidence, or why a claim is true.",
        keywords=(
            "because",
            "since",
            "as a result of",
            "due to",
            "therefore",
            "thus",
            "so",
            "reason",
            "caused by",
            "leads to",
            "explains",
            "evidence",
            "proof",
        ),
    ),
    Label(
        key="example_elaboration",
        display="Example / Elaboration",
        japanese="具体例",
        description="Examples, details, elaboration, or concrete illustration.",
        keywords=(
            "for example",
            "for instance",
            "such as",
            "including",
            "in particular",
            "specifically",
            "to illustrate",
            "one example",
            "another example",
            "details",
        ),
    ),
    Label(
        key="contrast_concession",
        display="Contrast / Concession",
        japanese="反論",
        description="Counterargument, concession, contrast, or limitation.",
        keywords=(
            "although",
            "though",
            "however",
            "but",
            "yet",
            "nevertheless",
            "on the other hand",
            "in contrast",
            "despite",
            "whereas",
            "while",
            "some people argue",
            "critics argue",
            "opponents",
        ),
    ),
    Label(
        key="background_circumstance",
        display="Background / Circumstance",
        japanese="背景",
        description="Context, situation, condition, or factual setup.",
        keywords=(
            "today",
            "currently",
            "in recent years",
            "historically",
            "before",
            "when",
            "in many countries",
            "society",
            "background",
            "context",
            "circumstances",
            "during",
        ),
    ),
    Label(
        key="summary_conclusion",
        display="Summary / Conclusion",
        japanese="結論",
        description="Conclusion, summary, final recommendation, or closing claim.",
        keywords=(
            "in conclusion",
            "to conclude",
            "overall",
            "in summary",
            "to sum up",
            "ultimately",
            "therefore",
            "for these reasons",
            "we should",
            "must",
            "should",
            "it is clear that",
        ),
    ),
    Label(
        key="evaluation_interpretation",
        display="Evaluation / Interpretation",
        japanese="解釈",
        description="Judgment, interpretation, importance, meaning, or implication.",
        keywords=(
            "important",
            "significant",
            "valuable",
            "harmful",
            "beneficial",
            "effective",
            "problematic",
            "means that",
            "suggests that",
            "implies",
            "indicates",
            "impact",
            "consequence",
            "better",
            "worse",
        ),
    ),
)


SENTENCE_RE = re.compile(r"[^.!?]+(?:[.!?]+|$)", re.MULTILINE)
WORD_RE = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+)?")


LABEL_BY_KEY = {label.key: label for label in LABELS}
LABEL_KEYS = tuple(label.key for label in LABELS)


def split_sentences(text: str) -> list[str]:
    return [match.group(0).strip() for match in SENTENCE_RE.finditer(text) if match.group(0).strip()]


def label_payload(label: Label) -> dict:
    return {
        "key": label.key,
        "display": label.display,
        "japanese": label.japanese,
        "description": label.description,
    }


def label_payloads() -> list[dict]:
    return [label_payload(label) for label in LABELS]


def check_english(text: str) -> dict:
    words = WORD_RE.findall(text)
    ascii_letters = sum(1 for char in text if char.isascii() and char.isalpha())
    alpha_chars = sum(1 for char in text if char.isalpha())
    ascii_ratio = ascii_letters / alpha_chars if alpha_chars else 0.0
    common_hits = _count_common_words(words)
    likely_english = ascii_ratio > 0.85 and (len(words) < 5 or common_hits >= 1)
    return {
        "likely_english": likely_english,
        "ascii_letter_ratio": round(ascii_ratio, 4),
        "word_count": len(words),
        "warning": None
        if likely_english
        else "This MVP is English-only. Results may be unreliable for non-English text.",
    }


def build_text_response(model_name: str, text: str, sentence_results: list[dict]) -> dict:
    label_counts: dict[str, int] = {}
    for item in sentence_results:
        label_counts[item["label"]["key"]] = label_counts.get(item["label"]["key"], 0) + 1

    return {
        "ok": True,
        "model": model_name,
        "language": check_english(text),
        "labels": label_payloads(),
        "summary": {
            "sentence_count": len(sentence_results),
            "label_counts": label_counts,
        },
        "sentences": sentence_results,
    }


def _count_common_words(words: Iterable[str]) -> int:
    common = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "because",
        "although",
        "for",
        "to",
        "of",
        "in",
        "is",
        "are",
        "should",
        "people",
        "this",
        "that",
    }
    return sum(1 for word in words if word.lower() in common)


class RuleBasedClassifier:
    model_name = "rule-based-six-class-mvp"

    def classify_text(self, text: str) -> dict:
        text = text.strip()
        if not text:
            return {"ok": False, "error": "empty_text", "message": "Text is required."}

        sentences = split_sentences(text)
        if not sentences:
            return {"ok": False, "error": "no_sentences", "message": "No sentences found."}

        results = [self.classify_sentence(sentence, i) for i, sentence in enumerate(sentences)]
        return build_text_response(self.model_name, text, results)

    def classify_sentence(self, sentence: str, index: int = 0) -> dict:
        scores = self._score_sentence(sentence)
        best_key = max(scores, key=scores.get)
        best_label = LABEL_BY_KEY[best_key]
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        confidence = sorted_scores[0][1]
        margin = sorted_scores[0][1] - sorted_scores[1][1]

        return {
            "index": index,
            "text": sentence,
            "label": label_payload(best_label),
            "confidence": round(confidence, 4),
            "margin": round(margin, 4),
            "scores": {key: round(value, 4) for key, value in scores.items()},
        }

    def _score_sentence(self, sentence: str) -> dict[str, float]:
        normalized = f" {sentence.lower()} "
        scores = {label.key: label.base_score for label in LABELS}

        for label in LABELS:
            for keyword in label.keywords:
                if keyword in normalized:
                    scores[label.key] += 1.0 if " " in keyword.strip() else 0.55

        if sentence.strip().endswith("?"):
            scores["background_circumstance"] += 0.2

        first_words = " ".join(WORD_RE.findall(sentence.lower())[:4])
        if first_words.startswith(("although", "however", "despite", "while")):
            scores["contrast_concession"] += 0.75
        if first_words.startswith(("for example", "for instance")):
            scores["example_elaboration"] += 0.9
        if first_words.startswith(("in conclusion", "overall", "ultimately")):
            scores["summary_conclusion"] += 0.9

        total = sum(scores.values())
        return {key: value / total for key, value in scores.items()}

    def _check_english(self, text: str) -> dict:
        return check_english(text)

    def _count_common_words(self, words: Iterable[str]) -> int:
        return _count_common_words(words)

    def _label_by_key(self, key: str) -> Label:
        return LABEL_BY_KEY[key]

    def _label_payload(self, label: Label) -> dict:
        return label_payload(label)
