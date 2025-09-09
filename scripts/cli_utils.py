#!/usr/bin/env python3
"""
Common CLI utilities for Anki card generation scripts.

Provides shared functionality for argument parsing, file I/O,
and error handling across all card generation tools.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List, TextIO, Callable, Any


class CLIBase:
    """Base class for CLI applications with common functionality."""
    
    def __init__(self, description: str, epilog: str = None):
        """
        Initialize CLI base.
        
        Args:
            description: Program description
            epilog: Additional help text
        """
        self.parser = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog
        )
        self.setup_common_args()
    
    def setup_common_args(self):
        """Set up common command-line arguments."""
        self.parser.add_argument(
            'input', nargs='?', type=argparse.FileType('r', encoding='utf-8'),
            default=sys.stdin,
            help='Input file (default: stdin)'
        )
        self.parser.add_argument(
            '-o', '--output', type=argparse.FileType('w', encoding='utf-8'),
            default=sys.stdout,
            help='Output file (default: stdout)'
        )
        self.parser.add_argument(
            '-v', '--verbose', action='store_true',
            help='Enable verbose output'
        )
        self.parser.add_argument(
            '--demo', action='store_true',
            help='Run demo with example data'
        )
    
    def add_argument(self, *args, **kwargs):
        """Add custom argument to parser."""
        return self.parser.add_argument(*args, **kwargs)
    
    def add_argument_group(self, *args, **kwargs):
        """Add argument group to parser."""
        return self.parser.add_argument_group(*args, **kwargs)
    
    def parse_args(self, args=None):
        """Parse command-line arguments."""
        return self.parser.parse_args(args)
    
    def read_input(self, input_file: TextIO) -> str:
        """
        Read input from file or stdin.
        
        Args:
            input_file: File object to read from
            
        Returns:
            Input text
        """
        try:
            return input_file.read()
        except Exception as e:
            self.error(f"Error reading input: {e}")
    
    def write_output(self, output_file: TextIO, content: str):
        """
        Write output to file or stdout.
        
        Args:
            output_file: File object to write to
            content: Content to write
        """
        try:
            output_file.write(content)
            if output_file != sys.stdout:
                output_file.close()
        except Exception as e:
            self.error(f"Error writing output: {e}")
    
    def log(self, message: str, verbose_only: bool = False):
        """
        Log message to stderr.
        
        Args:
            message: Message to log
            verbose_only: Only log if verbose mode is enabled
        """
        if not verbose_only or (hasattr(self, 'args') and self.args.verbose):
            print(message, file=sys.stderr)
    
    def error(self, message: str, exit_code: int = 1):
        """
        Print error message and exit.
        
        Args:
            message: Error message
            exit_code: Exit code
        """
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(exit_code)
    
    def run_demo(self, demo_function: Callable):
        """
        Run demo mode with example data.
        
        Args:
            demo_function: Function to call for demo
        """
        print("=" * 60)
        print("DEMO MODE")
        print("=" * 60)
        demo_function()
        print("=" * 60)
    
    def validate_file_exists(self, file_path: str) -> Path:
        """
        Validate that a file exists.
        
        Args:
            file_path: Path to file
            
        Returns:
            Path object if file exists
        """
        path = Path(file_path)
        if not path.exists():
            self.error(f"File not found: {file_path}")
        return path
    
    def validate_directory_exists(self, dir_path: str) -> Path:
        """
        Validate that a directory exists.
        
        Args:
            dir_path: Path to directory
            
        Returns:
            Path object if directory exists
        """
        path = Path(dir_path)
        if not path.exists():
            self.error(f"Directory not found: {dir_path}")
        if not path.is_dir():
            self.error(f"Not a directory: {dir_path}")
        return path


class ProgressTracker:
    """Track and display progress for long-running operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize progress tracker.
        
        Args:
            total: Total number of items
            description: Description of operation
        """
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = None
    
    def start(self):
        """Start progress tracking."""
        import time
        self.start_time = time.time()
        self.update(0)
    
    def update(self, count: int = 1):
        """
        Update progress.
        
        Args:
            count: Number of items processed
        """
        self.current += count
        percentage = (self.current / self.total * 100) if self.total > 0 else 0
        
        # Simple progress bar
        bar_length = 40
        filled = int(bar_length * self.current / self.total) if self.total > 0 else 0
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\r{self.description}: [{bar}] {percentage:.1f}% ({self.current}/{self.total})", 
              end='', file=sys.stderr)
        
        if self.current >= self.total:
            print(file=sys.stderr)  # New line at completion
    
    def finish(self):
        """Finish progress tracking and show summary."""
        if self.start_time:
            import time
            elapsed = time.time() - self.start_time
            print(f"Completed in {elapsed:.2f} seconds", file=sys.stderr)


def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        prompt: Confirmation prompt
        default: Default response if user just presses Enter
        
    Returns:
        True if confirmed, False otherwise
    """
    suffix = " [Y/n]" if default else " [y/N]"
    response = input(prompt + suffix + " ").strip().lower()
    
    if not response:
        return default
    return response in ['y', 'yes']


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def create_safe_filename(text: str, max_length: int = 50) -> str:
    """
    Create safe filename from text.
    
    Args:
        text: Text to convert to filename
        max_length: Maximum filename length
        
    Returns:
        Safe filename
    """
    import re
    # Remove unsafe characters
    safe = re.sub(r'[^a-zA-Z0-9_-]', '_', text)
    # Remove multiple underscores
    safe = re.sub(r'_+', '_', safe)
    # Trim to max length
    if len(safe) > max_length:
        safe = safe[:max_length]
    return safe.strip('_') or 'output'


def parse_key_value_file(file_path: Path) -> dict:
    """
    Parse file with key: value format.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary of key-value pairs
    """
    data = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
    return data


def batch_process(items: List[Any], processor: Callable, 
                 batch_size: int = 100, show_progress: bool = True) -> List[Any]:
    """
    Process items in batches with optional progress display.
    
    Args:
        items: List of items to process
        processor: Function to process each item
        batch_size: Size of each batch
        show_progress: Whether to show progress
        
    Returns:
        List of processed results
    """
    results = []
    
    if show_progress:
        tracker = ProgressTracker(len(items), "Processing items")
        tracker.start()
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        for item in batch:
            results.append(processor(item))
        
        if show_progress:
            tracker.update(len(batch))
    
    if show_progress:
        tracker.finish()
    
    return results


# Common argument patterns
def add_format_args(parser: argparse.ArgumentParser):
    """Add common formatting arguments."""
    format_group = parser.add_argument_group('formatting options')
    format_group.add_argument(
        '--no-html', action='store_true',
        help='Disable HTML formatting'
    )
    format_group.add_argument(
        '--no-latex', action='store_true',
        help='Disable LaTeX conversion'
    )
    format_group.add_argument(
        '--preserve-newlines', action='store_true',
        help='Preserve newlines in output'
    )


def add_filter_args(parser: argparse.ArgumentParser):
    """Add common filtering arguments."""
    filter_group = parser.add_argument_group('filtering options')
    filter_group.add_argument(
        '--min-length', type=int,
        help='Minimum text length to process'
    )
    filter_group.add_argument(
        '--max-length', type=int,
        help='Maximum text length to process'
    )
    filter_group.add_argument(
        '--include-pattern', type=str,
        help='Only process text matching this pattern'
    )
    filter_group.add_argument(
        '--exclude-pattern', type=str,
        help='Skip text matching this pattern'
    )