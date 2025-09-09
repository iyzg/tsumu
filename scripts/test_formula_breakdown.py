#!/usr/bin/env python3
"""
tests for formula breakdown generator
"""

import unittest
from formula_breakdown import (
    parse_formula_line,
    extract_variables,
    create_component_cards,
    create_progressive_cards,
    create_unit_cards,
    process_formulas
)


class TestFormulaBreakdown(unittest.TestCase):
    """test cases for formula breakdown generator."""
    
    def test_parse_formula_line(self):
        """test parsing formula line."""
        line = "E = mc^2 | E:energy, m:mass, c:speed of light | Einstein's equation"
        result = parse_formula_line(line)
        
        self.assertEqual(result['formula'], "E = mc^2")
        self.assertEqual(result['components']['E'], "energy")
        self.assertEqual(result['components']['m'], "mass")
        self.assertEqual(result['components']['c'], "speed of light")
        self.assertEqual(result['description'], "Einstein's equation")
    
    def test_parse_formula_line_no_description(self):
        """test parsing formula line without description."""
        line = "F = ma | F:force, m:mass, a:acceleration"
        result = parse_formula_line(line)
        
        self.assertEqual(result['formula'], "F = ma")
        self.assertEqual(len(result['components']), 3)
        self.assertEqual(result['description'], "")
    
    def test_extract_variables(self):
        """test extracting variables from formula."""
        formula = "E = mc^2"
        variables = extract_variables(formula)
        
        self.assertIn('E', variables)
        self.assertIn('m', variables)
        self.assertIn('c', variables)
    
    def test_extract_variables_with_subscripts(self):
        """test extracting subscripted variables."""
        formula = "v = v_0 + at"
        variables = extract_variables(formula)
        
        self.assertIn('v', variables)
        self.assertIn('v_0', variables)
        self.assertIn('a', variables)
        self.assertIn('t', variables)
    
    def test_create_component_cards(self):
        """test creating component cards."""
        formula = "F = ma"
        components = {'F': 'force', 'm': 'mass', 'a': 'acceleration'}
        description = "Newton's second law"
        
        cards = create_component_cards(formula, components, description)
        
        # should create cards for each component
        self.assertTrue(any("what does f represent" in card[0].lower() for card in cards))
        self.assertTrue(any("what does m represent" in card[0].lower() for card in cards))
        self.assertTrue(any("what does a represent" in card[0].lower() for card in cards))
        
        # should create formula completion card
        self.assertTrue(any("Complete the formula" in card[0] for card in cards))
        
        # should create description card
        self.assertTrue(any(description in card[0] for card in cards))
    
    def test_create_component_cards_minimal(self):
        """test creating cards with minimal input."""
        formula = "E = mc^2"
        components = {'E': 'energy'}
        
        cards = create_component_cards(formula, components)
        
        # at minimum, should create variable definition card
        self.assertTrue(len(cards) >= 1)
        self.assertTrue(any("what does e represent" in card[0].lower() for card in cards))
    
    def test_create_progressive_cards(self):
        """test creating progressive buildup cards."""
        formula = "E = mc^2"
        components = {'E': 'energy', 'm': 'mass', 'c': 'speed of light'}
        
        cards = create_progressive_cards(formula, components)
        
        # should create cards that build up understanding
        self.assertTrue(len(cards) > 0)
        
        # should have a card listing all components
        self.assertTrue(any("Given these quantities" in card[0] for card in cards))
    
    def test_create_unit_cards(self):
        """test creating unit cards."""
        formula = "F = ma"
        components = {'F': 'force', 'm': 'mass', 'a': 'acceleration'}
        
        cards = create_unit_cards(formula, components)
        
        # should create unit cards for known quantities
        self.assertTrue(len(cards) > 0)
        self.assertTrue(any("SI unit" in card[0] for card in cards))
    
    def test_create_unit_cards_with_custom_units(self):
        """test creating unit cards with custom units."""
        formula = "P = IV"
        components = {'P': 'power', 'I': 'current', 'V': 'voltage'}
        units = {'P': 'watts', 'I': 'amperes', 'V': 'volts'}
        
        cards = create_unit_cards(formula, components, units)
        
        # should use provided units
        self.assertTrue(any("watts" in card[1] for card in cards))
        self.assertTrue(any("amperes" in card[1] for card in cards))
    
    def test_process_formulas_basic(self):
        """test processing multiple formulas."""
        input_text = """
F = ma | F:force, m:mass, a:acceleration | Newton's second law
E = mc^2 | E:energy, m:mass, c:speed of light | Mass-energy equivalence
"""
        
        cards = process_formulas(input_text)
        
        # should generate cards for both formulas
        self.assertTrue(len(cards) > 4)  # at least 2 cards per formula
        
        # should have cards for both formulas
        card_texts = str(cards)
        self.assertIn("F = ma", card_texts)
        self.assertIn("E = mc", card_texts)
    
    def test_process_formulas_with_options(self):
        """test processing with various options."""
        input_text = "F = ma | F:force, m:mass, a:acceleration | Newton's second law"
        
        # test with reverse cards
        cards = process_formulas(input_text, reverse=True)
        self.assertTrue(any("Newton's second law" in card[1] for card in cards))
        
        # test with progressive cards
        cards = process_formulas(input_text, progressive=True)
        initial_len = len(cards)
        
        # test with units
        cards = process_formulas(input_text, include_units=True)
        self.assertTrue(any("unit" in card[0].lower() for card in cards))
    
    def test_process_formulas_skip_comments(self):
        """test that comment lines are skipped."""
        input_text = """
# This is a comment
F = ma | F:force, m:mass, a:acceleration
# Another comment
E = mc^2 | E:energy, m:mass, c:speed of light
"""
        
        cards = process_formulas(input_text)
        
        # comments should not affect card generation
        card_texts = str(cards)
        self.assertNotIn("#", card_texts)
        self.assertIn("F = ma", card_texts)
        self.assertIn("E = mc", card_texts)


if __name__ == "__main__":
    unittest.main()