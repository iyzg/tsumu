#!/usr/bin/env python3
"""
Test suite for timeline cards generator.
"""

import unittest
from timeline_cards import (
    parse_timeline_input,
    parse_date_for_sorting,
    generate_absolute_date_cards,
    generate_relative_timing_cards,
    generate_sequence_cards,
    generate_time_gap_cards,
    generate_period_cards,
    generate_timeline_cards
)


class TestTimelineCards(unittest.TestCase):
    """Test cases for timeline cards generation."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_input = """
1492 | Columbus discovers America
1776 | American Declaration of Independence
1789 | French Revolution begins
1969 | Moon landing
2001 | 9/11 attacks
"""
        self.events = parse_timeline_input(self.sample_input)
    
    def test_parse_timeline_input(self):
        """Test parsing timeline input."""
        events = parse_timeline_input(self.sample_input)
        self.assertEqual(len(events), 5)
        self.assertEqual(events[0], ('1492', 'Columbus discovers America'))
        self.assertEqual(events[-1], ('2001', '9/11 attacks'))
        
        # Test with comments and empty lines
        input_with_comments = """
# This is a comment
1492 | Columbus discovers America

1776 | American Declaration of Independence
# Another comment
"""
        events = parse_timeline_input(input_with_comments)
        self.assertEqual(len(events), 2)
    
    def test_parse_date_for_sorting(self):
        """Test date parsing for sorting."""
        # Regular years
        self.assertEqual(parse_date_for_sorting('1492'), 1492)
        self.assertEqual(parse_date_for_sorting('2001'), 2001)
        
        # BCE dates
        self.assertEqual(parse_date_for_sorting('500 BCE'), -500)
        self.assertEqual(parse_date_for_sorting('44 BC'), -44)
        
        # Century notation
        self.assertAlmostEqual(parse_date_for_sorting('19th century'), 1850, delta=100)
        self.assertAlmostEqual(parse_date_for_sorting('5th century'), 450, delta=100)
    
    def test_absolute_date_cards(self):
        """Test absolute date card generation."""
        cards = generate_absolute_date_cards(self.events)
        
        # Should generate 2 cards per event (date->event and event->date)
        self.assertEqual(len(cards), 10)
        
        # Check format
        self.assertIn('What year/date: Columbus discovers America?', cards[0])
        self.assertIn('1492', cards[0])
        self.assertIn('What happened in 1492?', cards[1])
        self.assertIn('Columbus discovers America', cards[1])
    
    def test_relative_timing_cards(self):
        """Test relative timing card generation."""
        cards = generate_relative_timing_cards(self.events, window_size=2)
        
        # Should generate before/after cards
        self.assertTrue(len(cards) > 0)
        
        # Check for before/after questions
        cards_text = '\n'.join(cards)
        self.assertIn('What came before', cards_text)
        self.assertIn('What came after', cards_text)
        self.assertIn('What happened between', cards_text)
    
    def test_sequence_cards(self):
        """Test sequence ordering card generation."""
        cards = generate_sequence_cards(self.events, sequence_length=3)
        
        # Should generate cards for ordering events
        self.assertTrue(len(cards) > 0)
        
        # Check format
        cards_text = '\n'.join(cards)
        self.assertIn('Order chronologically:', cards_text)
        self.assertIn('Correct order:', cards_text)
    
    def test_time_gap_cards(self):
        """Test time gap card generation."""
        cards = generate_time_gap_cards(self.events)
        
        # Should generate gap cards between consecutive events
        self.assertTrue(len(cards) > 0)
        
        # Check format
        cards_text = '\n'.join(cards)
        self.assertIn('How many years between', cards_text)
        self.assertIn('years', cards_text)
        
        # Verify specific gap
        # Between 1492 and 1776 is 284 years
        self.assertIn('284', cards_text)
    
    def test_period_cards(self):
        """Test period grouping card generation."""
        # Add more events in same periods
        extended_input = """
1960 | JFK elected
1963 | JFK assassination
1969 | Moon landing
1969 | Woodstock
2001 | 9/11 attacks
2008 | Financial crisis
"""
        events = parse_timeline_input(extended_input)
        cards = generate_period_cards(events)
        
        # Should generate cards for periods with multiple events
        self.assertTrue(len(cards) > 0)
        
        # Check format
        cards_text = '\n'.join(cards)
        self.assertIn('What events happened in the', cards_text)
        self.assertIn('1960s', cards_text)
    
    def test_generate_timeline_cards_all_types(self):
        """Test generating all card types."""
        output = generate_timeline_cards(
            self.sample_input,
            absolute=True,
            relative=True,
            sequence=True,
            gaps=True,
            periods=True
        )
        
        # Should contain all card type headers
        self.assertIn('# Absolute Date Cards', output)
        self.assertIn('# Relative Timing Cards', output)
        self.assertIn('# Sequence Ordering Cards', output)
        self.assertIn('# Time Gap Cards', output)
        
        # Should contain actual cards
        self.assertIn('Columbus discovers America', output)
        self.assertIn('1776', output)
    
    def test_generate_timeline_cards_selective(self):
        """Test generating only specific card types."""
        # Only absolute cards
        output = generate_timeline_cards(
            self.sample_input,
            absolute=True,
            relative=False,
            sequence=False,
            gaps=False,
            periods=False
        )
        
        self.assertIn('# Absolute Date Cards', output)
        self.assertNotIn('# Relative Timing Cards', output)
        self.assertNotIn('# Sequence Ordering Cards', output)
    
    def test_empty_input(self):
        """Test handling of empty input."""
        output = generate_timeline_cards('')
        self.assertIn('No timeline events found', output)
    
    def test_bce_dates(self):
        """Test handling of BCE dates."""
        bce_input = """
753 BCE | Founding of Rome
509 BCE | Roman Republic established
44 BCE | Julius Caesar assassinated
476 CE | Fall of Western Roman Empire
"""
        events = parse_timeline_input(bce_input)
        
        # Should be sorted correctly (BCE dates before CE)
        self.assertEqual(events[0][0], '753 BCE')
        self.assertEqual(events[-1][0], '476 CE')
        
        # Generate cards
        cards = generate_absolute_date_cards(events)
        self.assertTrue(len(cards) > 0)
        self.assertIn('753 BCE', '\n'.join(cards))


if __name__ == '__main__':
    unittest.main()