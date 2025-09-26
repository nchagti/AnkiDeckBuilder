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
    parser.add_argument('--color', action='store_true', help='Color-code Anagrams deck answers by number of anagrams, Leaves deck questions by leave value range, and Definitions deck answers by part of speech.')
    parser.add_argument('--output', '-o', default='Anki Decks', help='Output folder for the .apkg file')
    parser.add_argument('--format', '-f', choices=['apkg', 'csv', 'both'], default='apkg', help='Output format: apkg (default), csv, or both')

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    saved_files = []

    if args.type == 'anagrams':
        cards = anagram_deck_builder.build_cards(args.input, args.db)
        if args.format in ('apkg', 'both'):
            path = anagram_deck_builder.create_anki_deck(
                cards, args.deck_name, save_folder=args.output, use_custom_css=args.color
            )
            saved_files.append(path)
        if args.format in ('csv', 'both'):
            path = anagram_deck_builder.write_csv_for_anki(cards, args.deck_name, save_folder=args.output)
            saved_files.append(path)

    elif args.type == 'defs':
        cards = defs_deck_builder.parse_file(args.input, args.db)
        if args.format in ('apkg', 'both'):
            defs_deck_builder.create_anki_deck(
                cards, args.deck_name, save_folder=args.output, use_custom_css=args.color
            )
            saved_files.append(os.path.join(args.output, f"{args.deck_name}.apkg"))
        if args.format in ('csv', 'both'):
            path = defs_deck_builder.write_csv_for_anki(cards, args.deck_name, save_folder=args.output)
            saved_files.append(path)

    elif args.type == 'leaves':
        cards = leaves_deck_builder.parse_file(args.input)
        if args.format in ('apkg', 'both'):
            leaves_deck_builder.create_anki_deck(
                cards, args.deck_name, save_folder=args.output, use_custom_css=args.color
            )
            saved_files.append(os.path.join(args.output, f"{args.deck_name}.apkg"))
        if args.format in ('csv', 'both'):
            path = leaves_deck_builder.write_csv_for_anki(cards, args.deck_name, save_folder=args.output)
            saved_files.append(path)

    else:
        raise ValueError("Unknown deck type")

    if saved_files:
        print("Success! Generated" + "\n".join(saved_files))


if __name__ == '__main__':
    main()
