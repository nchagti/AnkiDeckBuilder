import sqlite3
from .common import make_deck_id, parse_definition, POS_MAP
import os
import genanki
from .anki_css import default_defs_css, custom_defs_css


def parse_file(filepath, db_path):
    cards = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        words = [line.strip().upper() for line in f if line.strip()]

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        BATCH_SIZE = 900

        for i in range(0, len(words), BATCH_SIZE):
            batch = words[i:i + BATCH_SIZE]
            placeholders = ','.join('?' for _ in batch)
            query = f"""
            SELECT word, is_front_hook, is_back_hook, front_hooks, back_hooks, definition
                FROM words 
                WHERE word IN ({placeholders})
            """
            cursor.execute(query, batch)
            results = cursor.fetchall()

            for word, is_front_hook, is_back_hook, front_hooks, back_hooks, def_text in results:
                # Add inner hook markers
                display_word = word
                if is_front_hook:
                    display_word = '·' + display_word
                if is_back_hook:
                    display_word = display_word + '·'

                # Add outer front/back hooks 
                question_parts = []
                if front_hooks:
                    question_parts.append(front_hooks)
                question_parts.append(display_word)
                if back_hooks:
                    question_parts.append(back_hooks)

                question = " ".join(question_parts)

                # Tag part of speech for each definition and alt spellings
                tags = set()
                definitions = [d.strip() for d in def_text.split(' / ') if d.strip()]
                for d in definitions:
                    try:
                        root, clean_def, alt_spellings, pos, conj = parse_definition(d)
                    except ValueError:
                        continue

                    if pos in POS_MAP:
                        tags.add(POS_MAP[pos])
                    if alt_spellings:
                        tags.add("alternate_spellings")

                if is_front_hook or is_back_hook:
                    tags.add("inner_hook")

                cards[question] = {
                    "answer": def_text,
                    "tags": sorted(tags)
                }

    return cards

def write_csv_for_anki(cards: dict, deck_name: str, save_folder: str | None = None) -> str:
    """
    Writes a CSV with columns that exactly match the note type's field order.
    """
    import csv

    if save_folder is None:
        save_folder = os.path.join(os.getcwd(), "Anki Decks")
    os.makedirs(save_folder, exist_ok=True)

    csv_path = os.path.join(save_folder, f"{deck_name}.csv")

    # Deterministic order: alphabetical by Question
    items = sorted(cards.items(), key=lambda kv: kv[0])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        for question, data in items:
            wrapped_answer = f"<div class='definition-answer'>{data['answer']}</div>"
            w.writerow([question, wrapped_answer])

    print(f"CSV saved to: {csv_path}")
    return csv_path


def create_anki_deck(cards, deck_name, save_folder=None, use_custom_css=False):
    deck_id = make_deck_id(deck_name)

    # Create "Anki Decks" folder if it doesn't exist
    if save_folder is None:
        save_folder = os.path.join(os.getcwd(), "Anki Decks")

    os.makedirs(save_folder, exist_ok=True)
    output_file = os.path.join(save_folder, f"{deck_name}.apkg")


    model = genanki.Model(
        1443640762,
        'Definitions Model',
        fields=[{'name': 'Question'}, {'name': 'Answer'}],
        templates=[{
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer"><div class={{Tags}}>{{Answer}}</div>'
        }],
        css=custom_defs_css() if use_custom_css else default_defs_css()
    )

    deck = genanki.Deck(deck_id, deck_name)

    for word, data in cards.items():
        wrapped_answer = f"<div class='definition-answer'>{data['answer']}</div>"
        note = genanki.Note(
            model=model,
            fields=[word, wrapped_answer],
            tags=data['tags']
        )
        deck.add_note(note)


    genanki.Package(deck).write_to_file(output_file)
    print(f"Anki deck '{deck_name}' saved to: {output_file}")
