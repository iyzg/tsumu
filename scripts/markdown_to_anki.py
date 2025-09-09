#!/usr/bin/env python3
"""
Markdown to Anki Converter
Converts markdown notes into Anki flashcards using various patterns.
"""

import sys
import re
import argparse
from typing import List, Tuple, Optional
from anki_utils import AnkiFormatter, AnkiWriter, TextParser


class MarkdownParser:
    """Parse markdown and extract card-worthy content."""
    
    def __init__(self):
        self.formatter = AnkiFormatter()
        self.cards = []
    
    def parse_markdown(self, content: str) -> List[Tuple[str, str]]:
        """Parse markdown content and generate cards."""
        self.cards = []
        
        # Parse different patterns
        self._parse_headers_and_content(content)
        self._parse_definition_lists(content)
        self._parse_qa_blocks(content)
        self._parse_code_blocks(content)
        self._parse_bullet_lists(content)
        self._parse_tables(content)
        
        return self.cards
    
    def _parse_headers_and_content(self, content: str) -> None:
        """Create cards from headers and their content."""
        # Split by headers
        sections = re.split(r'^(#{1,6}\s+.+)$', content, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                header = sections[i].strip()
                body = sections[i + 1].strip()
                
                if body:
                    # Extract header level and text
                    match = re.match(r'^(#{1,6})\s+(.+)$', header)
                    if match:
                        level = len(match.group(1))
                        title = match.group(2)
                        
                        # Only create cards for h2 and h3 (usually most content-rich)
                        if level in [2, 3]:
                            # Clean up the body
                            body_lines = body.split('\n')
                            clean_body = []
                            
                            for line in body_lines:
                                # Stop at next header or empty section
                                if line.startswith('#'):
                                    break
                                clean_body.append(line)
                            
                            body_text = '\n'.join(clean_body).strip()
                            
                            if body_text and len(body_text) > 20:  # Minimum content
                                front = f"Explain: <b>{title}</b>"
                                back = self.formatter.process_text(body_text)
                                self.cards.append((front, back))
    
    def _parse_definition_lists(self, content: str) -> None:
        """Parse definition patterns (term: definition)."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Look for definition pattern
            if ':' in line and not line.startswith('#'):
                match = re.match(r'^([^:]+):\s*(.+)$', line.strip())
                if match:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()
                    
                    # Check if definition continues on next lines
                    j = i + 1
                    while j < len(lines) and lines[j].startswith('  '):
                        definition += ' ' + lines[j].strip()
                        j += 1
                    
                    if term and definition:
                        # Forward card
                        front = f"Define: <b>{term}</b>"
                        back = self.formatter.process_text(definition)
                        self.cards.append((front, back))
                        
                        # Reverse card
                        front = f"What term is defined as:<br><br>{self.formatter.process_text(definition)}"
                        back = term
                        self.cards.append((front, back))
    
    def _parse_qa_blocks(self, content: str) -> None:
        """Parse Q&A patterns."""
        # Pattern 1: Q: ... A: ...
        qa_pattern = r'Q:\s*(.+?)\s*A:\s*(.+?)(?=Q:|$)'
        matches = re.findall(qa_pattern, content, re.DOTALL)
        
        for question, answer in matches:
            front = self.formatter.process_text(question.strip())
            back = self.formatter.process_text(answer.strip())
            self.cards.append((front, back))
        
        # Pattern 2: Question marks followed by answer
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().endswith('?'):
                question = line.strip()
                # Look for answer in next non-empty line
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        answer = lines[j].strip()
                        front = self.formatter.process_text(question)
                        back = self.formatter.process_text(answer)
                        self.cards.append((front, back))
                        break
    
    def _parse_code_blocks(self, content: str) -> None:
        """Create cards from code blocks with descriptions."""
        # Find code blocks with language specified
        pattern = r'```(\w+)\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for language, code in matches:
            # Look for description before the code block
            code_start = content.find(f'```{language}\n{code}\n```')
            before_text = content[:code_start].strip().split('\n')
            
            if before_text:
                # Get the last line before code as description
                description = before_text[-1].strip()
                
                if description and not description.startswith('#'):
                    # Clean code
                    code_lines = code.strip().split('\n')
                    if len(code_lines) <= 15:  # Don't create cards for very long code
                        front = f"Write {language} code for:<br><br><b>{description}</b>"
                        # Escape HTML but preserve code formatting
                        escaped_code = self.formatter.escape_html(code)
                        back = f"<pre><code>{escaped_code}</code></pre>"
                        self.cards.append((front, back))
                        
                        # Also create a "what does this code do" card
                        front = f"What does this {language} code do?<br><br><pre><code>{escaped_code}</code></pre>"
                        back = description
                        self.cards.append((front, back))
    
    def _parse_bullet_lists(self, content: str) -> None:
        """Create cards from bullet point lists."""
        # Find bullet lists
        list_pattern = r'^[-*+]\s+(.+)$'
        lines = content.split('\n')
        
        current_list = []
        list_title = None
        
        for i, line in enumerate(lines):
            if re.match(list_pattern, line):
                # Extract item
                item = re.sub(r'^[-*+]\s+', '', line).strip()
                current_list.append(item)
                
                # Look for title if this is first item
                if len(current_list) == 1 and i > 0:
                    # Check previous line for title
                    prev_line = lines[i - 1].strip()
                    if prev_line and not prev_line.startswith('#'):
                        list_title = prev_line.rstrip(':')
            else:
                # End of list, create card if we have items
                if len(current_list) >= 3 and list_title:
                    front = f"List the items for:<br><br><b>{list_title}</b>"
                    back = '<br>'.join([f"• {item}" for item in current_list])
                    back = self.formatter.process_text(back)
                    self.cards.append((front, back))
                
                current_list = []
                list_title = None
    
    def _parse_tables(self, content: str) -> None:
        """Create cards from markdown tables."""
        # Simple table parser (header | cells)
        lines = content.split('\n')
        in_table = False
        headers = []
        rows = []
        
        for line in lines:
            if '|' in line:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Exclude empty first/last
                
                if not in_table:
                    headers = cells
                    in_table = True
                elif all(set(cell.strip()) <= {'-', ':'} for cell in cells):
                    # Separator line
                    continue
                else:
                    rows.append(cells)
            else:
                # End of table, create cards
                if in_table and headers and rows:
                    for row in rows:
                        if len(row) >= 2:
                            # Create card from first two columns
                            front = f"{headers[0]}: <b>{row[0]}</b>"
                            back = self.formatter.process_text(row[1])
                            
                            # Add additional columns if present
                            for i in range(2, min(len(headers), len(row))):
                                back += f"<br><br><b>{headers[i]}:</b> {row[i]}"
                            
                            self.cards.append((front, back))
                
                in_table = False
                headers = []
                rows = []


class MarkdownToAnki:
    """Main converter class."""
    
    def __init__(self):
        self.parser = MarkdownParser()
    
    def convert_file(self, input_file, output_file, min_cards: int = 1):
        """Convert markdown file to Anki cards."""
        content = input_file.read()
        
        # Parse markdown
        cards = self.parser.parse_markdown(content)
        
        # Filter out duplicates
        unique_cards = []
        seen = set()
        for card in cards:
            card_tuple = (card[0], card[1])
            if card_tuple not in seen:
                seen.add(card_tuple)
                unique_cards.append(card)
        
        # Only output if we have minimum number of cards
        if len(unique_cards) >= min_cards:
            AnkiWriter.write_csv(unique_cards, output_file)
            return len(unique_cards)
        
        return 0


def main():
    parser = argparse.ArgumentParser(
        description='Convert markdown notes to Anki flashcards',
        epilog='''
Supported patterns:
  - Headers with content (## Topic -> card)
  - Definition lists (term: definition)
  - Q&A blocks (Q: ... A: ...)
  - Code blocks with descriptions
  - Bullet lists with titles
  - Markdown tables
        '''
    )
    
    parser.add_argument(
        'input', nargs='?', type=argparse.FileType('r'), 
        default=sys.stdin,
        help='Input markdown file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), 
        default=sys.stdout,
        help='Output CSV file (default: stdout)'
    )
    parser.add_argument(
        '--min-cards', type=int, default=1,
        help='Minimum number of cards to generate output (default: 1)'
    )
    
    args = parser.parse_args()
    
    converter = MarkdownToAnki()
    num_cards = converter.convert_file(args.input, args.output, args.min_cards)
    
    if args.output != sys.stdout:
        print(f"Generated {num_cards} cards", file=sys.stderr)


if __name__ == '__main__':
    main()