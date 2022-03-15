import unittest

from digspec import extract_ad_info


class TestExtractAdInfo(unittest.TestCase):
    def test_get_raw_data(self):
        """
        Test that it can read data file
        """
        result = extract_ad_info.get_raw_data(["tmp-year"])
        self.assertEqual(result, [[{"data": "test"}, "tmp-year"]])
    def test_extract_fields(self):
        """
        Test that it can read data file
        """
        result = extract_ad_info.extract_fields([{
                "occupation_group": {
                    "concept_id": "Group A"
                },
                "publication_date": "2022-03-10",
                "id": "123",
                "headline": "Ad1",
                "description": {
                    "text": "Ad1 Text"
                },
                "employer": {"name": "Ad1 Corp"}
            },
            {
                "occupation_group": {
                    "concept_id": "Group B"
                },
                "publication_date": "2022-03-10",
                "id": "1234",
                "headline": "Ad2",
                "description": {
                    "text": "Ad2 Text"
                },
                "employer": {"name": "Ad2 Corp"}
            },
            {
                "occupation_group": {
                    "concept_id": "Group A"
                },
                "publication_date": "2022-03-10",
                "id": "12345",
                "headline": "Ad3",
                "description": {
                    "text": "Ad3 Text\nNewline"
                },
                "employer": {"name": "Ad3 Corp"}
            }
        ], ["Group A"])
        self.assertEqual(result, [
            {
                "date": "2022-03-10",
                "doc_id": "123",
                "doc_headline": "ad1",
                "doc_text": "ad1 text",
                "employer": "Ad1 Corp"
            },
            {
                "date": "2022-03-10",
                "doc_id": "12345",
                "doc_headline": "ad3",
                "doc_text": "ad3 text newline",
                "employer": "Ad3 Corp"
            }
        ])

if __name__ == '__main__':
    unittest.main()

