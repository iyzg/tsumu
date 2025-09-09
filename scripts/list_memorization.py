#!/usr/bin/env python3
"""
list memorization tool - generates comprehensive cards for memorizing ordered lists.

inspired by gwern's mnemo4.hs - creates ordinal position, before/after, and succession
questions to thoroughly memorize the order of items in a list.

example usage:
    echo -e "mercury\\nvenus\\nearth\\nmars" | python list_memorization.py
    
    python list_memorization.py --context "president" < presidents.txt > president_cards.tsv
    
    # with custom context word
    echo -e "shang\\nzhou\\nhan" | python list_memorization.py --context "dynasty"
"""

import argparse
import sys
from typing import List, Tuple, Optional


def format_ordinal(n: int) -> str:
    """
    convert number to ordinal string (1st, 2nd, 3rd, etc).
    
    args:
        n: positive integer
    
    returns:
        ordinal string representation
    
    examples:
        >>> format_ordinal(1)
        '1st'
        >>> format_ordinal(22)
        '22nd'
        >>> format_ordinal(103)
        '103rd'
    """
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def generate_ordinal_cards(items: List[str], context: str = "") -> List[Tuple[str, str]]:
    """
    generate ordinal position cards (position → item and item → position).
    
    args:
        items: list of items to memorize
        context: optional context word for questions (e.g., "dynasty", "president")
    
    returns:
        list of (question, answer) tuples
    """
    cards = []
    context_str = f" {context}" if context else ""
    
    for i, item in enumerate(items, 1):
        ordinal = format_ordinal(i)
        
        # position → item
        cards.append((f"What{context_str} was {ordinal}?", item))
        
        # item → position
        cards.append((f"What position{context_str} was {item}?", ordinal))
    
    return cards


def generate_before_after_cards(items: List[str], context: str = "") -> List[Tuple[str, str]]:
    """
    generate before/after relationship cards.
    
    args:
        items: list of items to memorize
        context: optional context word for questions
    
    returns:
        list of (question, answer) tuples
    """
    cards = []
    context_str = f" {context}" if context else ""
    
    for i, item in enumerate(items):
        # what came before this item?
        if i > 0:
            cards.append((
                f"What{context_str} came before {item}?",
                items[i - 1]
            ))
            cards.append((
                f"What{context_str} preceded {item}?",
                items[i - 1]
            ))
        
        # what came after this item?
        if i < len(items) - 1:
            cards.append((
                f"What{context_str} did {item} come before?",
                items[i + 1]
            ))
            cards.append((
                f"What{context_str} succeeded {item}?",
                items[i + 1]
            ))
    
    return cards


def generate_all_cards(items: List[str], context: str = "") -> List[Tuple[str, str]]:
    """
    generate all types of cards for list memorization.
    
    args:
        items: list of items to memorize
        context: optional context word for questions
    
    returns:
        list of all (question, answer) tuples
    """
    cards = []
    
    # add ordinal position cards
    cards.extend(generate_ordinal_cards(items, context))
    
    # add before/after relationship cards
    cards.extend(generate_before_after_cards(items, context))
    
    return cards


def process_list(items: List[str], context: str = "") -> List[str]:
    """
    process a list of items and return formatted cards.
    
    args:
        items: list of items to memorize
        context: optional context word for questions
    
    returns:
        list of tab-separated question-answer pairs
    """
    if not items:
        return []
    
    # generate all cards
    cards = generate_all_cards(items, context)
    
    # format as tab-separated values
    return [f"{question}\t{answer}" for question, answer in cards]


def main():
    """main entry point for the list memorization tool."""
    parser = argparse.ArgumentParser(
        description='generate cards for memorizing ordered lists',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
    echo -e "mercury\\\\nvenus\\\\nearth" | %(prog)s
    
    %(prog)s --context "president" < presidents.txt > cards.tsv
    
    echo -e "shang\\\\nzhou\\\\nhan" | %(prog)s --context "dynasty"
        """
    )
    
    parser.add_argument(
        '--context', '-c',
        default='',
        help='context word for questions (e.g., "dynasty", "president")'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='show statistics about generated cards'
    )
    
    parser.add_argument(
        '--skip-ordinal',
        action='store_true',
        help='skip ordinal position cards'
    )
    
    parser.add_argument(
        '--skip-relations',
        action='store_true',
        help='skip before/after relationship cards'
    )
    
    args = parser.parse_args()
    
    # read items from stdin
    items = [line.strip() for line in sys.stdin if line.strip()]
    
    if not items:
        print("Error: No items provided", file=sys.stderr)
        return 1
    
    # generate cards based on options
    cards = []
    
    if not args.skip_ordinal:
        cards.extend(generate_ordinal_cards(items, args.context))
    
    if not args.skip_relations:
        cards.extend(generate_before_after_cards(items, args.context))
    
    # format and output cards
    for question, answer in cards:
        print(f"{question}\t{answer}")
    
    # show statistics if verbose
    if args.verbose:
        ordinal_count = len(items) * 2 if not args.skip_ordinal else 0
        
        # calculate relationship cards
        relation_count = 0
        if not args.skip_relations:
            # each middle item has 4 cards, first and last have 2 each
            if len(items) > 1:
                relation_count = 2 + 2  # first and last items
                if len(items) > 2:
                    relation_count += (len(items) - 2) * 4  # middle items
        
        total = ordinal_count + relation_count
        
        print(f"\n# generated {total} cards from {len(items)} items:", 
              file=sys.stderr)
        if not args.skip_ordinal:
            print(f"#   - {ordinal_count} ordinal position cards", file=sys.stderr)
        if not args.skip_relations:
            print(f"#   - {relation_count} relationship cards", file=sys.stderr)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())