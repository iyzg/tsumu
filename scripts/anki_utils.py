#!/usr/bin/env python3
"""
Shared utilities for Anki card generation scripts.
"""

import re
import csv
import sys
from typing import List, Tuple, TextIO, Any


class AnkiFormatter:
    """Common formatting utilities for Anki cards."""
    
    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML characters for Anki."""
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    @staticmethod
    def convert_latex(text: str) -> str:
        """Convert LaTeX notation for MathJax compatibility in Anki.
        
        Converts:
        - $$...$$ to \\[...\\] (display math)
        - $...$ to \\(...\\) (inline math)
        """
        # Convert display math
        text = re.sub(r'\$\$([^$]+)\$\$', r'\\[\1\\]', text)
        # Convert inline math
        text = re.sub(r'\$([^$]+)\$', r'\\(\1\\)', text)
        return text
    
    @staticmethod
    def format_newlines(text: str) -> str:
        """Convert newlines to HTML breaks for Anki."""
        return text.replace('\n', '<br>')
    
    @staticmethod
    def process_text(text: str, escape_html: bool = True, 
                    convert_latex: bool = True, 
                    format_newlines: bool = True) -> str:
        """Apply all formatting transformations to text."""
        if escape_html:
            text = AnkiFormatter.escape_html(text)
        if convert_latex:
            text = AnkiFormatter.convert_latex(text)
        if format_newlines:
            text = AnkiFormatter.format_newlines(text)
        return text


class AnkiWriter:
    """Utilities for writing Anki-compatible output."""
    
    @staticmethod
    def write_csv(cards: List[Tuple[str, ...]], output: TextIO, 
                  delimiter: str = '\t', add_header: bool = False,
                  header: List[str] = None) -> None:
        """Write cards to CSV format for Anki import.
        
        Args:
            cards: List of tuples representing card fields
            output: Output file handle
            delimiter: CSV delimiter (tab for Anki)
            add_header: Whether to add header row
            header: Custom header fields
        """
        writer = csv.writer(output, delimiter=delimiter, 
                           quoting=csv.QUOTE_MINIMAL)
        
        if add_header and header:
            writer.writerow(header)
        
        for card in cards:
            writer.writerow(card)
    
    @staticmethod
    def write_cloze_csv(cards: List[str], output: TextIO) -> None:
        """Write cloze deletion cards to CSV."""
        writer = csv.writer(output, delimiter='\t')
        writer.writerow(['Text'])  # Header for Anki cloze type
        for card in cards:
            writer.writerow([card])


class TextParser:
    """Utilities for parsing input text."""
    
    @staticmethod
    def extract_list_items(text: str) -> List[str]:
        """Extract list items from text, handling various formats."""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Remove common list markers
            line = re.sub(r'^[-•*]\s*', '', line)
            line = re.sub(r'^\d+[\.)]\s*', '', line)
            line = re.sub(r'^[a-zA-Z][\.)]\s*', '', line)  # Letter lists
            
            if line:
                items.append(line)
        
        return items
    
    @staticmethod
    def split_sentences(text: str) -> List[str]:
        """Split text into sentences."""
        # Split on sentence endings, but keep the punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def parse_key_value(text: str, delimiter: str = ':') -> List[Tuple[str, str]]:
        """Parse key-value pairs from text."""
        pairs = []
        lines = text.split('\n')
        
        for line in lines:
            if delimiter in line:
                parts = line.split(delimiter, 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if key and value:
                        pairs.append((key, value))
        
        return pairs
    
    @staticmethod
    def parse_structured_fact(text: str) -> dict:
        """Parse a structured fact with multi-line values."""
        lines = text.strip().split('\n')
        fact = {}
        current_key = None
        current_value = []
        
        for line in lines:
            # Check if line starts a new field
            if ':' in line and not line.startswith(' '):
                if current_key:
                    fact[current_key] = '\n'.join(current_value).strip()
                
                parts = line.split(':', 1)
                current_key = parts[0].strip().lower()
                current_value = [parts[1].strip()] if len(parts) > 1 else []
            else:
                # Continuation of previous field
                current_value.append(line.strip())
        
        # Don't forget the last field
        if current_key:
            fact[current_key] = '\n'.join(current_value).strip()
        
        return fact


class ClozeGenerator:
    """Utilities for generating cloze deletions."""
    
    @staticmethod
    def create_cloze(text: str, target: str, cloze_num: int = 1, 
                    case_sensitive: bool = False) -> str:
        """Create a single cloze deletion."""
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.escape(target)
        return re.sub(pattern, f"{{{{c{cloze_num}::{target}}}}}", 
                     text, flags=flags)
    
    @staticmethod
    def create_overlapping_cloze(text: str, targets: List[str]) -> str:
        """Create overlapping cloze deletions (all use c1)."""
        result = text
        for target in targets:
            result = ClozeGenerator.create_cloze(result, target, 1)
        return result
    
    @staticmethod
    def create_sequential_cloze(text: str, targets: List[str]) -> str:
        """Create sequential cloze deletions (c1, c2, c3...)."""
        result = text
        for i, target in enumerate(targets, 1):
            result = ClozeGenerator.create_cloze(result, target, i)
        return result


def create_argument_parser(description: str) -> Any:
    """Create a standard argument parser with common options."""
    import argparse
    
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        'input', nargs='?', type=argparse.FileType('r'), 
        default=sys.stdin,
        help='Input file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), 
        default=sys.stdout,
        help='Output file (default: stdout)'
    )
    
    return parser