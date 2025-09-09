#!/usr/bin/env python3
"""
Smart text parser that automatically detects content types and generates appropriate Anki cards.

Detects:
- Definitions (term : description or term - description)
- Questions and answers (? ending indicates question)
- Lists and enumerations
- Code blocks
- Formulas and equations
- Examples (lines starting with e.g., ex:, example:)
- Key concepts (bold text, capitalized terms)
"""

import re
import sys
from typing import List, Tuple, Dict, Any
from anki_utils import AnkiFormatter, AnkiWriter, TextParser


class ContentDetector:
    """Detects different types of content in text."""
    
    @staticmethod
    def is_definition(line: str) -> bool:
        """Check if line is a definition."""
        patterns = [
            r'^[A-Za-z][^:]{2,50}:\s+.+',  # Term: definition
            r'^[A-Za-z][^-]{2,50}\s+-\s+.+',  # Term - definition
            r'^\*\*[^*]+\*\*:?\s+.+',  # **Term**: definition
        ]
        return any(re.match(p, line.strip()) for p in patterns)
    
    @staticmethod
    def is_question(line: str) -> bool:
        """Check if line is a question."""
        return line.strip().endswith('?')
    
    @staticmethod
    def is_formula(line: str) -> bool:
        """Check if line contains mathematical formula."""
        patterns = [
            r'\$[^$]+\$',  # LaTeX inline
            r'\$\$[^$]+\$\$',  # LaTeX display
            r'=',  # Equations
            r'[+\-*/^]',  # Math operators
        ]
        return any(re.search(p, line) for p in patterns[:2]) or \
               (re.search(r'=', line) and re.search(r'[+\-*/^()]', line))
    
    @staticmethod
    def is_example(line: str) -> bool:
        """Check if line is an example."""
        patterns = [
            r'^(e\.g\.|eg\.|example:|ex:|for example)',
            r'^Example \d+:',
            r'^\d+\.',  # Numbered examples
        ]
        return any(re.match(p, line.strip(), re.IGNORECASE) for p in patterns)
    
    @staticmethod
    def is_list_item(line: str) -> bool:
        """Check if line is a list item."""
        patterns = [
            r'^[-•*]\s+',  # Bullet points
            r'^\d+[\.)]\s+',  # Numbered lists
            r'^[a-z][\.)]\s+',  # Letter lists
        ]
        return any(re.match(p, line.strip()) for p in patterns)
    
    @staticmethod
    def extract_key_concepts(text: str) -> List[str]:
        """Extract key concepts from text (bold, capitalized terms)."""
        concepts = []
        
        # Bold text
        bold_matches = re.findall(r'\*\*([^*]+)\*\*', text)
        concepts.extend(bold_matches)
        
        # Capitalized terms (2+ words)
        cap_matches = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        concepts.extend(cap_matches)
        
        # Quoted terms
        quote_matches = re.findall(r'"([^"]+)"', text)
        concepts.extend(quote_matches)
        
        return list(set(concepts))  # Remove duplicates


class SmartParser:
    """Intelligently parse text and generate appropriate Anki cards."""
    
    def __init__(self):
        self.formatter = AnkiFormatter()
        self.detector = ContentDetector()
        self.parser = TextParser()
    
    def parse_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse text and identify content blocks with their types."""
        blocks = []
        lines = text.split('\n')
        current_block = {'type': None, 'content': [], 'metadata': {}}
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if not stripped:
                # Empty line - save current block if it has content
                if current_block['content']:
                    blocks.append(current_block)
                    current_block = {'type': None, 'content': [], 'metadata': {}}
                i += 1
                continue
            
            # Detect content type
            if self.detector.is_definition(stripped):
                self._add_definition_block(blocks, stripped)
            elif self.detector.is_question(stripped):
                # Look for answer in next lines
                answer_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() and not self.detector.is_question(lines[i]):
                    answer_lines.append(lines[i].strip())
                    i += 1
                i -= 1  # Back up one since we'll increment at loop end
                
                if answer_lines:
                    blocks.append({
                        'type': 'qa',
                        'content': [stripped, '\n'.join(answer_lines)],
                        'metadata': {}
                    })
            elif self.detector.is_formula(stripped):
                blocks.append({
                    'type': 'formula',
                    'content': [stripped],
                    'metadata': {'has_latex': '$' in stripped}
                })
            elif self.detector.is_example(stripped):
                blocks.append({
                    'type': 'example',
                    'content': [stripped],
                    'metadata': {}
                })
            elif self.detector.is_list_item(stripped):
                # Collect all consecutive list items
                list_items = [stripped]
                i += 1
                while i < len(lines) and self.detector.is_list_item(lines[i].strip()):
                    list_items.append(lines[i].strip())
                    i += 1
                i -= 1  # Back up one
                
                blocks.append({
                    'type': 'list',
                    'content': list_items,
                    'metadata': {'count': len(list_items)}
                })
            else:
                # Generic text - check for key concepts
                concepts = self.detector.extract_key_concepts(stripped)
                if concepts:
                    blocks.append({
                        'type': 'concept',
                        'content': [stripped],
                        'metadata': {'concepts': concepts}
                    })
                else:
                    current_block['type'] = 'text'
                    current_block['content'].append(stripped)
            
            i += 1
        
        # Don't forget last block
        if current_block['content']:
            blocks.append(current_block)
        
        return blocks
    
    def _add_definition_block(self, blocks: List[Dict], line: str):
        """Parse and add a definition block."""
        # Try different separators
        for separator in [':', ' - ', ' – ']:
            if separator in line:
                parts = line.split(separator, 1)
                if len(parts) == 2:
                    term = parts[0].strip().strip('*')
                    definition = parts[1].strip()
                    blocks.append({
                        'type': 'definition',
                        'content': [term, definition],
                        'metadata': {}
                    })
                    return
    
    def blocks_to_cards(self, blocks: List[Dict[str, Any]]) -> List[Tuple[str, str, str]]:
        """Convert content blocks to Anki cards."""
        cards = []
        
        for block in blocks:
            block_type = block['type']
            content = block['content']
            metadata = block.get('metadata', {})
            
            if block_type == 'definition':
                if len(content) >= 2:
                    term = self.formatter.process_text(content[0])
                    definition = self.formatter.process_text(content[1])
                    cards.append((term, definition, 'definition'))
                    # Also create reverse card
                    cards.append((f"What term means: {definition}", term, 'definition_reverse'))
            
            elif block_type == 'qa':
                if len(content) >= 2:
                    question = self.formatter.process_text(content[0])
                    answer = self.formatter.process_text(content[1])
                    cards.append((question, answer, 'qa'))
            
            elif block_type == 'formula':
                formula = content[0]
                formatted = self.formatter.process_text(formula)
                # Extract formula name if present
                if '=' in formula:
                    parts = formula.split('=', 1)
                    cards.append((f"Formula for {parts[0].strip()}", formatted, 'formula'))
                else:
                    cards.append(("What does this formula represent?", formatted, 'formula'))
            
            elif block_type == 'example':
                example = self.formatter.process_text('\n'.join(content))
                cards.append(("Provide an example:", example, 'example'))
            
            elif block_type == 'list':
                items = [self.formatter.process_text(item) for item in content]
                list_text = '<br>'.join(items)
                count = metadata.get('count', len(items))
                cards.append((f"List {count} items:", list_text, 'list'))
                
                # Also create individual cards for each item if list is long
                if count > 3:
                    for i, item in enumerate(items):
                        cards.append((f"Item {i+1} of {count}:", item, 'list_item'))
            
            elif block_type == 'concept':
                text = self.formatter.process_text('\n'.join(content))
                concepts = metadata.get('concepts', [])
                for concept in concepts:
                    cards.append((f"Explain: {concept}", text, 'concept'))
            
            elif block_type == 'text':
                # For generic text, create a summary card
                text = self.formatter.process_text('\n'.join(content))
                if len(text) > 50:  # Only for substantial text
                    cards.append(("Summarize:", text, 'summary'))
        
        return cards
    
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """Analyze text and return statistics about content types."""
        blocks = self.parse_text(text)
        
        stats = {
            'total_blocks': len(blocks),
            'types': {},
            'cards_potential': 0
        }
        
        for block in blocks:
            block_type = block['type']
            stats['types'][block_type] = stats['types'].get(block_type, 0) + 1
            
            # Estimate cards per block type
            if block_type in ['definition', 'qa']:
                stats['cards_potential'] += 2  # Front and back
            elif block_type == 'list':
                count = block.get('metadata', {}).get('count', 1)
                stats['cards_potential'] += 1 + (count if count > 3 else 0)
            elif block_type == 'concept':
                concepts = block.get('metadata', {}).get('concepts', [])
                stats['cards_potential'] += len(concepts)
            else:
                stats['cards_potential'] += 1
        
        return stats


def main():
    """Process text input and generate Anki cards."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Smart text parser for automatic Anki card generation'
    )
    parser.add_argument(
        'input', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin,
        help='Input text file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'),
        default=sys.stdout,
        help='Output CSV file (default: stdout)'
    )
    parser.add_argument(
        '--analyze', action='store_true',
        help='Analyze content without generating cards'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Show detailed processing information'
    )
    
    args = parser.parse_args()
    
    # Read input
    text = args.input.read()
    
    # Create parser
    smart_parser = SmartParser()
    
    if args.analyze:
        # Just analyze and show statistics
        stats = smart_parser.analyze_content(text)
        print(f"Content Analysis:", file=sys.stderr)
        print(f"  Total blocks: {stats['total_blocks']}", file=sys.stderr)
        print(f"  Potential cards: {stats['cards_potential']}", file=sys.stderr)
        print(f"  Content types found:", file=sys.stderr)
        for content_type, count in stats['types'].items():
            print(f"    - {content_type}: {count}", file=sys.stderr)
    else:
        # Parse and generate cards
        blocks = smart_parser.parse_text(text)
        
        if args.verbose:
            print(f"Detected {len(blocks)} content blocks", file=sys.stderr)
        
        cards = smart_parser.blocks_to_cards(blocks)
        
        if args.verbose:
            print(f"Generated {len(cards)} cards", file=sys.stderr)
        
        # Write output
        AnkiWriter.write_csv(cards, args.output)
        
        if args.output != sys.stdout:
            print(f"Wrote {len(cards)} cards to {args.output.name}", file=sys.stderr)


if __name__ == '__main__':
    main()