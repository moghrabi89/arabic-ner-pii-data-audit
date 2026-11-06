import unittest

from src.common import WIKIANN_LABELS, bio_errors, normalize_text


class CoreAuditTests(unittest.TestCase):
    def test_normalize_text_collapses_whitespace(self):
        self.assertEqual(normalize_text("  A\n  B\tC  "), "A B C")

    def test_bio_errors_accepts_valid_sequence(self):
        tags = [0, 1, 2, 0, 3, 4]
        self.assertEqual(bio_errors(tags), 0)

    def test_bio_errors_flags_orphan_i_tag(self):
        tags = [0, 2, 0]
        self.assertEqual(bio_errors(tags), 1)

    def test_wikiann_label_contract(self):
        self.assertEqual(WIKIANN_LABELS[1], "B-PER")
        self.assertEqual(WIKIANN_LABELS[6], "I-LOC")


if __name__ == "__main__":
    unittest.main()
