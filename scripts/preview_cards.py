#!/usr/bin/env python3
"""
Card Preview Tool for Anki Flashcards

Preview generated flashcards in various formats before importing to Anki.
Supports interactive browsing, HTML rendering, and statistics.

Examples:
    python preview_cards.py cards.csv
    python preview_cards.py cards.csv --format html > preview.html
    python preview_cards.py cards.csv --stats
    python preview_cards.py cards.csv --interactive
"""

import argparse
import csv
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
import html


class CardPreview:
    """Handles flashcard preview and formatting."""
    
    def __init__(self, cards: List[Dict[str, str]]):
        """
        Initialize preview with cards.
        
        Args:
            cards: List of card dictionaries with 'front' and 'back' keys
        """
        self.cards = cards
        self.current_index = 0
    
    def format_card_text(self, text: str) -> str:
        """
        Format card text for display.
        
        Args:
            text: Card text with HTML/LaTeX
            
        Returns:
            Formatted text for console display
        """
        # Remove HTML tags for console display
        text = re.sub(r'<[^>]+>', '', text)
        
        # Convert LaTeX delimiters to readable format
        text = text.replace('\\(', '[').replace('\\)', ']')
        text = text.replace('\\[', '\n[').replace('\\]', ']\n')
        
        # Format cloze deletions
        text = re.sub(r'\{\{c(\d+)::(.*?)\}\}', r'[...\2...]', text)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        return text
    
    def preview_text(self, max_cards: int = None) -> str:
        """
        Generate text preview of cards.
        
        Args:
            max_cards: Maximum number of cards to preview
            
        Returns:
            Formatted text preview
        """
        output = []
        cards_to_show = self.cards[:max_cards] if max_cards else self.cards
        
        for i, card in enumerate(cards_to_show, 1):
            output.append(f"\n{'='*60}")
            output.append(f"Card #{i}")
            output.append(f"{'='*60}")
            output.append(f"FRONT:")
            output.append(self.format_card_text(card['front']))
            output.append(f"\nBACK:")
            output.append(self.format_card_text(card['back']))
        
        if max_cards and len(self.cards) > max_cards:
            output.append(f"\n... and {len(self.cards) - max_cards} more cards")
        
        return '\n'.join(output)
    
    def preview_html(self) -> str:
        """
        Generate HTML preview of cards.
        
        Returns:
            HTML string with styled card preview
        """
        html_parts = ['''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Anki Card Preview</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        .stats {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card {
            background: white;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .card-header {
            background: #4CAF50;
            color: white;
            padding: 10px 15px;
            font-weight: bold;
        }
        .card-content {
            padding: 20px;
        }
        .front, .back {
            margin: 10px 0;
        }
        .label {
            font-weight: bold;
            color: #666;
            margin-bottom: 5px;
            text-transform: uppercase;
            font-size: 0.9em;
        }
        .content {
            padding: 10px;
            background: #f9f9f9;
            border-left: 3px solid #4CAF50;
            border-radius: 4px;
        }
        .cloze {
            background: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: bold;
        }
        code {
            background: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .math {
            font-style: italic;
            color: #0066cc;
        }
    </style>
    <script>
        MathJax = {
            tex: {
                inlineMath: [['\\\\(', '\\\\)']],
                displayMath: [['\\\\[', '\\\\]']]
            }
        };
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <h1>Anki Card Preview</h1>
''']
        
        # Add statistics
        stats = self.get_statistics()
        html_parts.append('<div class="stats">')
        html_parts.append(f'<h2>Statistics</h2>')
        html_parts.append(f'<p>Total cards: {stats["total"]}</p>')
        html_parts.append(f'<p>Card types: {", ".join(f"{k}: {v}" for k, v in stats["types"].items())}</p>')
        html_parts.append(f'<p>Average front length: {stats["avg_front_length"]} characters</p>')
        html_parts.append(f'<p>Average back length: {stats["avg_back_length"]} characters</p>')
        html_parts.append('</div>')
        
        # Add cards
        for i, card in enumerate(self.cards, 1):
            # Process cloze deletions for HTML
            front_html = re.sub(
                r'\{\{c(\d+)::(.*?)\}\}',
                r'<span class="cloze">[...]</span>',
                card['front']
            )
            back_html = re.sub(
                r'\{\{c(\d+)::(.*?)\}\}',
                r'<span class="cloze">\2</span>',
                card['back']
            )
            
            html_parts.append(f'''
    <div class="card">
        <div class="card-header">Card #{i}</div>
        <div class="card-content">
            <div class="front">
                <div class="label">Front:</div>
                <div class="content">{front_html}</div>
            </div>
            <div class="back">
                <div class="label">Back:</div>
                <div class="content">{back_html}</div>
            </div>
        </div>
    </div>
''')
        
        html_parts.append('</body></html>')
        return ''.join(html_parts)
    
    def preview_markdown(self) -> str:
        """
        Generate Markdown preview of cards.
        
        Returns:
            Markdown formatted string
        """
        output = ['# Anki Card Preview\n']
        
        # Add statistics
        stats = self.get_statistics()
        output.append('## Statistics\n')
        output.append(f'- **Total cards:** {stats["total"]}')
        output.append(f'- **Card types:** {", ".join(f"{k}: {v}" for k, v in stats["types"].items())}')
        output.append(f'- **Average front length:** {stats["avg_front_length"]} characters')
        output.append(f'- **Average back length:** {stats["avg_back_length"]} characters\n')
        
        output.append('## Cards\n')
        
        for i, card in enumerate(self.cards, 1):
            output.append(f'### Card #{i}\n')
            output.append('**Front:**')
            output.append(f'```\n{self.format_card_text(card["front"])}\n```\n')
            output.append('**Back:**')
            output.append(f'```\n{self.format_card_text(card["back"])}\n```\n')
            output.append('---\n')
        
        return '\n'.join(output)
    
    def get_statistics(self) -> Dict:
        """
        Calculate statistics about the cards.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total': len(self.cards),
            'types': {},
            'avg_front_length': 0,
            'avg_back_length': 0,
            'has_latex': 0,
            'has_cloze': 0,
            'has_html': 0
        }
        
        if not self.cards:
            return stats
        
        total_front_length = 0
        total_back_length = 0
        
        for card in self.cards:
            # Calculate lengths
            total_front_length += len(card['front'])
            total_back_length += len(card['back'])
            
            # Detect card types
            if '{{c' in card['front'] or '{{c' in card['back']:
                stats['has_cloze'] += 1
                stats['types']['Cloze'] = stats['types'].get('Cloze', 0) + 1
            elif '\\(' in card['front'] or '\\[' in card['front']:
                stats['has_latex'] += 1
                stats['types']['Math'] = stats['types'].get('Math', 0) + 1
            elif '<' in card['front'] and '>' in card['front']:
                stats['has_html'] += 1
                stats['types']['HTML'] = stats['types'].get('HTML', 0) + 1
            else:
                stats['types']['Basic'] = stats['types'].get('Basic', 0) + 1
        
        stats['avg_front_length'] = total_front_length // len(self.cards)
        stats['avg_back_length'] = total_back_length // len(self.cards)
        
        return stats
    
    def interactive_preview(self):
        """Run interactive card preview session."""
        print("\n" + "="*60)
        print("INTERACTIVE CARD PREVIEW")
        print("="*60)
        print("Commands: [n]ext, [p]revious, [g]oto, [s]tats, [q]uit")
        print("="*60)
        
        while True:
            if self.current_index < len(self.cards):
                card = self.cards[self.current_index]
                print(f"\nCard {self.current_index + 1} of {len(self.cards)}")
                print("-"*40)
                print("FRONT:")
                print(self.format_card_text(card['front']))
                print("\n[Press ENTER to reveal back]")
                input()
                print("BACK:")
                print(self.format_card_text(card['back']))
                print("-"*40)
            
            command = input("\nCommand: ").strip().lower()
            
            if command in ['n', 'next', '']:
                if self.current_index < len(self.cards) - 1:
                    self.current_index += 1
                else:
                    print("Already at last card")
            
            elif command in ['p', 'prev', 'previous']:
                if self.current_index > 0:
                    self.current_index -= 1
                else:
                    print("Already at first card")
            
            elif command in ['g', 'goto']:
                try:
                    num = int(input("Go to card number: "))
                    if 1 <= num <= len(self.cards):
                        self.current_index = num - 1
                    else:
                        print(f"Invalid card number (1-{len(self.cards)})")
                except ValueError:
                    print("Invalid number")
            
            elif command in ['s', 'stats']:
                stats = self.get_statistics()
                print("\nSTATISTICS:")
                print(f"Total cards: {stats['total']}")
                print(f"Card types: {stats['types']}")
                print(f"Average lengths: Front={stats['avg_front_length']}, Back={stats['avg_back_length']}")
            
            elif command in ['q', 'quit', 'exit']:
                break
            
            else:
                print("Unknown command. Use: n, p, g, s, or q")


def load_cards(file_path: Path) -> List[Dict[str, str]]:
    """
    Load cards from CSV file.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of card dictionaries
    """
    cards = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Try to detect delimiter
        sample = f.read(1024)
        f.seek(0)
        
        if '\t' in sample:
            delimiter = '\t'
        else:
            delimiter = ','
        
        # Check if file has headers
        first_line = f.readline()
        f.seek(0)
        
        # If the first line doesn't look like headers, assume no headers
        if delimiter in first_line and not any(
            header in first_line.lower() 
            for header in ['front', 'back', 'question', 'answer', 'text']
        ):
            # No headers, read as simple rows
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                if len(row) >= 2:
                    cards.append({
                        'front': row[0],
                        'back': row[1]
                    })
                elif len(row) == 1:
                    # Single column, might be cloze
                    cards.append({
                        'front': row[0],
                        'back': row[0]
                    })
        else:
            # Has headers, use DictReader
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in reader:
                # Handle different possible column names
                front = row.get('Front') or row.get('front') or row.get('Question') or ''
                back = row.get('Back') or row.get('back') or row.get('Answer') or ''
                
                # Handle cloze cards
                if 'Text' in row:
                    front = row['Text']
                    back = row['Text']
                
                cards.append({
                    'front': front,
                    'back': back
                })
    
    return cards


def main():
    parser = argparse.ArgumentParser(
        description='Preview Anki flashcards before importing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'input', type=argparse.FileType('r', encoding='utf-8'),
        help='CSV file with flashcards'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'html', 'markdown'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '-n', '--number', type=int,
        help='Maximum number of cards to preview'
    )
    parser.add_argument(
        '-i', '--interactive', action='store_true',
        help='Interactive preview mode'
    )
    parser.add_argument(
        '-s', '--stats', action='store_true',
        help='Show statistics only'
    )
    
    args = parser.parse_args()
    
    # Load cards
    cards = load_cards(Path(args.input.name))
    args.input.close()
    
    if not cards:
        print("No cards found in file", file=sys.stderr)
        return 1
    
    # Create previewer
    previewer = CardPreview(cards)
    
    # Handle different modes
    if args.stats:
        stats = previewer.get_statistics()
        print(f"Total cards: {stats['total']}")
        print(f"Card types: {stats['types']}")
        print(f"Average front length: {stats['avg_front_length']} characters")
        print(f"Average back length: {stats['avg_back_length']} characters")
        if stats['has_latex']:
            print(f"Cards with LaTeX: {stats['has_latex']}")
        if stats['has_cloze']:
            print(f"Cloze deletion cards: {stats['has_cloze']}")
    
    elif args.interactive:
        previewer.interactive_preview()
    
    else:
        # Generate preview in requested format
        if args.format == 'html':
            print(previewer.preview_html())
        elif args.format == 'markdown':
            print(previewer.preview_markdown())
        else:
            print(previewer.preview_text(max_cards=args.number))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())