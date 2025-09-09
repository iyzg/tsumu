#!/usr/bin/env python3
"""
Integration tests for the unified Anki CLI.

Run with:
    python -m unittest test_cli_integration.py
"""

import unittest
import subprocess
import tempfile
import os
import csv
from pathlib import Path


class TestAnkiCLI(unittest.TestCase):
    """Integration tests for anki.py unified CLI."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.cli_path = Path(__file__).parent / 'anki.py'
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def run_cli(self, command, input_text=None):
        """Helper to run CLI commands."""
        cmd = ['python', str(self.cli_path)] + command.split()
        
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result
    
    def test_help_command(self):
        """Test that help command works."""
        result = self.run_cli('--help')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Unified Anki flashcard generation toolkit', result.stdout)
        self.assertIn('csv', result.stdout)
        self.assertIn('mnemonic', result.stdout)
    
    def test_markdown_conversion(self):
        """Test markdown to flashcard conversion."""
        markdown_text = """## Python Lists

Definition: Ordered, mutable sequences

Q: What is a list?
A: An ordered collection of items

```python
my_list = [1, 2, 3]
```
"""
        
        output_file = Path(self.test_dir) / 'cards.csv'
        result = self.run_cli(f'markdown -- -o {output_file}', markdown_text)
        
        self.assertEqual(result.returncode, 0)
        self.assertTrue(output_file.exists())
        
        # Check output content
        with open(output_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            cards = list(reader)
            self.assertGreater(len(cards), 0)
    
    def test_mnemonic_sequence(self):
        """Test mnemonic sequence generation."""
        items = "Monday\nTuesday\nWednesday"
        
        result = self.run_cli('mnemonic -- -t sequence -c day', items)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('What day was 1st?', result.stdout)
        self.assertIn('Monday', result.stdout)
        self.assertIn('What day came after Monday?', result.stdout)
    
    def test_cloze_generation(self):
        """Test cloze deletion generation."""
        text = "The quick brown fox jumps over the lazy dog."
        
        result = self.run_cli('cloze -- --mode basic', text)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('{{c1::', result.stdout)
        self.assertIn('quick', result.stdout)
    
    def test_fact_conversion(self):
        """Test fact to cards conversion."""
        fact = """Term: CPU
Definition: Central Processing Unit
Function: Executes program instructions"""
        
        result = self.run_cli('fact -- -t basic', fact)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('<b>CPU</b>', result.stdout)
        self.assertIn('Definition?', result.stdout)
        self.assertIn('Central Processing Unit', result.stdout)
    
    def test_invalid_command(self):
        """Test handling of invalid command."""
        result = self.run_cli('nonexistent')
        
        # Should show help or error
        self.assertNotEqual(result.returncode, 0)
    
    def test_piping_between_commands(self):
        """Test that output can be piped to other commands."""
        # Generate some cards and count lines
        text = "Test sentence one. Test sentence two."
        
        # Run cloze generator
        result = self.run_cli('cloze -- --mode sentence', text)
        
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().split('\n')
        # Should have header + 2 sentence cards
        self.assertEqual(len(lines), 3)
    
    def test_mnemonic_acronym(self):
        """Test mnemonic acronym generation."""
        items = "Red\nOrange\nYellow"
        
        result = self.run_cli('mnemonic -- -t acronym', items)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('ROY', result.stdout)
        self.assertIn('What is the acronym', result.stdout)
    
    def test_csv_formatter_passthrough(self):
        """Test CSV formatter works through CLI."""
        csv_content = "Front,Back\nQuestion 1,Answer 1"
        
        result = self.run_cli('csv -- -d ,', csv_content)
        
        self.assertEqual(result.returncode, 0)
        # Should have tab-separated output
        self.assertIn('Question 1\tAnswer 1', result.stdout)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in the CLI."""
    
    def setUp(self):
        self.cli_path = Path(__file__).parent / 'anki.py'
    
    def run_cli(self, command, input_text=None):
        """Helper to run CLI commands."""
        cmd = ['python', str(self.cli_path)] + command.split()
        
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result
    
    def test_empty_input(self):
        """Test handling of empty input."""
        result = self.run_cli('markdown --', '')
        
        # Should handle gracefully
        self.assertEqual(result.returncode, 0)
    
    def test_malformed_fact(self):
        """Test handling of malformed fact input."""
        bad_fact = "This is not a properly formatted fact"
        
        result = self.run_cli('fact -- -t basic', bad_fact)
        
        # Should still complete, possibly with no output
        self.assertEqual(result.returncode, 0)


def run_tests():
    """Run all integration tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAnkiCLI))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == '__main__':
    run_tests()