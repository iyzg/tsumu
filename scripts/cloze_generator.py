#!/usr/bin/env python3
"""
Cloze Deletion Generator for Anki
Creates cloze deletion cards from text with various patterns.
"""

import sys
import argparse
import re
import csv


def create_basic_cloze(text, keywords):
    """Create cloze deletions for specified keywords."""
    cards = []
    for i, keyword in enumerate(keywords, 1):
        # Create a cloze for each keyword occurrence
        pattern = re.escape(keyword)
        cloze_text = re.sub(
            pattern, 
            f"{{{{c{i}::{keyword}}}}}", 
            text, 
            flags=re.IGNORECASE
        )
        if cloze_text != text:  # Only add if keyword was found
            cards.append(cloze_text)
    return cards


def create_sentence_cloze(text):
    """Create cloze deletions for each sentence."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cards = []
    
    for i, sentence in enumerate(sentences, 1):
        if sentence.strip():
            cloze_text = text.replace(
                sentence, 
                f"{{{{c{i}::{sentence}}}}}"
            )
            cards.append(cloze_text)
    
    return cards


def create_numbered_list_cloze(text):
    """Create cloze deletions for numbered list items."""
    lines = text.split('\n')
    cards = []
    cloze_counter = 1
    
    # Pattern for numbered lists (1. or 1) style)
    pattern = r'^(\d+[\.\)])\s+(.+)$'
    
    processed_text = text
    for line in lines:
        match = re.match(pattern, line.strip())
        if match:
            number, content = match.groups()
            full_item = f"{number} {content}"
            cloze_item = f"{number} {{{{c{cloze_counter}::{content}}}}}"
            processed_text = processed_text.replace(full_item, cloze_item)
            cloze_counter += 1
    
    if cloze_counter > 1:  # If we found any numbered items
        cards.append(processed_text)
    
    return cards


def create_definition_cloze(text):
    """Create cloze deletions for definition patterns (term: definition)."""
    lines = text.split('\n')
    cards = []
    
    for line in lines:
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                term = parts[0].strip()
                definition = parts[1].strip()
                
                # Card 1: Hide the term
                card1 = line.replace(term, f"{{{{c1::{term}}}}}")
                cards.append(card1)
                
                # Card 2: Hide the definition
                card2 = line.replace(definition, f"{{{{c1::{definition}}}}}")
                cards.append(card2)
    
    return cards


def create_incremental_cloze(text, chunk_size=20):
    """Create incremental cloze cards revealing text progressively."""
    words = text.split()
    cards = []
    
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i+chunk_size])
        cloze_num = (i // chunk_size) + 1
        
        # Build the card with previous chunks visible
        card_text = ' '.join(words[:i]) + ' ' if i > 0 else ''
        card_text += f"{{{{c1::{chunk}}}}}"
        
        # Add remaining text as context (optional)
        if i + chunk_size < len(words):
            card_text += ' ' + ' '.join(words[i+chunk_size:])
        
        cards.append(card_text.strip())
    
    return cards


def process_text(text, mode='basic', keywords=None, chunk_size=20):
    """Process text based on selected mode."""
    if mode == 'basic':
        if not keywords:
            return []
        return create_basic_cloze(text, keywords)
    elif mode == 'sentence':
        return create_sentence_cloze(text)
    elif mode == 'list':
        return create_numbered_list_cloze(text)
    elif mode == 'definition':
        return create_definition_cloze(text)
    elif mode == 'incremental':
        return create_incremental_cloze(text, chunk_size)
    else:
        return []


def main():
    parser = argparse.ArgumentParser(
        description='Generate cloze deletion cards for Anki'
    )
    parser.add_argument(
        'input', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
        help='Input text file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), default=sys.stdout,
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '-m', '--mode', 
        choices=['basic', 'sentence', 'list', 'definition', 'incremental'],
        default='basic',
        help='Cloze generation mode'
    )
    parser.add_argument(
        '-k', '--keywords', nargs='+',
        help='Keywords for basic mode'
    )
    parser.add_argument(
        '-c', '--chunk-size', type=int, default=20,
        help='Chunk size for incremental mode (default: 20 words)'
    )
    parser.add_argument(
        '--csv', action='store_true',
        help='Output as CSV with Text column'
    )
    
    args = parser.parse_args()
    
    # Read input text
    text = args.input.read().strip()
    
    # Generate cloze cards
    cards = process_text(
        text, 
        mode=args.mode, 
        keywords=args.keywords,
        chunk_size=args.chunk_size
    )
    
    # Output cards
    if args.csv:
        writer = csv.writer(args.output)
        writer.writerow(['Text'])  # Header for Anki
        for card in cards:
            writer.writerow([card])
    else:
        for card in cards:
            args.output.write(card + '\n\n')


if __name__ == '__main__':
    main()