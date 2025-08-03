import hashlib
import re

def make_deck_id(name):
    return int(hashlib.sha1(name.encode('utf-8')).hexdigest(), 16) % (1 << 31)

POS_MAP = {
    'n': 'noun',
    'v': 'verb',
    'adj': 'adjective',
    'adv': 'adverb',
    'prep': 'preposition',
    'pron': 'pronoun',
    'interj': 'interjection',
    'conj': 'conjunction',
}

def parse_definition(definition):
    root_word = None
    alt_spellings = None
    part_of_speech = None
    conjugations = None

    definition = definition.strip()

    # Extract root word if it exists
    root_word_match = re.match(r'^([A-Z]+),', definition)
    if root_word_match:
        root_word = root_word_match.group(1)
        definition = definition[len(root_word) + 1:].strip()

    # Extract part of speech and conjugations if they exist
    pos_and_conj_match = re.search(r'\[([^]]+)\]', definition)
    if pos_and_conj_match:
        pos_and_conj = pos_and_conj_match.group(1)
        split_by_pos = pos_and_conj.split(" ", 1)
        part_of_speech = split_by_pos[0]
        if len(split_by_pos) > 1:
            conjugations = [x.strip() for x in split_by_pos[1].split(",")]

    # Extract alternate spellings if they exist
    alt_spellings_match = re.search(r', also ([^[]+)', definition)
    if alt_spellings_match:
        alt_spellings = [x.strip() for x in alt_spellings_match.group(1).split(",")]

    return root_word, definition, alt_spellings, part_of_speech, conjugations
