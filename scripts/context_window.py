#!/usr/bin/env python3
"""
context window cards generator

creates anki cards with varying amounts of surrounding context for learning text in context.
starts with full context and gradually reduces to test true understanding.

usage:
    python context_window.py input.txt -o output.txt
    python context_window.py --text "The quick brown fox jumps over the lazy dog" --focus "brown fox"
    
options:
    --window-sizes: comma-separated list of context window sizes (default: "full,10,5,2,0")
    --focus-pattern: regex pattern to identify focus phrases (default: matches quoted text)
    --separator: card separator (default: "---")
    --include-hints: add hints about context size on cards
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from io_utils import (
    read_input, write_output, format_card,
    create_argument_parser, add_common_arguments
)


def extract_focus_phrases(text: str, pattern: Optional[str] = None) -> List[Tuple[str, int, int]]:
    """
    extract phrases to focus on from the text.
    
    args:
        text: input text
        pattern: regex pattern to match focus phrases
        
    returns:
        list of (phrase, start_index, end_index) tuples
    """
    if pattern:
        # use custom pattern
        matches = []
        for match in re.finditer(pattern, text):
            matches.append((match.group(), match.start(), match.end()))
        return matches
    
    # default: find quoted phrases or capitalized proper nouns
    patterns = [
        (r'"([^"]+)"', True),  # quoted phrases - extract content
        (r"'([^']+)'", True),  # single-quoted phrases - extract content
        (r'\*\*([^*]+)\*\*', True),  # markdown bold - extract content
        (r'__([^_]+)__', True),  # markdown bold alt - extract content
        (r'(?<!\*)\*([^*]+)\*(?!\*)', True),  # markdown italic - extract content
        (r'(?<!_)_([^_]+)_(?!_)', True),  # markdown italic alt - extract content
    ]
    
    matches = []
    seen_positions = set()
    for pattern, extract_group in patterns:
        for match in re.finditer(pattern, text):
            # avoid duplicate matches at same position
            if match.start() in seen_positions:
                continue
            seen_positions.add(match.start())
            
            # extract the content without the markers if needed
            if extract_group and match.groups():
                content = match.group(1)
            else:
                content = match.group()
            matches.append((content, match.start(), match.end()))
    
    # if no matches found, extract important-looking phrases
    if not matches:
        # find capitalized sequences (potential proper nouns/important terms)
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        for match in re.finditer(pattern, text):
            if len(match.group()) > 3:  # skip short words like "The"
                matches.append((match.group(), match.start(), match.end()))
    
    return sorted(matches, key=lambda x: x[1])  # sort by position


def get_context_window(text: str, start: int, end: int, window_size: str, 
                      text_lines: Optional[List[str]] = None) -> Tuple[str, str, str]:
    """
    get context window around a phrase.
    
    args:
        text: full text
        start: start index of focus phrase
        end: end index of focus phrase
        window_size: "full", or number of words/lines
        text_lines: pre-split lines for line-based windows
        
    returns:
        (before_context, focus_phrase, after_context)
    """
    focus = text[start:end]
    
    if window_size == "full":
        return text[:start], focus, text[end:]
    
    try:
        size = int(window_size)
    except ValueError:
        # treat as full if can't parse
        return text[:start], focus, text[end:]
    
    if size == 0:
        return "", focus, ""
    
    # word-based window
    words_before = text[:start].split()
    words_after = text[end:].split()
    
    # take last N words before and first N words after
    context_before = " ".join(words_before[-size:]) if words_before else ""
    context_after = " ".join(words_after[:size]) if words_after else ""
    
    # add ellipsis if truncated
    if len(words_before) > size and size > 0:
        context_before = "..." + context_before
    if len(words_after) > size and size > 0:
        context_after = context_after + "..."
    
    return context_before, focus, context_after


def create_context_card(phrase: str, before: str, after: str, 
                        window_size: str, include_hint: bool = False) -> dict:
    """
    create a card for a phrase with context.
    
    args:
        phrase: the focus phrase
        before: context before the phrase
        after: context after the phrase
        window_size: size of the context window
        include_hint: whether to include hint about context size
        
    returns:
        card dictionary with front and back
    """
    # create cloze deletion for the focus phrase
    if before or after:
        front = f"{before}[...]{after}".strip()
    else:
        front = "[...]"
    
    # optionally add hint
    if include_hint:
        if window_size == "full":
            hint = " (full context)"
        elif window_size == "0":
            hint = " (no context)"
        else:
            hint = f" (±{window_size} words)"
        front += hint
    
    back = phrase
    
    # for very short phrases AND when there's significant context, add context to answer
    if len(phrase.split()) <= 2 and (before or after) and window_size != "0":
        # show a bit of context on the answer side too
        context_preview = []
        if before:
            preview_words = before.replace("...", "").strip().split()[-3:]
            if preview_words:
                context_preview.append("..." + " ".join(preview_words))
        
        context_preview.append(f"[{phrase}]")
        
        if after:
            preview_words = after.replace("...", "").strip().split()[:3]
            if preview_words:
                context_preview.append(" ".join(preview_words) + "...")
        
        if len(context_preview) > 1:  # only use if we actually have context
            back = " ".join(context_preview)
        else:
            back = phrase
    
    return {"front": front, "back": back}


def generate_context_cards(text: str, window_sizes: List[str], 
                          focus_pattern: Optional[str] = None,
                          include_hints: bool = False) -> List[dict]:
    """
    generate context window cards from text.
    
    args:
        text: input text
        window_sizes: list of window sizes to use
        focus_pattern: regex pattern for focus phrases
        include_hints: whether to include context size hints
        
    returns:
        list of card dictionaries
    """
    cards = []
    
    # extract focus phrases
    focus_phrases = extract_focus_phrases(text, focus_pattern)
    
    if not focus_phrases:
        print("warning: no focus phrases found in text", file=sys.stderr)
        return cards
    
    # generate cards for each phrase and window size
    for phrase, start, end in focus_phrases:
        for window_size in window_sizes:
            before, focus, after = get_context_window(text, start, end, window_size)
            
            card = create_context_card(
                focus, before, after, window_size, include_hints
            )
            cards.append(card)
    
    return cards


def main():
    """main entry point."""
    parser = create_argument_parser(
        "context window cards generator",
        "generate anki cards with varying context windows"
    )
    
    # add common arguments
    add_common_arguments(parser)
    
    # add specific arguments
    parser.add_argument(
        "--text",
        help="text to process (alternative to input file)"
    )
    parser.add_argument(
        "--focus",
        help="specific phrase to focus on"
    )
    parser.add_argument(
        "--window-sizes",
        default="full,10,5,2,0",
        help="comma-separated list of context window sizes"
    )
    parser.add_argument(
        "--focus-pattern",
        help="regex pattern to identify focus phrases"
    )
    parser.add_argument(
        "--include-hints",
        action="store_true",
        help="add hints about context size on cards"
    )
    parser.add_argument(
        "--min-phrase-length",
        type=int,
        default=2,
        help="minimum word count for focus phrases"
    )
    
    args = parser.parse_args()
    
    # get input text
    if args.text:
        text = args.text
    else:
        text = read_input(args.input)
    
    if not text:
        print("error: no input text provided", file=sys.stderr)
        return 1
    
    # if specific focus phrase provided, use it
    if args.focus:
        # create a temporary text with the focus phrase marked
        text = text.replace(args.focus, f'"{args.focus}"')
    
    # parse window sizes
    window_sizes = [s.strip() for s in args.window_sizes.split(",")]
    
    # generate cards
    cards = generate_context_cards(
        text,
        window_sizes,
        args.focus_pattern,
        args.include_hints
    )
    
    if not cards:
        print("warning: no cards generated", file=sys.stderr)
        return 1
    
    # format and write output
    card_tuples = [(card["front"], card["back"]) for card in cards]
    write_output(card_tuples, args.output)
    
    print(f"generated {len(cards)} context window cards", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())