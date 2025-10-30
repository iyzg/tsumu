*tsumu, something new*

# anki flashcard automation toolkit

turn your notes, code, and knowledge into high-quality anki flashcards.

## quick start

```bash
# install
make install

# run tests
make test

# generate cards
python scripts/anki.py <command> [options]
```

available commands:
- `csv` - format csv files for anki import
- `cloze` - generate cloze deletion cards
- `markdown` - convert markdown notes to flashcards
- `code` - generate cards from code snippets
- `image` - create image occlusion cards
- `fact` - convert structured facts to q&a cards
- `mnemonic` - generate mnemonic cards using memory techniques
- `poetry` - generate cards for memorizing poetry and verse
- `list` - generate cards for memorizing ordered lists
- `overlap` - generate overlapping cloze deletion cards
- `reveal` - generate progressive reveal cards for text memorization
- `synonym` - generate interconnected vocabulary cards with synonyms/antonyms
- `context` - generate cards with varying context windows for deeper learning
- `formula` - break down complex formulas into component-based cards
- `timeline` - generate chronological learning cards for dates and events
- `incremental` - break long texts into incremental reading chunks

## common examples

```bash
# markdown → flashcards
python scripts/anki.py markdown notes.md -o cards.csv

# code → syntax cards
python scripts/anki.py code example.py -t syntax -o code.csv

# text → cloze deletions
python scripts/anki.py cloze text.txt --type sentence -o cloze.csv

# poetry memorization
python scripts/anki.py poetry poem.txt -o poem.csv

# list memorization
echo -e "item1\nitem2\nitem3" | python scripts/anki.py list
```

## advanced usage

```bash
# batch processing
python scripts/batch_processor.py notes/ -p "*.md" -c markdown -o cards/

# preview cards
python scripts/preview_cards.py cards.csv --interactive

# smart parsing
python scripts/smart_parser.py notes.txt --analyze

# deck building
python scripts/deck_builder.py *.csv -o deck.csv --remove-duplicates
```

see [COOKBOOK.md](COOKBOOK.md) for more examples and recipes.

## testing

```bash
make test       # run all tests
make test-fast  # run core tests only
```

## tips for quality cards

1. keep cards atomic - one concept per card
2. use cloze deletions for lists and sequences
3. add context to prevent ambiguity
4. preview cards before bulk import
5. combine tools for better results

## installation

```bash
make install  # installs package in development mode
```

or manually:
```bash
pip install -e .
```

## development

### project structure

```
tsumu/
├── scripts/              # main package directory
│   ├── __init__.py      # package initialization
│   ├── anki.py          # unified CLI entry point
│   ├── anki_utils.py    # comprehensive utility library
│   ├── io_utils.py      # backward compatibility wrapper
│   └── [generators]/    # individual card generators
├── pyproject.toml       # package configuration
├── README.md            # this file
└── COOKBOOK.md          # usage recipes
```

### for contributors

when creating new card generators:

1. import utilities from `anki_utils`:
```python
from anki_utils import (
    InputHandler, OutputHandler, ArgumentParser,
    AnkiFormatter, check_input_not_empty
)
```

2. use standardized patterns:
```python
def main():
    parser = ArgumentParser.create_basic_parser("your description")
    # add your specific arguments
    args = parser.parse_args()

    text = InputHandler.get_input(args.input)
    check_input_not_empty(text)

    cards = generate_cards(text)
    OutputHandler.write_cards(cards, args.output)
```

3. register your generator in `scripts/anki.py`

---

*making memorization delightful, one card at a time*