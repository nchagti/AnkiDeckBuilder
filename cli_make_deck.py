import argparse
import os
from deck_builder import anagram_deck_builder, leaves_deck_builder, defs_deck_builder

def main():
    parser = argparse.ArgumentParser(description="Create an Anki deck from a custom format")
    parser.add_argument('--input', '-i', required=True,
                        help='Input file: .txt for defs/anagrams, .csv or .jqz for leaves')
    parser.add_argument('--deck-name', '-d', required=True, help='Name of the Anki deck')
    parser.add_argument('--type', '-t', required=True,
                        choices=['leaves', 'defs', 'anagrams'], help='Type of deck to build')
    parser.add_argument('--db', help='Path to lexicon .db file (required for anagrams and defs type)')
    parser.add_argument('--color', action='store_true', help='Color-code Anagrams deck answers by number of anagrams. Color-code Leaves deck questions by leave value range. Color-code Definitions deck answers by part of speech.')
    parser.add_argument('--output', '-o', default='Anki Decks', help='Output folder for the .apkg file')

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if args.type in ['anagrams', 'defs'] and not args.db:
        parser.error(f"--db is required when --type is '{args.type}'")

    if args.type == 'anagrams':
        cards = anagram_deck_builder.build_cards(args.input, args.db)
        anagram_deck_builder.create_anki_deck(cards, args.deck_name, save_folder=args.output, use_custom_css=args.color)

    elif args.type == 'defs':
        cards = defs_deck_builder.parse_file(args.input, args.db)
        defs_deck_builder.create_anki_deck(cards, args.deck_name, save_folder=args.output, use_custom_css=args.color)


    elif args.type == 'leaves':
        cards = leaves_deck_builder.parse_file(args.input)
        leaves_deck_builder.create_anki_deck(cards, args.deck_name, save_folder=args.output, use_custom_css=args.color)

    else:
        raise ValueError("Unknown deck type")

if __name__ == '__main__':
    main()
