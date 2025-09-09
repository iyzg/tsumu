#!/usr/bin/env python3
"""
test suite for incremental reading processor
"""

import unittest
import sys
from io import StringIO
from incremental_reading import IncrementalReadingProcessor


class TestIncrementalReading(unittest.TestCase):
    """test incremental reading card generation"""
    
    def setUp(self):
        """set up test fixtures"""
        self.processor = IncrementalReadingProcessor()
        
        # sample texts
        self.short_text = "This is a short text for testing."
        
        self.long_text = """
        The history of computing began long before the modern computer.
        Early humans used tally sticks and abacuses for calculation.
        The mechanical age brought devices like the Pascaline and Difference Engine.
        Electronic computers emerged in the 20th century, starting with ENIAC.
        Personal computers revolutionized society in the 1980s.
        The internet connected the world in the 1990s.
        Mobile computing and smartphones changed everything in the 2000s.
        Today, artificial intelligence is transforming how we interact with technology.
        """
        
        self.paragraph_text = """
        First paragraph discusses the introduction of the topic.
        It sets the stage for what's to come.
        
        Second paragraph delves deeper into the details.
        More information is provided here.
        
        Third paragraph concludes the discussion.
        Final thoughts are presented.
        """
    
    def test_chunk_by_words(self):
        """test word-based chunking"""
        processor = IncrementalReadingProcessor(chunk_size=10, overlap=2, chunk_type='words')
        chunks = processor.chunk_text(self.long_text)
        
        self.assertGreater(len(chunks), 1)
        # verify chunks have correct size (except possibly the last one)
        words_in_first = len(chunks[0].split())
        self.assertLessEqual(words_in_first, 10)
    
    def test_chunk_by_sentences(self):
        """test sentence-based chunking"""
        processor = IncrementalReadingProcessor(chunk_size=2, overlap=1, chunk_type='sentences')
        chunks = processor.chunk_text(self.long_text)
        
        self.assertGreater(len(chunks), 1)
        # verify overlap exists
        if len(chunks) > 1:
            # check that chunks share some content due to overlap
            self.assertTrue(any(sentence in chunks[1] for sentence in chunks[0].split('.')[-2:]))
    
    def test_chunk_by_paragraphs(self):
        """test paragraph-based chunking"""
        processor = IncrementalReadingProcessor(chunk_type='paragraphs')
        chunks = processor.chunk_text(self.paragraph_text)
        
        self.assertEqual(len(chunks), 3)
        self.assertIn("First paragraph", chunks[0])
        self.assertIn("Second paragraph", chunks[1])
        self.assertIn("Third paragraph", chunks[2])
    
    def test_difficulty_calculation(self):
        """test text difficulty scoring"""
        processor = IncrementalReadingProcessor()
        
        simple = "cat dog run"
        complex = "pharmaceutical biotechnology infrastructure"
        
        simple_score = processor.calculate_difficulty(simple)
        complex_score = processor.calculate_difficulty(complex)
        
        self.assertLess(simple_score, complex_score)
        self.assertGreaterEqual(simple_score, 0)
        self.assertLessEqual(complex_score, 1)
    
    def test_generate_chunk_cards(self):
        """test card generation from chunks"""
        processor = IncrementalReadingProcessor(chunk_size=30, overlap=5)
        chunks = processor.chunk_text(self.long_text)
        cards = processor.generate_chunk_cards(chunks)
        
        # verify card types are generated
        card_types = [card[2] for card in cards]
        self.assertIn("reading", card_types)
        self.assertIn("continuation", card_types)
        self.assertIn("summary", card_types)
        self.assertIn("connection", card_types)
        
        # verify we have cards for each chunk
        reading_cards = [c for c in cards if c[2] == "reading"]
        self.assertEqual(len(reading_cards), len(chunks))
    
    def test_no_summaries_option(self):
        """test disabling summary cards"""
        processor = IncrementalReadingProcessor(
            chunk_size=30, 
            add_summaries=False
        )
        chunks = processor.chunk_text(self.long_text)
        cards = processor.generate_chunk_cards(chunks)
        
        card_types = [card[2] for card in cards]
        self.assertNotIn("summary", card_types)
    
    def test_no_connections_option(self):
        """test disabling connection cards"""
        processor = IncrementalReadingProcessor(
            chunk_size=30,
            add_connections=False
        )
        chunks = processor.chunk_text(self.long_text)
        cards = processor.generate_chunk_cards(chunks)
        
        card_types = [card[2] for card in cards]
        self.assertNotIn("connection", card_types)
    
    def test_difficulty_progression(self):
        """test difficulty-based ordering"""
        # create text with clear difficulty progression
        mixed_text = """
        Simple words here. Cat dog run.
        Intermediate vocabulary appears subsequently.
        Sophisticated terminology encompasses multifaceted concepts.
        Easy text again. Sun moon star.
        """
        
        processor = IncrementalReadingProcessor(
            chunk_size=10,
            overlap=0,
            difficulty_progression=True
        )
        
        chunks = processor.chunk_text(mixed_text)
        cards = processor.generate_chunk_cards(chunks)
        
        # verify cards were generated
        self.assertGreater(len(cards), 0)
        
        # get all reading cards
        reading_cards = [c for c in cards if c[2] == "reading"]
        self.assertGreater(len(reading_cards), 1)
        
        # verify that simpler content appears in earlier cards than complex content
        first_card_text = reading_cards[0][1].lower()
        last_card_text = reading_cards[-1][1].lower() if len(reading_cards) > 1 else ""
        
        # at least one simple word should be in the earlier cards
        simple_words = ["simple", "easy", "cat", "dog", "run", "sun", "moon", "star"]
        complex_words = ["sophisticated", "terminology", "encompasses", "multifaceted"]
        
        # check that at least one simple word appears early
        has_simple_early = any(word in first_card_text for word in simple_words)
        
        # or that complex words appear later
        has_complex_late = any(word in last_card_text for word in complex_words)
        
        self.assertTrue(has_simple_early or has_complex_late)
    
    def test_process_empty_text(self):
        """test processing empty or whitespace text"""
        processor = IncrementalReadingProcessor()
        
        self.assertEqual(processor.process(""), [])
        self.assertEqual(processor.process("   \n\n   "), [])
    
    def test_process_short_text(self):
        """test processing text shorter than chunk size"""
        processor = IncrementalReadingProcessor(chunk_size=100)
        cards = processor.process(self.short_text)
        
        # should still generate at least one reading card
        self.assertGreater(len(cards), 0)
        reading_cards = [c for c in cards if c[2] == "reading"]
        self.assertEqual(len(reading_cards), 1)
    
    def test_continuation_cards(self):
        """test continuation card generation"""
        processor = IncrementalReadingProcessor(chunk_size=30, overlap=5)
        chunks = processor.chunk_text(self.long_text)
        cards = processor.generate_chunk_cards(chunks)
        
        # find continuation cards
        continuation_cards = [c for c in cards if c[2] == "continuation"]
        
        # should have one less continuation card than chunks
        self.assertEqual(len(continuation_cards), len(chunks) - 1)
        
        # verify format
        for card in continuation_cards:
            self.assertIn("After:", card[0])
            self.assertIn("what comes next?", card[0])
    
    def test_overview_cards(self):
        """test generation of overview cards for multiple chunks"""
        processor = IncrementalReadingProcessor(chunk_size=30)
        chunks = processor.chunk_text(self.long_text)
        cards = processor.generate_chunk_cards(chunks)
        
        # find overview cards
        sequence_cards = [c for c in cards if c[2] == "sequence"]
        theme_cards = [c for c in cards if c[2] == "theme"]
        
        # should have overview cards if more than 2 chunks
        if len(chunks) > 2:
            self.assertEqual(len(sequence_cards), 1)
            self.assertEqual(len(theme_cards), 1)
    
    def test_chunk_overlap(self):
        """test that overlap works correctly"""
        processor = IncrementalReadingProcessor(
            chunk_size=20,
            overlap=5,
            chunk_type='words'
        )
        
        text = " ".join([f"word{i}" for i in range(50)])
        chunks = processor.chunk_text(text)
        
        # verify overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            current_words = chunks[i].split()
            next_words = chunks[i + 1].split()
            
            # last words of current should appear in next
            if len(current_words) >= 5:
                overlap_words = current_words[-5:]
                for word in overlap_words:
                    self.assertIn(word, next_words)


def run_tests():
    """run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()