*tsumu, something new*

# anki flashcard automation toolkit

a collection of python scripts for turning your notes, code, and knowledge into high-quality anki flashcards. designed to make spaced repetition learning effortless.

## quick start

use the unified cli for all card generation:

```bash
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

## usage examples

### markdown to flashcards
convert your markdown notes into cards:
```bash
python scripts/anki.py markdown notes.md -o cards.csv
```

supports headers, definition lists, q&a blocks, code blocks, and tables.

### code snippet cards
learn programming patterns and syntax:
```bash
python scripts/anki.py code example.py -t syntax function -o code_cards.csv
```

### mnemonic sequences
memorize ordered lists with before/after cards:
```bash
echo -e "mercury\nvenus\nearth\nmars" | python scripts/anki.py mnemonic -- -t sequence -c planet
```

### cloze deletions
create fill-in-the-blank cards:
```bash
python scripts/anki.py cloze text.txt --type sentence -o cloze.csv
```

### structured facts
convert detailed facts into multiple card types:
```bash
cat facts.txt | python scripts/anki.py fact -- -t basic list example -o fact_cards.csv
```

## script details

### shared utilities (`anki_utils.py`)
core formatting and parsing functions used by all scripts:
- html escaping for anki
- latex math notation support
- csv writing utilities
- text parsing helpers

### individual generators

each generator can be used standalone or through the unified cli:

- **csv_formatter.py**: clean and format existing csv files
- **cloze_generator.py**: create various cloze deletion patterns
- **markdown_to_anki.py**: intelligent markdown parsing
- **code_to_anki.py**: programming-focused cards
- **image_occlusion.py**: visual learning with svg overlays
- **fact_to_cards.py**: multi-perspective fact cards
- **mnemonic_generator.py**: memory palace and association techniques

## testing

run the test suite:
```bash
python -m unittest scripts/test_anki_utils.py
```

## tips for quality cards

- keep cards atomic - one concept per card
- use cloze deletions for lists and sequences
- add context to prevent ambiguity
- use images when visual memory helps
- create reverse cards for important definitions
- test your cards before bulk creating

## examples directory

check `.examples/` for sample input files and generated output.

## resources

see `.resources/` for:
- anki import documentation
- card writing guidelines
- spaced repetition best practices

---

*making memorization delightful, one card at a time*