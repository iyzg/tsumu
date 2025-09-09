#!/usr/bin/env python3
"""
common input/output utilities for anki card generators

provides consistent file handling, argument parsing helpers, and output formatting
across all card generation scripts.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, TextIO, List, Union
import csv


class InputHandler:
    """standardized input handling for all scripts"""
    
    @staticmethod
    def get_input(source: Optional[Union[str, Path]] = None, 
                  encoding: str = 'utf-8') -> str:
        """
        get input text from file or stdin
        
        args:
            source: file path or None for stdin
            encoding: text encoding (default: utf-8)
            
        returns:
            input text as string
        """
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
        """
        get input as list of lines
        
        args:
            source: file path or None for stdin
            skip_empty: skip empty lines
            strip: strip whitespace from lines
            
        returns:
            list of lines
        """
        text = InputHandler.get_input(source)
        lines = text.splitlines()
        
        if strip:
            lines = [line.strip() for line in lines]
        
        if skip_empty:
            lines = [line for line in lines if line]
        
        return lines


class OutputHandler:
    """standardized output handling for all scripts"""
    
    @staticmethod
    def get_output_file(path: Optional[Union[str, Path]] = None,
                        mode: str = 'w',
                        encoding: str = 'utf-8') -> TextIO:
        """
        get output file handle
        
        args:
            path: output file path or None for stdout
            mode: file open mode
            encoding: text encoding
            
        returns:
            file handle (stdout or opened file)
        """
        if path:
            output_path = Path(path) if not isinstance(path, Path) else path
            # create parent directories if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            return open(output_path, mode, encoding=encoding, newline='')
        else:
            return sys.stdout
    
    @staticmethod
    def write_cards(cards: List[tuple], 
                   output: Optional[Union[str, Path]] = None,
                   delimiter: str = '\t',
                   add_header: bool = False,
                   header: Optional[List[str]] = None,
                   verbose: bool = True) -> None:
        """
        write cards to csv format
        
        args:
            cards: list of card tuples
            output: output file path or None for stdout
            delimiter: csv delimiter (tab for anki)
            add_header: whether to add header row
            header: custom header fields
            verbose: print status messages
        """
        output_file = OutputHandler.get_output_file(output)
        
        try:
            writer = csv.writer(output_file, delimiter=delimiter, 
                              quoting=csv.QUOTE_MINIMAL)
            
            if add_header and header:
                writer.writerow(header)
            
            for card in cards:
                writer.writerow(card)
            
            if verbose and output:
                print(f"wrote {len(cards)} cards to {output}", file=sys.stderr)
        
        finally:
            if output:  # only close if we opened a file
                output_file.close()


class ArgumentParser:
    """common argument parser patterns for anki scripts"""
    
    @staticmethod
    def create_basic_parser(description: str, 
                           epilog: Optional[str] = None) -> argparse.ArgumentParser:
        """
        create basic argument parser with common options
        
        args:
            description: script description
            epilog: additional help text
            
        returns:
            configured argument parser
        """
        parser = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog
        )
        
        # common arguments
        parser.add_argument('input', nargs='?', type=str,
                          help='input file (or use stdin)')
        parser.add_argument('-o', '--output', type=str,
                          help='output csv file (default: stdout)')
        parser.add_argument('-v', '--verbose', action='store_true',
                          help='verbose output')
        parser.add_argument('--delimiter', type=str, default='\t',
                          help='csv delimiter (default: tab)')
        
        return parser
    
    @staticmethod
    def add_format_options(parser: argparse.ArgumentParser) -> None:
        """add common formatting options to parser"""
        parser.add_argument('--no-html', action='store_true',
                          help='disable html formatting')
        parser.add_argument('--preserve-newlines', action='store_true',
                          help='preserve newlines in output')
        parser.add_argument('--escape-latex', action='store_true',
                          help='escape latex math notation')
    
    @staticmethod
    def add_filter_options(parser: argparse.ArgumentParser) -> None:
        """add common filtering options to parser"""
        parser.add_argument('--max-cards', type=int,
                          help='maximum number of cards to generate')
        parser.add_argument('--min-length', type=int,
                          help='minimum text length for cards')
        parser.add_argument('--max-length', type=int,
                          help='maximum text length for cards')


class CardFormatter:
    """common card formatting utilities"""
    
    @staticmethod
    def format_card_count(count: int, card_type: str = "card") -> str:
        """
        format card count message
        
        args:
            count: number of cards
            card_type: type of cards (for pluralization)
            
        returns:
            formatted message
        """
        plural = "s" if count != 1 else ""
        return f"{count} {card_type}{plural}"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, 
                     suffix: str = "...") -> str:
        """
        truncate text to maximum length
        
        args:
            text: text to truncate
            max_length: maximum length
            suffix: suffix to add if truncated
            
        returns:
            truncated text
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def validate_cards(cards: List[tuple], 
                      min_fields: int = 2) -> List[tuple]:
        """
        validate and filter cards
        
        args:
            cards: list of card tuples
            min_fields: minimum required fields
            
        returns:
            filtered list of valid cards
        """
        valid_cards = []
        
        for card in cards:
            if len(card) >= min_fields:
                # check that fields aren't empty
                if all(field and str(field).strip() for field in card[:min_fields]):
                    valid_cards.append(card)
        
        return valid_cards


# convenience functions for backward compatibility
def read_input(input_file: Optional[str] = None) -> str:
    """read input from file or stdin (backward compatible)"""
    return InputHandler.get_input(input_file)


def write_output(cards: List[tuple], output_file: Optional[str] = None,
                delimiter: str = '\t') -> None:
    """write cards to output (backward compatible)"""
    OutputHandler.write_cards(cards, output_file, delimiter, verbose=False)


def format_card(front: str, back: str, separator: str = '\t') -> str:
    """format a card as tab-separated values"""
    return f"{front}{separator}{back}"


def create_argument_parser(prog_name: str, description: str) -> argparse.ArgumentParser:
    """create a standard argument parser"""
    return ArgumentParser.create_basic_parser(description)


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """add common arguments to a parser"""
    parser.add_argument('--separator', default='---',
                       help='card separator (default: ---)')