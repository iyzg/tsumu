#!/usr/bin/env python3
"""
unit tests for the overlapping cloze deletion tool.
"""

import unittest
from overlapping_cloze import ClozeElement, parse_text, generate_combinations, process_line


class TestOverlappingCloze(unittest.TestCase):
    """test cases for overlapping cloze functionality."""
    
    def test_parse_text_single_answer(self):
        """test parsing text with a single marked answer."""
        elements = parse_text("david hume was born in %1711%")
        
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[0].content, "david hume was born in ")
        self.assertFalse(elements[0].is_answer)
        self.assertEqual(elements[1].content, "1711")
        self.assertTrue(elements[1].is_answer)
    
    def test_parse_text_multiple_answers(self):
        """test parsing text with multiple marked answers."""
        elements = parse_text("born in %1711% in %edinburgh%")
        
        self.assertEqual(len(elements), 4)
        self.assertEqual(elements[0].content, "born in ")
        self.assertEqual(elements[1].content, "1711")
        self.assertEqual(elements[2].content, " in ")
        self.assertEqual(elements[3].content, "edinburgh")
    
    def test_parse_text_custom_delimiter(self):
        """test parsing with a custom delimiter."""
        elements = parse_text("the @capital@ of france", delimiter='@')
        
        self.assertEqual(len(elements), 3)
        self.assertEqual(elements[0].content, "the ")
        self.assertEqual(elements[1].content, "capital")
        self.assertTrue(elements[1].is_answer)
        self.assertEqual(elements[2].content, " of france")
        self.assertFalse(elements[2].is_answer)
    
    def test_parse_text_no_answers(self):
        """test parsing text with no marked answers."""
        elements = parse_text("plain text without answers")
        
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].content, "plain text without answers")
        self.assertFalse(elements[0].is_answer)
    
    def test_generate_combinations_single_answer(self):
        """test generating combinations with one answer."""
        elements = [
            ClozeElement("the answer is ", is_answer=False),
            ClozeElement("42", is_answer=True)
        ]
        
        combinations = generate_combinations(elements)
        
        self.assertEqual(len(combinations), 1)
        self.assertEqual(combinations[0], ("the answer is ____", "42"))
    
    def test_generate_combinations_two_answers(self):
        """test generating combinations with two answers."""
        elements = [
            ClozeElement("born in ", is_answer=False),
            ClozeElement("1711", is_answer=True),
            ClozeElement(" in ", is_answer=False),
            ClozeElement("edinburgh", is_answer=True)
        ]
        
        combinations = generate_combinations(elements)
        
        # should generate 3 combinations (2^2 - 1)
        self.assertEqual(len(combinations), 3)
        
        # check specific combinations
        questions = [q for q, _ in combinations]
        answers = [a for _, a in combinations]
        
        self.assertIn("born in 1711 in ____", questions)
        self.assertIn("born in ____ in edinburgh", questions)
        self.assertIn("born in ____ in ____", questions)
        
        self.assertIn("edinburgh", answers)
        self.assertIn("1711", answers)
        self.assertIn("1711, edinburgh", answers)
    
    def test_generate_combinations_three_answers(self):
        """test generating combinations with three answers."""
        elements = [
            ClozeElement("", is_answer=False),
            ClozeElement("a", is_answer=True),
            ClozeElement(" ", is_answer=False),
            ClozeElement("b", is_answer=True),
            ClozeElement(" ", is_answer=False),
            ClozeElement("c", is_answer=True)
        ]
        
        combinations = generate_combinations(elements)
        
        # should generate 7 combinations (2^3 - 1)
        self.assertEqual(len(combinations), 7)
    
    def test_process_line(self):
        """test processing a complete line."""
        cards = process_line("the %capital% of %france% is %paris%")
        
        # should generate 7 cards (2^3 - 1)
        self.assertEqual(len(cards), 7)
        
        # check that all cards are tab-separated
        for card in cards:
            self.assertIn('\t', card)
            parts = card.split('\t')
            self.assertEqual(len(parts), 2)
    
    def test_process_line_empty(self):
        """test processing an empty line."""
        cards = process_line("")
        self.assertEqual(len(cards), 0)
    
    def test_process_line_no_answers(self):
        """test processing a line with no answers."""
        cards = process_line("plain text without answers")
        self.assertEqual(len(cards), 0)
    
    def test_special_characters_in_answers(self):
        """test handling special characters in answers."""
        elements = parse_text("formula: %a² + b² = c²%")
        
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[1].content, "a² + b² = c²")
        
        cards = process_line("formula: %a² + b² = c²%")
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0], "formula: ____\ta² + b² = c²")


if __name__ == '__main__':
    unittest.main()