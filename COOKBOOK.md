# anki automation cookbook

practical recipes for creating high-quality flashcards from your content.

## quick recipes

### 1. convert lecture notes to cards

```bash
# parse markdown notes with smart detection
python scripts/smart_parser.py lecture_notes.md -o lecture_cards.csv

# or use markdown-specific parser for structured notes
python scripts/anki.py markdown lecture_notes.md -o lecture_cards.csv
```

### 2. learn a new programming language

```bash
# extract syntax patterns from code files
python scripts/anki.py code examples.py -t syntax function -o python_cards.csv

# create cards for code snippets with explanations
python scripts/anki.py code tutorial.js -t concept -o js_concepts.csv
```

### 3. memorize a sequence (planets, historical events, etc.)

```bash
# create before/after cards for sequences
echo -e "mercury\nvenus\nearth\nmars\njupiter" | \
    python scripts/mnemonic_generator.py -t sequence -c planets -o planets.csv
```

### 4. study from textbook chapters

```bash
# extract definitions and key concepts
python scripts/smart_parser.py chapter1.txt --analyze  # preview first
python scripts/smart_parser.py chapter1.txt -o ch1_cards.csv

# process multiple chapters and combine
python scripts/batch_processor.py textbook/ -p "*.txt" \
    -c smart_parser -o textbook_cards.csv --merge
```

### 5. create comprehensive study deck

```bash
# combine cards from multiple sources
python scripts/deck_builder.py \
    vocab.csv \
    formulas.csv \
    examples.csv \
    -o final_deck.csv \
    --name "Physics 101" \
    --tags physics semester1 \
    --remove-duplicates \
    --add-hints
```

## advanced workflows

### batch processing entire course materials

```bash
# 1. convert all markdown notes
python scripts/batch_processor.py notes/ -p "*.md" \
    -c markdown -o cards/

# 2. extract from all code examples
python scripts/batch_processor.py code_examples/ -p "*.py" \
    -c code --args "-t" "syntax" -o cards/

# 3. combine everything into master deck
python scripts/deck_builder.py cards/*.csv \
    -o master_deck.csv \
    --name "Complete Course" \
    --remove-duplicates \
    --priority-tags important exam \
    --add-hints
```

### interactive card preview and editing

```bash
# preview cards before importing
python scripts/preview_cards.py deck.csv --format html > preview.html

# browse cards interactively
python scripts/preview_cards.py deck.csv --interactive

# get statistics about your deck
python scripts/preview_cards.py deck.csv --stats
```

### smart content parsing pipeline

```bash
# 1. analyze content to see what cards will be generated
python scripts/smart_parser.py content.txt --analyze

# 2. generate cards if satisfied
python scripts/smart_parser.py content.txt -o smart_cards.csv

# 3. preview the cards
python scripts/preview_cards.py smart_cards.csv --format text | less

# 4. import to anki
# in anki: file -> import -> select smart_cards.csv
```

### creating cloze deletions from text

```bash
# basic cloze for key terms
python scripts/anki.py cloze definitions.txt --type basic -o cloze.csv

# sentence-level cloze for memorization
python scripts/anki.py cloze poem.txt --type sentence -o poem_cloze.csv

# incremental cloze for complex topics
python scripts/anki.py cloze process.txt --type incremental -o process_cloze.csv
```

### mnemonic techniques for better retention

```bash
# acronym generation
echo "create retrieve update delete" | \
    python scripts/mnemonic_generator.py -t acronym -o crud.csv

# association chains for linked concepts
cat concepts.txt | python scripts/mnemonic_generator.py \
    -t chain --context "biology" -o bio_chains.csv

# cloze halves for poems or quotes
python scripts/mnemonic_generator.py -t halves \
    --input poem.txt -o poem_halves.csv
```

### overlapping cloze deletions for comprehensive learning

```bash
# create multiple overlapping blanks from marked text
echo "the %mitochondria% is the %powerhouse% of the %cell%" | \
    python scripts/anki.py overlap -o cell_cards.tsv

# use custom delimiter for marking answers
echo "einstein published the @theory of relativity@ in @1905@" | \
    python scripts/anki.py overlap --delimiter @ -o einstein.tsv

# process file with facts (generates all combinations)
python scripts/anki.py overlap < facts.txt > comprehensive_cards.tsv
```

### memorizing ordered lists comprehensively

```bash
# generate cards for learning positions in a list
echo -e "george washington\njohn adams\nthomas jefferson" | \
    python scripts/anki.py list -c president -o presidents.csv

# creates cards asking:
# - what is the 1st president?
# - what position is john adams?
# - what comes after george washington?
# - what comes before thomas jefferson?
```

### progressive reveal for text memorization

```bash
# progressively reveal text word by word
echo "to be or not to be" | python scripts/anki.py reveal -o hamlet.csv

# reveal by lines for poetry
python scripts/anki.py reveal poem.txt --unit line -o poem_cards.csv

# reverse mode - start visible, progressively hide
python scripts/anki.py reveal quote.txt --reverse -o quote_cards.csv

# reveal multiple words at once
python scripts/anki.py reveal passage.txt --chunk-size 2 -o passage.csv
```

## content preparation tips

### formatting for smart parser

the smart parser works best with properly formatted content:

```text
Python: A high-level programming language.

What is recursion?
A technique where a function calls itself.

Formula: E = mc²

Key features:
- interpreted language
- dynamic typing
- extensive libraries

Example: print("hello world") outputs text to console
```

### markdown structure for best results

```markdown
# Chapter Title

## Definition: Key Term
The explanation of the key term goes here.

## Q: Question about concept?
A: The answer explaining the concept.

## Code Example
\`\`\`python
def example():
    return "this becomes a code card"
\`\`\`

## Important Points
- First point
- Second point
- Third point
```

### organizing files for batch processing

```
course_materials/
├── week1/
│   ├── lecture1.md
│   ├── examples.py
│   └── homework.txt
├── week2/
│   ├── lecture2.md
│   └── lab.py
└── week3/
    └── review.md
```

then process with:
```bash
python scripts/batch_processor.py course_materials/ \
    --recursive -p "*.md" -c markdown \
    --merge -o complete_course.csv
```

## vocabulary learning

### synonym web for interconnected learning

create cards that test word relationships and build vocabulary networks:

```bash
# basic synonym/antonym cards from word list
echo "happy sad big small fast slow" | python scripts/anki.py synonym

# explore related words to depth 2
python scripts/anki.py synonym core_vocab.txt --depth 2 -o vocab_network.csv

# specific card types only
python scripts/anki.py synonym words.txt --types synonym antonym starts_with

# context-based cards
python scripts/anki.py synonym words.txt --types context odd_one_out -o context_cards.csv

# without wordnet (uses basic built-in data)
python scripts/anki.py synonym words.txt --no-wordnet -o basic_vocab.csv
```

card types generated:
- **synonym**: "give a synonym for: happy"
- **antonym**: "give an antonym for: big"
- **starts_with**: "give a synonym for fast that starts with R"
- **context**: "fill in with synonym of good: the ___ solution worked"
- **odd_one_out**: "which is not a synonym of happy? [list of words]"
- **hypernym**: "what is a more general term for dog?"
- **hyponym**: "what is a specific type of vehicle?"

## common patterns

### daily review deck

```bash
# create subset of cards for daily review
python scripts/deck_builder.py all_cards.csv \
    -o daily_review.csv \
    --max-cards 20 \
    --filter-tags review important \
    --sort random
```

### exam preparation

```bash
# prioritize exam-relevant cards
python scripts/deck_builder.py course_cards.csv \
    -o exam_prep.csv \
    --priority-tags exam midterm important \
    --remove-duplicates \
    --sort length  # start with shorter cards
```

### incremental learning

```bash
# week 1: basics only
python scripts/deck_builder.py all_cards.csv \
    -o week1.csv --filter-tags basic fundamental

# week 2: add intermediate
python scripts/deck_builder.py all_cards.csv \
    -o week2.csv --filter-tags basic intermediate

# week 3: everything
python scripts/deck_builder.py all_cards.csv \
    -o week3.csv --add-hints
```

## tips for quality cards

### use smart parser for mixed content
- automatically detects definitions, q&a, lists
- generates both forward and reverse cards
- adds appropriate formatting

### combine tools for best results
1. use `smart_parser` for initial extraction
2. add mnemonics with `mnemonic_generator`
3. combine with `deck_builder`
4. preview with `preview_cards`

### tag strategically
- source tags: which lecture/chapter
- difficulty tags: easy, medium, hard
- topic tags: for filtered decks
- priority tags: for exam prep

### preview before importing
- check card formatting
- verify latex rendering
- ensure no duplicates
- review card counts

## troubleshooting

### handling special characters

```bash
# csv formatter handles escaping automatically
python scripts/csv_formatter.py raw_cards.csv -o clean_cards.csv
```

### dealing with large files

```bash
# process in chunks
python scripts/deck_builder.py huge_deck.csv \
    -o part1.csv --max-cards 1000

# or split by tags
python scripts/deck_builder.py huge_deck.csv \
    -o basics.csv --filter-tags basic
```

### checking for errors

```bash
# validate csv format
python scripts/preview_cards.py deck.csv --stats

# test small sample first
head -20 deck.csv | python scripts/preview_cards.py - --format text
```

remember: quality over quantity. a few well-crafted cards are better than many poor ones.