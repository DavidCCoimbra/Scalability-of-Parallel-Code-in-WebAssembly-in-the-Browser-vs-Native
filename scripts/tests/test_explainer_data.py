import unittest

from scripts.explainer_data import CODE_KEY, excerpt, malformed_keys


class ExplainerDataTest(unittest.TestCase):
    def test_page_keys_are_found_in_attributes_and_calls(self) -> None:
        page = '<div data-code="a/b.rs|fn main|3"></div> UI.code("c.py|def f|2", {})'
        self.assertEqual(CODE_KEY.findall(page), ["a/b.rs|fn main|3", "c.py|def f|2"])

    def test_an_excerpt_starts_at_the_line_holding_its_anchor(self) -> None:
        found = excerpt("scripts/explainer_data.py|def excerpt(key|2")
        self.assertEqual(found.file, "scripts/explainer_data.py")
        self.assertTrue(found.text.startswith("def excerpt(key: str) -> Excerpt:"))
        self.assertEqual(len(found.text.splitlines()), 2)

    def test_an_anchor_no_longer_in_the_file_stops_the_script(self) -> None:
        with self.assertRaises(ValueError):
            excerpt("scripts/explainer_data.py|this text is not in the file|2")

    def test_a_key_whose_anchor_holds_the_separator_is_malformed(self) -> None:
        page = '<div data-code="a.sh|echo off | sudo tee|3"></div><div data-code="b.rs|fn f|2"></div>'
        self.assertEqual(malformed_keys(page), ["a.sh|echo off | sudo tee|3"])

    def test_an_anchor_on_two_lines_stops_the_script(self) -> None:
        with self.assertRaises(ValueError):
            excerpt("scripts/explainer_data.py|import|1")


if __name__ == "__main__":
    unittest.main()
