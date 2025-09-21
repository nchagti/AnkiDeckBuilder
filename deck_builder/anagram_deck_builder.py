import os
import sqlite3
import genanki
from html import escape as _esc
from .common import make_deck_id, parse_definition, POS_MAP
from .anki_css import custom_anagrams_css, default_anagrams_css

def extract_alphagrams_from_file(filepath):
    """
    Read a file and return a deduplicated list of uppercase alphagrams.
    Handles lines that are either full words or already alphagrams.
    """
    alphagrams = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            word = line.strip().upper()
            if not word:
                print(f"[DEBUG] Skipping empty line at index {i}")  # i = line number
                continue
            alphagram = ''.join(sorted(word))
            alphagrams.add(alphagram)
    return sorted(alphagrams)

def build_cards(input_file, db_path):
    alphagrams = extract_alphagrams_from_file(input_file)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return build_card_data(conn, alphagrams)

def batch_query_by_alphagram(conn, alphagrams):
    cursor = conn.cursor()
    all_results = []
    BATCH_SIZE = 900

    for i in range(0, len(alphagrams), BATCH_SIZE):
        batch = alphagrams[i:i+BATCH_SIZE]
        placeholders = ','.join('?' for _ in batch)
        query = f"SELECT * FROM words WHERE alphagram IN ({placeholders})"
        cursor.execute(query, batch)
        all_results.extend(cursor.fetchall())

    return all_results

def build_card_data(db_conn, alphagram_list):
    card_dict = {}
    rows = batch_query_by_alphagram(db_conn, alphagram_list)

    # Group rows by alphagram
    rows_by_alphagram = {}
    for row in rows:
        rows_by_alphagram.setdefault(row["alphagram"], []).append(row)

    for alphagram in alphagram_list:
        rows = rows_by_alphagram.get(alphagram)
        if not rows:
            continue

        entry_lines = []
        tags = set()

        first = rows[0] # get repeating info for all anagrams in first instance of anagram
        length = first["length"]
        num_anagrams = first["num_anagrams"]
        num_vowels = first["num_vowels"]
        point_value = first["point_value"]
        num_unique_letters = first["num_unique_letters"]

        tags.add(f"anagrams_{num_anagrams}")

        tags.add(f"len{length}")

        if any(c in alphagram for c in 'JKQXZ'):
            tags.add(f"len{length}::jkqxz")

        if (length == 7 and num_vowels >= 4):
            tags.add("len7::vowels::4plus")
            tags.add("vowel_dump")
        elif (length == 8 and num_vowels >= 5):
            tags.add("len8::vowels::5plus")
            tags.add("vowel_dump")
        elif (length == 4 and num_vowels >= 3):
            tags.add("len4::vowels::3plus")
            tags.add("vowel_dump")
        elif (length == 5 and num_vowels >= 4):
            tags.add("len5::vowels::4plus")
            tags.add("vowel_dump")
        elif (length == 6 and num_vowels >= 4):
            tags.add("len6::vowels::4plus")
            tags.add("vowel_dump")

        if num_vowels == 0:
            if 4 <= length <= 8:
                tags.add("consonant_dump")
        elif num_vowels == 1:
            if 5 <= length <= 8:
                tags.add("consonant_dump")

        tags.add(f"len{length}::vowels::{num_vowels}")

        # Sort entries
        for row in sorted(rows, key=lambda r: r["word"]):
            word = row["word"]
            play_order = row["playability_order"]
            prob_order = row["probability_order1"]
            front_hooks = row["front_hooks"] or ''
            back_hooks = row["back_hooks"] or ''
            is_front_hook = row["is_front_hook"]
            is_back_hook = row["is_back_hook"]
            definition = row["definition"]

            # High Five logic
            if length == 5:
                high_five_letters = set('FHKVWY')
                disqualifying_letters = set('JQXZ')
                if not any(c in word for c in disqualifying_letters):
                    if word[0] in high_five_letters or word[-1] in high_five_letters:
                        tags.add("len5::high_five")


            # Add inner hook markers
            display_word = word
            if is_front_hook:
                display_word = '·' + display_word
            if is_back_hook:
                display_word = display_word + '·'

            # Escape HTML special characters
            front_hooks_disp = _esc(front_hooks or "")
            back_hooks_disp  = _esc(back_hooks or "")
            word_disp        = _esc(display_word)
            def_disp         = _esc(definition)

            # Extract and map part of speech
            definitions = [d.strip() for d in definition.split(' / ') if d.strip()]
            for d in definitions:
                try:
                    root, clean_def, alt_spellings, pos, conj = parse_definition(d)
                except ValueError:
                    continue

                if pos in POS_MAP:
                    tags.add(POS_MAP[pos])
                if alt_spellings:
                    tags.add("alternate_spellings")

            # Tag by bucket
            if length in (4, 5, 6):
                # tags.add(f"len{length}::play::{play_order}")
                play_bucket = (play_order - 1) // 500 * 500 + 1
                tags.add(f"len{length}::play::{play_bucket}-{play_bucket + 499}")
            elif length in (7, 8, 9):
                # tags.add(f"len{length}::prob::{prob_order}")
                prob_bucket = (prob_order - 1) // 500 * 500 + 1
                tags.add(f"len{length}::prob::{prob_bucket}-{prob_bucket + 499}")

            entry_html = (
                f"<div class='entry-row'>"
                f"<div class='col front'>{front_hooks_disp}</div>"
                f"<div class='col anagram'>{word_disp}</div>"
                f"<div class='col back'>{back_hooks_disp}</div>"
                f"<div class='col definition'>{def_disp}</div>"
                f"</div>"
            )
            entry_lines.append(entry_html)

        prob_vals = sorted([r["probability_order1"] for r in rows if r["probability_order1"]])
        play_vals = sorted([r["playability_order"]  for r in rows if r["playability_order"]])

        prob_orders = ", ".join(map(str, prob_vals))
        play_orders = ", ".join(map(str, play_vals))

        prob_sort_key = f"{(prob_vals[0] if prob_vals else 999999):06d}"
        play_sort_key = f"{(play_vals[0] if play_vals else 999999):06d}"


        card_dict[alphagram] = {
            "entries": entry_lines,
            "tags": sorted(tags),
            "length": str(length),
            "num_vowels": str(num_vowels),
            "num_anagrams": str(num_anagrams),
            "prob_orders": prob_orders,
            "play_orders": play_orders,
            "prob_sort_key": prob_sort_key,
            "play_sort_key": play_sort_key,
            "num_unique_letters": str(num_unique_letters),
            "point_value": str(point_value)
            }

    return card_dict

def _len_aware_sort_key(item):
    alphagram, data = item
    L = int(data["length"])

    if L >= 7:
        s = data["prob_orders"]
        prob_key = int(s.split(",")[0].strip()) if s else 10**9
        return (0, prob_key, alphagram)   # bucket 0 = 7+ sorted by probability
    else:
        s = data["play_orders"]
        play_key = int(s.split(",")[0].strip()) if s else 10**9
        return (1, play_key, alphagram)   # bucket 1 = 3–6 sorted by playability


def create_anki_deck(cards_dict, deck_name, save_folder=None, use_custom_css=False):
    deck_id = make_deck_id(deck_name)

    if save_folder is None:
        save_folder = os.path.join(os.getcwd(), "Anki Decks")
    os.makedirs(save_folder, exist_ok=True)
    output_file = os.path.join(save_folder, f"{deck_name}.apkg")

    model = genanki.Model(
        1607392319,
        'Anagram Model',
        fields=[
            {'name': 'Alphagram'}, 
            {'name': 'Back'},
            {'name': 'Length'},
            {'name': 'NumVowels'},
            {'name': 'NumUniqueLetters'},
            {'name': 'PointValue'},
            {'name': 'ProbOrderList'},
            {'name': 'PlayOrderList'},
            {'name': 'ProbSortKey'},
            {'name': 'PlaySortKey'},
            {'name': 'NumAnagrams'}],

        templates=[{
            'name': 'Card 1',
            'qfmt': '{{Alphagram}}',
            'afmt': '{{FrontSide}}<hr id="answer"><div class="{{Tags}}">{{Back}}</div>',
        }],
        css=custom_anagrams_css() if use_custom_css else default_anagrams_css()
    )

    deck = genanki.Deck(deck_id, deck_name)

    for alphagram, data in sorted(cards_dict.items(), key=_len_aware_sort_key):
        back = "<div class='entry-table'>" + "\n".join(data['entries']) + "</div>"
        note = genanki.Note(
            model=model,
            fields=[
                alphagram,
                back,
                data['length'],
                data['num_vowels'],
                data['num_unique_letters'],
                data['point_value'],
                data['prob_orders'],
                data['play_orders'],
                data['prob_sort_key'],
                data['play_sort_key'],
                data['num_anagrams'],
        ],
            tags=data['tags']
        )
        deck.add_note(note)

    genanki.Package(deck).write_to_file(output_file)
    print(f"Anki deck saved to: {output_file}")

