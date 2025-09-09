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
- `poetry` - generate cards for memorizing poetry and verse
- `list` - generate cards for memorizing ordered lists
- `overlap` - generate overlapping cloze deletion cards
- `reveal` - generate progressive reveal cards for text memorization
- `synonym` - generate interconnected vocabulary cards with synonyms/antonyms

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

### batch processing
process multiple files or entire directories at once:
```bash
python scripts/batch_processor.py notes/*.md -t markdown -o output/
python scripts/batch_processor.py code/ -t code --recursive --merge
```

### preview cards
preview generated cards before importing to anki:
```bash
python scripts/preview_cards.py cards.csv              # text preview
python scripts/preview_cards.py cards.csv -f html > preview.html
python scripts/preview_cards.py cards.csv --interactive  # browse cards
```

### smart content parsing
automatically detect and convert various content types:
```bash
python scripts/smart_parser.py notes.txt --analyze  # preview what will be generated
python scripts/smart_parser.py notes.txt -o smart_cards.csv
```

### vocabulary learning
comprehensive vocabulary cards with multiple learning angles:
```bash
python scripts/anki.py vocabulary words.txt --all-types -o vocab.csv
python scripts/anki.py vocabulary words.txt --etymology --synonyms
```

### poetry memorization
create progressive cards for memorizing poems and verse:
```bash
echo -e "roses are red\nviolets are blue" | python scripts/anki.py poetry
python scripts/anki.py poetry poem.txt --progressive --preserve-rhymes -o poem_cards.csv
```

### progressive reveal
memorize passages by progressively revealing or hiding text:
```bash
echo "to be or not to be" | python scripts/anki.py reveal -o shakespeare.csv
python scripts/anki.py reveal speech.txt --unit line --reverse -o speech_cards.csv
```

### synonym web
create interconnected vocabulary cards with word relationships:
```bash
echo "happy sad big small" | python scripts/anki.py synonym --no-wordnet
python scripts/anki.py synonym words.txt --depth 2 --types synonym antonym context -o vocab_web.csv
```

### deck building
combine and organize cards from multiple sources:
```bash
python scripts/deck_builder.py vocab.csv formulas.csv examples.csv \
    -o study_deck.csv --name "Physics 101" --remove-duplicates
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
- **vocabulary_cards.py**: comprehensive vocabulary learning with etymology and context
- **poetry_memorization.py**: progressive cloze deletion for memorizing poetry and verse
- **list_memorization.py**: comprehensive cards for memorizing ordered sequences
- **overlapping_cloze.py**: multiple overlapping cloze deletions for thorough learning
- **progressive_reveal.py**: progressively reveal or hide text for passage memorization
- **synonym_web.py**: interconnected vocabulary cards with word relationships
- **batch_processor.py**: bulk processing of multiple files
- **preview_cards.py**: preview and browse cards before import
- **smart_parser.py**: auto-detect content types and generate appropriate cards
- **deck_builder.py**: combine, organize, and optimize card decks
- **cli_utils.py**: shared cli utilities and helpers

## testing

run the test suites:
```bash
python scripts/test_anki_utils.py          # unit tests
python scripts/test_cli_integration.py     # cli integration tests  
python scripts/test_batch_preview.py       # batch & preview tests
```

## tips for quality cards

- keep cards atomic - one concept per card
- use cloze deletions for lists and sequences
- add context to prevent ambiguity
- use images when visual memory helps
- create reverse cards for important definitions
- test your cards before bulk creating

## cookbook

check out `COOKBOOK.md` for detailed recipes and workflows for common use cases.

## examples directory

check `.examples/` for sample input files and generated output.

## resources

see `.resources/` for:
- anki import documentation
- card writing guidelines
- spaced repetition best practices

---

*making memorization delightful, one card at a time*