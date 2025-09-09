#!/usr/bin/env python3
"""
incremental reading processor - break long texts into incremental learning chunks

this tool implements the incremental reading technique, breaking long texts into
manageable chunks that build on each other. each card references previous chunks
for context, creating a progressive learning experience.

features:
- smart text chunking by sentences, paragraphs, or custom size
- context preservation with previous chunk references
- progressive difficulty with vocabulary analysis
- summary cards for each chunk
- connection cards between chunks

usage:
    echo "long text here" | python incremental_reading.py
    python incremental_reading.py article.txt -o cards.csv
    python incremental_reading.py book.txt --chunk-size 200 --overlap 50
"""

import sys
import re
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from io_utils import InputHandler, OutputHandler, ArgumentParser
from anki_utils import escape_html


class IncrementalReadingProcessor:
    """generate incremental reading cards from long texts"""
    
    def __init__(self, chunk_size: int = 150, overlap: int = 30,
                 chunk_type: str = 'words', add_summaries: bool = True,
                 add_connections: bool = True, difficulty_progression: bool = False):
        """
        initialize incremental reading processor
        
        args:
            chunk_size: size of each chunk
            overlap: overlap between chunks (for context)
            chunk_type: 'words', 'sentences', or 'paragraphs'
            add_summaries: generate summary cards for each chunk
            add_connections: generate connection cards between chunks
            difficulty_progression: order chunks by vocabulary difficulty
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunk_type = chunk_type
        self.add_summaries = add_summaries
        self.add_connections = add_connections
        self.difficulty_progression = difficulty_progression
        
    def chunk_text(self, text: str) -> List[str]:
        """
        break text into chunks based on chunk_type
        
        args:
            text: input text
            
        returns:
            list of text chunks
        """
        if self.chunk_type == 'paragraphs':
            # split by double newlines or multiple spaces
            paragraphs = re.split(r'\n\n+|\n\s*\n', text.strip())
            return [p.strip() for p in paragraphs if p.strip()]
            
        elif self.chunk_type == 'sentences':
            # split by sentence boundaries
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
            
            # group sentences into chunks
            chunks = []
            current_chunk = []
            current_count = 0
            
            for sentence in sentences:
                current_chunk.append(sentence)
                current_count += 1
                
                if current_count >= self.chunk_size:
                    chunks.append(' '.join(current_chunk))
                    # keep overlap sentences
                    if self.overlap > 0:
                        current_chunk = current_chunk[-self.overlap:]
                        current_count = self.overlap
                    else:
                        current_chunk = []
                        current_count = 0
            
            # add remaining sentences
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                
            return chunks
            
        else:  # words
            words = text.split()
            chunks = []
            
            for i in range(0, len(words), self.chunk_size - self.overlap):
                chunk_words = words[i:i + self.chunk_size]
                if chunk_words:
                    chunks.append(' '.join(chunk_words))
            
            return chunks
    
    def calculate_difficulty(self, text: str) -> float:
        """
        calculate text difficulty based on vocabulary
        
        args:
            text: text to analyze
            
        returns:
            difficulty score (0-1)
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        # simple difficulty metrics
        avg_word_length = sum(len(w) for w in words) / len(words)
        unique_ratio = len(set(words)) / len(words)
        
        # normalize to 0-1 range
        length_score = min(avg_word_length / 10, 1.0)
        
        # combine metrics
        difficulty = (length_score + unique_ratio) / 2
        return difficulty
    
    def generate_chunk_cards(self, chunks: List[str]) -> List[Tuple[str, str, str]]:
        """
        generate cards for text chunks
        
        args:
            chunks: list of text chunks
            
        returns:
            list of (front, back, type) tuples
        """
        cards = []
        
        # optionally sort by difficulty
        if self.difficulty_progression:
            chunk_difficulties = [(chunk, self.calculate_difficulty(chunk)) 
                                 for chunk in chunks]
            chunk_difficulties.sort(key=lambda x: x[1])
            chunks = [chunk for chunk, _ in chunk_difficulties]
        
        for i, chunk in enumerate(chunks):
            chunk_num = i + 1
            
            # main reading card
            if i == 0:
                # first chunk - no context needed
                front = f"[Chunk {chunk_num}] Read and understand this text"
                back = escape_html(chunk)
            else:
                # include reference to previous chunk
                front = f"[Chunk {chunk_num}] Continue reading (follows Chunk {i})"
                back = escape_html(chunk)
                
                # add context hint if overlapping
                if self.overlap > 0:
                    back += f"<br><br><i>Context: Continues from previous chunk</i>"
            
            cards.append((front, back, "reading"))
            
            # comprehension card - what comes next?
            if i < len(chunks) - 1:
                front = f"[Chunk {chunk_num}] After: '{self._get_chunk_end(chunk)}' what comes next?"
                next_start = self._get_chunk_start(chunks[i + 1])
                back = f"'{next_start}'"
                cards.append((front, back, "continuation"))
            
            # summary card
            if self.add_summaries:
                front = f"[Chunk {chunk_num}] Summarize the main idea"
                back = f"<i>Chunk text:</i><br>{escape_html(self._truncate(chunk, 100))}<br><br><i>Write your own summary</i>"
                cards.append((front, back, "summary"))
            
            # connection card
            if self.add_connections and i > 0:
                front = f"[Chunks {i}-{chunk_num}] How does Chunk {chunk_num} relate to Chunk {i}?"
                back = f"<i>Consider themes, progression, contrast, or continuation</i>"
                cards.append((front, back, "connection"))
        
        # add overview cards
        if len(chunks) > 2:
            # sequence card
            front = "List the chunk sequence in order"
            back = f"Chunks 1 through {len(chunks)}"
            cards.append((front, back, "sequence"))
            
            # theme card
            front = "What is the overall theme across all chunks?"
            back = "<i>Consider the progression from beginning to end</i>"
            cards.append((front, back, "theme"))
        
        return cards
    
    def _get_chunk_start(self, chunk: str, length: int = 30) -> str:
        """get the beginning of a chunk"""
        words = chunk.split()[:5]
        start = ' '.join(words)
        if len(chunk) > len(start):
            start += "..."
        return start
    
    def _get_chunk_end(self, chunk: str, length: int = 30) -> str:
        """get the end of a chunk"""
        words = chunk.split()[-5:]
        end = ' '.join(words)
        if len(chunk) > len(end):
            end = "..." + end
        return end
    
    def _truncate(self, text: str, max_length: int) -> str:
        """truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def process(self, text: str) -> List[Tuple[str, str, str]]:
        """
        process text into incremental reading cards
        
        args:
            text: input text
            
        returns:
            list of (front, back, type) tuples
        """
        # clean the text
        text = text.strip()
        if not text:
            return []
        
        # chunk the text
        chunks = self.chunk_text(text)
        
        if not chunks:
            return []
        
        # generate cards
        cards = self.generate_chunk_cards(chunks)
        
        return cards


def main():
    """main entry point"""
    parser = ArgumentParser.create_basic_parser(
        "incremental reading processor - break long texts into learning chunks",
        epilog="""
examples:
    # process article with default settings
    python incremental_reading.py article.txt -o cards.csv
    
    # use sentence-based chunking
    python incremental_reading.py book.txt --chunk-type sentences --chunk-size 5
    
    # add difficulty progression
    python incremental_reading.py complex_text.txt --difficulty-progression
    
    # minimal cards (no summaries or connections)
    python incremental_reading.py text.txt --no-summaries --no-connections
    
chunk types:
    words      - chunk by word count (default)
    sentences  - chunk by sentence count
    paragraphs - chunk by paragraphs
        """
    )
    
    # chunk settings
    parser.add_argument('--chunk-size', type=int, default=150,
                       help='size of each chunk (default: 150)')
    parser.add_argument('--overlap', type=int, default=30,
                       help='overlap between chunks (default: 30)')
    parser.add_argument('--chunk-type', choices=['words', 'sentences', 'paragraphs'],
                       default='words', help='how to chunk text (default: words)')
    
    # card generation options
    parser.add_argument('--no-summaries', action='store_true',
                       help='skip summary cards')
    parser.add_argument('--no-connections', action='store_true',
                       help='skip connection cards')
    parser.add_argument('--difficulty-progression', action='store_true',
                       help='order chunks by vocabulary difficulty')
    
    # output options
    parser.add_argument('--include-type', action='store_true',
                       help='include card type as third field')
    
    args = parser.parse_args()
    
    # read input
    try:
        text = InputHandler.get_input(args.input)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # create processor
    processor = IncrementalReadingProcessor(
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        chunk_type=args.chunk_type,
        add_summaries=not args.no_summaries,
        add_connections=not args.no_connections,
        difficulty_progression=args.difficulty_progression
    )
    
    # process text
    cards = processor.process(text)
    
    if not cards:
        print("no cards generated", file=sys.stderr)
        sys.exit(1)
    
    # format output
    if args.include_type:
        output_cards = cards  # already includes type
    else:
        output_cards = [(front, back) for front, back, _ in cards]
    
    # write output
    OutputHandler.write_cards(
        output_cards,
        args.output,
        delimiter=args.delimiter,
        verbose=args.verbose
    )
    
    if args.verbose:
        # count card types
        type_counts = {}
        for _, _, card_type in cards:
            type_counts[card_type] = type_counts.get(card_type, 0) + 1
        
        print(f"\ncard breakdown:", file=sys.stderr)
        for card_type, count in sorted(type_counts.items()):
            print(f"  {card_type}: {count}", file=sys.stderr)


if __name__ == '__main__':
    main()