#!/usr/bin/env python3
"""
Batch Processing Tool for Anki Card Generation

Process multiple files or directories to generate flashcards in bulk.
Supports various input formats and conversion types.

Examples:
    python batch_processor.py notes/*.md -t markdown -o output/
    python batch_processor.py code_examples/ -t code --recursive
    python batch_processor.py facts.txt vocab.txt -t fact --merge
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path
import json
import csv
from typing import List, Dict, Any


class BatchProcessor:
    """Handles batch processing of files for Anki card generation."""
    
    def __init__(self, output_dir: str = None, merge: bool = False):
        """
        Initialize batch processor.
        
        Args:
            output_dir: Directory for output files
            merge: Whether to merge all outputs into single file
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.merge = merge
        self.results = []
        
    def process_file(self, file_path: Path, converter_type: str, 
                    converter_args: List[str] = None) -> Dict[str, Any]:
        """
        Process a single file with specified converter.
        
        Args:
            file_path: Path to input file
            converter_type: Type of converter to use
            converter_args: Additional arguments for converter
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'input': str(file_path),
            'converter': converter_type,
            'status': 'pending',
            'output': None,
            'error': None,
            'card_count': 0
        }
        
        try:
            # Determine script to use
            script_map = {
                'markdown': 'markdown_to_anki.py',
                'code': 'code_to_anki.py',
                'fact': 'fact_to_cards.py',
                'cloze': 'cloze_generator.py',
                'csv': 'csv_formatter.py'
            }
            
            if converter_type not in script_map:
                raise ValueError(f"Unknown converter type: {converter_type}")
            
            script_path = Path(__file__).parent / script_map[converter_type]
            
            # Prepare output file
            if self.merge:
                output_file = self.output_dir / f"merged_{converter_type}_cards.csv"
            else:
                output_file = self.output_dir / f"{file_path.stem}_{converter_type}_cards.csv"
            
            # Build command
            cmd = [sys.executable, str(script_path)]
            
            # Add input file
            with open(file_path, 'r', encoding='utf-8') as f:
                input_text = f.read()
            
            # Add converter-specific arguments
            if converter_args:
                cmd.extend(converter_args)
            
            # Add output file
            cmd.extend(['-o', str(output_file)])
            
            # Run converter
            process = subprocess.run(
                cmd,
                input=input_text,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if process.returncode == 0:
                result['status'] = 'success'
                result['output'] = str(output_file)
                
                # Count generated cards
                if output_file.exists():
                    with open(output_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f, delimiter='\t')
                        result['card_count'] = sum(1 for _ in reader) - 1  # Subtract header
            else:
                result['status'] = 'error'
                result['error'] = process.stderr or "Unknown error"
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def process_directory(self, dir_path: Path, pattern: str = '*', 
                         recursive: bool = False, converter_type: str = 'markdown',
                         converter_args: List[str] = None) -> List[Dict[str, Any]]:
        """
        Process all matching files in directory.
        
        Args:
            dir_path: Directory to process
            pattern: File pattern to match
            recursive: Whether to search recursively
            converter_type: Type of converter to use
            converter_args: Additional arguments for converter
            
        Returns:
            List of processing results
        """
        results = []
        
        if recursive:
            files = dir_path.rglob(pattern)
        else:
            files = dir_path.glob(pattern)
        
        for file_path in files:
            if file_path.is_file():
                result = self.process_file(file_path, converter_type, converter_args)
                results.append(result)
                self.results.append(result)
        
        return results
    
    def merge_outputs(self, output_file: Path = None):
        """
        Merge all successful outputs into single file.
        
        Args:
            output_file: Path for merged output
        """
        if not output_file:
            output_file = self.output_dir / 'merged_cards.csv'
        
        all_cards = []
        
        for result in self.results:
            if result['status'] == 'success' and result['output']:
                output_path = Path(result['output'])
                if output_path.exists():
                    with open(output_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f, delimiter='\t')
                        # Skip header for all but first file
                        if all_cards:
                            next(reader)
                        all_cards.extend(reader)
        
        # Write merged file
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(all_cards)
        
        print(f"Merged {len(all_cards) - 1} cards to {output_file}")
    
    def print_summary(self):
        """Print processing summary."""
        total = len(self.results)
        successful = sum(1 for r in self.results if r['status'] == 'success')
        failed = sum(1 for r in self.results if r['status'] == 'error')
        total_cards = sum(r['card_count'] for r in self.results)
        
        print("\n" + "=" * 50)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 50)
        print(f"Files processed: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total cards generated: {total_cards}")
        
        if failed > 0:
            print("\nFailed files:")
            for result in self.results:
                if result['status'] == 'error':
                    print(f"  - {result['input']}: {result['error']}")
        
        print("\nOutput files:")
        for result in self.results:
            if result['status'] == 'success':
                print(f"  - {result['output']} ({result['card_count']} cards)")


def main():
    parser = argparse.ArgumentParser(
        description='Batch process files for Anki card generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'inputs', nargs='+',
        help='Input files or directories to process'
    )
    parser.add_argument(
        '-t', '--type', 
        choices=['markdown', 'code', 'fact', 'cloze', 'csv'],
        default='markdown',
        help='Type of converter to use (default: markdown)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory for generated files (default: current directory)'
    )
    parser.add_argument(
        '-p', '--pattern', default='*',
        help='File pattern to match when processing directories (default: *)'
    )
    parser.add_argument(
        '-r', '--recursive', action='store_true',
        help='Recursively process subdirectories'
    )
    parser.add_argument(
        '--merge', action='store_true',
        help='Merge all outputs into single file'
    )
    parser.add_argument(
        '--converter-args', nargs=argparse.REMAINDER,
        help='Additional arguments to pass to converter'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show what would be processed without actually processing'
    )
    parser.add_argument(
        '--config', type=argparse.FileType('r'),
        help='JSON configuration file with processing options'
    )
    
    args = parser.parse_args()
    
    # Load config if provided
    if args.config:
        config = json.load(args.config)
        # Override args with config values
        for key, value in config.items():
            if hasattr(args, key):
                setattr(args, key, value)
    
    # Create processor
    processor = BatchProcessor(
        output_dir=args.output_dir,
        merge=args.merge
    )
    
    # Process inputs
    for input_path in args.inputs:
        path = Path(input_path)
        
        if not path.exists():
            print(f"Warning: {input_path} does not exist, skipping")
            continue
        
        if path.is_file():
            if args.dry_run:
                print(f"Would process file: {path}")
            else:
                result = processor.process_file(
                    path, 
                    args.type,
                    args.converter_args
                )
                print(f"Processed {path}: {result['status']}")
        
        elif path.is_dir():
            if args.dry_run:
                pattern = args.pattern
                if args.recursive:
                    files = list(path.rglob(pattern))
                else:
                    files = list(path.glob(pattern))
                print(f"Would process {len(files)} files from {path}")
                for f in files[:5]:  # Show first 5
                    print(f"  - {f}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more")
            else:
                results = processor.process_directory(
                    path,
                    args.pattern,
                    args.recursive,
                    args.type,
                    args.converter_args
                )
                print(f"Processed {len(results)} files from {path}")
    
    if not args.dry_run:
        # Merge if requested
        if args.merge and processor.results:
            processor.merge_outputs()
        
        # Print summary
        processor.print_summary()


if __name__ == '__main__':
    main()