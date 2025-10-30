#!/usr/bin/env python3
"""
Backward compatibility wrapper for io_utils.

This module re-exports everything from anki_utils for backward compatibility.
New code should import from anki_utils directly.

Deprecated: Use anki_utils instead.
"""

# Import everything from the consolidated anki_utils module
from anki_utils import (
    # Classes
    AnkiFormatter,
    InputHandler,
    OutputHandler,
    TextParser,
    ClozeGenerator,
    CardFormatter,
    ArgumentParser,
    AnkiWriter,

    # Functions
    read_input,
    write_output,
    format_card,
    create_argument_parser,
    add_common_arguments,
)

# Re-export for backward compatibility
__all__ = [
    'AnkiFormatter',
    'InputHandler',
    'OutputHandler',
    'TextParser',
    'ClozeGenerator',
    'CardFormatter',
    'ArgumentParser',
    'AnkiWriter',
    'read_input',
    'write_output',
    'format_card',
    'create_argument_parser',
    'add_common_arguments',
]
