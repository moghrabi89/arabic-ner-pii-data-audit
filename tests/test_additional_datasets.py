import unittest

from src.additional_datasets import _parse_inline_annotation, _reconstruct_anercorp


class AdditionalDatasetAuditTests(unittest.TestCase):
    def test_cv18_inline_annotation_parser(self):
        tokens, tags, errors = _parse_inline_annotation(
            "قال <سامي B-PERS> إنه في <نيويورك B-GPE> اليوم"
        )
        self.assertEqual(tokens, ["قال", "سامي", "إنه", "في", "نيويورك", "اليوم"])
        self.assertEqual(tags, ["O", "B-PERS", "O", "O", "B-GPE", "O"])
        self.assertEqual(errors, 0)

    def test_anercorp_period_boundary_reconstruction(self):
        rows = [
            {"word": "مرحبا", "tag": "O"},
            {"word": ".", "tag": "O"},
            {"word": "سعيد", "tag": "B-PERS"},
            {"word": ".", "tag": "O"},
        ]
        sentences = _reconstruct_anercorp(rows)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0]["tokens"], ["مرحبا", "."])
        self.assertEqual(sentences[1]["labels"], ["B-PERS", "O"])


if __name__ == "__main__":
    unittest.main()
