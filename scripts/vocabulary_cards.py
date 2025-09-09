#!/usr/bin/env python3
"""
Vocabulary Card Generator for Anki

Creates comprehensive vocabulary flashcards with multiple learning angles:
- Basic definition cards
- Context sentences with cloze deletions
- Etymology-based memory aids
- Synonyms and antonyms
- Word families and derivatives
- Common collocations

Example usage:
    # Basic word list
    python vocabulary_cards.py words.txt -o vocab.csv
    
    # With etymology and examples
    python vocabulary_cards.py words.txt --etymology --examples -o vocab.csv
    
    # From CSV with custom fields
    python vocabulary_cards.py vocab.csv --format csv -o cards.csv
    
    # Generate all card types
    python vocabulary_cards.py words.txt --all-types -o comprehensive.csv
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

from anki_utils import AnkiFormatter, AnkiWriter


@dataclass
class VocabularyEntry:
    """Represents a complete vocabulary entry with all components."""
    word: str
    pronunciation: str = ""
    part_of_speech: str = ""
    definitions: List[str] = field(default_factory=list)
    example_sentences: List[str] = field(default_factory=list)
    etymology: str = ""
    synonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)
    word_family: List[str] = field(default_factory=list)
    collocations: List[str] = field(default_factory=list)
    notes: str = ""
    difficulty: str = ""
    tags: List[str] = field(default_factory=list)


class VocabularyCardGenerator:
    """Generates various types of vocabulary flashcards."""
    
    def __init__(self, include_etymology=False, include_examples=True,
                 include_synonyms=False, include_word_family=False,
                 include_collocations=False):
        self.include_etymology = include_etymology
        self.include_examples = include_examples
        self.include_synonyms = include_synonyms
        self.include_word_family = include_word_family
        self.include_collocations = include_collocations
    
    def parse_input_file(self, filepath: Path, format_type: str = "list") -> List[VocabularyEntry]:
        """Parse input file based on format type."""
        entries = []
        
        if format_type == "list":
            entries = self._parse_word_list(filepath)
        elif format_type == "csv":
            entries = self._parse_csv(filepath)
        elif format_type == "context":
            entries = self._parse_context_text(filepath)
        else:
            raise ValueError(f"Unknown format type: {format_type}")
        
        return entries
    
    def _parse_word_list(self, filepath: Path) -> List[VocabularyEntry]:
        """Parse simple word list, one word per line."""
        entries = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Support inline definitions with ::
                if '::' in line:
                    word, definition = line.split('::', 1)
                    entry = VocabularyEntry(
                        word=word.strip(),
                        definitions=[definition.strip()]
                    )
                else:
                    entry = VocabularyEntry(word=line)
                
                # Generate placeholder data for demonstration
                entry = self._enrich_entry(entry)
                entries.append(entry)
        
        return entries
    
    def _parse_csv(self, filepath: Path) -> List[VocabularyEntry]:
        """Parse CSV file with vocabulary data."""
        entries = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry = VocabularyEntry(
                    word=row.get('word', ''),
                    pronunciation=row.get('pronunciation', ''),
                    part_of_speech=row.get('part_of_speech', ''),
                    definitions=row.get('definitions', '').split('|') if row.get('definitions') else [],
                    example_sentences=row.get('examples', '').split('|') if row.get('examples') else [],
                    etymology=row.get('etymology', ''),
                    synonyms=row.get('synonyms', '').split(',') if row.get('synonyms') else [],
                    antonyms=row.get('antonyms', '').split(',') if row.get('antonyms') else [],
                    word_family=row.get('word_family', '').split(',') if row.get('word_family') else [],
                    collocations=row.get('collocations', '').split('|') if row.get('collocations') else [],
                    difficulty=row.get('difficulty', ''),
                    tags=row.get('tags', '').split(',') if row.get('tags') else []
                )
                entries.append(entry)
        
        return entries
    
    def _parse_context_text(self, filepath: Path) -> List[VocabularyEntry]:
        """Extract vocabulary from text with context."""
        entries = []
        vocab_pattern = r'\*\*(.*?)\*\*'  # Words marked with **word**
        
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            sentences = text.split('.')
            
            for sentence in sentences:
                matches = re.findall(vocab_pattern, sentence)
                for word in matches:
                    # Check if we already have this word
                    existing = next((e for e in entries if e.word == word), None)
                    if existing:
                        existing.example_sentences.append(sentence.strip() + '.')
                    else:
                        entry = VocabularyEntry(
                            word=word,
                            example_sentences=[sentence.strip() + '.']
                        )
                        entry = self._enrich_entry(entry)
                        entries.append(entry)
        
        return entries
    
    def _enrich_entry(self, entry: VocabularyEntry) -> VocabularyEntry:
        """Add placeholder enrichment data for demonstration."""
        if not entry.definitions:
            # Placeholder definitions
            entry.definitions = [f"Definition of {entry.word}"]
        
        if self.include_etymology and not entry.etymology:
            # Placeholder etymology
            entry.etymology = f"Origin: derives from [root] meaning [meaning]"
        
        if self.include_examples and not entry.example_sentences:
            # Placeholder examples
            entry.example_sentences = [
                f"The {entry.word} was evident in the situation.",
                f"She demonstrated {entry.word} in her approach."
            ]
        
        if self.include_synonyms and not entry.synonyms:
            # Placeholder synonyms
            entry.synonyms = ["similar_word1", "similar_word2"]
        
        if self.include_word_family and not entry.word_family:
            # Generate basic word family
            base = entry.word.lower()
            if base.endswith('e'):
                base = base[:-1]
            entry.word_family = [f"{base}ing", f"{base}ed", f"{base}er"]
        
        if self.include_collocations and not entry.collocations:
            # Placeholder collocations
            entry.collocations = [f"to {entry.word}", f"{entry.word} with"]
        
        return entry
    
    def generate_cards(self, entries: List[VocabularyEntry]) -> List[Dict[str, str]]:
        """Generate all flashcards from vocabulary entries."""
        cards = []
        
        for entry in entries:
            # Basic definition cards
            cards.extend(self._create_definition_cards(entry))
            
            # Context cards with cloze
            if self.include_examples:
                cards.extend(self._create_context_cards(entry))
            
            # Etymology cards
            if self.include_etymology and entry.etymology:
                cards.extend(self._create_etymology_cards(entry))
            
            # Synonym/Antonym cards
            if self.include_synonyms:
                cards.extend(self._create_synonym_cards(entry))
            
            # Word family cards
            if self.include_word_family:
                cards.extend(self._create_word_family_cards(entry))
            
            # Collocation cards
            if self.include_collocations:
                cards.extend(self._create_collocation_cards(entry))
        
        return cards
    
    def _create_definition_cards(self, entry: VocabularyEntry) -> List[Dict[str, str]]:
        """Create basic definition cards."""
        cards = []
        word_with_pron = entry.word
        if entry.pronunciation:
            word_with_pron += f" [{entry.pronunciation}]"
        
        for i, definition in enumerate(entry.definitions, 1):
            # Forward card: word -> definition
            cards.append({
                'front': word_with_pron,
                'back': definition,
                'tags': ','.join(['vocabulary', 'definition'] + entry.tags),
                'type': 'basic'
            })
            
            # Reverse card: definition -> word
            if len(entry.definitions) == 1:  # Only for single definitions
                cards.append({
                    'front': f"What word means: {definition}",
                    'back': word_with_pron,
                    'tags': ','.join(['vocabulary', 'definition_reverse'] + entry.tags),
                    'type': 'basic'
                })
        
        return cards
    
    def _create_context_cards(self, entry: VocabularyEntry) -> List[Dict[str, str]]:
        """Create context-based cards with cloze deletions."""
        cards = []
        
        for sentence in entry.example_sentences[:3]:  # Limit to 3 examples
            if entry.word in sentence:
                # Create cloze deletion
                cloze_sentence = sentence.replace(entry.word, '{{c1::' + entry.word + '}}')
                cards.append({
                    'front': cloze_sentence,
                    'back': '',  # Cloze cards don't need separate back
                    'tags': ','.join(['vocabulary', 'context', 'cloze'] + entry.tags),
                    'type': 'cloze'
                })
        
        return cards
    
    def _create_etymology_cards(self, entry: VocabularyEntry) -> List[Dict[str, str]]:
        """Create etymology-based memory cards."""
        cards = []
        
        if entry.etymology:
            cards.append({
                'front': f"Etymology of '{entry.word}'",
                'back': entry.etymology,
                'tags': ','.join(['vocabulary', 'etymology'] + entry.tags),
                'type': 'basic'
            })
            
            # Memory hook card
            cards.append({
                'front': f"Word with etymology: {entry.etymology}",
                'back': entry.word,
                'tags': ','.join(['vocabulary', 'etymology_reverse'] + entry.tags),
                'type': 'basic'
            })
        
        return cards
    
    def _create_synonym_cards(self, entry: VocabularyEntry) -> List[Dict[str, str]]:
        """Create synonym and antonym cards."""
        cards = []
        
        if entry.synonyms:
            cards.append({
                'front': f"Synonyms of '{entry.word}'",
                'back': ', '.join(entry.synonyms),
                'tags': ','.join(['vocabulary', 'synonyms'] + entry.tags),
                'type': 'basic'
            })
        
        if entry.antonyms:
            cards.append({
                'front': f"Antonyms of '{entry.word}'",
                'back': ', '.join(entry.antonyms),
                'tags': ','.join(['vocabulary', 'antonyms'] + entry.tags),
                'type': 'basic'
            })
        
        return cards
    
    def _create_word_family_cards(self, entry: VocabularyEntry) -> List[Dict[str, str]]:
        """Create word family cards."""
        cards = []
        
        if entry.word_family:
            cards.append({
                'front': f"Word family of '{entry.word}'",
                'back': ', '.join(entry.word_family),
                'tags': ','.join(['vocabulary', 'word_family'] + entry.tags),
                'type': 'basic'
            })
            
            # Individual derivative cards
            for derivative in entry.word_family[:3]:  # Limit to avoid too many cards
                cards.append({
                    'front': f"Derivative of '{entry.word}': {derivative[:-2] if len(derivative) > 2 else derivative}___",
                    'back': derivative,
                    'tags': ','.join(['vocabulary', 'derivatives'] + entry.tags),
                    'type': 'basic'
                })
        
        return cards
    
    def _create_collocation_cards(self, entry: VocabularyEntry) -> List[Dict[str, str]]:
        """Create collocation cards."""
        cards = []
        
        for collocation in entry.collocations:
            cards.append({
                'front': f"Common phrase with '{entry.word}': ___",
                'back': collocation,
                'tags': ','.join(['vocabulary', 'collocations'] + entry.tags),
                'type': 'basic'
            })
        
        return cards
    
    def write_cards(self, cards: List[Dict[str, str]], output_path: Path):
        """Write cards to CSV file in Anki format."""
        # Convert cards to tuples for AnkiWriter
        card_tuples = []
        for card in cards:
            if card['type'] == 'cloze':
                # Cloze cards only need the text field
                card_tuples.append((card['front'], card['tags']))
            else:
                # Basic cards need front and back
                card_tuples.append((card['front'], card['back'], card['tags']))
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            AnkiWriter.write_csv(card_tuples, f)
        
        print(f"Generated {len(cards)} cards to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate vocabulary flashcards for Anki',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('input', type=Path, help='Input file (word list, CSV, or text)')
    parser.add_argument('-o', '--output', type=Path, default=Path('vocabulary_cards.csv'),
                        help='Output CSV file (default: vocabulary_cards.csv)')
    parser.add_argument('-f', '--format', choices=['list', 'csv', 'context'],
                        default='list', help='Input format type')
    
    # Card type options
    parser.add_argument('--etymology', action='store_true',
                        help='Include etymology-based cards')
    parser.add_argument('--examples', action='store_true', default=True,
                        help='Include example sentences (default: True)')
    parser.add_argument('--synonyms', action='store_true',
                        help='Include synonym/antonym cards')
    parser.add_argument('--word-family', action='store_true',
                        help='Include word family cards')
    parser.add_argument('--collocations', action='store_true',
                        help='Include collocation cards')
    parser.add_argument('--all-types', action='store_true',
                        help='Generate all card types')
    
    args = parser.parse_args()
    
    # Handle --all-types flag
    if args.all_types:
        args.etymology = True
        args.examples = True
        args.synonyms = True
        args.word_family = True
        args.collocations = True
    
    # Create generator
    generator = VocabularyCardGenerator(
        include_etymology=args.etymology,
        include_examples=args.examples,
        include_synonyms=args.synonyms,
        include_word_family=args.word_family,
        include_collocations=args.collocations
    )
    
    # Parse input
    entries = generator.parse_input_file(args.input, args.format)
    
    if not entries:
        print("No vocabulary entries found in input file")
        return 1
    
    print(f"Parsed {len(entries)} vocabulary entries")
    
    # Generate cards
    cards = generator.generate_cards(entries)
    
    # Write output
    generator.write_cards(cards, args.output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())