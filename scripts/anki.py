#!/usr/bin/env python3
"""
Unified CLI interface for Anki flashcard generation tools.

This script provides a single entry point for all card generation utilities.

Usage:
    python anki.py <command> [options]
    
Commands:
    csv         Format CSV files for Anki import
    cloze       Generate cloze deletion cards
    markdown    Convert markdown to flashcards
    code        Generate cards from code snippets
    image       Create image occlusion cards
    fact        Convert facts to Q&A cards
    mnemonic    Generate mnemonic cards using memory techniques
    vocabulary  Generate comprehensive vocabulary flashcards
    poetry      Generate cards for memorizing poetry and verse
    
Examples:
    python anki.py markdown notes.md -o cards.csv
    python anki.py cloze text.txt --type sentence -o cloze.csv
    python anki.py code example.py -t syntax -o code_cards.csv
"""

import argparse
import sys
import subprocess
from pathlib import Path

# Script mapping
COMMANDS = {
    'csv': {
        'script': 'csv_formatter.py',
        'help': 'Format CSV files for Anki import'
    },
    'cloze': {
        'script': 'cloze_generator.py', 
        'help': 'Generate cloze deletion cards from text'
    },
    'markdown': {
        'script': 'markdown_to_anki.py',
        'help': 'Convert markdown notes to flashcards'
    },
    'code': {
        'script': 'code_to_anki.py',
        'help': 'Generate cards from code snippets'
    },
    'image': {
        'script': 'image_occlusion.py',
        'help': 'Create image occlusion cards'
    },
    'fact': {
        'script': 'fact_to_cards.py',
        'help': 'Convert facts to Q&A cards'
    },
    'mnemonic': {
        'script': 'mnemonic_generator.py',
        'help': 'Generate mnemonic cards using memory techniques'
    },
    'vocabulary': {
        'script': 'vocabulary_cards.py',
        'help': 'Generate comprehensive vocabulary flashcards'
    },
    'poetry': {
        'script': 'poetry_memorization.py',
        'help': 'Generate cards for memorizing poetry and verse'
    }
}


def main():
    parser = argparse.ArgumentParser(
        description='Unified Anki flashcard generation toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )
    
    # Create subparser for each command
    for cmd, info in COMMANDS.items():
        subparser = subparsers.add_parser(
            cmd,
            help=info['help'],
            add_help=False  # Let the actual script handle its own help
        )
        # Capture all remaining arguments to pass to the script
        subparser.add_argument(
            'args',
            nargs=argparse.REMAINDER,
            help='Arguments to pass to the script'
        )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Get script path
    script_dir = Path(__file__).parent
    script_path = script_dir / COMMANDS[args.command]['script']
    
    if not script_path.exists():
        print(f"Error: Script {script_path} not found", file=sys.stderr)
        return 1
    
    # Run the selected script with remaining arguments
    try:
        # Filter out the '--' separator if present
        script_args = args.args
        if script_args and script_args[0] == '--':
            script_args = script_args[1:]
        
        # Pass stdin through to the subprocess
        result = subprocess.run(
            [sys.executable, str(script_path)] + script_args,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            check=False
        )
        return result.returncode
    except Exception as e:
        print(f"Error running {args.command}: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())