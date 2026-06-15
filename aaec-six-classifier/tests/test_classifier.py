import unittest

from app.classifier import RuleBasedClassifier
from app.factory import create_classifier


class RuleBasedClassifierTest(unittest.TestCase):
    def setUp(self):
        self.classifier = RuleBasedClassifier()

    def test_classifies_common_markers(self):
        cases = {
            "Because the policy reduces pollution, it helps cities.": "cause_explanation",
            "For example, buses can carry many people at once.": "example_elaboration",
            "Although it is expensive, the benefit is large.": "contrast_concession",
            "In recent years, cities have grown rapidly.": "background_circumstance",
            "In conclusion, governments should invest in transit.": "summary_conclusion",
            "This suggests that public transit is socially important.": "evaluation_interpretation",
        }
        for sentence, expected in cases.items():
            with self.subTest(sentence=sentence):
                result = self.classifier.classify_sentence(sentence)
                self.assertEqual(result["label"]["key"], expected)

    def test_text_response_shape(self):
        result = self.classifier.classify_text("Because it works. For example, it saves time.")
        self.assertTrue(result["ok"])
        self.assertEqual(result["summary"]["sentence_count"], 2)
        self.assertIn("labels", result)
        self.assertIn("sentences", result)

    def test_default_factory_uses_rule_based_classifier(self):
        self.assertIsInstance(create_classifier(), RuleBasedClassifier)


if __name__ == "__main__":
    unittest.main()
