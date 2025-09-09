#!/usr/bin/env python3
"""
Study deck builder for combining and organizing Anki cards.

Features:
- Merge multiple CSV files into a single deck
- Add tags based on source files or custom tags
- Sort cards by priority/difficulty
- Remove duplicates
- Add deck-level metadata
"""

import csv
import hashlib
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set
import argparse
from datetime import datetime


class DeckBuilder:
    """Build and organize Anki study decks from multiple sources."""
    
    def __init__(self):
        self.cards = []
        self.sources = {}
        self.duplicates_removed = 0
        self.total_processed = 0
    
    def load_csv(self, filepath: str, source_tag: str = None) -> int:
        """Load cards from a CSV file.
        
        Returns number of cards loaded.
        """
        path = Path(filepath)
        if not path.exists():
            print(f"Warning: File {filepath} not found", file=sys.stderr)
            return 0
        
        if source_tag is None:
            source_tag = path.stem  # Use filename without extension
        
        cards_loaded = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            
            # Skip header if present
            first_row = next(reader, None)
            if first_row and self._is_header(first_row):
                pass  # Skip header
            elif first_row:
                # Not a header, process as card
                self._add_card(first_row, source_tag)
                cards_loaded += 1
            
            # Process remaining rows
            for row in reader:
                if row:  # Skip empty rows
                    self._add_card(row, source_tag)
                    cards_loaded += 1
        
        self.sources[source_tag] = cards_loaded
        self.total_processed += cards_loaded
        return cards_loaded
    
    def _is_header(self, row: List[str]) -> bool:
        """Check if a row is likely a header."""
        common_headers = ['front', 'back', 'text', 'question', 'answer', 'tags']
        return any(h in row[0].lower() for h in common_headers)
    
    def _add_card(self, row: List[str], source_tag: str):
        """Add a card with source tag."""
        # Ensure row has at least 2 fields (front/back)
        if len(row) < 2:
            if len(row) == 1:
                # Cloze card - single field
                row.append('')  # Add empty back
        
        # Add source tag to existing tags or create tags field
        if len(row) >= 3:
            # Has tags field
            existing_tags = row[2] if len(row) > 2 else ''
            tags = f"{existing_tags} {source_tag}".strip()
            row[2] = tags
        else:
            # Add tags field
            row.append(source_tag)
        
        # Add metadata fields if needed
        while len(row) < 4:
            row.append('')
        
        self.cards.append(row)
    
    def remove_duplicates(self) -> int:
        """Remove duplicate cards based on content hash.
        
        Returns number of duplicates removed.
        """
        seen = set()
        unique_cards = []
        
        for card in self.cards:
            # Create hash of front and back content
            content = f"{card[0]}|{card[1]}"
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            if content_hash not in seen:
                seen.add(content_hash)
                unique_cards.append(card)
            else:
                self.duplicates_removed += 1
        
        self.cards = unique_cards
        return self.duplicates_removed
    
    def add_global_tags(self, tags: List[str]):
        """Add tags to all cards in the deck."""
        for card in self.cards:
            existing_tags = card[2] if len(card) > 2 else ''
            new_tags = ' '.join(tags)
            card[2] = f"{existing_tags} {new_tags}".strip()
    
    def sort_cards(self, method: str = 'random'):
        """Sort cards by specified method.
        
        Methods:
        - random: Randomize order
        - length: Short to long
        - alpha: Alphabetical by front
        - source: Group by source tag
        """
        import random
        
        if method == 'random':
            random.shuffle(self.cards)
        elif method == 'length':
            self.cards.sort(key=lambda c: len(c[0]) + len(c[1]))
        elif method == 'alpha':
            self.cards.sort(key=lambda c: c[0].lower())
        elif method == 'source':
            # Sort by source tag (third field)
            self.cards.sort(key=lambda c: c[2] if len(c) > 2 else '')
    
    def prioritize_cards(self, priority_tags: List[str]):
        """Move cards with priority tags to the front."""
        priority_cards = []
        regular_cards = []
        
        for card in self.cards:
            tags = card[2] if len(card) > 2 else ''
            if any(tag in tags for tag in priority_tags):
                priority_cards.append(card)
            else:
                regular_cards.append(card)
        
        self.cards = priority_cards + regular_cards
    
    def add_spaced_repetition_hints(self):
        """Add initial interval hints based on card complexity."""
        for card in self.cards:
            front = card[0]
            back = card[1]
            
            # Estimate complexity
            complexity = 0
            
            # Length factor
            total_length = len(front) + len(back)
            if total_length > 200:
                complexity += 2
            elif total_length > 100:
                complexity += 1
            
            # Formula/code factor
            if '\\[' in front or '\\[' in back or '<code>' in front:
                complexity += 1
            
            # List factor
            if '<br>' in back and back.count('<br>') > 2:
                complexity += 1
            
            # Set initial interval based on complexity
            if complexity >= 3:
                interval_hint = 'hard'
            elif complexity >= 1:
                interval_hint = 'medium'
            else:
                interval_hint = 'easy'
            
            # Add to metadata field
            if len(card) > 3:
                card[3] = interval_hint
            else:
                card.append(interval_hint)
    
    def get_statistics(self) -> Dict:
        """Get statistics about the deck."""
        stats = {
            'total_cards': len(self.cards),
            'sources': self.sources,
            'duplicates_removed': self.duplicates_removed,
            'cards_processed': self.total_processed,
            'unique_tags': set(),
            'card_types': {'basic': 0, 'cloze': 0, 'list': 0, 'formula': 0}
        }
        
        for card in self.cards:
            # Collect tags
            if len(card) > 2 and card[2]:
                tags = card[2].split()
                stats['unique_tags'].update(tags)
            
            # Detect card type
            front = card[0]
            back = card[1]
            
            if '{{c' in front or '{{c' in back:
                stats['card_types']['cloze'] += 1
            elif '\\[' in front or '\\[' in back:
                stats['card_types']['formula'] += 1
            elif '<br>' in back and back.count('<br>') > 2:
                stats['card_types']['list'] += 1
            else:
                stats['card_types']['basic'] += 1
        
        stats['unique_tags'] = list(stats['unique_tags'])
        return stats
    
    def export_deck(self, output_file, include_header: bool = True, 
                    deck_name: str = None):
        """Export the deck to a CSV file."""
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            
            # Add header if requested
            if include_header:
                if deck_name:
                    writer.writerow([f'#deck:{deck_name}'])
                writer.writerow(['Front', 'Back', 'Tags', 'Metadata'])
            
            # Write cards
            for card in self.cards:
                writer.writerow(card)
    
    def create_subset(self, max_cards: int = None, tag_filter: List[str] = None) -> 'DeckBuilder':
        """Create a subset of the deck based on criteria."""
        subset = DeckBuilder()
        
        filtered_cards = self.cards
        
        # Filter by tags if specified
        if tag_filter:
            filtered_cards = [
                card for card in filtered_cards
                if any(tag in (card[2] if len(card) > 2 else '') for tag in tag_filter)
            ]
        
        # Limit number of cards
        if max_cards and len(filtered_cards) > max_cards:
            filtered_cards = filtered_cards[:max_cards]
        
        subset.cards = filtered_cards
        return subset


def main():
    """Build an Anki deck from multiple sources."""
    parser = argparse.ArgumentParser(
        description='Build and organize Anki study decks'
    )
    parser.add_argument(
        'files', nargs='+',
        help='CSV files to combine into deck'
    )
    parser.add_argument(
        '-o', '--output', required=True,
        help='Output deck file'
    )
    parser.add_argument(
        '--name', default='Combined Deck',
        help='Deck name'
    )
    parser.add_argument(
        '--tags', nargs='+',
        help='Global tags to add to all cards'
    )
    parser.add_argument(
        '--priority-tags', nargs='+',
        help='Tags to prioritize (move to front)'
    )
    parser.add_argument(
        '--sort', choices=['random', 'length', 'alpha', 'source'],
        default='random',
        help='Sort method for cards'
    )
    parser.add_argument(
        '--remove-duplicates', action='store_true',
        help='Remove duplicate cards'
    )
    parser.add_argument(
        '--add-hints', action='store_true',
        help='Add spaced repetition difficulty hints'
    )
    parser.add_argument(
        '--max-cards', type=int,
        help='Maximum number of cards in deck'
    )
    parser.add_argument(
        '--filter-tags', nargs='+',
        help='Only include cards with these tags'
    )
    parser.add_argument(
        '--stats', action='store_true',
        help='Show deck statistics'
    )
    
    args = parser.parse_args()
    
    # Create deck builder
    builder = DeckBuilder()
    
    # Load all input files
    print(f"Loading cards from {len(args.files)} files...", file=sys.stderr)
    for filepath in args.files:
        count = builder.load_csv(filepath)
        print(f"  Loaded {count} cards from {Path(filepath).name}", file=sys.stderr)
    
    # Remove duplicates if requested
    if args.remove_duplicates:
        removed = builder.remove_duplicates()
        if removed > 0:
            print(f"Removed {removed} duplicate cards", file=sys.stderr)
    
    # Add global tags
    if args.tags:
        builder.add_global_tags(args.tags)
        print(f"Added global tags: {' '.join(args.tags)}", file=sys.stderr)
    
    # Sort cards
    builder.sort_cards(args.sort)
    print(f"Sorted cards by: {args.sort}", file=sys.stderr)
    
    # Prioritize certain tags
    if args.priority_tags:
        builder.prioritize_cards(args.priority_tags)
        print(f"Prioritized tags: {' '.join(args.priority_tags)}", file=sys.stderr)
    
    # Add difficulty hints
    if args.add_hints:
        builder.add_spaced_repetition_hints()
        print("Added spaced repetition difficulty hints", file=sys.stderr)
    
    # Create subset if filters applied
    if args.filter_tags or args.max_cards:
        original_count = len(builder.cards)
        builder = builder.create_subset(
            max_cards=args.max_cards,
            tag_filter=args.filter_tags
        )
        print(f"Filtered deck from {original_count} to {len(builder.cards)} cards", file=sys.stderr)
    
    # Show statistics if requested
    if args.stats:
        stats = builder.get_statistics()
        print("\nDeck Statistics:", file=sys.stderr)
        print(f"  Total cards: {stats['total_cards']}", file=sys.stderr)
        print(f"  Cards processed: {stats['cards_processed']}", file=sys.stderr)
        print(f"  Duplicates removed: {stats['duplicates_removed']}", file=sys.stderr)
        print(f"  Card types:", file=sys.stderr)
        for card_type, count in stats['card_types'].items():
            if count > 0:
                print(f"    - {card_type}: {count}", file=sys.stderr)
        print(f"  Unique tags: {len(stats['unique_tags'])}", file=sys.stderr)
        if len(stats['unique_tags']) <= 10:
            print(f"    Tags: {', '.join(sorted(stats['unique_tags']))}", file=sys.stderr)
    
    # Export deck
    builder.export_deck(args.output, include_header=True, deck_name=args.name)
    print(f"\nExported {len(builder.cards)} cards to {args.output}", file=sys.stderr)
    
    # Add creation timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Deck created: {timestamp}", file=sys.stderr)


if __name__ == '__main__':
    main()