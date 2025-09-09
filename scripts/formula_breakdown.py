#!/usr/bin/env python3
"""
formula breakdown cards generator

creates anki cards that build up from simple components to complex formulas.
perfect for learning math, physics, chemistry, and other formula-heavy subjects.

usage:
    python formula_breakdown.py --formula "E = mc^2" --components "E:energy,m:mass,c:speed of light"
    python formula_breakdown.py formulas.txt -o cards.txt
    
input format (for file):
    E = mc^2 | E:energy, m:mass, c:speed of light | Einstein's mass-energy equivalence
    F = ma | F:force, m:mass, a:acceleration | Newton's second law
    
options:
    --reverse: also create reverse cards (formula -> description)
    --include-units: add unit information to cards
    --progressive: create progressive buildup cards
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from io_utils import (
    read_input, write_output,
    create_argument_parser, add_common_arguments
)


def parse_formula_line(line: str) -> Optional[Dict]:
    """
    parse a formula line into components.
    
    format: formula | components | description
    
    args:
        line: input line
        
    returns:
        dictionary with formula info or None
    """
    parts = line.split('|')
    if len(parts) < 2:
        return None
    
    formula = parts[0].strip()
    components_str = parts[1].strip()
    description = parts[2].strip() if len(parts) > 2 else ""
    
    # parse components (format: "var:meaning, var2:meaning2")
    components = {}
    for comp in components_str.split(','):
        comp = comp.strip()
        if ':' in comp:
            var, meaning = comp.split(':', 1)
            components[var.strip()] = meaning.strip()
    
    return {
        'formula': formula,
        'components': components,
        'description': description
    }


def extract_variables(formula: str) -> List[str]:
    """
    extract variables from a formula.
    
    args:
        formula: the formula string
        
    returns:
        list of unique variables in order of appearance
    """
    # common patterns for variables in formulas
    # single letters, greek letters, subscripted variables
    patterns = [
        r'[a-zA-Z]_\w+',  # subscripted variables first (e.g., v_0)
        r'\\[a-zA-Z]+',  # latex commands (e.g., \\theta)
        r'[a-zA-Z]',  # single letters (no word boundary to catch all)
    ]
    
    variables = []
    seen = set()
    skip_words = {'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt'}
    
    for pattern in patterns:
        for match in re.finditer(pattern, formula):
            var = match.group()
            if var not in seen and var not in skip_words:
                variables.append(var)
                seen.add(var)
    
    return variables


def create_component_cards(formula: str, components: Dict[str, str], 
                          description: str = "") -> List[Tuple[str, str]]:
    """
    create cards for formula components.
    
    args:
        formula: the formula
        components: dictionary of variable -> meaning
        description: optional formula description
        
    returns:
        list of (front, back) card tuples
    """
    cards = []
    
    # card 1: what does each variable mean?
    for var, meaning in components.items():
        front = f"In the formula {formula}, what does {var} represent?"
        back = meaning
        cards.append((front, back))
    
    # card 2: formula completion
    if len(components) > 1:
        # hide the right side of the equation
        if '=' in formula:
            left, right = formula.split('=', 1)
            front = f"Complete the formula: {left.strip()} = ?"
            back = formula
            if description:
                back += f"\n({description})"
            cards.append((front, back))
    
    # card 3: full formula identification
    if description:
        front = f"What formula is this describing?\n{description}"
        back = formula
        cards.append((front, back))
    
    return cards


def create_progressive_cards(formula: str, components: Dict[str, str],
                            description: str = "") -> List[Tuple[str, str]]:
    """
    create progressive buildup cards.
    
    args:
        formula: the formula
        components: dictionary of variable -> meaning
        description: optional formula description
        
    returns:
        list of (front, back) card tuples
    """
    cards = []
    
    # start with component definitions
    if len(components) >= 2:
        # card 1: just the components
        comp_list = [f"{var}: {meaning}" for var, meaning in components.items()]
        front = "Given these quantities:\n" + "\n".join(comp_list) + "\nWhat formula relates them?"
        back = formula
        if description:
            back += f"\n({description})"
        cards.append((front, back))
    
    # card 2: partial formula with one variable missing
    variables = extract_variables(formula)
    if len(variables) >= 3 and '=' in formula:
        left, right = formula.split('=', 1)
        # try to identify a variable to hide
        for var in variables:
            if var in right:
                # create a card with this variable as unknown
                front = f"Solve for {var}:\n{formula}"
                if var in components:
                    front += f"\n({var} = {components[var]})"
                back = f"Rearrange to isolate {var}"
                if description:
                    back += f"\n({description})"
                cards.append((front, back))
                break
    
    return cards


def create_unit_cards(formula: str, components: Dict[str, str],
                      units: Optional[Dict[str, str]] = None) -> List[Tuple[str, str]]:
    """
    create cards with unit information.
    
    args:
        formula: the formula
        components: dictionary of variable -> meaning
        units: optional dictionary of variable -> unit
        
    returns:
        list of (front, back) card tuples
    """
    cards = []
    
    # common units for physics formulas
    default_units = {
        'E': 'J (joules)',
        'F': 'N (newtons)',
        'm': 'kg (kilograms)',
        'a': 'm/s² (meters per second squared)',
        'v': 'm/s (meters per second)',
        't': 's (seconds)',
        'P': 'W (watts)',
        'W': 'J (joules)',
        'q': 'C (coulombs)',
        'V': 'V (volts)',
        'I': 'A (amperes)',
        'R': 'Ω (ohms)',
        'c': 'm/s (meters per second)',
    }
    
    if units is None:
        units = {}
    
    # add default units for known variables
    for var in components.keys():
        if var not in units and var in default_units:
            units[var] = default_units[var]
    
    # create unit cards
    for var, unit in units.items():
        if var in components:
            front = f"What is the SI unit for {components[var]} ({var}) in the formula {formula}?"
            back = unit
            cards.append((front, back))
    
    # dimensional analysis card
    if len(units) >= 2 and '=' in formula:
        front = f"Verify the dimensional consistency of: {formula}"
        unit_list = [f"{var}: {unit}" for var, unit in units.items()]
        back = "Units:\n" + "\n".join(unit_list)
        cards.append((front, back))
    
    return cards


def process_formulas(input_text: str, reverse: bool = False,
                     include_units: bool = False,
                     progressive: bool = False) -> List[Tuple[str, str]]:
    """
    process formulas from input text.
    
    args:
        input_text: input text with formulas
        reverse: create reverse cards
        include_units: add unit information
        progressive: create progressive buildup
        
    returns:
        list of (front, back) card tuples
    """
    cards = []
    lines = input_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        formula_info = parse_formula_line(line)
        if not formula_info:
            continue
        
        formula = formula_info['formula']
        components = formula_info['components']
        description = formula_info['description']
        
        # create basic component cards
        cards.extend(create_component_cards(formula, components, description))
        
        # create reverse cards if requested
        if reverse and description:
            cards.append((formula, description))
        
        # create progressive cards if requested
        if progressive:
            cards.extend(create_progressive_cards(formula, components, description))
        
        # create unit cards if requested
        if include_units:
            cards.extend(create_unit_cards(formula, components))
    
    return cards


def main():
    """main entry point."""
    parser = create_argument_parser(
        "formula breakdown generator",
        "generate anki cards for learning formulas"
    )
    
    # add common arguments
    add_common_arguments(parser)
    
    # add specific arguments
    parser.add_argument(
        "--formula",
        help="single formula to process"
    )
    parser.add_argument(
        "--components",
        help="components for single formula (format: 'var:meaning,var2:meaning2')"
    )
    parser.add_argument(
        "--description",
        help="description for single formula"
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="also create reverse cards (formula -> description)"
    )
    parser.add_argument(
        "--include-units",
        action="store_true",
        help="add unit information to cards"
    )
    parser.add_argument(
        "--progressive",
        action="store_true",
        help="create progressive buildup cards"
    )
    
    args = parser.parse_args()
    
    # handle single formula input
    if args.formula:
        if not args.components:
            print("error: --components required when using --formula", file=sys.stderr)
            return 1
        
        input_text = f"{args.formula} | {args.components}"
        if args.description:
            input_text += f" | {args.description}"
    else:
        # read from file or stdin
        input_text = read_input(args.input)
    
    if not input_text:
        print("error: no input provided", file=sys.stderr)
        return 1
    
    # process formulas
    cards = process_formulas(
        input_text,
        args.reverse,
        args.include_units,
        args.progressive
    )
    
    if not cards:
        print("warning: no cards generated", file=sys.stderr)
        return 1
    
    # write output
    write_output(cards, args.output)
    
    print(f"generated {len(cards)} formula cards", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())