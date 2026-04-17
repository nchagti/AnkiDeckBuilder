import os
import sys
import sqlite3
import genanki
from html import escape as _esc
from .common import make_deck_id, parse_definition, POS_MAP
from .anki_css import custom_anagrams_css, default_anagrams_css, custom_colors_css
import csv
from pathlib import Path
import re

# When running as a PyInstaller .exe, bundled files land in sys._MEIPASS.
# When running as a plain .py script, they live next to this source file.
if getattr(sys, 'frozen', False):
    _assets_base = Path(sys._MEIPASS)
else:
    _assets_base = Path(__file__).resolve().parent

font_path = _assets_base / "assets" / "_protiles.ttf"

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

def sort_consonants_first(alphagram):
    vowels = set('AEIOU')
    consonants = ''.join(sorted(c for c in alphagram if c not in vowels))
    vowel_part = ''.join(sorted(c for c in alphagram if c in vowels))
    return consonants + vowel_part

def sort_vowels_first(alphagram):
    vowels = set('AEIOU')
    vowel_part = ''.join(sorted(c for c in alphagram if c in vowels))
    consonants = ''.join(sorted(c for c in alphagram if c not in vowels))
    return vowel_part + consonants

def sort_tiles(alphagram, order='alpha'):
    """Rearranged according to order (alphabetical, consonants first, vowels first)
    """
    if order == 'cons':
        return sort_consonants_first(alphagram)
    elif order == 'vow':
        return sort_vowels_first(alphagram)
    else:  
        return alphagram

def _annotate_definition(definition: str, lexicon_lookup: dict) -> str:
    def replace(match):
        word = match.group(0)
        sym = lexicon_lookup.get(word, "")
        return word + sym
    return re.sub(r'[A-Z]{2,}', replace, definition)

def build_cards(input_file, db_path, tile_order='alpha', show_lexicon_symbols=False):
    alphagrams = extract_alphagrams_from_file(input_file)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return build_card_data(conn, alphagrams, tile_order=tile_order, show_lexicon_symbols=show_lexicon_symbols)

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

def bucketed_tags(tags, length, label, order, bucket_sizes=(500, 1000, 5000, 10000)):
    for size in bucket_sizes:
        start = ((order - 1) // size) * size + 1
        end = start + size - 1
        tags.add(f"len{length}::{label}::{start}-{end}")

def build_front_html(sorted_alphagram, alphagram, first_word):
    """attempting to make cool tiles that you can click on to go to the word's Neighborhood page """
    spans = "".join(f"<span class='tile'><span class='letter'>{c}</span></span>" for c in sorted_alphagram)
    return (
        f"<a class='alphalink' "
        f"href='https://www.studycade.com/#/neighborhood?query={alphagram}&word={first_word}'>"
        f"<div class='rack'>"
        f"  <div class='tiles'>{spans}</div>"
        f"</div>"
        f"</a>"
    )

def control_buttons():
    return """
    <div class="controls">
    <button class="ctrl-btn" id="shuffleBtn" onclick="shuffleTiles()" title="Shuffle">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor">
        <path d="M403.8 34.4c12-5 25.7-2.2 34.9 6.9l64 64c6 6 9.4 14.1 9.4 22.6s-3.4 16.6-9.4 22.6l-64 64c-9.2 9.2-22.9 11.9-34.9 6.9S384 204.9 384 192l0-32-32 0c-10.1 0-19.6 4.7-25.6 12.8l-32.4 43.2-40-53.3 21.2-28.3C293.3 110.2 321.8 96 352 96l32 0 0-32c0-12.9 7.8-24.6 19.8-29.6zM154 296l40 53.3-21.2 28.3C154.7 401.8 126.2 416 96 416l-64 0c-17.7 0-32-14.3-32-32s14.3-32 32-32l64 0c10.1 0 19.6-4.7 25.6-12.8L154 296zM438.6 470.6c-9.2 9.2-22.9 11.9-34.9 6.9S384 460.9 384 448l0-32-32 0c-30.2 0-58.7-14.2-76.8-38.4L121.6 172.8c-6-8.1-15.5-12.8-25.6-12.8l-64 0c-17.7 0-32-14.3-32-32S14.3 96 32 96l64 0c30.2 0 58.7 14.2 76.8 38.4L326.4 339.2c6 8.1 15.5 12.8 25.6 12.8l32 0 0-32c0-12.9 7.8-24.6 19.8-29.6s25.7-2.2 34.9 6.9l64 64c6 6 9.4 14.1 9.4 22.6s-3.4 16.6-9.4 22.6l-64 64z"></path>
        </svg>
    </button>

    <button class="ctrl-btn" id="resetBtn" onclick="resetTiles()" title="Reset">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" fill="currentColor">
        <path d="M297.4 566.6C309.9 579.1 330.2 579.1 342.7 566.6L502.7 406.6C515.2 394.1 515.2 373.8 502.7 361.3C490.2 348.8 469.9 348.8 457.4 361.3L352 466.7L352 96C352 78.3 337.7 64 320 64C302.3 64 288 78.3 288 96L288 466.7L182.6 361.3C170.1 348.8 149.8 348.8 137.3 361.3C124.8 373.8 124.8 394.1 137.3 406.6L297.3 566.6z"></path>
        </svg>
    </button>

    <button class="ctrl-btn" id="hintBtn" onclick="nextHint()" title="Hint">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" fill="currentColor">
        <path d="M424.5 355.1C449 329.2 464 294.4 464 256C464 176.5 399.5 112 320 112C240.5 112 176 176.5 176 256C176 294.4 191 329.2 215.5 355.1C236.8 377.5 260.4 409.1 268.8 448L371.2 448C379.6 409 403.2 377.5 424.5 355.1zM459.3 388.1C435.7 413 416 443.4 416 477.7L416 496C416 540.2 380.2 576 336 576L304 576C259.8 576 224 540.2 224 496L224 477.7C224 443.4 204.3 413 180.7 388.1C148 353.7 128 307.2 128 256C128 150 214 64 320 64C426 64 512 150 512 256C512 307.2 492 353.7 459.3 388.1zM272 248C272 261.3 261.3 272 248 272C234.7 272 224 261.3 224 248C224 199.4 263.4 160 312 160C325.3 160 336 170.7 336 184C336 197.3 325.3 208 312 208C289.9 208 272 225.9 272 248z"></path>
        </svg>
    </button>
    <span class="hint-display" id="hintDisplay"></span>
    </div>

    <script>
    (function () {
    var container = document.querySelector('.tiles');
    var originalOrder = container ? Array.from(container.children) : [];

    function shuffleTiles() {
        if (!container) return;
        var tiles = Array.from(container.children);
        for (var i = tiles.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        container.appendChild(tiles[j]);
        tiles[j] = tiles[i];
        }
    }
    window.shuffleTiles = shuffleTiles;

    function resetTiles() {
        if (!container) return;
        originalOrder.forEach(function (tile) {
        container.appendChild(tile);
        });
    }
    window.resetTiles = resetTiles;

    var raw = "{{Anagrams}}";
    var words = raw.split(',')
        .map(function (w) { return w.trim().toUpperCase(); })
        .filter(function (w) { return w.length > 0; })
        .sort();

    var firstLetters = words.map(function (w) { return w[0]; });
    var hintIndex = -1;

    var FLASH_MS = 120;

    function clearHints() {
    Array.from(container.children).forEach(function (tile) {
        tile.classList.remove('hint-active');
    });
    }

    function setHint(index) {
    clearHints();
    var letter = firstLetters[index];
    var found = false;
    Array.from(container.children).forEach(function (tile) {
        if (found) return;
        var el = tile.querySelector('.letter');
        if (el && el.textContent.trim()[0] === letter) {
        tile.classList.add('hint-active');
        found = true;
        }
    });
    }

    function nextHint() {
    if (firstLetters.length === 0) return;

    var nextIndex = (hintIndex + 1) % (firstLetters.length + 1);

    // Step lands on "clear" state
    if (nextIndex === firstLetters.length) {
        hintIndex = nextIndex;
        clearHints();
        return;
    }

    // Check if we're cycling through the same letter again
    var sameAsPrev = hintIndex >= 0
        && hintIndex < firstLetters.length
        && firstLetters[nextIndex] === firstLetters[hintIndex];

    hintIndex = nextIndex;

    if (sameAsPrev) {
        clearHints();
        setTimeout(function () { setHint(hintIndex); }, FLASH_MS);
    } else {
        setHint(hintIndex);
    }
    }
    window.nextHint = nextHint;

    document.addEventListener('keydown', function(e) {
    switch(e.key) {
    case 'j': shuffleTiles(); break;
    case 'k': resetTiles(); break;
    case 'l': nextHint(); break;
    }
    });

    })();
    </script>
"""

def _back_html_from_data(data: dict) -> str:
    return "<div class='entry-table'>" + "\n".join(data["entries"]) + "</div>"

def build_card_data(db_conn, alphagram_list, tile_order='alpha', show_lexicon_symbols=False):
    card_dict = {}
    rows = batch_query_by_alphagram(db_conn, alphagram_list)

    # Group rows by alphagram
    rows_by_alphagram = {}
    for row in rows:
        rows_by_alphagram.setdefault(row["alphagram"], []).append(row)

    lexicon_lookup = {}
    if show_lexicon_symbols:
        cursor = db_conn.cursor()
        cursor.execute("SELECT word, lexicon_symbols FROM words WHERE lexicon_symbols IS NOT NULL AND lexicon_symbols != ''")
        lexicon_lookup = {row["word"]: row["lexicon_symbols"] for row in cursor.fetchall()}


    for alphagram in alphagram_list:
        rows = rows_by_alphagram.get(alphagram)
        if not rows:
            continue

        entry_lines = []
        tags = set()

        first = rows[0] # get repeating info for all anagrams in first instance of anagram
        first_word = first["word"]
        sorted_alphagram = sort_tiles(alphagram, tile_order)
        front_html = build_front_html(sorted_alphagram, alphagram, first_word)
        length = first["length"]
        num_anagrams = first["num_anagrams"]
        num_vowels = first["num_vowels"]
        point_value = first["point_value"]
        num_unique_letters = first["num_unique_letters"]

        # General tags
        tags.add(f"anagrams_{num_anagrams}")
        tags.add(f"len{length}")

        if any(c in alphagram for c in 'JQXZ'):
            tags.add(f"len{length}::jqxz")

        if (length == 7 and num_vowels >= 4):
            tags.add("len7::vowels::4plus")
            tags.add("len7::vowel_dump")
        elif (length == 8 and num_vowels >= 5):
            tags.add("len8::vowels::5plus")
            tags.add("len8::vowel_dump")
        elif (length == 4 and num_vowels >= 3):
            tags.add("len4::vowels::3plus")
            tags.add("len4::vowel_dump")
        elif (length == 5 and num_vowels >= 4):
            tags.add("len5::vowels::4plus")
            tags.add("len5::vowel_dump")
        elif (length == 6 and num_vowels >= 4):
            tags.add("len6::vowels::4plus")
            tags.add("len6::vowel_dump")

        if num_vowels == 0:
            if 3 <= length <= 8:
                tags.add("consonant_dump")
        elif num_vowels == 1:
            if 5 <= length <= 8:
                tags.add("consonant_dump")

        tags.add(f"len{length}::vowels::{num_vowels}")

        hooks_by_word = {}

        # Sort entries
        for row in sorted(rows, key=lambda r: r["word"]): #sorting words alphabetically
            word = row["word"]
            play_order = row["playability_order"]
            prob_order = row["probability_order2"]
            front_hooks = row["front_hooks"] or ''
            back_hooks = row["back_hooks"] or ''
            hooks_by_word[word] = (front_hooks, back_hooks)
            is_front_hook = row["is_front_hook"]
            is_back_hook = row["is_back_hook"]
            definition = row["definition"]

            # High Five logic
            if length == 5:
                high_five_letters = set('FHKVWY')
                disqualifying_letters = set('JQXZ')
                if not any(c in word for c in disqualifying_letters):
                    if word[0] in high_five_letters or word[-1] in high_five_letters:
                        tags.add("high_five")

            lexicon_syms = (row["lexicon_symbols"] or "").strip() if show_lexicon_symbols else ""
            # Add inner hook markers
            display_word = word
            if is_front_hook:
                display_word = '·' + display_word
            if is_back_hook:
                display_word = display_word + '·' + lexicon_syms
            elif lexicon_syms:
                display_word = display_word + lexicon_syms

            # Play/Prob order strings
            main_order = play_order if length in (4, 5, 6) else prob_order #still want to display prob and play orders
            order_str = "" if main_order is None else str(main_order)
            
            # Escape HTML special characters
            front_hooks_disp = _esc(front_hooks or "")
            back_hooks_disp  = _esc(back_hooks or "")
            word_disp        = _esc(display_word)
            annotated_def     = _annotate_definition(definition, lexicon_lookup) if show_lexicon_symbols else definition
            def_disp         = _esc(annotated_def)


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

            # Tag by indv prob + indv play
            tags.add(f"len{length}::prob::{prob_order}")
            tags.add(f"len{length}::play::{play_order}")

            entry_html = (
                f"<div class='entry-row'>"
                f"<div class='col order'>{order_str}</div>"
                f"<div class='col front'>{front_hooks_disp}</div>"
                f"<div class='col anagram'>{word_disp}</div>"
                f"<div class='col back'>{back_hooks_disp}</div>"
                f"<div class='col definition'>{def_disp}</div>"
                f"</div>"
            )
            entry_lines.append(entry_html)

        #sort the PlayOrderList and ProbOrderList fields by ascending order
        prob_vals = sorted([r["probability_order2"] for r in rows if r["probability_order2"]]) 
        play_vals = sorted([r["playability_order"]  for r in rows if r["playability_order"]])

        #tag buckets based on first value in each list
        if prob_vals:
            bucketed_tags(tags, length, "prob", prob_vals[0])

        if play_vals:
            bucketed_tags(tags, length, "play", play_vals[0])

        prob_orders = ", ".join(map(str, prob_vals))
        play_orders = ", ".join(map(str, play_vals))

        #create zero-padded sort key fields
        prob_sort_key = f"{(prob_vals[0] if prob_vals else 999999):06d}"
        play_sort_key = f"{(play_vals[0] if play_vals else 999999):06d}"

        words = sorted([r["word"] for r in rows if r["word"]])
        anagrams = ", ".join(words)

        # Pool all unique hook letters across every anagram in this card, sorted A-Z
        all_front_hook_letters = sorted(set("".join(hooks[0] for hooks in hooks_by_word.values())))
        all_back_hook_letters  = sorted(set("".join(hooks[1] for hooks in hooks_by_word.values())))
        front_hooks_field = "".join(all_front_hook_letters)
        back_hooks_field  = "".join(all_back_hook_letters)

        card_dict[alphagram] = {
            "sorted_alphagram": sorted_alphagram,
            "alphagram": alphagram,
            "front_html": front_html,
            "entries": entry_lines,
            "anagrams": anagrams,
            "first_word": first_word,
            "front_hooks_field": front_hooks_field,
            "back_hooks_field": back_hooks_field,
            "tags": sorted(tags),
            "length": str(length),
            "num_vowels": str(num_vowels),
            "num_anagrams": str(num_anagrams),
            "prob_orders": prob_orders,
            "play_orders": play_orders,
            "prob_sort_key": prob_sort_key,
            "play_sort_key": play_sort_key,
            "num_unique_letters": str(num_unique_letters),
            "point_value": str(point_value),            
            }

    return card_dict


#Sort 7s and up by probability, 3-6 by playability
def _len_aware_sort_key(item):
    alphagram, data = item
    L = int(data["length"])

    if L >= 7:
        order_str = data["prob_orders"]
        prob_key = int(order_str.split(",")[0].strip()) if order_str else 10**9
        return (0, prob_key, data["sorted_alphagram"])   # bucket 0 = 7+ sorted by probability
    else:
        order_str = data["play_orders"]
        play_key = int(order_str.split(",")[0].strip()) if order_str else 10**9
        return (1, play_key, data["sorted_alphagram"])   # bucket 1 = <7 sorted by playability

def write_csv_for_anki(cards_dict: dict, deck_name: str, save_folder: str | None = None) -> str:
    """
    Writes a CSV with columns that exactly match the note type's field order, plus a Tags column.
    """
    if save_folder is None:
        save_folder = os.path.join(os.getcwd(), "Anki Decks")
    os.makedirs(save_folder, exist_ok=True)

    csv_path = Path(save_folder) / f"{deck_name}.csv"

    # Deterministic row order (not required by Anki, but nice to have)
    items = sorted(cards_dict.items(), key=_len_aware_sort_key)

    def tags_to_str(tags): # anki wants space-separated tags
        return " ".join(sorted(tags))

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        for alphagram, data in items:
            back_html = _back_html_from_data(data)
            tags_str = tags_to_str(data["tags"])
            sorted_alphagram = data["sorted_alphagram"]
            writer.writerow([
                alphagram,
                sorted_alphagram,
                data["front_html"],
                back_html,
                data["anagrams"],
                data["first_word"],
                data["front_hooks_field"],
                data["back_hooks_field"],
                data["length"],
                data["num_vowels"],
                data["num_unique_letters"],
                data["point_value"],
                data["prob_orders"],
                data["play_orders"],
                data["prob_sort_key"],
                data["play_sort_key"],
                data["num_anagrams"],
                tags_str,
            ])

    print(f"CSV saved to: {csv_path}")
    return str(csv_path)

def build_and_export(input_file, db_path, deck_name, save_folder=None, use_custom_css=False):
    cards_dict = build_cards(input_file, db_path)

    # Create .apkg as before (optional)
    create_anki_deck(cards_dict, deck_name, save_folder=save_folder, use_custom_css=use_custom_css)

    # Also write a CSV for "Update existing notes" imports
    write_csv_for_anki(cards_dict, deck_name, save_folder=save_folder)


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
            {'name': 'SortedAlphagram'},
            {'name': 'FrontHTML'},
            {'name': 'Back'},
            {'name': 'Anagrams'},
            {'name': 'FirstWord'},
            {'name': 'FrontHooks'},
            {'name': 'BackHooks'},
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
            'qfmt': '{{FrontHTML}}' + control_buttons(),
            'afmt': '{{FrontSide}}<hr id="answer"><div class="{{Tags}}">{{Back}}</div>',
        }],
        css= (
            custom_anagrams_css() 
            if use_custom_css 
            else default_anagrams_css() + "\n\n@media not all {\n" + custom_colors_css() + "\n}")
    )

    deck = genanki.Deck(deck_id, deck_name)

    for alphagram, data in sorted(cards_dict.items(), key=_len_aware_sort_key):
        back = "<div class='entry-table'>" + "\n".join(data['entries']) + "</div>"
        note = genanki.Note(
            model=model,
            fields=[
                alphagram,
                data['sorted_alphagram'],
                data['front_html'],
                back,
                data['anagrams'],
                data['first_word'],
                data['front_hooks_field'],
                data['back_hooks_field'],
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

    package = genanki.Package(deck)
    print(f"Font_path: {font_path}")
    print(f"Font exists: {font_path.exists()}")
    if font_path.exists():
        package.media_files = [str(font_path)]
        print(f"media_files set to: {package.media_files}")
    package.write_to_file(output_file)
    print(f"Anki deck saved to: {output_file}")
    return output_file


