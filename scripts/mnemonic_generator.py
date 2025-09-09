#!/usr/bin/env python3
"""
Mnemonic card generator inspired by gwern's algorithms.

Creates cards using various mnemonic techniques:
- List ordering (what comes before/after)
- Cloze deletion with partial hiding
- Position-based memorization
- Association chains

Usage:
    python mnemonic_generator.py input.txt -t sequence -o cards.csv
    python mnemonic_generator.py --demo
"""

import argparse
import csv
import re
import sys
from typing import List, Tuple, Optional
from anki_utils import AnkiFormatter, AnkiWriter, create_argument_parser


class MnemonicGenerator:
    """Generate mnemonic cards using various techniques."""
    
    def __init__(self):
        self.formatter = AnkiFormatter()
    
    def sequence_cards(self, items: List[str], context: str = "") -> List[Tuple[str, str]]:
        """Generate cards for memorizing sequences.
        
        Creates cards asking:
        - What comes before/after each item
        - What position is each item
        - What item is at each position
        
        Args:
            items: List of items to memorize in order
            context: Optional context word (e.g., "dynasty", "president")
        
        Returns:
            List of (question, answer) tuples
        """
        cards = []
        
        for i, item in enumerate(items):
            position = self._ordinal(i + 1)
            
            # Position cards
            cards.append((
                f"What {context + ' ' if context else ''}was {position}?",
                item
            ))
            cards.append((
                f"What position {context + ' ' if context else ''}was {item}?",
                position
            ))
            
            # Before/after cards
            if i > 0:
                prev_item = items[i - 1]
                cards.append((
                    f"What {context + ' ' if context else ''}came before {item}?",
                    prev_item
                ))
                cards.append((
                    f"What {context + ' ' if context else ''}preceded {item}?",
                    prev_item
                ))
            
            if i < len(items) - 1:
                next_item = items[i + 1]
                cards.append((
                    f"What {context + ' ' if context else ''}came after {item}?",
                    next_item
                ))
                cards.append((
                    f"What {context + ' ' if context else ''}succeeded {item}?",
                    next_item
                ))
                cards.append((
                    f"What did {item} come before?",
                    next_item
                ))
        
        return cards
    
    def cloze_halves(self, lines: List[str]) -> List[str]:
        """Generate cloze cards by hiding halves of text.
        
        For memorizing poems, quotes, etc. Creates variations where
        different halves are hidden.
        
        Args:
            lines: Lines of text to memorize
        
        Returns:
            List of cloze deletion cards
        """
        cards = []
        n_half = len(lines) // 2
        
        # Generate all combinations of hiding n_half lines
        for mask in self._generate_masks(len(lines), n_half):
            card_lines = []
            for i, line in enumerate(lines):
                if mask[i]:
                    # Hide this line
                    hidden = self._hide_text(line)
                    card_lines.append(f"{{{{c1::{line}::{hidden}}}}}")
                else:
                    card_lines.append(line)
            
            cards.append("<br>".join(card_lines))
        
        return cards
    
    def association_chain(self, items: List[str]) -> List[Tuple[str, str]]:
        """Create cards for memorizing association chains.
        
        Each item is linked to the next, forming a chain of associations.
        
        Args:
            items: List of items to chain together
        
        Returns:
            List of (question, answer) tuples
        """
        cards = []
        
        for i in range(len(items) - 1):
            current = items[i]
            next_item = items[i + 1]
            
            # Direct association
            cards.append((
                f"What is associated with {current}?",
                next_item
            ))
            
            # Reverse association
            cards.append((
                f"What leads to {next_item}?",
                current
            ))
            
            # Chain position
            if i > 0:
                prev_item = items[i - 1]
                cards.append((
                    f"In the chain starting with {items[0]}, what comes between {prev_item} and {next_item}?",
                    current
                ))
        
        return cards
    
    def acronym_cards(self, items: List[str], acronym: Optional[str] = None) -> List[Tuple[str, str]]:
        """Generate cards for acronym-based memorization.
        
        Args:
            items: List of items to create acronym from
            acronym: Optional pre-defined acronym
        
        Returns:
            List of (question, answer) tuples
        """
        cards = []
        
        # Generate acronym if not provided
        if not acronym:
            acronym = ''.join(word[0].upper() for word in items)
        
        # Full acronym card
        cards.append((
            f"What is the acronym for: {', '.join(items)}?",
            acronym
        ))
        
        cards.append((
            f"What does the acronym {acronym} stand for?",
            ', '.join(items)
        ))
        
        # Individual letter cards
        for i, (letter, item) in enumerate(zip(acronym, items)):
            cards.append((
                f"In {acronym}, what does the {self._ordinal(i+1)} letter '{letter}' stand for?",
                item
            ))
            
            cards.append((
                f"What letter represents '{item}' in {acronym}?",
                letter
            ))
        
        return cards
    
    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)."""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"
    
    def _hide_text(self, text: str) -> str:
        """Hide alphanumeric characters with underscores."""
        return re.sub(r'[a-zA-Z0-9]', '_', text)
    
    def _generate_masks(self, n: int, k: int) -> List[List[bool]]:
        """Generate all ways to choose k items from n items."""
        if k == 0:
            return [[False] * n]
        if k == n:
            return [[True] * n]
        if k > n:
            return []
        
        masks = []
        # Recursive generation of combinations
        def generate(pos: int, selected: int, mask: List[bool]):
            if selected == k:
                masks.append(mask[:])
                return
            if pos == n:
                return
            
            # Include current position
            mask[pos] = True
            generate(pos + 1, selected + 1, mask)
            
            # Exclude current position
            mask[pos] = False
            generate(pos + 1, selected, mask)
        
        generate(0, 0, [False] * n)
        return masks


def demo():
    """Run demonstration of mnemonic techniques."""
    generator = MnemonicGenerator()
    
    print("=== Sequence Memorization Demo ===")
    dynasties = ["Shang", "Zhou", "Han"]
    cards = generator.sequence_cards(dynasties, "dynasty")
    for q, a in cards[:3]:
        print(f"Q: {q}")
        print(f"A: {a}")
        print()
    
    print("=== Cloze Halves Demo ===")
    poem = [
        "Roses are red",
        "Violets are blue",
        "Sugar is sweet",
        "And so are you"
    ]
    cloze_cards = generator.cloze_halves(poem)
    print(f"Generated {len(cloze_cards)} cloze variations")
    print(f"Example: {cloze_cards[0]}")
    print()
    
    print("=== Association Chain Demo ===")
    chain = ["Thunder", "Lightning", "Rain", "Rainbow"]
    chain_cards = generator.association_chain(chain)
    for q, a in chain_cards[:2]:
        print(f"Q: {q}")
        print(f"A: {a}")
        print()
    
    print("=== Acronym Demo ===")
    planets = ["Mercury", "Venus", "Earth", "Mars"]
    acronym_cards = generator.acronym_cards(planets)
    for q, a in acronym_cards[:2]:
        print(f"Q: {q}")
        print(f"A: {a}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate mnemonic flashcards using various techniques'
    )
    
    parser.add_argument(
        'input', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin,
        help='Input file with items (one per line)'
    )
    
    parser.add_argument(
        '-t', '--type',
        choices=['sequence', 'cloze', 'chain', 'acronym'],
        default='sequence',
        help='Type of mnemonic technique to use'
    )
    
    parser.add_argument(
        '-c', '--context',
        help='Context word for sequence cards (e.g., "president", "element")'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Output CSV file'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demonstration'
    )
    
    args = parser.parse_args()
    
    if args.demo:
        demo()
        return
    
    # Read input
    lines = [line.strip() for line in args.input if line.strip()]
    
    if not lines:
        print("Error: No input provided", file=sys.stderr)
        return 1
    
    generator = MnemonicGenerator()
    writer = csv.writer(args.output, delimiter='\t')
    
    # Generate cards based on type
    if args.type == 'sequence':
        cards = generator.sequence_cards(lines, args.context or "")
        for q, a in cards:
            writer.writerow([q, a])
    
    elif args.type == 'cloze':
        cards = generator.cloze_halves(lines)
        writer.writerow(['Text'])  # Header for cloze type
        for card in cards:
            writer.writerow([card])
    
    elif args.type == 'chain':
        cards = generator.association_chain(lines)
        for q, a in cards:
            writer.writerow([q, a])
    
    elif args.type == 'acronym':
        cards = generator.acronym_cards(lines)
        for q, a in cards:
            writer.writerow([q, a])
    
    return 0


if __name__ == '__main__':
    sys.exit(main())