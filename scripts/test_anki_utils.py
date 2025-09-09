#!/usr/bin/env python3
"""
Unit tests for anki_utils module.

Run with:
    python -m unittest test_anki_utils.py
"""

import unittest
import tempfile
import csv
from pathlib import Path
from anki_utils import AnkiFormatter, AnkiWriter, TextParser, ClozeGenerator


class TestAnkiFormatter(unittest.TestCase):
    """Test AnkiFormatter class."""
    
    def setUp(self):
        self.formatter = AnkiFormatter()
    
    def test_escape_html(self):
        """Test HTML escaping."""
        text = '<div>Hello & "world"</div>'
        expected = '&lt;div&gt;Hello &amp; &quot;world&quot;&lt;/div&gt;'
        self.assertEqual(self.formatter.escape_html(text), expected)
    
    def test_convert_latex(self):
        """Test LaTeX conversion."""
        text = 'The equation $x^2 + y^2 = z^2$ is famous'
        expected = 'The equation \\(x^2 + y^2 = z^2\\) is famous'
        self.assertEqual(self.formatter.convert_latex(text), expected)
        
        text = 'Block equation: $$E = mc^2$$'
        expected = 'Block equation: \\[E = mc^2\\]'
        self.assertEqual(self.formatter.convert_latex(text), expected)
    
    def test_format_newlines(self):
        """Test newline formatting."""
        text = 'Line 1\nLine 2\nLine 3'
        expected = 'Line 1<br>Line 2<br>Line 3'
        self.assertEqual(self.formatter.format_newlines(text), expected)
    
    def test_format_all(self):
        """Test combined formatting."""
        text = 'Math: $x < 5$ and\nHTML: <tag>'
        result = self.formatter.process_text(text)
        self.assertIn('\\(', result)
        self.assertIn('&lt;', result)
        self.assertIn('<br>', result)


class TestAnkiWriter(unittest.TestCase):
    """Test AnkiWriter class."""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        self.temp_file.close()
        self.writer = AnkiWriter()
    
    def tearDown(self):
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_write_csv(self):
        """Test writing cards to CSV."""
        cards = [
            ('What is 2+2?', '4'),
            ('Capital of France?', 'Paris')
        ]
        
        with open(self.temp_file.name, 'w') as f:
            self.writer.write_csv(cards, f)
        
        with open(self.temp_file.name, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0][0], 'What is 2+2?')
            self.assertEqual(rows[0][1], '4')
    
    def test_write_cloze_csv(self):
        """Test writing cloze cards."""
        cards = ['The capital of France is {{c1::Paris}}']
        
        with open(self.temp_file.name, 'w') as f:
            self.writer.write_cloze_csv(cards, f)
        
        with open(self.temp_file.name, 'r') as f:
            content = f.read()
            self.assertIn('{{c1::Paris}}', content)


class TestTextParser(unittest.TestCase):
    """Test TextParser class."""
    
    def setUp(self):
        self.parser = TextParser()
    
    def test_extract_list_items(self):
        """Test list item extraction."""
        text = """
        - Item 1
        - Item 2
        * Item 3
        1. First
        2. Second
        """
        items = self.parser.extract_list_items(text)
        self.assertEqual(len(items), 5)
        self.assertIn('Item 1', items)
        self.assertIn('First', items)
    
    def test_split_sentences(self):
        """Test sentence splitting."""
        text = "First sentence. Second one! Third? Fourth."
        sentences = self.parser.split_sentences(text)
        self.assertEqual(len(sentences), 4)
        self.assertEqual(sentences[0], "First sentence.")
    
    def test_parse_key_value(self):
        """Test key-value pair parsing."""
        text = """
        Name: John Doe
        Age: 30
        City: New York
        Random text here
        Email: john@example.com
        """
        pairs = self.parser.parse_key_value(text)
        self.assertEqual(len(pairs), 4)
        # Convert to dict for easier testing
        pairs_dict = dict(pairs)
        self.assertEqual(pairs_dict['Name'], 'John Doe')
        self.assertEqual(pairs_dict['Age'], '30')


class TestClozeGenerator(unittest.TestCase):
    """Test ClozeGenerator class."""
    
    def setUp(self):
        self.generator = ClozeGenerator()
    
    def test_create_cloze(self):
        """Test single cloze creation."""
        text = "The quick brown fox"
        result = self.generator.create_cloze(text, "quick")
        self.assertEqual(result, "The {{c1::quick}} brown fox")
    
    def test_create_overlapping_cloze(self):
        """Test overlapping cloze generation."""
        text = "The quick brown fox jumps"
        targets = ["quick", "brown", "fox"]
        result = self.generator.create_overlapping_cloze(text, targets)
        self.assertIn('{{c1::quick}}', result)
        self.assertIn('{{c1::brown}}', result)
        self.assertIn('{{c1::fox}}', result)
    
    def test_create_sequential_cloze(self):
        """Test sequential cloze generation."""
        text = "The quick brown fox jumps"
        targets = ["quick", "brown", "fox"]
        result = self.generator.create_sequential_cloze(text, targets)
        self.assertIn('{{c1::quick}}', result)
        self.assertIn('{{c2::brown}}', result)
        self.assertIn('{{c3::fox}}', result)


def run_tests():
    """Run all tests with verbose output."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()