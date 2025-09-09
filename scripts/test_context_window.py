#!/usr/bin/env python3
"""
tests for context window cards generator
"""

import unittest
import tempfile
import os
from pathlib import Path
from context_window import (
    extract_focus_phrases,
    get_context_window,
    create_context_card,
    generate_context_cards
)


class TestContextWindow(unittest.TestCase):
    """test cases for context window generator."""
    
    def test_extract_quoted_phrases(self):
        """test extracting quoted phrases."""
        text = 'The "quick brown" fox jumps over the "lazy dog".'
        phrases = extract_focus_phrases(text)
        
        self.assertEqual(len(phrases), 2)
        self.assertEqual(phrases[0][0], 'quick brown')  # content without quotes
        self.assertEqual(phrases[1][0], 'lazy dog')  # content without quotes
    
    def test_extract_markdown_emphasis(self):
        """test extracting markdown emphasized text."""
        text = "The **important term** and *italic phrase* are highlighted."
        phrases = extract_focus_phrases(text)
        
        self.assertEqual(len(phrases), 2)
        self.assertEqual(phrases[0][0], "important term")
        self.assertEqual(phrases[1][0], "italic phrase")
    
    def test_extract_with_custom_pattern(self):
        """test extraction with custom regex pattern."""
        text = "The ISBN-123 and ISBN-456 are book codes."
        pattern = r"ISBN-\d+"
        phrases = extract_focus_phrases(text, pattern)
        
        self.assertEqual(len(phrases), 2)
        self.assertEqual(phrases[0][0], "ISBN-123")
        self.assertEqual(phrases[1][0], "ISBN-456")
    
    def test_get_full_context_window(self):
        """test getting full context window."""
        text = "The quick brown fox jumps over the lazy dog."
        before, focus, after = get_context_window(text, 4, 15, "full")
        
        self.assertEqual(before, "The ")
        self.assertEqual(focus, "quick brown")
        self.assertEqual(after, " fox jumps over the lazy dog.")
    
    def test_get_limited_context_window(self):
        """test getting limited word context window."""
        text = "The quick brown fox jumps over the lazy dog."
        before, focus, after = get_context_window(text, 16, 19, "2")
        
        self.assertEqual(focus, "fox")
        self.assertTrue("quick brown" in before)
        self.assertTrue("jumps over" in after)
    
    def test_get_zero_context_window(self):
        """test getting zero context window."""
        text = "The quick brown fox jumps over the lazy dog."
        before, focus, after = get_context_window(text, 16, 19, "0")
        
        self.assertEqual(before, "")
        self.assertEqual(focus, "fox")
        self.assertEqual(after, "")
    
    def test_create_context_card_with_full_context(self):
        """test creating card with full context."""
        card = create_context_card(
            "brown fox",
            "The quick ",
            " jumps over",
            "full"
        )
        
        self.assertEqual(card["front"], "The quick [...] jumps over")
        # brown fox is 2 words, so it should have context in answer
        self.assertIn("brown fox", card["back"])
        self.assertIn("quick", card["back"])  # should include some context
    
    def test_create_context_card_with_hint(self):
        """test creating card with context hint."""
        card = create_context_card(
            "fox",
            "...quick brown ",
            " jumps...",
            "2",
            include_hint=True
        )
        
        self.assertTrue("(±2 words)" in card["front"])
    
    def test_create_context_card_no_context(self):
        """test creating card with no context."""
        card = create_context_card(
            "important",
            "",
            "",
            "0",
            include_hint=True
        )
        
        self.assertEqual(card["front"], "[...] (no context)")
        self.assertEqual(card["back"], "important")
    
    def test_generate_multiple_window_sizes(self):
        """test generating cards with multiple window sizes."""
        text = 'Learn the "important concept" thoroughly.'
        cards = generate_context_cards(
            text,
            ["full", "2", "0"],
            include_hints=False
        )
        
        # should generate 3 cards (one for each window size)
        self.assertEqual(len(cards), 3)
        
        # check that different contexts are generated
        fronts = [card["front"] for card in cards]
        self.assertEqual(len(set(fronts)), 3)  # all different
    
    def test_generate_with_multiple_phrases(self):
        """test generating cards for multiple focus phrases."""
        text = 'The "first term" and the "second term" are important.'
        cards = generate_context_cards(
            text,
            ["full", "0"],
            include_hints=False
        )
        
        # 2 phrases × 2 window sizes = 4 cards
        self.assertEqual(len(cards), 4)
    
    def test_short_phrase_context_in_answer(self):
        """test that short phrases include context in answer."""
        card = create_context_card(
            "AI",
            "The field of ",
            " is growing rapidly",
            "full"
        )
        
        # short phrase should have context preview in answer
        self.assertTrue("AI" in card["back"])
        self.assertTrue(len(card["back"]) > 2)  # more than just "AI"


if __name__ == "__main__":
    unittest.main()