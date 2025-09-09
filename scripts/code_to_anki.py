#!/usr/bin/env python3
"""
Code Snippet to Anki Card Generator
Creates flashcards from code snippets with various patterns.
"""

import sys
import argparse
import re
import ast
from typing import List, Tuple, Optional, Dict
from anki_utils import AnkiFormatter, AnkiWriter


class CodeParser:
    """Parse code and extract educational content."""
    
    def __init__(self, language: str = 'python'):
        self.language = language
        self.formatter = AnkiFormatter()
    
    def parse_function(self, code: str) -> Dict:
        """Parse a function and extract its components."""
        info = {
            'name': None,
            'params': [],
            'return_type': None,
            'docstring': None,
            'body': None,
            'decorators': []
        }
        
        if self.language == 'python':
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        info['name'] = node.name
                        info['params'] = [arg.arg for arg in node.args.args]
                        
                        # Get return type if annotated
                        if node.returns:
                            info['return_type'] = ast.unparse(node.returns)
                        
                        # Get docstring
                        docstring = ast.get_docstring(node)
                        if docstring:
                            info['docstring'] = docstring
                        
                        # Get decorators
                        info['decorators'] = [ast.unparse(d) for d in node.decorator_list]
                        
                        # Get body (excluding docstring)
                        body_lines = code.split('\n')
                        start_line = node.lineno
                        info['body'] = '\n'.join(body_lines[start_line:])
                        
                        break
            except:
                pass
        
        return info
    
    def extract_comments(self, code: str) -> List[Tuple[str, str]]:
        """Extract comments and their associated code."""
        pairs = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Python comments
            if '#' in line and not line.strip().startswith('#'):
                code_part = line.split('#')[0].strip()
                comment_part = line.split('#', 1)[1].strip()
                if code_part and comment_part:
                    pairs.append((code_part, comment_part))
            
            # Standalone comments followed by code
            elif line.strip().startswith('#'):
                comment = line.strip()[1:].strip()
                # Look for code in next line
                if i + 1 < len(lines) and lines[i + 1].strip():
                    next_line = lines[i + 1].strip()
                    if not next_line.startswith('#'):
                        pairs.append((next_line, comment))
        
        return pairs
    
    def extract_patterns(self, code: str) -> List[Dict]:
        """Extract common programming patterns."""
        patterns = []
        
        # List comprehensions
        list_comp_pattern = r'\[.+\s+for\s+.+\s+in\s+.+\]'
        for match in re.finditer(list_comp_pattern, code):
            patterns.append({
                'type': 'list_comprehension',
                'code': match.group(0),
                'description': 'List comprehension'
            })
        
        # Lambda functions
        lambda_pattern = r'lambda\s+[^:]+:\s+.+'
        for match in re.finditer(lambda_pattern, code):
            patterns.append({
                'type': 'lambda',
                'code': match.group(0),
                'description': 'Lambda function'
            })
        
        # Decorator usage
        decorator_pattern = r'^@\w+.*$'
        for match in re.finditer(decorator_pattern, code, re.MULTILINE):
            patterns.append({
                'type': 'decorator',
                'code': match.group(0),
                'description': 'Decorator'
            })
        
        return patterns


class CodeCardGenerator:
    """Generate different types of cards from code."""
    
    def __init__(self, language: str = 'python'):
        self.parser = CodeParser(language)
        self.formatter = AnkiFormatter()
    
    def generate_syntax_cards(self, code: str, title: str = "Code") -> List[Tuple[str, str]]:
        """Generate cards for syntax understanding."""
        cards = []
        
        # Card 1: What does this code do?
        front = f"What does this {self.parser.language} code do?<br><br>"
        front += self._format_code(code)
        back = f"Analyze the code to understand its functionality"
        cards.append((front, back))
        
        # Card 2: Identify the output
        if 'print' in code or 'return' in code:
            front = f"What is the output/return value of this code?<br><br>"
            front += self._format_code(code)
            back = "Trace through the code to determine the output"
            cards.append((front, back))
        
        return cards
    
    def generate_function_cards(self, code: str) -> List[Tuple[str, str]]:
        """Generate cards from function definitions."""
        cards = []
        info = self.parser.parse_function(code)
        
        if info['name']:
            # Card 1: Function signature
            front = f"Write the function signature for: <b>{info['name']}</b>"
            if info['docstring']:
                front += f"<br><br>Purpose: {info['docstring'].split('.')[0]}"
            
            signature = f"def {info['name']}({', '.join(info['params'])})"
            if info['return_type']:
                signature += f" -> {info['return_type']}"
            back = self._format_code(signature)
            cards.append((front, back))
            
            # Card 2: Parameters
            if info['params']:
                front = f"What parameters does <b>{info['name']}</b> take?"
                back = '<br>'.join([f"• {param}" for param in info['params']])
                cards.append((front, back))
            
            # Card 3: Implementation
            if info['docstring']:
                front = f"Implement a function that:<br><br>{info['docstring']}"
                back = self._format_code(code)
                cards.append((front, back))
        
        return cards
    
    def generate_fill_in_cards(self, code: str, blanks: List[str]) -> List[Tuple[str, str]]:
        """Generate fill-in-the-blank cards."""
        cards = []
        
        for blank in blanks:
            if blank in code:
                # Create version with blank
                blanked_code = code.replace(blank, '___')
                
                front = f"Fill in the blank:<br><br>"
                front += self._format_code(blanked_code)
                back = f"<code>{self.formatter.escape_html(blank)}</code>"
                cards.append((front, back))
        
        return cards
    
    def generate_error_cards(self, code: str, errors: List[Dict]) -> List[Tuple[str, str]]:
        """Generate cards about common errors."""
        cards = []
        
        for error in errors:
            buggy_code = code.replace(error['correct'], error['buggy'])
            
            front = f"Find and fix the error in this code:<br><br>"
            front += self._format_code(buggy_code)
            
            back = f"Error: {error['description']}<br><br>"
            back += f"Fix: Replace <code>{self.formatter.escape_html(error['buggy'])}</code> "
            back += f"with <code>{self.formatter.escape_html(error['correct'])}</code>"
            
            cards.append((front, back))
        
        return cards
    
    def generate_pattern_cards(self, code: str) -> List[Tuple[str, str]]:
        """Generate cards for programming patterns."""
        cards = []
        patterns = self.parser.extract_patterns(code)
        
        for pattern in patterns:
            # Card 1: Identify pattern
            front = f"What programming pattern is this?<br><br>"
            front += self._format_code(pattern['code'])
            back = pattern['description']
            cards.append((front, back))
            
            # Card 2: When to use
            front = f"When would you use a {pattern['description']}?"
            back = self._get_pattern_use_case(pattern['type'])
            if back:
                cards.append((front, back))
        
        return cards
    
    def generate_comment_cards(self, code: str) -> List[Tuple[str, str]]:
        """Generate cards from code comments."""
        cards = []
        pairs = self.parser.extract_comments(code)
        
        for code_part, comment in pairs:
            # Card: What does this line do?
            front = f"What does this line do?<br><br>"
            front += self._format_code(code_part)
            back = comment
            cards.append((front, back))
            
            # Reverse card: Write code for
            front = f"Write code to: {comment}"
            back = self._format_code(code_part)
            cards.append((front, back))
        
        return cards
    
    def _format_code(self, code: str) -> str:
        """Format code for display in Anki."""
        escaped = self.formatter.escape_html(code)
        return f"<pre><code>{escaped}</code></pre>"
    
    def _get_pattern_use_case(self, pattern_type: str) -> Optional[str]:
        """Get use case description for a pattern."""
        use_cases = {
            'list_comprehension': "Use list comprehensions for creating lists from iterables with optional filtering, more readable and often faster than loops",
            'lambda': "Use lambda functions for short, simple functions that are used once, especially as arguments to functions like map, filter, or sort",
            'decorator': "Use decorators to modify or enhance functions without changing their code, common for logging, timing, or access control",
            'generator': "Use generators for memory-efficient iteration over large datasets or infinite sequences",
            'context_manager': "Use context managers (with statement) for resource management and ensuring cleanup"
        }
        return use_cases.get(pattern_type)


def process_code_file(input_file, output_file, card_types, language='python'):
    """Process a code file and generate cards."""
    generator = CodeCardGenerator(language)
    code = input_file.read()
    
    all_cards = []
    
    # Generate different card types
    if 'syntax' in card_types:
        all_cards.extend(generator.generate_syntax_cards(code))
    
    if 'function' in card_types:
        all_cards.extend(generator.generate_function_cards(code))
    
    if 'pattern' in card_types:
        all_cards.extend(generator.generate_pattern_cards(code))
    
    if 'comment' in card_types:
        all_cards.extend(generator.generate_comment_cards(code))
    
    # Write output
    AnkiWriter.write_csv(all_cards, output_file)
    return len(all_cards)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Anki cards from code snippets',
        epilog='''
Card types:
  syntax: What does this code do?
  function: Function signatures and parameters
  pattern: Programming patterns (list comp, lambda, etc.)
  comment: Cards from code comments
  fill: Fill-in-the-blank (requires --blanks)
  error: Find and fix errors (requires --errors-file)
        '''
    )
    
    parser.add_argument(
        'input', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin,
        help='Input code file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'),
        default=sys.stdout,
        help='Output CSV file (default: stdout)'
    )
    parser.add_argument(
        '-l', '--language', default='python',
        choices=['python', 'javascript', 'java', 'cpp'],
        help='Programming language'
    )
    parser.add_argument(
        '-t', '--types', nargs='+',
        choices=['syntax', 'function', 'pattern', 'comment', 'fill', 'error'],
        default=['syntax', 'function'],
        help='Card types to generate'
    )
    parser.add_argument(
        '--blanks', nargs='+',
        help='Terms to blank out for fill-in cards'
    )
    parser.add_argument(
        '--errors-file', type=argparse.FileType('r'),
        help='JSON file with error definitions'
    )
    
    args = parser.parse_args()
    
    generator = CodeCardGenerator(args.language)
    code = args.input.read()
    
    all_cards = []
    
    # Generate different card types
    if 'syntax' in args.types:
        all_cards.extend(generator.generate_syntax_cards(code))
    
    if 'function' in args.types:
        all_cards.extend(generator.generate_function_cards(code))
    
    if 'pattern' in args.types:
        all_cards.extend(generator.generate_pattern_cards(code))
    
    if 'comment' in args.types:
        all_cards.extend(generator.generate_comment_cards(code))
    
    if 'fill' in args.types and args.blanks:
        all_cards.extend(generator.generate_fill_in_cards(code, args.blanks))
    
    if 'error' in args.types and args.errors_file:
        import json
        errors = json.load(args.errors_file)
        all_cards.extend(generator.generate_error_cards(code, errors))
    
    # Write output
    AnkiWriter.write_csv(all_cards, args.output)
    
    if args.output != sys.stdout:
        print(f"Generated {len(all_cards)} cards from code", file=sys.stderr)


if __name__ == '__main__':
    main()