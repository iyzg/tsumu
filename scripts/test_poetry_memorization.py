#!/usr/bin/env python3
"""
Unit tests for poetry memorization tool.
"""

import unittest
import sys
import os
from io import StringIO
from unittest.mock import patch

# Add the parent directory to path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poetry_memorization import (
    Line, Stanza, PoetryParser, PoetryMemorizer
)


class TestPoetryParser(unittest.TestCase):
    """Test poetry parsing functionality."""
    
    def test_parse_simple_poem(self):
        """Test parsing a simple 4-line poem."""
        text = "Roses are red\nViolets are blue\nSugar is sweet\nAnd so are you"
        stanzas = PoetryParser.parse_text(text)
        
        self.assertEqual(len(stanzas), 1)
        self.assertEqual(len(stanzas[0].lines), 4)
        self.assertEqual(stanzas[0].lines[0].text, "Roses are red")
        self.assertEqual(stanzas[0].lines[0].line_num, 0)
    
    def test_parse_multi_stanza(self):
        """Test parsing poem with multiple stanzas."""
        text = "First line\nSecond line\n\nThird line\nFourth line"
        stanzas = PoetryParser.parse_text(text)
        
        self.assertEqual(len(stanzas), 2)
        self.assertEqual(len(stanzas[0].lines), 2)
        self.assertEqual(len(stanzas[1].lines), 2)
        self.assertEqual(stanzas[1].lines[0].text, "Third line")
    
    def test_extract_rhyme_word(self):
        """Test rhyme word extraction."""
        self.assertEqual(
            PoetryParser.extract_rhyme_word("Roses are red"),
            "red"
        )
        self.assertEqual(
            PoetryParser.extract_rhyme_word("And so are you!"),
            "you"
        )
        self.assertEqual(
            PoetryParser.extract_rhyme_word(""),
            None
        )


class TestPoetryMemorizer(unittest.TestCase):
    """Test card generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simple_poem = "Roses are red\nViolets are blue"
        self.stanzas = PoetryParser.parse_text(self.simple_poem)
        self.memorizer = PoetryMemorizer()
    
    def test_hide_line(self):
        """Test line hiding function."""
        result = self.memorizer._hide_line("Roses are red")
        self.assertEqual(result, "_____ ___ ___")
        
        result = self.memorizer._hide_line("Test! 123")
        self.assertEqual(result, "____! ___")
    
    def test_hide_except_word(self):
        """Test selective word hiding."""
        result = self.memorizer._hide_except_word(
            "Roses are red", "red"
        )
        self.assertEqual(result, "_____ ___ red")
        
        result = self.memorizer._hide_except_word(
            "The red rose is red", "red"
        )
        self.assertEqual(result, "___ red ____ __ red")
    
    def test_get_first_letters(self):
        """Test first letter extraction."""
        result = self.memorizer._get_first_letters("Roses are red")
        self.assertEqual(result, "R. A. R.")
        
        result = self.memorizer._get_first_letters("Hello world!")
        self.assertEqual(result, "H. W.")
    
    def test_create_line_cloze_cards(self):
        """Test line cloze card generation."""
        cards = self.memorizer.create_line_cloze_cards(self.stanzas)
        
        self.assertEqual(len(cards), 2)  # One card per line
        
        # First card should hide first line
        question, answer = cards[0]
        self.assertIn("_____ ___ ___", question)
        self.assertIn("Violets are blue", question)
        self.assertIn("Roses are red", answer)
    
    def test_create_sequential_cards(self):
        """Test sequential card generation."""
        cards = self.memorizer.create_sequential_cards(self.stanzas)
        
        # Should create "what comes after" and "what comes before" cards
        self.assertEqual(len(cards), 2)
        
        # Check first card
        question, answer = cards[0]
        self.assertIn("What comes after", question)
        self.assertIn("Roses are red", question)
        self.assertEqual(answer, "Violets are blue")
    
    def test_create_first_letter_cards(self):
        """Test first letter card generation."""
        cards = self.memorizer.create_first_letter_cards(self.stanzas)
        
        self.assertEqual(len(cards), 2)  # One per line
        
        question, answer = cards[0]
        self.assertIn("R. A. R.", question)
        self.assertEqual(answer, "Roses are red")
    
    def test_preserve_rhymes_option(self):
        """Test rhyme preservation in cloze cards."""
        memorizer = PoetryMemorizer(preserve_rhymes=True)
        cards = memorizer.create_line_cloze_cards(self.stanzas)
        
        # First card should preserve "red" as rhyme hint
        question, answer = cards[0]
        self.assertIn("red", question)
        self.assertIn("_____", question)
    
    def test_progressive_cards(self):
        """Test progressive difficulty card generation."""
        memorizer = PoetryMemorizer(progressive=True)
        poem = "Line one\nLine two\nLine three"
        stanzas = PoetryParser.parse_text(poem)
        
        cards = memorizer.create_cards(stanzas)
        
        # Should have regular cards plus progressive ones
        self.assertGreater(len(cards), 6)  # More than just basic cards


class TestCLIIntegration(unittest.TestCase):
    """Test command-line interface."""
    
    def test_empty_input(self):
        """Test handling of empty input."""
        with patch('sys.stdin', StringIO('')):
            with patch('sys.stderr', new_callable=StringIO) as mock_err:
                with self.assertRaises(SystemExit):
                    from poetry_memorization import main
                    main()
                
                self.assertIn("No input provided", mock_err.getvalue())
    
    def test_basic_poem_processing(self):
        """Test processing a basic poem through CLI."""
        poem = "Test line one\nTest line two"
        
        with patch('sys.stdin', StringIO(poem)):
            with patch('sys.stdout', new_callable=StringIO) as mock_out:
                with patch('sys.stderr', new_callable=StringIO) as mock_err:
                    with patch('sys.argv', ['poetry_memorization.py']):
                        from poetry_memorization import main
                        main()
                
                # Should generate cards to stdout
                output = mock_out.getvalue()
                self.assertIn("Test line", output)
                
                # Should report card count to stderr
                stderr = mock_err.getvalue()
                self.assertIn("Generated", stderr)
                self.assertIn("cards", stderr)


if __name__ == '__main__':
    unittest.main()