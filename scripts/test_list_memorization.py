#!/usr/bin/env python3
"""
unit tests for the list memorization tool.
"""

import unittest
from list_memorization import (
    format_ordinal,
    generate_ordinal_cards,
    generate_before_after_cards,
    generate_all_cards,
    process_list
)


class TestListMemorization(unittest.TestCase):
    """test cases for list memorization functionality."""
    
    def test_format_ordinal(self):
        """test ordinal number formatting."""
        self.assertEqual(format_ordinal(1), "1st")
        self.assertEqual(format_ordinal(2), "2nd")
        self.assertEqual(format_ordinal(3), "3rd")
        self.assertEqual(format_ordinal(4), "4th")
        self.assertEqual(format_ordinal(11), "11th")
        self.assertEqual(format_ordinal(12), "12th")
        self.assertEqual(format_ordinal(13), "13th")
        self.assertEqual(format_ordinal(21), "21st")
        self.assertEqual(format_ordinal(22), "22nd")
        self.assertEqual(format_ordinal(23), "23rd")
        self.assertEqual(format_ordinal(101), "101st")
        self.assertEqual(format_ordinal(111), "111th")
    
    def test_generate_ordinal_cards_basic(self):
        """test generating ordinal position cards."""
        items = ["first", "second", "third"]
        cards = generate_ordinal_cards(items)
        
        # should generate 2 cards per item
        self.assertEqual(len(cards), 6)
        
        # check specific cards
        self.assertIn(("What was 1st?", "first"), cards)
        self.assertIn(("What position was first?", "1st"), cards)
        self.assertIn(("What was 2nd?", "second"), cards)
        self.assertIn(("What position was second?", "2nd"), cards)
    
    def test_generate_ordinal_cards_with_context(self):
        """test generating ordinal cards with context word."""
        items = ["shang", "zhou"]
        cards = generate_ordinal_cards(items, context="dynasty")
        
        self.assertIn(("What dynasty was 1st?", "shang"), cards)
        self.assertIn(("What position dynasty was shang?", "1st"), cards)
    
    def test_generate_before_after_cards_basic(self):
        """test generating before/after relationship cards."""
        items = ["a", "b", "c"]
        cards = generate_before_after_cards(items)
        
        # first item: 2 cards (what comes after)
        # middle items: 4 cards each (before and after)
        # last item: 2 cards (what comes before)
        # total: 2 + 4 + 2 = 8
        self.assertEqual(len(cards), 8)
        
        # check specific relationships
        self.assertIn(("What did a come before?", "b"), cards)
        self.assertIn(("What succeeded a?", "b"), cards)
        self.assertIn(("What came before b?", "a"), cards)
        self.assertIn(("What preceded b?", "a"), cards)
        self.assertIn(("What did b come before?", "c"), cards)
        self.assertIn(("What came before c?", "b"), cards)
    
    def test_generate_before_after_cards_single_item(self):
        """test relationship cards with single item (should be empty)."""
        items = ["only"]
        cards = generate_before_after_cards(items)
        
        self.assertEqual(len(cards), 0)
    
    def test_generate_before_after_cards_two_items(self):
        """test relationship cards with two items."""
        items = ["first", "second"]
        cards = generate_before_after_cards(items)
        
        # each item has 2 cards (4 total)
        self.assertEqual(len(cards), 4)
        
        self.assertIn(("What did first come before?", "second"), cards)
        self.assertIn(("What succeeded first?", "second"), cards)
        self.assertIn(("What came before second?", "first"), cards)
        self.assertIn(("What preceded second?", "first"), cards)
    
    def test_generate_before_after_cards_with_context(self):
        """test relationship cards with context word."""
        items = ["mercury", "venus"]
        cards = generate_before_after_cards(items, context="planet")
        
        self.assertIn(("What planet did mercury come before?", "venus"), cards)
        self.assertIn(("What planet came before venus?", "mercury"), cards)
    
    def test_generate_all_cards(self):
        """test generating all types of cards."""
        items = ["x", "y", "z"]
        cards = generate_all_cards(items)
        
        # ordinal: 3 items * 2 = 6 cards
        # relationships: 2 + 4 + 2 = 8 cards
        # total: 14 cards
        self.assertEqual(len(cards), 14)
        
        # check both types are present
        questions = [q for q, _ in cards]
        self.assertTrue(any("1st" in q for q in questions))  # ordinal
        self.assertTrue(any("before" in q for q in questions))  # relationship
    
    def test_process_list_empty(self):
        """test processing empty list."""
        cards = process_list([])
        self.assertEqual(len(cards), 0)
    
    def test_process_list_formatting(self):
        """test that output is tab-separated."""
        items = ["alpha", "beta"]
        cards = process_list(items)
        
        self.assertTrue(len(cards) > 0)
        
        for card in cards:
            self.assertIn('\t', card)
            parts = card.split('\t')
            self.assertEqual(len(parts), 2)
    
    def test_process_list_with_context(self):
        """test processing with context word."""
        items = ["intro", "verse", "chorus"]
        cards = process_list(items, context="section")
        
        # check context appears in questions
        for card in cards:
            question, answer = card.split('\t')
            if "was" in question or "before" in question or "succeeded" in question:
                self.assertIn("section", question)


if __name__ == '__main__':
    unittest.main()