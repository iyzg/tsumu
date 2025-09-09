# Anki Flashcard Automation Plan

## Current State Analysis

### Existing Scripts
1. **fact_to_cards.py** - Converts structured facts into multiple card types (basic, list, comparison, example, formula)
2. **cloze_generator.py** - Creates cloze deletion cards with various patterns (basic, sentence, list, definition, incremental)
3. **csv_formatter.py** - Formats CSV for Anki import with HTML escaping and LaTeX conversion
4. **sequence.py** (example) - Generates predecessor/successor cards for sequences

### Strengths
- Good foundation with multiple card generation approaches
- LaTeX support for mathematical content
- CSV export for direct Anki import
- Command-line interface for automation

### Areas for Improvement
1. **Modularity** - Scripts have overlapping functionality (LaTeX conversion, CSV writing)
2. **Testing** - No test files or validation scripts
3. **Advanced Features** - Could implement ideas from .gwern/ files (mnemonic generation)
4. **Documentation** - Need examples and usage guides for each script
5. **Integration** - Scripts work independently, could benefit from a unified interface

## Ideas for New Functionality

### From .gwern/ Directory Analysis
- Mnemonic generation algorithms (mnemo*.hs files suggest memory palace/peg system generation)
- Advanced spaced repetition scheduling optimization
- Pattern recognition for automatic card generation from unstructured text

### Based on Guidelines
1. **Image Occlusion Generator** - Create cards by masking parts of diagrams/images
2. **Context-Aware Card Generator** - Add automatic context cues to reduce interference
3. **Redundancy Builder** - Generate multiple perspectives of the same fact
4. **Priority Optimizer** - Automatically tag/prioritize cards based on complexity

### Practical Utilities
1. **Markdown to Anki Converter** - Parse markdown notes into cards
2. **Code Snippet Card Generator** - Create programming flashcards from code examples
3. **Definition Extractor** - Extract and format definitions from textbooks/PDFs
4. **Question-Answer Pair Generator** - Convert Q&A formats into cards

## Implementation Priorities

### Phase 1: Refactoring (Today)
- [ ] Create shared utility module for common functions
- [ ] Add proper error handling and validation
- [ ] Standardize CSV output format across scripts

### Phase 2: Testing Framework
- [ ] Create test data directory
- [ ] Write unit tests for each script
- [ ] Add integration tests for card generation

### Phase 3: New Features
- [ ] Implement markdown to Anki converter
- [ ] Create image occlusion script
- [ ] Build unified CLI interface

### Phase 4: Advanced Features
- [ ] Mnemonic generation based on .gwern/ algorithms
- [ ] Smart card prioritization system
- [ ] Batch processing pipeline

## Next Steps
1. Start with refactoring to create a solid foundation
2. Build test suite to ensure reliability
3. Incrementally add new features based on utility
4. Document everything with clear examples