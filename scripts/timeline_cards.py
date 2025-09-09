#!/usr/bin/env python3
"""
Timeline Cards Generator

Creates flashcards for learning chronological information and timelines.
Generates various card types to test temporal relationships and dates.

Usage:
    python timeline_cards.py -i events.txt -o timeline_cards.txt
    python timeline_cards.py -i history.txt -o cards.txt --relative --absolute --sequence
    
Input format:
    1492 | Columbus discovers America
    1776 | American Declaration of Independence
    1789 | French Revolution begins
    1969 | Moon landing
    
Card types generated:
    - Absolute dates: What year did X happen?
    - Relative timing: What came before/after X?
    - Sequence ordering: Order these events chronologically
    - Time gaps: How many years between X and Y?
    - Period questions: What happened in the 1960s?
"""

import argparse
import sys
import random
from typing import List, Tuple, Dict
from datetime import datetime
from io_utils import format_card, create_argument_parser, add_common_arguments


def parse_timeline_input(content: str) -> List[Tuple[str, str]]:
    """
    Parse timeline input into (date, event) tuples.
    
    Args:
        content: Input text with date | event format
        
    Returns:
        List of (date, event) tuples
    """
    events = []
    
    for line in content.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if '|' in line:
            parts = line.split('|', 1)
            if len(parts) == 2:
                date = parts[0].strip()
                event = parts[1].strip()
                if date and event:
                    events.append((date, event))
    
    return sorted(events, key=lambda x: parse_date_for_sorting(x[0]))


def parse_date_for_sorting(date_str: str) -> float:
    """
    Convert date string to sortable number.
    Handles years, year ranges, decades, centuries, BCE/CE.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Numeric value for sorting
    """
    date_str = date_str.upper().strip()
    
    # Handle BCE/BC dates
    bce_multiplier = -1 if any(marker in date_str for marker in ['BCE', 'BC', 'B.C.']) else 1
    
    # Extract numeric part
    import re
    numbers = re.findall(r'-?\d+', date_str)
    
    if numbers:
        # Take the first number (for ranges, use start date)
        year = float(numbers[0])
        
        # Handle century notation (e.g., "19th century" = 1800s)
        if 'CENTURY' in date_str:
            if 'TH' in date_str or 'ST' in date_str or 'ND' in date_str or 'RD' in date_str:
                # Convert ordinal century to year (19th century = 1801-1900, sort by 1850)
                century_num = abs(year)
                year = (century_num - 1) * 100 + 50
        
        return year * bce_multiplier
    
    return 0


def generate_absolute_date_cards(events: List[Tuple[str, str]]) -> List[str]:
    """
    Generate cards asking for absolute dates.
    
    Args:
        events: List of (date, event) tuples
        
    Returns:
        List of formatted cards
    """
    cards = []
    
    for date, event in events:
        # Event to date
        front = f"What year/date: {event}?"
        back = date
        cards.append(format_card(front, back))
        
        # Date to event
        front = f"What happened in {date}?"
        back = event
        cards.append(format_card(front, back))
    
    return cards


def generate_relative_timing_cards(events: List[Tuple[str, str]], 
                                  window_size: int = 3) -> List[str]:
    """
    Generate cards asking about relative timing (before/after).
    
    Args:
        events: Sorted list of (date, event) tuples
        window_size: Number of nearby events to consider
        
    Returns:
        List of formatted cards
    """
    cards = []
    
    for i, (date, event) in enumerate(events):
        # Before questions
        if i > 0:
            before_idx = max(0, i - window_size)
            for j in range(before_idx, i):
                before_date, before_event = events[j]
                front = f"What came before {event} ({date})?"
                back = f"{before_event} ({before_date})"
                cards.append(format_card(front, back))
        
        # After questions
        if i < len(events) - 1:
            after_idx = min(len(events), i + window_size + 1)
            for j in range(i + 1, after_idx):
                after_date, after_event = events[j]
                front = f"What came after {event} ({date})?"
                back = f"{after_event} ({after_date})"
                cards.append(format_card(front, back))
        
        # Between questions (if there are events on both sides)
        if 0 < i < len(events) - 1:
            before_date, before_event = events[i-1]
            after_date, after_event = events[i+1]
            front = f"What happened between {before_event} and {after_event}?"
            back = f"{event} ({date})"
            cards.append(format_card(front, back))
    
    return cards


def generate_sequence_cards(events: List[Tuple[str, str]], 
                           sequence_length: int = 3) -> List[str]:
    """
    Generate cards for ordering events chronologically.
    
    Args:
        events: List of (date, event) tuples
        sequence_length: Number of events to include in each sequence
        
    Returns:
        List of formatted cards
    """
    cards = []
    
    if len(events) < sequence_length:
        return cards
    
    # Generate sequences from consecutive events
    for i in range(len(events) - sequence_length + 1):
        sequence = events[i:i + sequence_length]
        
        # Shuffle for the question
        shuffled = list(sequence)
        random.shuffle(shuffled)
        
        # Create the card
        front = "Order chronologically:\n"
        for _, event in shuffled:
            front += f"• {event}\n"
        
        back = "Correct order:\n"
        for date, event in sequence:
            back += f"{date}: {event}\n"
        
        cards.append(format_card(front.strip(), back.strip()))
    
    return cards


def generate_time_gap_cards(events: List[Tuple[str, str]]) -> List[str]:
    """
    Generate cards asking about time gaps between events.
    
    Args:
        events: List of (date, event) tuples
        
    Returns:
        List of formatted cards
    """
    cards = []
    
    for i in range(len(events) - 1):
        date1, event1 = events[i]
        date2, event2 = events[i + 1]
        
        # Try to parse years for calculation
        try:
            year1 = parse_date_for_sorting(date1)
            year2 = parse_date_for_sorting(date2)
            
            if year1 and year2:
                gap = abs(year2 - year1)
                
                # Only create card if gap is meaningful
                if gap > 0:
                    front = f"How many years between {event1} and {event2}?"
                    back = f"{int(gap)} years\n({date1} to {date2})"
                    cards.append(format_card(front, back))
        except:
            continue
    
    return cards


def generate_period_cards(events: List[Tuple[str, str]]) -> List[str]:
    """
    Generate cards grouping events by time period.
    
    Args:
        events: List of (date, event) tuples
        
    Returns:
        List of formatted cards
    """
    cards = []
    
    # Group by decade/century
    periods: Dict[str, List[Tuple[str, str]]] = {}
    
    for date, event in events:
        try:
            year = parse_date_for_sorting(date)
            if year > 0:
                # Group by decade for recent events
                if year >= 1800:
                    decade = int(year // 10) * 10
                    period = f"{decade}s"
                # Group by century for older events
                else:
                    century = int(year // 100) + 1
                    period = f"{century}th century"
                
                if period not in periods:
                    periods[period] = []
                periods[period].append((date, event))
        except:
            continue
    
    # Create cards for periods with multiple events
    for period, period_events in periods.items():
        if len(period_events) >= 2:
            front = f"What events happened in the {period}?"
            back = "\n".join([f"• {event} ({date})" for date, event in period_events])
            cards.append(format_card(front, back))
    
    return cards


def generate_timeline_cards(content: str, 
                           absolute: bool = True,
                           relative: bool = True,
                           sequence: bool = True,
                           gaps: bool = True,
                           periods: bool = True,
                           window_size: int = 3,
                           sequence_length: int = 3) -> str:
    """
    Generate all types of timeline cards from input.
    
    Args:
        content: Input text with timeline data
        absolute: Generate absolute date cards
        relative: Generate relative timing cards
        sequence: Generate sequence ordering cards
        gaps: Generate time gap cards
        periods: Generate period grouping cards
        window_size: Window for relative timing cards
        sequence_length: Length of sequences to order
        
    Returns:
        Formatted cards as string
    """
    events = parse_timeline_input(content)
    
    if not events:
        return "# No timeline events found in input\n"
    
    all_cards = []
    
    if absolute:
        cards = generate_absolute_date_cards(events)
        if cards:
            all_cards.append("# Absolute Date Cards")
            all_cards.extend(cards)
    
    if relative:
        cards = generate_relative_timing_cards(events, window_size)
        if cards:
            all_cards.append("\n# Relative Timing Cards")
            all_cards.extend(cards)
    
    if sequence:
        cards = generate_sequence_cards(events, sequence_length)
        if cards:
            all_cards.append("\n# Sequence Ordering Cards")
            all_cards.extend(cards)
    
    if gaps:
        cards = generate_time_gap_cards(events)
        if cards:
            all_cards.append("\n# Time Gap Cards")
            all_cards.extend(cards)
    
    if periods:
        cards = generate_period_cards(events)
        if cards:
            all_cards.append("\n# Period Grouping Cards")
            all_cards.extend(cards)
    
    return '\n'.join(all_cards)


def main():
    """Main entry point for timeline cards generator."""
    parser = create_argument_parser(
        'Timeline Cards Generator',
        'Generate flashcards for learning chronological information'
    )
    add_common_arguments(parser)
    
    # Card type options
    parser.add_argument('--absolute', action='store_true', default=True,
                       help='Generate absolute date cards')
    parser.add_argument('--no-absolute', dest='absolute', action='store_false',
                       help='Skip absolute date cards')
    parser.add_argument('--relative', action='store_true', default=True,
                       help='Generate relative timing cards')
    parser.add_argument('--no-relative', dest='relative', action='store_false',
                       help='Skip relative timing cards')
    parser.add_argument('--sequence', action='store_true', default=True,
                       help='Generate sequence ordering cards')
    parser.add_argument('--no-sequence', dest='sequence', action='store_false',
                       help='Skip sequence ordering cards')
    parser.add_argument('--gaps', action='store_true', default=True,
                       help='Generate time gap cards')
    parser.add_argument('--no-gaps', dest='gaps', action='store_false',
                       help='Skip time gap cards')
    parser.add_argument('--periods', action='store_true', default=True,
                       help='Generate period grouping cards')
    parser.add_argument('--no-periods', dest='periods', action='store_false',
                       help='Skip period grouping cards')
    
    # Configuration options
    parser.add_argument('--window-size', type=int, default=3,
                       help='Number of nearby events for relative timing (default: 3)')
    parser.add_argument('--sequence-length', type=int, default=3,
                       help='Number of events in sequence cards (default: 3)')
    
    args = parser.parse_args()
    
    # Read input
    if args.input:
        with open(args.input, 'r') as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    # Generate cards
    output = generate_timeline_cards(
        content,
        absolute=args.absolute,
        relative=args.relative,
        sequence=args.sequence,
        gaps=args.gaps,
        periods=args.periods,
        window_size=args.window_size,
        sequence_length=args.sequence_length
    )
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Generated timeline cards written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()