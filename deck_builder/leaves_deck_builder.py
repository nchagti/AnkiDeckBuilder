import genanki
import os
import csv
from .common import make_deck_id
from .anki_css import default_leaves_css, custom_leaves_css

RANGE_LABELS = [
    ((float("-inf"), -21), "leave_value::<=-21"),
    ((-20, -16), "leave_value::-20to-16"),
    ((-15, -11), "leave_value::-15to-11"),
    ((-10, -6), "leave_value::-10to-6"),
    ((-5, -1), "leave_value::-5to-1"),
    ((0, 5), "leave_value::0-5"),
    ((6, 10), "leave_value::6-10"),
    ((11, 15), "leave_value::11-15"),
    ((16, 20), "leave_value::16-20"),
    ((21, 25), "leave_value::21-25"),
    ((26, 30), "leave_value::26-30"),
    ((31, 35), "leave_value::31-35"),
    ((36, float("inf")), "leave_value::>=36"),
]

def get_lv_tag(leave_value):
    """Assign a leave value tag based on the whole number value."""
    for (low, high), label in RANGE_LABELS:
        if low <= leave_value <= high:
            return label
    return "leave_value::unknown"

def get_length_tag(leave):
    return f"length::{len(leave)}"

def get_blank_tag(leave):
    num_blanks = leave.count('?')
    return "blanks::no" if num_blanks == 0 else f"blanks::yes::{num_blanks}"


def parse_file(filepath):
    if filepath.lower().endswith('.csv'):
        return parse_csv(filepath)
    else:
        return parse_jqz(filepath)

def parse_jqz(filepath):
    cards = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or '<br>' not in line:
                continue  # skip empty or malformed lines

            try:
                # Split at <br>
                top, bottom = line.split('<br>')

                # Left of <br>: "LEAVE;WHOLE_VALUE"
                leave, whole = top.split(';')

                # Right of <br>: "FLOAT_VALUE;0"
                float_val, _ = bottom.split(';')

                letters = sorted([letter for letter in leave.upper() if letter.isalpha()]) # normalize and sort
                characters = [character for character in leave if not character.isalpha()] # get blanks

                question = ''.join(letters) + ''.join(characters)

                answer = f"{whole}<br>{float_val}"
                cards[question] = answer
            except ValueError:
                continue  # Skip malformed lines
    return cards

def parse_csv(filepath):
    cards = {}
    with open(filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) < 2:
                continue
            leave, value = row[0].strip().upper(), row[1].strip()
            try:
                value_float = float(value)
                whole = round(value_float)
                letters = sorted([letter for letter in leave.upper() if letter.isalpha()]) # normalize and alphabetize
                characters = [character for character in leave if not character.isalpha()] # get blanks

                question = ''.join(letters) + ''.join(characters)
                answer = f"{whole}<br>{value_float}"
                cards[question] = answer
            except ValueError:
                continue
    return cards

def write_csv_for_anki(cards: dict[str, str], deck_name: str, save_folder: str | None = None) -> str:
    """
    Writes a CSV with columns that exactly match the note type's field order.
    """
    if save_folder is None:
        save_folder = os.path.join(os.getcwd(), "Anki Decks")
    os.makedirs(save_folder, exist_ok=True)

    csv_path = os.path.join(save_folder, f"{deck_name}.csv")

    # New sort order: length asc, then alphabetical
    items = sorted(cards.items(), key=lambda kv: (len(kv[0]), kv[0]))

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        for q, a in items:
            try:
                whole_lv_str, _ = a.split("<br>")
                leave_value = int(whole_lv_str)
            except Exception:
                leave_value = 0

            lv_tag = get_lv_tag(leave_value)
            html_class = (
                lv_tag.replace("::", "_")
                     .replace(">=", "greater_than_")
                     .replace("<=", "less_than_")
            )
            w.writerow([q, a, html_class])

    print(f"CSV saved to: {csv_path}")
    return csv_path


def create_anki_deck(cards, deck_name, save_folder=None, use_custom_css=False):
    deck_id = make_deck_id(deck_name)

    if save_folder is None:
        save_folder = os.path.join(os.getcwd(), "Anki Decks")
    os.makedirs(save_folder, exist_ok=True)
    output_file = os.path.join(save_folder, f"{deck_name}.apkg")

    model = genanki.Model(
        32947309,
        'Leaves Model',
        fields=[{'name': 'Question'}, {'name': 'Answer'}, {'name': 'LV_Tag'}],
        templates=[{
            'name': 'Card 1',
            'qfmt': '<div class ="question"><span class="question-highlight {{LV_Tag}}">{{Question}}</span></div>',
            'afmt': '{{FrontSide}}<hr id="answer"><div class="{{Tags}}">{{Answer}}</div>'
        }],
        css=custom_leaves_css() if use_custom_css else default_leaves_css()
    )

    deck = genanki.Deck(deck_id, deck_name)

    for q, a in cards.items():
        try:
            whole_lv_str, _ = a.split('<br>')
            leave_value = int(whole_lv_str)
            leave_value_tag = get_lv_tag(leave_value)
            html_class = leave_value_tag.replace("::", "_")
            html_class = html_class.replace(">=", "greater_than_")
            html_class = html_class.replace("<=", "less_than_")


            # Tag by leave length
            length_tag = get_length_tag(q)

            # Tag by whether it has a blank
            blank_tag = get_blank_tag(q)

            note = genanki.Note(
                model=model,
                fields=[q, a, html_class],
                tags=[leave_value_tag, length_tag, blank_tag]
            )
            deck.add_note(note)

        except Exception as e:
            print(f"Error tagging card {q}: {e}")


    genanki.Package(deck).write_to_file(output_file)
    print(f"Anki deck '{deck_name}' saved to: {output_file}")
