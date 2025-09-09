#!/usr/bin/env python3
"""
progressive reveal tool for text memorization.

generates anki cards that progressively reveal or hide text, useful for
memorizing passages, quotes, poems, or any structured text.

examples:
    # progressive reveal by words
    echo "to be or not to be" | python progressive_reveal.py
    
    # reverse progressive (hide more each time)
    python progressive_reveal.py quote.txt --reverse
    
    # reveal by lines instead of words
    python progressive_reveal.py poem.txt --unit line
    
    # reveal 2 words at a time
    python progressive_reveal.py passage.txt --chunk-size 2
"""

import argparse
import csv
import re
import sys
from typing import List, Tuple, Optional
from anki_utils import AnkiFormatter, AnkiWriter


class TextUnit:
    """represents a unit of text (word, line, etc.) that can be hidden or revealed."""
    
    def __init__(self, content: str, is_punctuation: bool = False):
        """
        initialize a text unit.
        
        args:
            content: the text content
            is_punctuation: whether this is punctuation (not hidden)
        """
        self.content = content
        self.is_punctuation = is_punctuation
    
    def hidden(self) -> str:
        """return hidden version of the unit."""
        if self.is_punctuation:
            return self.content
        # preserve length with underscores
        return '_' * len(self.content)


def parse_into_words(text: str) -> List[TextUnit]:
    """
    parse text into word units, preserving punctuation.
    
    args:
        text: input text to parse
    
    returns:
        list of text units
    """
    # split on word boundaries while keeping punctuation
    pattern = r'(\w+|[^\w\s]+|\s+)'
    parts = re.findall(pattern, text)
    
    units = []
    for part in parts:
        if re.match(r'\w+', part):
            # it's a word
            units.append(TextUnit(part, False))
        elif re.match(r'\s+', part):
            # whitespace - keep as is
            units.append(TextUnit(part, True))
        else:
            # punctuation
            units.append(TextUnit(part, True))
    
    return units


def parse_into_lines(text: str) -> List[TextUnit]:
    """
    parse text into line units.
    
    args:
        text: input text to parse
    
    returns:
        list of text units (one per line)
    """
    lines = text.strip().split('\n')
    return [TextUnit(line, False) for line in lines]


def parse_into_sentences(text: str) -> List[TextUnit]:
    """
    parse text into sentence units.
    
    args:
        text: input text to parse
    
    returns:
        list of text units (one per sentence)
    """
    # simple sentence splitting on common punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [TextUnit(sent, False) for sent in sentences if sent]


def generate_progressive_cards(
    units: List[TextUnit],
    chunk_size: int = 1,
    reverse: bool = False,
    keep_punctuation: bool = True,
    unit_type: str = 'word'
) -> List[Tuple[str, str]]:
    """
    generate progressive reveal cards.
    
    args:
        units: list of text units
        chunk_size: number of units to reveal at once
        reverse: if true, hide progressively instead of reveal
        keep_punctuation: if true, always show punctuation
    
    returns:
        list of (front, back) card tuples
    """
    cards = []
    
    # get only content units (non-punctuation) for counting
    content_units = [i for i, u in enumerate(units) if not u.is_punctuation]
    total_chunks = len(content_units)
    
    if total_chunks == 0:
        return cards
    
    # generate full text for the back of cards
    if unit_type == 'line':
        full_text = '\n'.join(u.content for u in units if not u.is_punctuation)
    else:
        full_text = ''.join(u.content for u in units)
    
    # generate cards with progressive reveal
    # for forward: start from 0 (all hidden) to total_chunks-1 (all but one revealed)
    # for reverse: start from total_chunks (all revealed) down to 1 (only one revealed)
    if reverse:
        steps = range(total_chunks - chunk_size, -1, -chunk_size)
    else:
        steps = range(0, total_chunks, chunk_size)
    
    for revealed_count in steps:
        if revealed_count < 0:
            continue
        
        # build the front text
        front_parts = []
        revealed_so_far = 0
        
        for unit in units:
            if unit.is_punctuation and keep_punctuation:
                # always show punctuation if requested
                front_parts.append(unit.content)
            elif unit.is_punctuation:
                # hide punctuation too
                front_parts.append(unit.hidden())
            elif revealed_so_far < revealed_count:
                # reveal this content unit
                front_parts.append(unit.content)
                revealed_so_far += 1
            else:
                # hide this content unit
                front_parts.append(unit.hidden())
        
        if unit_type == 'line':
            # for lines, join with newlines and only include non-empty parts
            front = '\n'.join(p for p in front_parts if p.strip() or p == '_' * len(p))
        else:
            front = ''.join(front_parts)
        
        # don't create a card where front equals back (fully revealed)
        if front != full_text:
            cards.append((AnkiFormatter.escape_html(front), AnkiFormatter.escape_html(full_text)))
    
    return cards


def process_text(
    text: str,
    unit: str = 'word',
    chunk_size: int = 1,
    reverse: bool = False,
    keep_punctuation: bool = True
) -> List[Tuple[str, str]]:
    """
    process text into progressive reveal cards.
    
    args:
        text: input text
        unit: 'word', 'line', or 'sentence'
        chunk_size: units to reveal at once
        reverse: hide instead of reveal
        keep_punctuation: always show punctuation
    
    returns:
        list of card tuples
    """
    # parse text into units
    if unit == 'word':
        units = parse_into_words(text)
    elif unit == 'line':
        units = parse_into_lines(text)
    elif unit == 'sentence':
        units = parse_into_sentences(text)
    else:
        raise ValueError(f"unknown unit type: {unit}")
    
    # generate cards
    return generate_progressive_cards(units, chunk_size, reverse, keep_punctuation, unit)


def main():
    """main entry point for progressive reveal generator."""
    parser = argparse.ArgumentParser(
        description='generate progressive reveal cards for text memorization'
    )
    parser.add_argument(
        'input',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='input file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='output csv file (default: stdout)'
    )
    parser.add_argument(
        '-u', '--unit',
        choices=['word', 'line', 'sentence'],
        default='word',
        help='unit to reveal (default: word)'
    )
    parser.add_argument(
        '-c', '--chunk-size',
        type=int,
        default=1,
        help='number of units to reveal at once (default: 1)'
    )
    parser.add_argument(
        '-r', '--reverse',
        action='store_true',
        help='hide progressively instead of reveal'
    )
    parser.add_argument(
        '--hide-punctuation',
        action='store_true',
        help='hide punctuation marks as well'
    )
    
    args = parser.parse_args()
    
    # read input text
    text = args.input.read()
    
    if not text.strip():
        print("error: no input text provided", file=sys.stderr)
        sys.exit(1)
    
    # process text into cards
    cards = process_text(
        text,
        unit=args.unit,
        chunk_size=args.chunk_size,
        reverse=args.reverse,
        keep_punctuation=not args.hide_punctuation
    )
    
    if not cards:
        print("warning: no cards generated", file=sys.stderr)
        sys.exit(0)
    
    # write output
    AnkiWriter.write_csv(cards, args.output)
    
    # report results if not stdout
    if args.output != sys.stdout:
        direction = "hide" if args.reverse else "reveal"
        print(f"generated {len(cards)} progressive {direction} cards", file=sys.stderr)


if __name__ == '__main__':
    main()