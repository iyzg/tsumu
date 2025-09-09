#!/usr/bin/env python3
"""
synonym web generator - create interconnected vocabulary cards

generates anki cards that test synonym, antonym, and related word knowledge
through various challenging formats. uses nltk wordnet for relationships.

examples:
    # basic synonym/antonym cards
    echo "happy sad big small" | python synonym_web.py
    
    # from file with custom depth
    python synonym_web.py words.txt --depth 2 -o vocab_web.csv
    
    # specific relationship types
    python synonym_web.py words.txt --types synonym antonym hypernym
    
    # with difficulty levels
    python synonym_web.py words.txt --difficulty progressive
"""

import argparse
import sys
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import random

try:
    from nltk.corpus import wordnet as wn
    import nltk
except ImportError:
    print("warning: nltk not installed. using basic synonym data only.")
    wn = None

from anki_utils import AnkiFormatter
from io_utils import InputHandler, OutputHandler, ArgumentParser

# basic synonym/antonym data for when nltk isn't available
BASIC_SYNONYMS = {
    'happy': ['joyful', 'cheerful', 'content', 'pleased', 'delighted'],
    'sad': ['unhappy', 'sorrowful', 'dejected', 'melancholy', 'gloomy'],
    'big': ['large', 'huge', 'enormous', 'vast', 'immense'],
    'small': ['little', 'tiny', 'minute', 'diminutive', 'petite'],
    'fast': ['quick', 'rapid', 'swift', 'speedy', 'hasty'],
    'slow': ['sluggish', 'leisurely', 'gradual', 'unhurried', 'languid'],
    'good': ['excellent', 'fine', 'superior', 'wonderful', 'great'],
    'bad': ['poor', 'inferior', 'terrible', 'awful', 'dreadful'],
    'hot': ['warm', 'heated', 'burning', 'scorching', 'torrid'],
    'cold': ['cool', 'chilly', 'freezing', 'frigid', 'icy']
}

BASIC_ANTONYMS = {
    'happy': ['sad', 'unhappy', 'miserable'],
    'sad': ['happy', 'joyful', 'cheerful'],
    'big': ['small', 'little', 'tiny'],
    'small': ['big', 'large', 'huge'],
    'fast': ['slow', 'sluggish', 'leisurely'],
    'slow': ['fast', 'quick', 'rapid'],
    'good': ['bad', 'poor', 'evil'],
    'bad': ['good', 'excellent', 'virtuous'],
    'hot': ['cold', 'cool', 'chilly'],
    'cold': ['hot', 'warm', 'heated']
}


class SynonymWeb:
    """generates interconnected vocabulary cards using word relationships"""
    
    def __init__(self, use_wordnet: bool = True):
        """initialize with or without wordnet support"""
        self.use_wordnet = use_wordnet and wn is not None
        if self.use_wordnet:
            try:
                # download wordnet data if not present
                nltk.data.find('corpora/wordnet')
            except LookupError:
                try:
                    nltk.download('wordnet', quiet=True)
                    nltk.download('omw-1.4', quiet=True)
                except:
                    self.use_wordnet = False
    
    def get_synonyms(self, word: str, max_results: int = 5) -> List[str]:
        """get synonyms for a word"""
        synonyms = set()
        
        if self.use_wordnet:
            for syn in wn.synsets(word):
                for lemma in syn.lemmas():
                    if lemma.name() != word and '_' not in lemma.name():
                        synonyms.add(lemma.name().lower())
        else:
            # use basic data
            if word.lower() in BASIC_SYNONYMS:
                synonyms.update(BASIC_SYNONYMS[word.lower()])
        
        return list(synonyms)[:max_results]
    
    def get_antonyms(self, word: str, max_results: int = 3) -> List[str]:
        """get antonyms for a word"""
        antonyms = set()
        
        if self.use_wordnet:
            for syn in wn.synsets(word):
                for lemma in syn.lemmas():
                    if lemma.antonyms():
                        for ant in lemma.antonyms():
                            antonyms.add(ant.name().lower())
        else:
            # use basic data
            if word.lower() in BASIC_ANTONYMS:
                antonyms.update(BASIC_ANTONYMS[word.lower()])
        
        return list(antonyms)[:max_results]
    
    def get_hypernyms(self, word: str, max_results: int = 3) -> List[str]:
        """get hypernyms (more general terms) for a word"""
        hypernyms = set()
        
        if self.use_wordnet:
            for syn in wn.synsets(word):
                for hyper in syn.hypernyms():
                    hypernyms.add(hyper.lemmas()[0].name().replace('_', ' ').lower())
        
        return list(hypernyms)[:max_results]
    
    def get_hyponyms(self, word: str, max_results: int = 3) -> List[str]:
        """get hyponyms (more specific terms) for a word"""
        hyponyms = set()
        
        if self.use_wordnet:
            for syn in wn.synsets(word):
                for hypo in syn.hyponyms():
                    hyponyms.add(hypo.lemmas()[0].name().replace('_', ' ').lower())
        
        return list(hyponyms)[:max_results]
    
    def generate_synonym_card(self, word: str, synonyms: List[str]) -> Optional[Dict[str, str]]:
        """generate a basic synonym card"""
        if not synonyms:
            return None
        
        return {
            'question': f"Give a synonym for: <b>{word}</b>",
            'answer': " or ".join(synonyms[:3])
        }
    
    def generate_antonym_card(self, word: str, antonyms: List[str]) -> Optional[Dict[str, str]]:
        """generate a basic antonym card"""
        if not antonyms:
            return None
        
        return {
            'question': f"Give an antonym for: <b>{word}</b>",
            'answer': " or ".join(antonyms[:3])
        }
    
    def generate_starts_with_card(self, word: str, synonyms: List[str]) -> Optional[Dict[str, str]]:
        """generate a card asking for synonym starting with specific letter"""
        if not synonyms:
            return None
        
        # group synonyms by first letter
        by_letter = defaultdict(list)
        for syn in synonyms:
            by_letter[syn[0].upper()].append(syn)
        
        if not by_letter:
            return None
        
        # pick a letter that has synonyms
        letter = random.choice(list(by_letter.keys()))
        
        return {
            'question': f"Give a synonym for <b>{word}</b> that starts with <b>{letter}</b>",
            'answer': " or ".join(by_letter[letter][:2])
        }
    
    def generate_relationship_card(self, word: str, related: List[str], 
                                 rel_type: str) -> Optional[Dict[str, str]]:
        """generate a card testing word relationships"""
        if not related:
            return None
        
        question_templates = {
            'hypernym': "What is a more general term for <b>{}</b>?",
            'hyponym': "What is a more specific type of <b>{}</b>?",
            'synonym': "What word means the same as <b>{}</b>?",
            'antonym': "What word means the opposite of <b>{}</b>?"
        }
        
        if rel_type not in question_templates:
            return None
        
        return {
            'question': question_templates[rel_type].format(word),
            'answer': " or ".join(related[:3])
        }
    
    def generate_context_card(self, word: str, synonyms: List[str]) -> Optional[Dict[str, str]]:
        """generate a card with word used in context"""
        if not synonyms:
            return None
        
        contexts = [
            "The weather today is very ___.",
            "She felt ___ about the news.",
            "The ___ solution worked perfectly.",
            "It was a ___ day for everyone.",
            "The results were ___."
        ]
        
        context = random.choice(contexts)
        
        return {
            'question': f"Fill in the blank with a synonym of <b>{word}</b>:<br><br>{context}",
            'answer': f"{word} (or: {', '.join(synonyms[:2])})"
        }
    
    def generate_odd_one_out_card(self, word: str, synonyms: List[str], 
                                 antonyms: List[str]) -> Optional[Dict[str, str]]:
        """generate odd-one-out card mixing synonyms and antonyms"""
        if len(synonyms) < 2 or not antonyms:
            return None
        
        # create list with synonyms and one antonym
        words = synonyms[:3] + [antonyms[0]]
        random.shuffle(words)
        
        return {
            'question': f"Which word is NOT a synonym of <b>{word}</b>?<br><br>" + 
                       "<br>".join(f"• {w}" for w in words),
            'answer': antonyms[0]
        }
    
    def generate_web_cards(self, word: str, depth: int = 1, 
                          card_types: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """generate all types of cards for a word"""
        if card_types is None:
            card_types = ['synonym', 'antonym', 'starts_with', 'context', 'odd_one_out']
        
        cards = []
        
        # get word relationships
        synonyms = self.get_synonyms(word)
        antonyms = self.get_antonyms(word)
        hypernyms = self.get_hypernyms(word)
        hyponyms = self.get_hyponyms(word)
        
        # generate cards based on requested types
        if 'synonym' in card_types and synonyms:
            card = self.generate_synonym_card(word, synonyms)
            if card:
                cards.append(card)
        
        if 'antonym' in card_types and antonyms:
            card = self.generate_antonym_card(word, antonyms)
            if card:
                cards.append(card)
        
        if 'starts_with' in card_types and synonyms:
            card = self.generate_starts_with_card(word, synonyms)
            if card:
                cards.append(card)
        
        if 'hypernym' in card_types and hypernyms:
            card = self.generate_relationship_card(word, hypernyms, 'hypernym')
            if card:
                cards.append(card)
        
        if 'hyponym' in card_types and hyponyms:
            card = self.generate_relationship_card(word, hyponyms, 'hyponym')
            if card:
                cards.append(card)
        
        if 'context' in card_types and synonyms:
            card = self.generate_context_card(word, synonyms)
            if card:
                cards.append(card)
        
        if 'odd_one_out' in card_types:
            card = self.generate_odd_one_out_card(word, synonyms, antonyms)
            if card:
                cards.append(card)
        
        # if depth > 1, also generate cards for related words
        if depth > 1:
            processed = {word}
            for syn in synonyms[:2]:  # limit to avoid explosion
                if syn not in processed:
                    processed.add(syn)
                    cards.extend(self.generate_web_cards(
                        syn, depth - 1, card_types
                    ))
        
        return cards


def main():
    """main entry point for synonym web generator"""
    parser = ArgumentParser.create_basic_parser(
        'Generate interconnected vocabulary cards with synonyms and antonyms',
        epilog=__doc__
    )
    
    # add specific arguments
    parser.add_argument('--depth', type=int, default=1,
                       help='Depth of word relationships to explore (default: 1)')
    parser.add_argument('--types', nargs='+', 
                       choices=['synonym', 'antonym', 'starts_with', 'hypernym', 
                               'hyponym', 'context', 'odd_one_out'],
                       help='Types of cards to generate')
    parser.add_argument('--no-wordnet', action='store_true',
                       help='Use basic data only (no WordNet)')
    parser.add_argument('--limit', type=int, default=10,
                       help='Max cards per word (default: 10)')
    
    args = parser.parse_args()
    
    # read input words using io_utils
    text = InputHandler.get_input(args.input)
    
    # extract words
    words = []
    for line in text.strip().split('\n'):
        words.extend(line.split())
    
    if not words:
        print("Error: No words provided", file=sys.stderr)
        return 1
    
    # generate cards
    web = SynonymWeb(use_wordnet=not args.no_wordnet)
    all_cards = []
    
    for word in words:
        word = word.strip().lower()
        if word:
            cards = web.generate_web_cards(word, args.depth, args.types)
            all_cards.extend(cards[:args.limit])
    
    if not all_cards:
        print("No cards generated. Check word list and try again.", file=sys.stderr)
        return 1
    
    # format for anki
    formatter = AnkiFormatter()
    formatted_cards = []
    for card in all_cards:
        formatted_cards.append((
            formatter.process_text(card['question'], escape_html=False, format_newlines=False),
            formatter.process_text(card['answer'], escape_html=False, format_newlines=False)
        ))
    
    # write output using io_utils
    OutputHandler.write_cards(formatted_cards, args.output, 
                             delimiter=args.delimiter, 
                             verbose=args.verbose)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())