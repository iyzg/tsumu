#!/usr/bin/env python3
"""
Tests for batch processor and preview tools.

Run with:
    python -m unittest test_batch_preview.py
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from batch_processor import BatchProcessor
from preview_cards import CardPreview, load_cards
from cli_utils import CLIBase, ProgressTracker, create_safe_filename


class TestBatchProcessor(unittest.TestCase):
    """Test batch processing functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.processor = BatchProcessor(output_dir=self.test_dir)
        
        # Create test files
        self.test_markdown = Path(self.test_dir) / 'test.md'
        self.test_markdown.write_text("""# Test Notes

## Definition
Python: A high-level programming language

Q: What is Python?
A: A high-level programming language
""")
        
        self.test_fact = Path(self.test_dir) / 'facts.txt'
        self.test_fact.write_text("""Term: CPU
Definition: Central Processing Unit
Function: Executes instructions
""")
    
    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_process_single_file(self):
        """Test processing a single file."""
        result = self.processor.process_file(
            self.test_markdown,
            'markdown'
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['converter'], 'markdown')
        self.assertIsNotNone(result['output'])
        self.assertGreater(result['card_count'], 0)
    
    def test_process_directory(self):
        """Test processing all files in a directory."""
        results = self.processor.process_directory(
            Path(self.test_dir),
            pattern='*.md',
            converter_type='markdown'
        )
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'success')
    
    def test_invalid_converter(self):
        """Test handling of invalid converter type."""
        result = self.processor.process_file(
            self.test_markdown,
            'invalid_type'
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Unknown converter', result['error'])
    
    def test_merge_outputs(self):
        """Test merging multiple outputs."""
        # Process multiple files
        self.processor.process_file(self.test_markdown, 'markdown')
        self.processor.process_file(self.test_fact, 'fact')
        
        # Merge outputs
        merged_file = Path(self.test_dir) / 'merged.csv'
        self.processor.merge_outputs(merged_file)
        
        self.assertTrue(merged_file.exists())


class TestCardPreview(unittest.TestCase):
    """Test card preview functionality."""
    
    def setUp(self):
        """Set up test cards."""
        self.cards = [
            {'front': 'What is Python?', 'back': 'A programming language'},
            {'front': '{{c1::Python}} is a language', 'back': 'Python is a language'},
            {'front': 'Math: \\(x^2\\)', 'back': 'x squared'},
        ]
        self.previewer = CardPreview(self.cards)
    
    def test_format_card_text(self):
        """Test card text formatting."""
        # Test HTML removal
        text = '<b>Bold</b> text'
        formatted = self.previewer.format_card_text(text)
        self.assertEqual(formatted, 'Bold text')
        
        # Test cloze formatting
        text = '{{c1::answer}}'
        formatted = self.previewer.format_card_text(text)
        self.assertEqual(formatted, '[...answer...]')
        
        # Test LaTeX formatting
        text = '\\(x^2\\)'
        formatted = self.previewer.format_card_text(text)
        self.assertEqual(formatted, '[x^2]')
    
    def test_get_statistics(self):
        """Test statistics calculation."""
        stats = self.previewer.get_statistics()
        
        self.assertEqual(stats['total'], 3)
        self.assertIn('Cloze', stats['types'])
        self.assertIn('Math', stats['types'])
        self.assertIn('Basic', stats['types'])
        self.assertGreater(stats['avg_front_length'], 0)
        self.assertGreater(stats['avg_back_length'], 0)
    
    def test_preview_text(self):
        """Test text preview generation."""
        preview = self.previewer.preview_text(max_cards=2)
        
        self.assertIn('Card #1', preview)
        self.assertIn('Card #2', preview)
        self.assertIn('and 1 more cards', preview)
        self.assertIn('What is Python?', preview)
    
    def test_preview_html(self):
        """Test HTML preview generation."""
        html = self.previewer.preview_html()
        
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('Card #1', html)
        self.assertIn('Statistics', html)
        self.assertIn('MathJax', html)  # Should include MathJax for LaTeX
    
    def test_preview_markdown(self):
        """Test Markdown preview generation."""
        markdown = self.previewer.preview_markdown()
        
        self.assertIn('# Anki Card Preview', markdown)
        self.assertIn('## Statistics', markdown)
        self.assertIn('### Card #1', markdown)
        self.assertIn('**Front:**', markdown)


class TestCLIUtils(unittest.TestCase):
    """Test CLI utility functions."""
    
    def test_create_safe_filename(self):
        """Test safe filename creation."""
        # Test unsafe characters removal
        unsafe = 'file/with\\unsafe:chars*.txt'
        safe = create_safe_filename(unsafe)
        self.assertNotIn('/', safe)
        self.assertNotIn('\\', safe)
        self.assertNotIn(':', safe)
        self.assertNotIn('*', safe)
        
        # Test length limiting
        long_name = 'a' * 100
        safe = create_safe_filename(long_name, max_length=50)
        self.assertEqual(len(safe), 50)
        
        # Test empty string
        safe = create_safe_filename('')
        self.assertEqual(safe, 'output')
    
    def test_progress_tracker(self):
        """Test progress tracking."""
        tracker = ProgressTracker(10, "Testing")
        tracker.start()
        
        for _ in range(10):
            tracker.update(1)
        
        self.assertEqual(tracker.current, 10)
        self.assertEqual(tracker.total, 10)
    
    def test_cli_base(self):
        """Test CLI base class."""
        cli = CLIBase("Test CLI", "Test epilog")
        
        # Test argument setup
        self.assertIsNotNone(cli.parser)
        
        # Test custom argument addition
        cli.add_argument('--test', help='Test argument')
        args = cli.parse_args(['--test', 'value'])
        self.assertEqual(args.test, 'value')


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_workflow(self):
        """Test complete workflow from input to preview."""
        # Create test input
        input_file = Path(self.test_dir) / 'input.md'
        input_file.write_text("""# Test
        
Q: What is testing?
A: Verifying code works correctly
""")
        
        # Process with batch processor
        processor = BatchProcessor(output_dir=self.test_dir)
        result = processor.process_file(input_file, 'markdown')
        
        self.assertEqual(result['status'], 'success')
        
        # Load and preview the output
        output_file = Path(result['output'])
        self.assertTrue(output_file.exists())
        
        cards = load_cards(output_file)
        self.assertGreater(len(cards), 0)
        
        # Check if cards have expected content
        # The markdown processor may generate multiple cards
        # Check both possible column names
        has_testing_card = False
        for card in cards:
            # Check all possible keys since CSV headers vary
            text_to_check = ' '.join(str(v) for v in card.values()).lower()
            if 'testing' in text_to_check:
                has_testing_card = True
                break
        
        self.assertTrue(has_testing_card, f"No card contains 'testing'. First card keys: {list(cards[0].keys()) if cards else 'no cards'}")


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBatchProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestCardPreview))
    suite.addTests(loader.loadTestsFromTestCase(TestCLIUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())