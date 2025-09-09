#!/usr/bin/env python3
"""
overlapping cloze deletion tool - creates multiple overlapping cloze cards from marked text.

inspired by gwern's mnemo3.hs - generates all possible combinations of cloze deletions
for text with delimiter-marked answers.

example usage:
    echo "david hume was born in %1711% in %edinburgh%" | python overlapping_cloze.py
    
    python overlapping_cloze.py --delimiter @ < facts.txt > cards.tsv
    
    # with custom delimiter
    echo "the @pythagorean theorem@ states that @a²+b²=c²@" | python overlapping_cloze.py --delimiter @
"""

import argparse
import re
import sys
from itertools import product
from typing import List, Tuple, Union
from io_utils import (
    read_input, write_output,
    create_argument_parser, add_common_arguments
)


class ClozeElement:
    """represents either a question part or an answer part of the text."""
    
    def __init__(self, content: str, is_answer: bool = False):
        self.content = content
        self.is_answer = is_answer
    
    def __repr__(self):
        return f"{'Answer' if self.is_answer else 'Question'}({self.content!r})"


def parse_text(text: str, delimiter: str = '%') -> List[ClozeElement]:
    """
    parse text with delimited answers into list of elements.
    
    args:
        text: input text with marked answers (e.g., "born in %1711%")
        delimiter: character used to mark answers (default: %)
    
    returns:
        list of ClozeElement objects
    
    example:
        >>> parse_text("david hume was born in %1711%")
        [Question('david hume was born in '), Answer('1711')]
    """
    # escape delimiter for regex if needed
    escaped_delim = re.escape(delimiter)
    
    # split by delimiter while keeping the delimiter
    pattern = f'({escaped_delim}[^{escaped_delim}]+{escaped_delim})'
    parts = re.split(pattern, text)
    
    elements = []
    for part in parts:
        if not part:
            continue
            
        # check if this is an answer (surrounded by delimiters)
        if part.startswith(delimiter) and part.endswith(delimiter):
            # strip the delimiters
            answer = part[len(delimiter):-len(delimiter)]
            if answer:  # only add non-empty answers
                elements.append(ClozeElement(answer, is_answer=True))
        else:
            # this is a question part
            if part:  # only add non-empty questions
                elements.append(ClozeElement(part, is_answer=False))
    
    return elements


def generate_combinations(elements: List[ClozeElement]) -> List[Tuple[str, str]]:
    """
    generate all possible cloze deletion combinations.
    
    for n answers, generates 2^n - 1 combinations (excluding the one with no blanks).
    
    args:
        elements: list of parsed text elements
    
    returns:
        list of (question, answer) tuples
    
    example:
        for text with 2 answers, generates:
        - first answer blanked, second shown
        - first shown, second blanked  
        - both blanked
    """
    # extract just the answers
    answers = [elem for elem in elements if elem.is_answer]
    
    if not answers:
        return []
    
    cards = []
    
    # generate all possible combinations of showing/hiding answers
    # use product to get all binary combinations
    for show_pattern in product([True, False], repeat=len(answers)):
        # skip the case where all answers are shown (no blanks)
        if all(show_pattern):
            continue
        
        # build the question and collect hidden answers
        question_parts = []
        hidden_answers = []
        answer_index = 0
        
        for elem in elements:
            if elem.is_answer:
                if show_pattern[answer_index]:
                    # show this answer in the question
                    question_parts.append(elem.content)
                else:
                    # blank this answer
                    question_parts.append("____")
                    hidden_answers.append(elem.content)
                answer_index += 1
            else:
                # regular text, always show
                question_parts.append(elem.content)
        
        # create the card if there are hidden answers
        if hidden_answers:
            question = ''.join(question_parts)
            answer = ', '.join(hidden_answers)
            cards.append((question, answer))
    
    return cards


def process_line(line: str, delimiter: str = '%') -> List[str]:
    """
    process a single line of text and return formatted cards.
    
    args:
        line: input line with marked answers
        delimiter: character used to mark answers
    
    returns:
        list of tab-separated question-answer pairs
    """
    # parse the line
    elements = parse_text(line, delimiter)
    
    # generate all combinations
    cards = generate_combinations(elements)
    
    # format as tab-separated values
    return [f"{question}\t{answer}" for question, answer in cards]


def main():
    """main entry point for the overlapping cloze tool."""
    parser = create_argument_parser(
        'overlapping cloze deletion tool',
        'generate overlapping cloze deletion cards from marked text'
    )
    
    # add common arguments (input, output, separator)
    add_common_arguments(parser)
    
    # add specific arguments for this tool
    parser.add_argument(
        '--answer-delimiter',
        default='%',
        help='delimiter character for marking answers in input text (default: %%)'
    )
    
    # update epilog with examples
    parser.epilog = """
examples:
    echo "david hume was born in %1711%" | python overlapping_cloze.py
    python overlapping_cloze.py facts.txt --answer-delimiter @ -o cards.tsv
    echo "the @capital@ of @france@ is @paris@" | python overlapping_cloze.py --answer-delimiter @
    """
    
    args = parser.parse_args()
    
    # read input using io_utils
    input_text = read_input(args.input)
    
    if not input_text:
        print("error: no input provided", file=sys.stderr)
        return 1
    
    lines = input_text.strip().split('\n')
    all_cards = []
    
    # process each line
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # generate cards for this line
        cards = process_line(line, args.answer_delimiter)
        
        # convert to tuples for io_utils
        for card in cards:
            parts = card.split('\t')
            if len(parts) == 2:
                all_cards.append((parts[0], parts[1]))
    
    # write output using io_utils
    if all_cards:
        write_output(all_cards, args.output)
    
    # show statistics if verbose
    if args.verbose:
        print(f"generated {len(all_cards)} cards from {len(lines)} lines", 
              file=sys.stderr)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())