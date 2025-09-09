#!/usr/bin/env python3
"""
CSV Formatter for Anki Import
Converts CSV data to Anki-compatible format with proper escaping and formatting.
"""

import csv
import sys
import argparse
import re


def escape_html(text):
    """Escape HTML characters for Anki."""
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def convert_latex(text):
    """Convert $...$ to \\(...\\) for MathJax compatibility in Anki."""
    # Convert display math $$...$$ to \[...\]
    text = re.sub(r'\$\$([^$]+)\$\$', r'\\[\1\\]', text)
    # Convert inline math $...$ to \(...\)
    text = re.sub(r'\$([^$]+)\$', r'\\(\1\\)', text)
    return text


def format_newlines(text):
    """Convert newlines to HTML breaks for Anki."""
    return text.replace('\n', '<br>')


def process_csv(input_file, output_file, delimiter=',', has_header=False, 
                escape=True, latex=True, newlines=True):
    """Process CSV file for Anki import."""
    
    reader = csv.reader(input_file, delimiter=delimiter)
    writer = csv.writer(output_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    
    if has_header:
        next(reader)  # Skip header row
    
    for row in reader:
        processed_row = []
        for field in row:
            if escape:
                field = escape_html(field)
            if latex:
                field = convert_latex(field)
            if newlines:
                field = format_newlines(field)
            processed_row.append(field)
        writer.writerow(processed_row)


def main():
    parser = argparse.ArgumentParser(
        description='Format CSV files for Anki import'
    )
    parser.add_argument(
        'input', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
        help='Input CSV file (default: stdin)'
    )
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), default=sys.stdout,
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '-d', '--delimiter', default=',',
        help='CSV delimiter (default: comma)'
    )
    parser.add_argument(
        '--header', action='store_true',
        help='Skip first row as header'
    )
    parser.add_argument(
        '--no-escape', action='store_true',
        help='Disable HTML escaping'
    )
    parser.add_argument(
        '--no-latex', action='store_true',
        help='Disable LaTeX conversion'
    )
    parser.add_argument(
        '--no-newlines', action='store_true',
        help='Disable newline to <br> conversion'
    )
    
    args = parser.parse_args()
    
    process_csv(
        args.input,
        args.output,
        delimiter=args.delimiter,
        has_header=args.header,
        escape=not args.no_escape,
        latex=not args.no_latex,
        newlines=not args.no_newlines
    )


if __name__ == '__main__':
    main()