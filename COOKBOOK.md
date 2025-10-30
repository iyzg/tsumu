# anki automation cookbook

practical recipes for creating high-quality flashcards.

## quick start recipes

### convert markdown notes to cards
```bash
python scripts/anki.py markdown notes.md -o cards.csv
```

### learn programming syntax
```bash
python scripts/anki.py code example.py -t syntax function -o code_cards.csv
```

### memorize sequences
```bash
echo -e "mercury\nvenus\nearth\nmars" | python scripts/anki.py list -c planets -o planets.csv
```

### create cloze deletions
```bash
python scripts/anki.py cloze definitions.txt --type basic -o cloze.csv
```

### memorize poetry
```bash
python scripts/anki.py poetry poem.txt --progressive -o poem_cards.csv
```

## common workflows

### batch process entire directory
```bash
python scripts/batch_processor.py notes/ -p "*.md" -c markdown -o cards/
python scripts/deck_builder.py cards/*.csv -o master_deck.csv --remove-duplicates
```

### preview before importing
```bash
python scripts/preview_cards.py deck.csv --format html > preview.html
python scripts/preview_cards.py deck.csv --interactive
```

### smart parsing pipeline
```bash
# analyze what will be generated
python scripts/smart_parser.py content.txt --analyze

# generate if satisfied
python scripts/smart_parser.py content.txt -o cards.csv

# preview before import
python scripts/preview_cards.py cards.csv
```

## advanced examples

### vocabulary with context
```bash
python scripts/anki.py synonym words.txt --depth 2 -o vocab.csv
python scripts/anki.py vocabulary words.txt --all-types -o vocab_detailed.csv
```

### overlapping cloze deletions
```bash
echo "The %mitochondria% is the %powerhouse% of the %cell%" | python scripts/anki.py overlap -o cell.tsv
```

### progressive text reveal
```bash
python scripts/anki.py reveal speech.txt --unit line --reverse -o speech.csv
```

### formula breakdown
```bash
echo "E = mc^2 | E:energy, m:mass, c:speed of light" | python scripts/anki.py formula -- --progressive
```

### timeline cards
```bash
echo -e "1492 | Columbus discovers America\n1776 | Declaration of Independence" | python scripts/anki.py timeline
```

### incremental reading
```bash
python scripts/anki.py incremental article.txt --chunk-size 200 --overlap 50
```

## tips for quality cards

1. **keep cards atomic** - one concept per card
2. **use cloze for lists** - better than multiple q&a cards
3. **add context** - prevents ambiguity
4. **preview before bulk import** - catch formatting issues early
5. **combine tools** - use smart_parser → preview → deck_builder pipeline

## content formatting tips

### markdown structure
```markdown
# Chapter Title

## Q: What is recursion?
A: A function calling itself

## Definition: Algorithm
A step-by-step procedure for solving a problem

## Code Example
\`\`\`python
def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)
\`\`\`
```

### structured facts
```text
Term: CPU
Definition: Central Processing Unit
Function: Executes program instructions
Example: Intel Core i7
```

### batch processing directory structure
```
course/
├── week1/
│   ├── lecture.md
│   └── examples.py
├── week2/
│   └── lecture.md
└── output/
    └── cards.csv
```

Process with:
```bash
python scripts/batch_processor.py course/ --recursive -p "*.md" -c markdown --merge -o output/cards.csv
```

## common issues

### special characters in CSV
```bash
python scripts/csv_formatter.py raw.csv -o clean.csv
```

### large files
```bash
# split by tags
python scripts/deck_builder.py huge.csv -o basics.csv --filter-tags basic

# limit cards
python scripts/deck_builder.py huge.csv -o sample.csv --max-cards 1000
```

### checking for errors
```bash
python scripts/preview_cards.py deck.csv --stats
```

---

*quality over quantity - fewer well-crafted cards beat many poor ones*
