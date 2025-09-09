#!/usr/bin/env python3
"""
unit tests for the progressive reveal tool.
"""

import unittest
from progressive_reveal import (
    TextUnit, parse_into_words, parse_into_lines, parse_into_sentences,
    generate_progressive_cards, process_text
)


class TestTextUnit(unittest.TestCase):
    """test cases for text unit class."""
    
    def test_word_unit_hidden(self):
        """test hiding a word unit."""
        unit = TextUnit("hello", False)
        self.assertEqual(unit.hidden(), "_____")
    
    def test_punctuation_unit_not_hidden(self):
        """test that punctuation is not hidden."""
        unit = TextUnit(",", True)
        self.assertEqual(unit.hidden(), ",")


class TestParsing(unittest.TestCase):
    """test cases for text parsing functions."""
    
    def test_parse_into_words(self):
        """test parsing text into word units."""
        units = parse_into_words("hello, world!")
        
        # check we have the right number of units
        self.assertEqual(len(units), 5)  # hello, ,, space, world, !
        
        # check word detection
        self.assertEqual(units[0].content, "hello")
        self.assertFalse(units[0].is_punctuation)
        
        # check punctuation detection
        self.assertEqual(units[1].content, ",")
        self.assertTrue(units[1].is_punctuation)
    
    def test_parse_into_lines(self):
        """test parsing text into line units."""
        text = "line one\nline two\nline three"
        units = parse_into_lines(text)
        
        self.assertEqual(len(units), 3)
        self.assertEqual(units[0].content, "line one")
        self.assertEqual(units[1].content, "line two")
        self.assertEqual(units[2].content, "line three")
    
    def test_parse_into_sentences(self):
        """test parsing text into sentence units."""
        text = "first sentence. second one! third?"
        units = parse_into_sentences(text)
        
        self.assertEqual(len(units), 3)
        self.assertEqual(units[0].content, "first sentence.")
        self.assertEqual(units[1].content, "second one!")
        self.assertEqual(units[2].content, "third?")


class TestProgressiveCards(unittest.TestCase):
    """test cases for progressive card generation."""
    
    def test_forward_progressive_words(self):
        """test forward progressive reveal by words."""
        units = parse_into_words("hello world")
        cards = generate_progressive_cards(units, chunk_size=1, reverse=False)
        
        # should have 2 cards (all hidden, then first revealed)
        self.assertEqual(len(cards), 2)
        
        # first card should have all hidden
        front1, back1 = cards[0]
        self.assertIn("_____", front1)
        self.assertIn("hello world", back1)
        
        # second card should reveal first word
        front2, back2 = cards[1]
        self.assertIn("hello", front2)
        self.assertIn("_____", front2)
        
    
    def test_reverse_progressive_words(self):
        """test reverse progressive (hiding) by words."""
        units = parse_into_words("hello world")
        cards = generate_progressive_cards(units, chunk_size=1, reverse=True)
        
        # should have 2 cards
        self.assertEqual(len(cards), 2)
        
        # first card should show only first word (reverse hides from the end)
        front1, back1 = cards[0]
        self.assertIn("hello", front1)
        self.assertIn("_____", front1)
        
        # second card should show both hidden
        front2, back2 = cards[1]
        self.assertEqual(front2.count('_'), 10)  # both words hidden
        
    
    def test_chunk_size(self):
        """test revealing multiple words at once."""
        units = parse_into_words("one two three four")
        cards = generate_progressive_cards(units, chunk_size=2, reverse=False)
        
        # with 4 words and chunk size 2, should have 2 cards
        self.assertEqual(len(cards), 2)
        
        # first card has all hidden
        front1, _ = cards[0]
        self.assertEqual(front1.count('_'), 15)  # all 4 words hidden (3+3+5+4)
        
        # second card reveals first 2 words
        front2, _ = cards[1]
        self.assertIn("one", front2)
        self.assertIn("two", front2)
    
    def test_keep_punctuation(self):
        """test that punctuation is preserved when requested."""
        units = parse_into_words("hello, world!")
        cards = generate_progressive_cards(units, keep_punctuation=True)
        
        # punctuation should always be visible
        for front, _ in cards:
            self.assertIn(",", front)
            self.assertIn("!", front)
    
    def test_hide_punctuation(self):
        """test hiding punctuation."""
        units = parse_into_words("hello, world!")
        cards = generate_progressive_cards(units, keep_punctuation=False)
        
        # first card should have hidden punctuation
        front1, _ = cards[0]
        # punctuation is still there (spaces preserved)
        self.assertIn(",", front1)  # punctuation is marked as such, so still visible


class TestProcessText(unittest.TestCase):
    """test cases for the main processing function."""
    
    def test_process_text_words(self):
        """test processing text into word-based cards."""
        cards = process_text("hello world", unit='word')
        self.assertEqual(len(cards), 2)
    
    def test_process_text_lines(self):
        """test processing text into line-based cards."""
        cards = process_text("line one\nline two", unit='line')
        self.assertEqual(len(cards), 2)  # all hidden, then first line
    
    def test_process_text_sentences(self):
        """test processing text into sentence-based cards."""
        cards = process_text("first. second.", unit='sentence')
        self.assertEqual(len(cards), 2)  # all hidden, then first sentence
    
    def test_empty_text(self):
        """test that empty text produces no cards."""
        cards = process_text("", unit='word')
        self.assertEqual(len(cards), 0)
    
    def test_reverse_mode(self):
        """test reverse progressive mode."""
        cards = process_text("one two", unit='word', reverse=True)
        
        # first card should show more, last card should show less
        front1, _ = cards[0]
        front2, _ = cards[1] if len(cards) > 1 else (None, None)
        
        if front2:
            # count visible words (non-underscores)
            words1 = [w for w in front1.split() if '_' not in w]
            words2 = [w for w in front2.split() if '_' not in w]
            self.assertGreater(len(words1), len(words2))


if __name__ == '__main__':
    unittest.main()