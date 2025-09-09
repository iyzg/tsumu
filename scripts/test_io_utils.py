#!/usr/bin/env python3
"""
test suite for io utilities
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
import sys
import io

from io_utils import (
    InputHandler, OutputHandler, ArgumentParser, 
    CardFormatter, read_input, write_output
)


class TestInputHandler(unittest.TestCase):
    """test input handling utilities"""
    
    def test_get_input_from_file(self):
        """test reading from file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content\nline 2")
            temp_path = f.name
        
        try:
            content = InputHandler.get_input(temp_path)
            self.assertEqual(content, "test content\nline 2")
        finally:
            os.unlink(temp_path)
    
    def test_get_input_from_stdin(self):
        """test reading from stdin"""
        with patch('sys.stdin', io.StringIO("stdin content")):
            content = InputHandler.get_input(None)
            self.assertEqual(content, "stdin content")
    
    def test_get_lines_skip_empty(self):
        """test getting lines with empty line skipping"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("line1\n\nline2\n  \nline3")
            temp_path = f.name
        
        try:
            lines = InputHandler.get_lines(temp_path, skip_empty=True)
            self.assertEqual(lines, ["line1", "line2", "line3"])
        finally:
            os.unlink(temp_path)
    
    def test_get_lines_no_strip(self):
        """test getting lines without stripping"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("  line1  \nline2")
            temp_path = f.name
        
        try:
            lines = InputHandler.get_lines(temp_path, strip=False)
            self.assertEqual(lines, ["  line1  ", "line2"])
        finally:
            os.unlink(temp_path)


class TestOutputHandler(unittest.TestCase):
    """test output handling utilities"""
    
    def test_get_output_file_stdout(self):
        """test getting stdout as output"""
        output = OutputHandler.get_output_file(None)
        self.assertEqual(output, sys.stdout)
    
    def test_get_output_file_path(self):
        """test getting file handle for path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.csv"
            handle = OutputHandler.get_output_file(output_path)
            self.assertIsNotNone(handle)
            handle.write("test")
            handle.close()
            self.assertTrue(output_path.exists())
    
    def test_write_cards_to_file(self):
        """test writing cards to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "cards.csv"
            cards = [("q1", "a1"), ("q2", "a2")]
            
            OutputHandler.write_cards(cards, output_path, verbose=False)
            
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn("q1\ta1", content)
                self.assertIn("q2\ta2", content)
    
    def test_write_cards_with_header(self):
        """test writing cards with header"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "cards.csv"
            cards = [("q1", "a1")]
            
            OutputHandler.write_cards(
                cards, output_path, 
                add_header=True, 
                header=["Question", "Answer"],
                verbose=False
            )
            
            with open(output_path, 'r') as f:
                lines = f.readlines()
                self.assertIn("Question\tAnswer", lines[0])


class TestArgumentParser(unittest.TestCase):
    """test argument parser utilities"""
    
    def test_create_basic_parser(self):
        """test creating basic parser"""
        parser = ArgumentParser.create_basic_parser("test description")
        
        # test with basic args
        args = parser.parse_args(["input.txt", "-o", "output.csv"])
        self.assertEqual(args.input, "input.txt")
        self.assertEqual(args.output, "output.csv")
    
    def test_add_format_options(self):
        """test adding format options"""
        parser = ArgumentParser.create_basic_parser("test")
        ArgumentParser.add_format_options(parser)
        
        args = parser.parse_args(["--no-html", "--preserve-newlines"])
        self.assertTrue(args.no_html)
        self.assertTrue(args.preserve_newlines)
    
    def test_add_filter_options(self):
        """test adding filter options"""
        parser = ArgumentParser.create_basic_parser("test")
        ArgumentParser.add_filter_options(parser)
        
        args = parser.parse_args(["--max-cards", "10", "--min-length", "5"])
        self.assertEqual(args.max_cards, 10)
        self.assertEqual(args.min_length, 5)


class TestCardFormatter(unittest.TestCase):
    """test card formatting utilities"""
    
    def test_format_card_count(self):
        """test formatting card count messages"""
        self.assertEqual(CardFormatter.format_card_count(1), "1 card")
        self.assertEqual(CardFormatter.format_card_count(2), "2 cards")
        self.assertEqual(CardFormatter.format_card_count(0, "item"), "0 items")
    
    def test_truncate_text(self):
        """test text truncation"""
        long_text = "a" * 150
        truncated = CardFormatter.truncate_text(long_text, max_length=100)
        self.assertEqual(len(truncated), 100)
        self.assertTrue(truncated.endswith("..."))
        
        short_text = "short"
        self.assertEqual(CardFormatter.truncate_text(short_text, 100), "short")
    
    def test_validate_cards(self):
        """test card validation"""
        cards = [
            ("q1", "a1"),
            ("q2", ""),  # empty answer
            ("q3", "a3", "extra"),
            ("",),  # not enough fields
            ("q4", "a4")
        ]
        
        valid = CardFormatter.validate_cards(cards)
        self.assertEqual(len(valid), 3)
        self.assertIn(("q1", "a1"), valid)
        self.assertIn(("q3", "a3", "extra"), valid)
        self.assertIn(("q4", "a4"), valid)


class TestBackwardCompatibility(unittest.TestCase):
    """test backward compatibility functions"""
    
    def test_read_input(self):
        """test backward compatible read_input"""
        with patch('sys.stdin', io.StringIO("test input")):
            content = read_input()
            self.assertEqual(content, "test input")
    
    def test_write_output(self):
        """test backward compatible write_output"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test.csv")
            cards = [("q", "a")]
            
            write_output(cards, output_path)
            
            with open(output_path, 'r') as f:
                self.assertIn("q\ta", f.read())


if __name__ == '__main__':
    unittest.main()