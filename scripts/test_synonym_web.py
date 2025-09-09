#!/usr/bin/env python3
"""
test suite for synonym web generator
"""

import unittest
import sys
import io
from unittest.mock import patch, MagicMock
from synonym_web import SynonymWeb


class TestSynonymWeb(unittest.TestCase):
    """test synonym web card generation"""
    
    def setUp(self):
        """set up test fixtures"""
        self.web = SynonymWeb(use_wordnet=False)
    
    def test_get_synonyms_basic(self):
        """test getting synonyms from basic data"""
        synonyms = self.web.get_synonyms('happy')
        self.assertIn('joyful', synonyms)
        self.assertIn('cheerful', synonyms)
        self.assertTrue(len(synonyms) <= 5)
    
    def test_get_antonyms_basic(self):
        """test getting antonyms from basic data"""
        antonyms = self.web.get_antonyms('happy')
        self.assertIn('sad', antonyms)
        self.assertTrue(len(antonyms) <= 3)
    
    def test_no_synonyms_for_unknown_word(self):
        """test that unknown words return empty list"""
        synonyms = self.web.get_synonyms('xyzabc')
        self.assertEqual(synonyms, [])
    
    def test_generate_synonym_card(self):
        """test synonym card generation"""
        card = self.web.generate_synonym_card('happy', ['joyful', 'cheerful'])
        self.assertIsNotNone(card)
        self.assertIn('synonym', card['question'].lower())
        self.assertIn('happy', card['question'])
        self.assertIn('joyful', card['answer'])
    
    def test_generate_antonym_card(self):
        """test antonym card generation"""
        card = self.web.generate_antonym_card('happy', ['sad', 'unhappy'])
        self.assertIsNotNone(card)
        self.assertIn('antonym', card['question'].lower())
        self.assertIn('sad', card['answer'])
    
    def test_generate_starts_with_card(self):
        """test starts-with card generation"""
        card = self.web.generate_starts_with_card('happy', ['joyful', 'jubilant', 'cheerful'])
        self.assertIsNotNone(card)
        self.assertIn('starts with', card['question'].lower())
    
    def test_generate_context_card(self):
        """test context fill-in card generation"""
        card = self.web.generate_context_card('happy', ['joyful', 'cheerful'])
        self.assertIsNotNone(card)
        self.assertIn('Fill in the blank', card['question'])
        self.assertIn('___', card['question'])
    
    def test_generate_odd_one_out_card(self):
        """test odd-one-out card generation"""
        card = self.web.generate_odd_one_out_card(
            'happy', 
            ['joyful', 'cheerful', 'pleased'],
            ['sad']
        )
        self.assertIsNotNone(card)
        self.assertIn('NOT a synonym', card['question'])
        self.assertEqual(card['answer'], 'sad')
    
    def test_generate_web_cards(self):
        """test generating multiple card types"""
        cards = self.web.generate_web_cards('happy', depth=1)
        self.assertGreater(len(cards), 0)
        
        # check that different card types are present
        questions = [card['question'] for card in cards]
        has_synonym = any('synonym' in q.lower() for q in questions)
        has_antonym = any('antonym' in q.lower() for q in questions)
        self.assertTrue(has_synonym or has_antonym)
    
    def test_depth_generation(self):
        """test that depth > 1 generates more cards"""
        cards_depth1 = self.web.generate_web_cards('happy', depth=1)
        cards_depth2 = self.web.generate_web_cards('happy', depth=2)
        # depth 2 should generate at least as many cards
        self.assertGreaterEqual(len(cards_depth2), len(cards_depth1))
    
    def test_card_type_filtering(self):
        """test that only requested card types are generated"""
        cards = self.web.generate_web_cards('happy', card_types=['synonym'])
        for card in cards:
            # all cards should be synonym-related
            self.assertIn('synonym', card['question'].lower())
    
    def test_empty_input_handling(self):
        """test handling of words with no relationships"""
        cards = self.web.generate_web_cards('xyzabc')
        # should return empty list for unknown word
        self.assertEqual(cards, [])


if __name__ == '__main__':
    unittest.main()