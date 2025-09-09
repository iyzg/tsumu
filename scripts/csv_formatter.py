#!/usr/bin/env python3
"""
CSV Formatter for Anki Import
Converts CSV data to Anki-compatible format with proper escaping and formatting.
"""

import csv
import sys
import argparse
from anki_utils import AnkiFormatter


def process_csv(input_file, output_file, delimiter=',', has_header=False, 
                escape=True, latex=True, newlines=True):
    """Process CSV file for Anki import."""
    
    formatter = AnkiFormatter()
    reader = csv.reader(input_file, delimiter=delimiter)
    writer = csv.writer(output_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    
    if has_header:
        next(reader)  # Skip header row
    
    for row in reader:
        processed_row = []
        for field in row:
            field = formatter.process_text(field, escape, latex, newlines)
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