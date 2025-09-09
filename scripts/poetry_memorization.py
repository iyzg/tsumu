#!/usr/bin/env python3
"""
Poetry Memorization Tool - Generate cards for memorizing poems and verse

Inspired by gwern's mnemonic tools, this creates various card types for
memorizing poetry, lyrics, and other structured text using progressive
cloze deletion and other techniques.

Usage:
    # Basic poem memorization with cloze deletions
    echo -e "Roses are red\\nViolets are blue\\nSugar is sweet\\nAnd so are you" | python poetry_memorization.py
    
    # Memorize with rhyme hints preserved
    python poetry_memorization.py --preserve-rhymes < poem.txt
    
    # Create cards for a song with verse/chorus structure
    python poetry_memorization.py --format song < lyrics.txt
    
    # Progressive difficulty cards
    python poetry_memorization.py --progressive < haiku.txt
"""

import sys
import re
import argparse
from typing import List, Tuple, Optional
from dataclasses import dataclass
from anki_utils import AnkiFormatter, AnkiWriter


@dataclass
class Line:
    """Represents a line of poetry with metadata"""
    text: str
    line_num: int
    stanza_num: int
    rhyme_word: Optional[str] = None
    

@dataclass
class Stanza:
    """Represents a stanza (verse) of poetry"""
    lines: List[Line]
    stanza_type: str = "verse"  # verse, chorus, bridge, etc.


class PoetryParser:
    """Parse poetry and extract structure"""
    
    @staticmethod
    def parse_text(text: str) -> List[Stanza]:
        """Parse text into stanzas and lines"""
        stanzas = []
        current_lines = []
        stanza_num = 0
        line_num = 0
        
        for line in text.strip().split('\n'):
            if line.strip() == '':
                if current_lines:
                    stanzas.append(Stanza(lines=current_lines))
                    current_lines = []
                    stanza_num += 1
            else:
                rhyme_word = PoetryParser.extract_rhyme_word(line)
                current_lines.append(Line(
                    text=line,
                    line_num=line_num,
                    stanza_num=stanza_num,
                    rhyme_word=rhyme_word
                ))
                line_num += 1
        
        if current_lines:
            stanzas.append(Stanza(lines=current_lines))
        
        return stanzas
    
    @staticmethod
    def extract_rhyme_word(line: str) -> Optional[str]:
        """Extract the last significant word for rhyme hints"""
        # Remove punctuation and get last word
        words = re.findall(r'\b\w+\b', line)
        return words[-1].lower() if words else None


class PoetryMemorizer:
    """Generate various card types for memorizing poetry"""
    
    def __init__(self, preserve_rhymes: bool = False, progressive: bool = False):
        self.preserve_rhymes = preserve_rhymes
        self.progressive = progressive
        self.formatter = AnkiFormatter()
    
    def create_cards(self, stanzas: List[Stanza]) -> List[Tuple[str, str]]:
        """Generate all card types for the poem"""
        cards = []
        
        # Create different card types
        cards.extend(self.create_line_cloze_cards(stanzas))
        cards.extend(self.create_sequential_cards(stanzas))
        
        if self.progressive:
            cards.extend(self.create_progressive_cards(stanzas))
        
        cards.extend(self.create_stanza_cards(stanzas))
        cards.extend(self.create_first_letter_cards(stanzas))
        
        return cards
    
    def create_line_cloze_cards(self, stanzas: List[Stanza]) -> List[Tuple[str, str]]:
        """Create cards with individual lines clozed out"""
        cards = []
        
        for stanza in stanzas:
            for i, line in enumerate(stanza.lines):
                # Create question with current line hidden
                question_lines = []
                for j, other_line in enumerate(stanza.lines):
                    if i == j:
                        if self.preserve_rhymes and line.rhyme_word:
                            # Keep rhyme word as hint
                            hidden = self._hide_except_word(other_line.text, line.rhyme_word)
                            question_lines.append(hidden)
                        else:
                            question_lines.append(self._hide_line(other_line.text))
                    else:
                        question_lines.append(other_line.text)
                
                question = self.formatter.format_newlines('\n'.join(question_lines))
                answer = self.formatter.format_newlines('\n'.join(l.text for l in stanza.lines))
                cards.append((question, answer))
        
        return cards
    
    def create_sequential_cards(self, stanzas: List[Stanza]) -> List[Tuple[str, str]]:
        """Create cards for memorizing line sequences"""
        cards = []
        
        all_lines = []
        for stanza in stanzas:
            all_lines.extend(stanza.lines)
        
        for i in range(len(all_lines) - 1):
            # Given line i, what comes next?
            question = f"What comes after:<br>{all_lines[i].text}"
            answer = all_lines[i + 1].text
            cards.append((question, answer))
            
            # Given line i+1, what comes before?
            question = f"What comes before:<br>{all_lines[i + 1].text}"
            answer = all_lines[i].text
            cards.append((question, answer))
        
        return cards
    
    def create_progressive_cards(self, stanzas: List[Stanza]) -> List[Tuple[str, str]]:
        """Create progressively harder cards (hide more lines)"""
        cards = []
        
        for stanza in stanzas:
            lines_text = [l.text for l in stanza.lines]
            
            # Progressive hiding - hide 1 line, then 2, then 3...
            for num_hidden in range(1, len(stanza.lines)):
                for start_idx in range(len(stanza.lines) - num_hidden + 1):
                    question_lines = []
                    for i, line in enumerate(lines_text):
                        if start_idx <= i < start_idx + num_hidden:
                            question_lines.append(self._hide_line(line))
                        else:
                            question_lines.append(line)
                    
                    question = self.formatter.format_newlines('\n'.join(question_lines))
                    answer = self.formatter.format_newlines('\n'.join(lines_text))
                    cards.append((question, answer))
        
        return cards
    
    def create_stanza_cards(self, stanzas: List[Stanza]) -> List[Tuple[str, str]]:
        """Create cards for whole stanza memorization"""
        cards = []
        
        if len(stanzas) > 1:
            for i, stanza in enumerate(stanzas):
                # Card: Given stanza number, recite it
                question = f"Recite stanza {i + 1}"
                answer = self.formatter.format_newlines(
                    '\n'.join(l.text for l in stanza.lines)
                )
                cards.append((question, answer))
                
                # Card: Given first line, complete stanza
                if stanza.lines:
                    question = f"Complete the stanza:<br>{stanza.lines[0].text}<br>..."
                    answer = self.formatter.format_newlines(
                        '\n'.join(l.text for l in stanza.lines)
                    )
                    cards.append((question, answer))
        
        return cards
    
    def create_first_letter_cards(self, stanzas: List[Stanza]) -> List[Tuple[str, str]]:
        """Create cards showing only first letters of words"""
        cards = []
        
        for stanza in stanzas:
            for line in stanza.lines:
                # Create first-letter version
                first_letters = self._get_first_letters(line.text)
                question = f"Complete from first letters:<br>{first_letters}"
                answer = line.text
                cards.append((question, answer))
        
        return cards
    
    def _hide_line(self, text: str) -> str:
        """Hide alphanumeric characters in a line"""
        return ''.join('_' if c.isalnum() else c for c in text)
    
    def _hide_except_word(self, text: str, word: str) -> str:
        """Hide line except for specified word"""
        # Simple approach - hide everything except the target word
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        
        result = []
        last_end = 0
        
        for match in pattern.finditer(text):
            # Hide text before match
            result.append(self._hide_line(text[last_end:match.start()]))
            # Keep the matched word
            result.append(text[match.start():match.end()])
            last_end = match.end()
        
        # Hide remaining text
        result.append(self._hide_line(text[last_end:]))
        
        return ''.join(result)
    
    def _get_first_letters(self, text: str) -> str:
        """Get first letters of each word"""
        words = re.findall(r'\b\w+\b', text)
        first_letters = [w[0].upper() + '.' for w in words]
        return ' '.join(first_letters)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Anki cards for memorizing poetry and verse'
    )
    parser.add_argument(
        '--preserve-rhymes',
        action='store_true',
        help='Keep rhyme words visible as hints'
    )
    parser.add_argument(
        '--progressive',
        action='store_true',
        help='Create progressively harder cards'
    )
    parser.add_argument(
        '--format',
        choices=['poem', 'song', 'prose'],
        default='poem',
        help='Input format (affects card generation)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output CSV file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Read input
    text = sys.stdin.read()
    
    if not text.strip():
        print("Error: No input provided", file=sys.stderr)
        sys.exit(1)
    
    # Parse poetry structure
    parser_obj = PoetryParser()
    stanzas = parser_obj.parse_text(text)
    
    # Generate cards
    memorizer = PoetryMemorizer(
        preserve_rhymes=args.preserve_rhymes,
        progressive=args.progressive
    )
    cards = memorizer.create_cards(stanzas)
    
    # Write output
    writer = AnkiWriter()
    
    if args.output:
        writer.write_csv(cards, args.output)
        print(f"Generated {len(cards)} cards to {args.output}", file=sys.stderr)
    else:
        # Write to stdout
        import csv
        output = csv.writer(sys.stdout)
        for card in cards:
            output.writerow(card)
        print(f"Generated {len(cards)} cards", file=sys.stderr)


if __name__ == '__main__':
    main()