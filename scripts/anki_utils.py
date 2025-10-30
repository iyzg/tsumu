#!/usr/bin/env python3
"""
Comprehensive utilities for Anki card generation scripts.

Provides formatting, I/O, parsing, and card generation utilities.
"""

import re
import csv
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, TextIO, Any, Optional, Union


# ============================================================================
# Formatting Utilities
# ============================================================================

class AnkiFormatter:
    """Formatting utilities for Anki cards."""

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


# ============================================================================
# Input/Output Handlers
# ============================================================================

class InputHandler:
    """Standardized input handling."""

    @staticmethod
    def get_input(source: Optional[Union[str, Path]] = None,
                  encoding: str = 'utf-8') -> str:
        """Get input text from file or stdin."""
        if source:
            path = Path(source) if not isinstance(source, Path) else source
            if not path.exists():
                raise FileNotFoundError(f"Input file not found: {path}")
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        else:
            return sys.stdin.read()

    @staticmethod
    def get_lines(source: Optional[Union[str, Path]] = None,
                  skip_empty: bool = True,
                  strip: bool = True) -> List[str]:
        """Get input as list of lines."""
        text = InputHandler.get_input(source)
        lines = text.splitlines()

        if strip:
            lines = [line.strip() for line in lines]

        if skip_empty:
            lines = [line for line in lines if line]

        return lines


class OutputHandler:
    """Standardized output handling."""

    @staticmethod
    def get_output_file(path: Optional[Union[str, Path]] = None,
                        mode: str = 'w',
                        encoding: str = 'utf-8') -> TextIO:
        """Get output file handle."""
        if path:
            output_path = Path(path) if not isinstance(path, Path) else path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            return open(output_path, mode, encoding=encoding, newline='')
        else:
            return sys.stdout

    @staticmethod
    def write_cards(cards: List[Tuple[str, ...]],
                   output: Optional[Union[str, Path, TextIO]] = None,
                   delimiter: str = '\t',
                   add_header: bool = False,
                   header: Optional[List[str]] = None,
                   verbose: bool = True) -> None:
        """Write cards to CSV format for Anki import."""
        # Handle both file paths and file objects
        if isinstance(output, (str, Path)):
            output_file = OutputHandler.get_output_file(output)
            should_close = True
        elif hasattr(output, 'write'):
            output_file = output
            should_close = False
        else:
            output_file = sys.stdout
            should_close = False

        try:
            writer = csv.writer(output_file, delimiter=delimiter,
                              quoting=csv.QUOTE_MINIMAL)

            if add_header and header:
                writer.writerow(header)

            for card in cards:
                writer.writerow(card)

            if verbose and isinstance(output, (str, Path)):
                print(f"Wrote {len(cards)} cards to {output}", file=sys.stderr)

        finally:
            if should_close:
                output_file.close()

    @staticmethod
    def write_csv(cards: List[Tuple[str, ...]], output: TextIO,
                  delimiter: str = '\t', add_header: bool = False,
                  header: Optional[List[str]] = None) -> None:
        """Write cards to CSV format (legacy method)."""
        writer = csv.writer(output, delimiter=delimiter,
                           quoting=csv.QUOTE_MINIMAL)

        if add_header and header:
            writer.writerow(header)

        for card in cards:
            writer.writerow(card)

    @staticmethod
    def write_cloze_csv(cards: List[str], output: TextIO) -> None:
        """Write cloze deletion cards to CSV (legacy method)."""
        writer = csv.writer(output, delimiter='\t')
        writer.writerow(['Text'])  # Header for Anki cloze type
        for card in cards:
            writer.writerow([card])


# ============================================================================
# Text Parsing Utilities
# ============================================================================

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


# ============================================================================
# Cloze Deletion Utilities
# ============================================================================

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


# ============================================================================
# Card Validation & Formatting
# ============================================================================

class CardFormatter:
    """Card formatting and validation utilities."""

    @staticmethod
    def format_card_count(count: int, card_type: str = "card") -> str:
        """Format card count message."""
        plural = "s" if count != 1 else ""
        return f"{count} {card_type}{plural}"

    @staticmethod
    def truncate_text(text: str, max_length: int = 100,
                     suffix: str = "...") -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def validate_cards(cards: List[Tuple],
                      min_fields: int = 2) -> List[Tuple]:
        """Validate and filter cards."""
        valid_cards = []

        for card in cards:
            if len(card) >= min_fields:
                # Check that fields aren't empty
                if all(field and str(field).strip() for field in card[:min_fields]):
                    valid_cards.append(card)

        return valid_cards


# ============================================================================
# Argument Parser Utilities
# ============================================================================

class ArgumentParser:
    """Common argument parser patterns."""

    @staticmethod
    def create_basic_parser(description: str,
                           epilog: Optional[str] = None) -> argparse.ArgumentParser:
        """Create basic argument parser with common options."""
        parser = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog
        )

        parser.add_argument('input', nargs='?', type=str,
                          help='Input file (or use stdin)')
        parser.add_argument('-o', '--output', type=str,
                          help='Output CSV file (default: stdout)')
        parser.add_argument('-v', '--verbose', action='store_true',
                          help='Verbose output')
        parser.add_argument('--delimiter', type=str, default='\t',
                          help='CSV delimiter (default: tab)')

        return parser

    @staticmethod
    def add_format_options(parser: argparse.ArgumentParser) -> None:
        """Add common formatting options to parser."""
        parser.add_argument('--no-html', action='store_true',
                          help='Disable HTML formatting')
        parser.add_argument('--preserve-newlines', action='store_true',
                          help='Preserve newlines in output')
        parser.add_argument('--escape-latex', action='store_true',
                          help='Escape LaTeX math notation')

    @staticmethod
    def add_filter_options(parser: argparse.ArgumentParser) -> None:
        """Add common filtering options to parser."""
        parser.add_argument('--max-cards', type=int,
                          help='Maximum number of cards to generate')
        parser.add_argument('--min-length', type=int,
                          help='Minimum text length for cards')
        parser.add_argument('--max-length', type=int,
                          help='Maximum text length for cards')


# ============================================================================
# Legacy Compatibility Aliases
# ============================================================================

# Keep old class names for backward compatibility
AnkiWriter = OutputHandler
create_argument_parser = ArgumentParser.create_basic_parser

# Convenience functions
def read_input(input_file: Optional[str] = None) -> str:
    """Read input from file or stdin (legacy function)."""
    return InputHandler.get_input(input_file)


def write_output(cards: List[Tuple], output_file: Optional[str] = None,
                delimiter: str = '\t') -> None:
    """Write cards to output (legacy function)."""
    OutputHandler.write_cards(cards, output_file, delimiter, verbose=False)


def format_card(front: str, back: str, separator: str = '\t') -> str:
    """Format a card as tab-separated values."""
    return f"{front}{separator}{back}"


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add common arguments to a parser (legacy function)."""
    parser.add_argument('--separator', default='---',
                       help='Card separator (default: ---)')


def check_input_not_empty(text: str, context: str = "input") -> None:
    """Validate that input text is not empty.

    Args:
        text: Input text to validate
        context: Description of input for error message

    Raises:
        ValueError: If text is empty or only whitespace
    """
    if not text or not text.strip():
        raise ValueError(f"Error: no {context} provided")


def validate_args(args: Any, required_attrs: List[str]) -> None:
    """Validate that required argument attributes are present.

    Args:
        args: Parsed arguments object
        required_attrs: List of required attribute names

    Raises:
        ValueError: If any required attribute is missing or None
    """
    for attr in required_attrs:
        if not hasattr(args, attr) or getattr(args, attr) is None:
            raise ValueError(f"Error: required argument '{attr}' is missing")
