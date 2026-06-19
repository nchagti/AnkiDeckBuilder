#!/usr/bin/env python3
"""
migrate_zyzzyva_to_anki.py

Migrates Zyzzyva/Xerafin Leitner cardbox stats from Anagrams.db into
an existing Anki collection by writing directly to collection.anki2.

IMPORTANT: Anki must be closed before running this script.

After running, open Anki. If you sync, choose "Upload to AnkiWeb".

Requirements: no extra packages needed

Usage:
    # Windows (Command Prompt):
    python migrate_zyzzyva_to_anki.py ^
        --db "path\to\Anagrams.db" ^
        --collection "C:\Users\you\AppData\Roaming\Anki2\ProfileName\collection.anki2" ^
        --deck "deckname" --field "Alphagram"
 
    # Windows (PowerShell):
    python migrate_zyzzyva_to_anki.py `
        --db "path\to\Anagrams.db" `
        --collection "C:\Users\you\AppData\Roaming\Anki2\ProfileName\collection.anki2" `
        --deck "deckname" --field "Alphagram"
 
    # macOS:
    python3 migrate_zyzzyva_to_anki.py \
        --db "path/to/Anagrams.db" \
        --collection "~/Library/Application Support/Anki2/ProfileName/collection.anki2" \
        --deck "deckname" --field "Alphagram"
 
    # Linux:
    python3 migrate_zyzzyva_to_anki.py \
        --db "path/to/Anagrams.db" \
        --collection "~/.local/share/Anki2/ProfileName/collection.anki2" \
        --deck "deckname" --field "Alphagram"
 
    # Dry run (any OS, add --dry-run to any of the above):
    python migrate_zyzzyva_to_anki.py --db ... --collection ... --deck "All" --field "Alphagram" --dry-run
 
    # Test with a small batch first (recommended):
    python migrate_zyzzyva_to_anki.py ... --limit 10
"""

import sqlite3
import argparse
import json
import sys
import time
from datetime import datetime, timezone

# ── Constants ────────────────────────────────────────────────────────────────

ANKI_EPOCH_UNIX = 1136073600   # 2006-01-01 UTC (fallback only)
PROGRESS_EVERY  = 1000

CARDBOX_TO_IVL = {
    0:  1,
    1:  4,
    2:  7,
    3:  12,
    4:  20,
    5:  30,
    6:  60,
    7:  90,
    8:  150,
    9:  270,
}
CARDBOX_MAX_IVL = 480

# ── Conversion helpers ────────────────────────────────────────────────────────

def cardbox_to_ivl(cardbox):
    return CARDBOX_TO_IVL.get(cardbox, CARDBOX_MAX_IVL)


def compute_interval(next_scheduled):
    # ivl = days from now until next_scheduled.
    if not next_scheduled or next_scheduled <= 0:
        return 1
    return max(1, (next_scheduled - int(time.time())) // 86400)


def compute_factor(lapses, correct):
    d = max(1.0, min(10.0, 5 + lapses - 0.5 * correct))
    factor = int(2500 - (d - 5) * 150)
    return max(1300, min(3500, factor))


def compute_due_day(next_scheduled, crt):
    # Due is days since collection creation time (col.crt)
    if not next_scheduled or next_scheduled <= 0:
        return max(0, (int(time.time()) - crt) // 86400)
    return max(0, (next_scheduled - crt) // 86400)


def compute_last_ivl(cardbox):
    return cardbox_to_ivl(max(0, cardbox - 1))

# ── Index builder ─────────────────────────────────────────────────────────────

def build_alphagram_index(anki_conn, deck, field):
    print(f"Building alphagram index for deck '{deck}' ...")
    cur = anki_conn.cursor()

    # ── Field ordinal lookup ──────────────────────────────────────────────────
    # Anki 2.1.45+ uses a separate `fields` table.
    # Older versions store field definitions as JSON in notetypes.flds.
    field_ord_by_ntid = {}
    try:
        cur.execute("SELECT ntid, ord, name FROM fields")
        for ntid, ord_, name in cur.fetchall():
            if name == field:
                field_ord_by_ntid[ntid] = ord_
        if not field_ord_by_ntid:
            raise ValueError("field not found in fields table")
    except (sqlite3.OperationalError, ValueError):
        # Fall back to JSON column
        try:
            cur.execute("SELECT id, flds FROM notetypes")
            for ntid, flds_json in cur.fetchall():
                try:
                    fields_list = json.loads(flds_json)
                    for f in fields_list:
                        if f.get("name") == field:
                            field_ord_by_ntid[ntid] = f.get("ord", 0)
                            break
                except Exception:
                    pass
        except sqlite3.OperationalError:
            pass

    if not field_ord_by_ntid:
        print(f"ERROR: Field '{field}' not found in any note type.")
        sys.exit(1)

    # ── Deck ID lookup ────────────────────────────────────────────────────────
    # Anki 2.1.45+ uses a separate `decks` table.
    # Older versions store deck info as JSON in col.decks.
    deck_ids = set()
    try:
        cur.execute("SELECT id, name FROM decks")
        for did, name in cur.fetchall():
            if name == deck or name.startswith(deck + "\x1f") or name.startswith(deck + "::"):
                deck_ids.add(int(did))
    except sqlite3.OperationalError:
        cur.execute("SELECT decks FROM col")
        row = cur.fetchone()
        decks_data = json.loads(row[0])
        for did, dinfo in decks_data.items():
            name = dinfo.get("name", "")
            if name == deck or name.startswith(deck + "\x1f") or name.startswith(deck + "::"):
                deck_ids.add(int(did))

    if not deck_ids:
        print(f"ERROR: Deck '{deck}' not found in collection.")
        sys.exit(1)

    print(f"  Found {len(deck_ids)} deck(s) matching '{deck}'.")

    # ── Fetch cards ───────────────────────────────────────────────────────────
    placeholders = ",".join("?" * len(deck_ids))
    cur.execute(f"""
        SELECT c.id, n.mid, n.flds
        FROM cards c
        JOIN notes n ON c.nid = n.id
        WHERE c.did IN ({placeholders})
    """, list(deck_ids))

    index = {}
    for card_id, mid, flds in cur.fetchall():
        ord_ = field_ord_by_ntid.get(mid)
        if ord_ is None:
            continue
        parts = flds.split("\x1f")
        if ord_ < len(parts):
            alphagram = parts[ord_].strip()
            if alphagram:
                index[alphagram] = card_id

    print(f"Index built: {len(index)} alphagrams mapped to card IDs.")
    return index

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Migrate Zyzzyva/Xerafin cardbox stats to Anki (direct SQLite write)"
    )
    parser.add_argument("--db",         required=True, help="Path to Anagrams.db")
    parser.add_argument("--collection", required=True, help="Path to collection.anki2")
    parser.add_argument("--deck",       required=True, help="Anki deck name (exact, or parent)")
    parser.add_argument("--field",      required=True, help="Note field containing the alphagram")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Print what would be done without making changes")
    parser.add_argument("--limit",      type=int, default=None,
                        help="Only process the first N rows (for testing)")
    args = parser.parse_args()

    # ── Load Anagrams.db ──────────────────────────────────────────────────────
    print(f"Opening {args.db} ...")
    zyz_conn = sqlite3.connect(args.db)
    zyz_conn.row_factory = sqlite3.Row

    query = """
        SELECT question, correct, incorrect, cardbox, last_correct, next_scheduled
        FROM questions
    """
    if args.limit:
        query += f" LIMIT {args.limit}"
    rows = zyz_conn.execute(query).fetchall()
    zyz_conn.close()
    print(f"Loaded {len(rows)} questions from Anagrams.db.")

    if args.dry_run:
        print("*** DRY RUN — no changes will be made ***\n")

    # ── Open collection.anki2 ─────────────────────────────────────────────────
    anki_conn = sqlite3.connect(args.collection)

    # ── Read collection creation time (used for due day calculation) ─────────
    crt = anki_conn.execute("SELECT crt FROM col").fetchone()[0]
    print(f"Collection epoch: {crt} ({__import__('datetime').datetime.fromtimestamp(crt).strftime('%Y-%m-%d')})")

    # ── Build index ───────────────────────────────────────────────────────────
    card_index = build_alphagram_index(anki_conn, args.deck, args.field)

    # ── Process ───────────────────────────────────────────────────────────────
    found = skipped = errors = 0
    t_start = time.time()
    now = int(time.time())

    card_updates  = []
    revlog_inserts = []

    for i, row in enumerate(rows):
        alphagram      = row["question"]
        correct        = row["correct"]        or 0
        incorrect      = row["incorrect"]      or 0
        cardbox        = row["cardbox"]        or 0
        last_correct   = row["last_correct"]   or 0
        next_scheduled = row["next_scheduled"] or 0

        reps     = correct + incorrect
        lapses   = incorrect
        ivl      = compute_interval(next_scheduled)
        factor   = compute_factor(lapses, correct)
        due_day  = compute_due_day(next_scheduled, crt)
        last_ivl = ivl  # set lastIvl == ivl so revlog is internally consistent

        if last_correct > 0:
            revlog_id = last_correct * 1000 + (i % 1000)
        else:
            revlog_id = now * 1000 + i

        if args.dry_run:
            due_str = (datetime.fromtimestamp(next_scheduled, tz=timezone.utc).strftime('%Y-%m-%d')
                       if next_scheduled else 'unknown')
            print(
                f"  {alphagram:16s}  reps={reps}  lapses={lapses}"
                f"  ivl={ivl}d  ease={factor/10:.0f}%  due={due_str}"
            )
            found += 1
            continue

        card_id = card_index.get(alphagram)
        if card_id is None:
            print(f"  SKIP  {alphagram}")
            skipped += 1
            continue

        card_updates.append((
            2,        # type  = review
            2,        # queue = review
            ivl,
            due_day,
            reps,
            lapses,
            factor,
            now,      # mod
            card_id,
        ))

        revlog_inserts.append((
            revlog_id,
            card_id,
            -1,       # usn = needs sync
            3,        # ease = Good
            ivl,
            last_ivl,
            factor,
            10000,    # time in ms
            1,        # type = review
        ))

        found += 1

        if found % PROGRESS_EVERY == 0:
            elapsed   = time.time() - t_start
            rate      = found / elapsed if elapsed > 0 else 0
            remaining = len(rows) - i - 1
            eta_s     = int(remaining / rate) if rate > 0 else 0
            eta_m, eta_s = divmod(eta_s, 60)
            print(
                f"  Queued: {found} cards, {skipped} skipped"
                f"  |  {rate:.0f} cards/s  |  ETA ~{eta_m}m{eta_s:02d}s"
            )

    # ── Write ─────────────────────────────────────────────────────────────────
    if not args.dry_run:
        print(f"\nWriting {len(card_updates)} card updates and {len(revlog_inserts)} revlog entries ...")
        try:
            cur = anki_conn.cursor()
            cur.executemany("""
                UPDATE cards
                SET type=?, queue=?, ivl=?, due=?, reps=?, lapses=?, factor=?, mod=?
                WHERE id=?
            """, card_updates)

            # Delete any existing revlog entries for these cards (from previous runs).
            # Chunk into batches of 500 to stay under SQLite's variable limit.
            card_ids_to_clean = [r[1] for r in revlog_inserts]
            chunk_size = 500
            for i in range(0, len(card_ids_to_clean), chunk_size):
                chunk = card_ids_to_clean[i:i+chunk_size]
                placeholders = ",".join("?" * len(chunk))
                cur.execute(f"DELETE FROM revlog WHERE cid IN ({placeholders})", chunk)

            cur.executemany("""
                INSERT INTO revlog (id, cid, usn, ease, ivl, lastIvl, factor, time, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, revlog_inserts)

            anki_conn.commit()
            print("Committed successfully.")
        except Exception as e:
            anki_conn.rollback()
            print(f"ERROR during write: {e}")
            errors += 1
        finally:
            anki_conn.close()

    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"Done in {elapsed:.1f}s.")
    print(f"  Updated : {found}")
    print(f"  Skipped : {skipped}  (alphagram not in deck)")
    print(f"  Errors  : {errors}")
    if args.dry_run:
        print("  (Dry run — no actual changes were written)")
    else:
        print("  Open Anki to verify. If you sync, choose 'Upload to AnkiWeb'.")


if __name__ == "__main__":
    main()