#!/usr/bin/env python3
"""
Fact to Cards Converter for Anki
Converts structured facts into multiple flashcard types.
"""

import sys
import argparse
import json
import csv
import re
from typing import List, Dict, Any, Tuple


class FactConverter:
    """Convert facts to various card formats."""
    
    def __init__(self):
        self.cards = []
    
    def parse_fact(self, text: str) -> Dict[str, Any]:
        """Parse a fact from text format."""
        lines = text.strip().split('\n')
        fact = {}
        current_key = None
        current_value = []
        
        for line in lines:
            # Check if line starts a new field (contains ':')
            if ':' in line and not line.startswith(' '):
                if current_key:
                    fact[current_key] = '\n'.join(current_value).strip()
                
                parts = line.split(':', 1)
                current_key = parts[0].strip().lower()
                current_value = [parts[1].strip()] if len(parts) > 1 else []
            else:
                # Continuation of previous field
                current_value.append(line.strip())
        
        # Don't forget the last field
        if current_key:
            fact[current_key] = '\n'.join(current_value).strip()
        
        return fact
    
    def create_basic_cards(self, fact: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Create basic front/back cards from fact."""
        cards = []
        
        # Get the main subject (title, name, term, or concept)
        subject = (fact.get('title') or fact.get('name') or 
                  fact.get('term') or fact.get('concept', 'Subject'))
        
        # Create cards for each field
        skip_fields = {'title', 'name', 'term', 'concept', 'tags', 'source'}
        
        for field, value in fact.items():
            if field not in skip_fields and value:
                # Forward card: field -> value
                front = f"<b>{subject}</b><br><br>{field.title()}?"
                back = value
                cards.append((front, back))
                
                # Reverse card for definitions
                if field in ['definition', 'meaning', 'description']:
                    front_rev = f"What term is defined as:<br><br>{value}"
                    back_rev = subject
                    cards.append((front_rev, back_rev))
        
        return cards
    
    def create_list_cards(self, fact: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Create cards for list-based facts."""
        cards = []
        subject = (fact.get('title') or fact.get('name') or 
                  fact.get('topic', 'Subject'))
        
        for field, value in fact.items():
            # Check if value contains a list
            if '\n' in value or '•' in value or '-' in value:
                items = self._extract_list_items(value)
                
                if len(items) > 1:
                    # Card asking for all items
                    front = f"<b>{subject}</b><br><br>List all {field}:"
                    back = '<br>'.join(f"• {item}" for item in items)
                    cards.append((front, back))
                    
                    # Individual cards for each item
                    for i, item in enumerate(items, 1):
                        front = f"<b>{subject}</b><br><br>{field.title()} #{i}?"
                        back = item
                        cards.append((front, back))
        
        return cards
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from text."""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Remove common list markers
            line = re.sub(r'^[-•*]\s*', '', line)
            line = re.sub(r'^\d+[\.)]\s*', '', line)
            
            if line:
                items.append(line)
        
        return items
    
    def create_comparison_cards(self, facts: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
        """Create comparison cards between multiple facts."""
        cards = []
        
        if len(facts) < 2:
            return cards
        
        # Find common fields
        common_fields = set(facts[0].keys())
        for fact in facts[1:]:
            common_fields &= set(fact.keys())
        
        # Remove metadata fields
        common_fields -= {'tags', 'source', 'notes'}
        
        # Create comparison cards
        for field in common_fields:
            if field in ['title', 'name', 'term']:
                continue
                
            # Create a comparison table
            comparison = f"<b>Compare {field.title()}</b><br><br>"
            comparison += "<table border='1'>"
            
            for fact in facts:
                name = fact.get('title') or fact.get('name', 'Item')
                value = fact.get(field, 'N/A')
                comparison += f"<tr><td><b>{name}</b></td><td>{value}</td></tr>"
            
            comparison += "</table>"
            
            front = f"Compare {field} between: {', '.join([f.get('title', f.get('name', 'Item')) for f in facts])}"
            cards.append((front, comparison))
        
        return cards
    
    def create_example_cards(self, fact: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Create cards from examples in facts."""
        cards = []
        subject = (fact.get('title') or fact.get('name') or 
                  fact.get('term', 'Subject'))
        
        # Look for example fields
        example_fields = ['example', 'examples', 'usage', 'application']
        
        for field in example_fields:
            if field in fact:
                examples = self._extract_list_items(fact[field])
                
                for i, example in enumerate(examples, 1):
                    # Ask to identify the concept from example
                    front = f"What concept does this example illustrate?<br><br>{example}"
                    back = subject
                    cards.append((front, back))
                    
                    # Ask for example of concept
                    if i == 1:  # Only for first example to avoid too many cards
                        front = f"Give an example of:<br><br><b>{subject}</b>"
                        back = example
                        cards.append((front, back))
        
        return cards
    
    def create_formula_cards(self, fact: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Create cards for mathematical formulas."""
        cards = []
        subject = fact.get('title') or fact.get('name', 'Formula')
        
        formula_fields = ['formula', 'equation', 'expression']
        
        for field in formula_fields:
            if field in fact:
                formula = fact[field]
                
                # Convert LaTeX if needed
                formula = re.sub(r'\$([^$]+)\$', r'\\(\1\\)', formula)
                
                # Card 1: Name to formula
                front = f"Write the formula for:<br><br><b>{subject}</b>"
                back = formula
                cards.append((front, back))
                
                # Card 2: Formula to name
                front = f"What is this formula?<br><br>{formula}"
                back = subject
                cards.append((front, back))
                
                # Card 3: Variables explanation if present
                if 'variables' in fact or 'where' in fact:
                    vars_text = fact.get('variables') or fact.get('where')
                    front = f"In the {subject} formula:<br><br>{formula}<br><br>What do the variables represent?"
                    back = vars_text
                    cards.append((front, back))
        
        return cards


def process_facts_file(input_file, output_file, card_types, format='csv'):
    """Process a file containing facts."""
    converter = FactConverter()
    
    # Read and parse facts
    content = input_file.read()
    
    # Split by double newlines to separate facts
    fact_texts = content.split('\n\n')
    facts = []
    
    for fact_text in fact_texts:
        if fact_text.strip():
            fact = converter.parse_fact(fact_text)
            if fact:
                facts.append(fact)
    
    # Generate cards based on types
    all_cards = []
    
    for fact in facts:
        if 'basic' in card_types:
            all_cards.extend(converter.create_basic_cards(fact))
        if 'list' in card_types:
            all_cards.extend(converter.create_list_cards(fact))
        if 'example' in card_types:
            all_cards.extend(converter.create_example_cards(fact))
        if 'formula' in card_types:
            all_cards.extend(converter.create_formula_cards(fact))
    
    if 'comparison' in card_types and len(facts) > 1:
        all_cards.extend(converter.create_comparison_cards(facts))
    
    # Output cards
    if format == 'csv':
        writer = csv.writer(output_file, delimiter='\t')
        for front, back in all_cards:
            writer.writerow([front, back])
    else:  # json
        json.dump([{'front': f, 'back': b} for f, b in all_cards], 
                 output_file, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Convert structured facts to Anki flashcards',
        epilog='''
Example fact format:
  Title: Python Lists
  Definition: Ordered, mutable sequences of objects
  Examples:
  - [1, 2, 3]
  - ["a", "b", "c"]
  Key Methods:
  - append(): Add item to end
  - pop(): Remove and return last item
        '''
    )
    parser.add_argument(
        'input', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
        help='Input facts file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), default=sys.stdout,
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '-t', '--types', nargs='+',
        choices=['basic', 'list', 'comparison', 'example', 'formula'],
        default=['basic'],
        help='Card types to generate'
    )
    parser.add_argument(
        '-f', '--format', choices=['csv', 'json'], default='csv',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    process_facts_file(args.input, args.output, args.types, args.format)


if __name__ == '__main__':
    main()