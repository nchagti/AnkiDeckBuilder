#---- bootstrap ----
# This section ensures that required dependencies are installed at runtime.

import os, sys, subprocess, importlib.util, re
from pathlib import Path

def _have(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except Exception:
        return False

def _ensure_tk_or_die():
    # Tk cannot be reliably installed via pip; it must come with Python/system pkgs
    if _have("tkinter"):
        return
    msg = (
        "[deps] tkinter is not available. The GUI cannot start without Tk.\n"
        "Suggested fixes by OS:\n"
        "  • Windows/macOS: Install Python from python.org (includes Tk).\n"
        "  • Ubuntu/Debian:  sudo apt-get install python3-tk\n"
        "  • Fedora:         sudo dnf install python3-tkinter\n"
        "  • Arch:           sudo pacman -S tk\n"
    )
    print(msg)
    sys.exit(1)

def _parse_requirements(req_path: Path) -> list[str]:
    """Return distribution specifiers exactly as written"""
    specs = []
    if not req_path.exists():
        return specs
    for line in req_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        specs.append(line)
    return specs

def _dist_name(spec: str) -> str:
    """
    Extract distribution name from a requirement spec."""
    return re.split(r"[<>=;\[\s]", spec, maxsplit=1)[0]

def _module_name_from_dist(dist: str) -> str:
    """
    Best-effort mapping from distribution to import module.
    Handles common differences (e.g., PyYAML -> yaml).
    """
    special = {
        "PyYAML": "yaml",
    }
    if dist in special:
        return special[dist]
    # heuristic: normalize dashes to underscores, lowercase
    return dist.replace("-", "_").lower()

def _missing_modules_from_requirements(req_specs: list[str]) -> list[str]:
    missing = []
    for spec in req_specs:
        dist = _dist_name(spec)
        mod = _module_name_from_dist(dist)
        if not _have(mod):
            missing.append(spec)  # keep full spec for pip install
    return missing

def _pip_install(args: list[str]) -> bool:
    cmd = [sys.executable, "-m", "pip", "install"] + args
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[deps] pip failed: {e}")
        return False

def _ensure_runtime_requirements():
    """
    If any modules in requirements.txt are missing, install them
    and re-execute the script exactly once.
    """
    project_dir = Path(__file__).resolve().parent
    req_path = project_dir / "requirements.txt"
    specs = _parse_requirements(req_path)
    if not specs:
        return  # no runtime requirements file; assume dev environment

    missing_specs = _missing_modules_from_requirements(specs)
    if not missing_specs:
        return  # all good

    if os.environ.get("ANKI_GUI_BOOTSTRAPPED") == "1":
        # already tried installing and restarted; avoid loops
        print("[deps] Missing modules remain after install attempt. Exiting.")
        sys.exit(1)

    print(f"[deps] Missing dependencies detected; installing from {req_path.name} ...")
    ok = _pip_install(["-r", str(req_path)])
    if not ok:
        print("[deps] Automatic install failed. Please run: pip install -r requirements.txt")
        sys.exit(1)

    # Re-execute the script so fresh modules are importable cleanly
    os.environ["ANKI_GUI_BOOTSTRAPPED"] = "1"
    os.execv(sys.executable, [sys.executable, *sys.argv])

# Order: Tk check first (cannot auto-install), then requirements
_ensure_tk_or_die()
_ensure_runtime_requirements()

# ---- end bootstrap ----


import customtkinter as ctk
from tkinter import filedialog, messagebox
from deck_builder import anagram_deck_builder, leaves_deck_builder, defs_deck_builder
from utils import save_last_folder, load_last_folder
import os

# Padding constants shared across build_ui and on_deck_type_change
LABEL_PADX = (15, 8)
WIDGET_PADX = (0, 15)


class AnkiDeckBuilder(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Anki Deck Builder")
        self.geometry("575x610")
        self.resizable(True, True)

        # State variables
        self.deck_name_var = ctk.StringVar()
        self.deck_type_var = ctk.StringVar(value="Anagrams")
        self.db_path_var = ctk.StringVar()
        self.tile_order_var = ctk.StringVar(value="Alphabetical")
        self.use_anagrams_css_var = ctk.BooleanVar(value=False)
        self.use_leaves_css_var = ctk.BooleanVar(value=False)
        self.use_defs_css_var = ctk.BooleanVar(value=False)
        self.show_lexicon_symbols_var = ctk.BooleanVar(value=False)
        self.input_file_path = None
        self.last_input_dir = load_last_folder("input")
        self.db_path_var.set(load_last_folder("last_db_folder") or "")
        self.output_format_var = ctk.StringVar(value="APKG (Anki deck)")  # APKG (Anki deck) | CSV | Both
        self.save_folder_path = load_last_folder()

        # Clear save_folder_path if the folder was deleted
        if self.save_folder_path and not os.path.isdir(self.save_folder_path):
            self.save_folder_path = None
        self.user_chose_folder = False
        self.status_text = ctk.StringVar()

        # UI Setup
        self.build_ui()

    def build_ui(self):
        # Grid layout: col 0 = labels (fixed width), col 1 = controls (expanding)
        # Each row: label inline to the left of its control — landscape-friendly form
        self.columnconfigure(0, weight=0, minsize=150)
        self.columnconfigure(1, weight=1)


        # Row 0: Deck Name
        ctk.CTkLabel(self, text="Deck Name:", anchor="w").grid(
            row=0, column=0, padx=LABEL_PADX, pady=(15, 0), sticky="w")
        self.deck_name_entry = ctk.CTkEntry(
            self, placeholder_text="Create a deck name", textvariable=self.deck_name_var, width=250)
        self.deck_name_entry.grid(row=0, column=1, padx=WIDGET_PADX, pady=(15, 0), sticky="w")

        # Row 1: Deck Type
        ctk.CTkLabel(self, text="Deck Type:", anchor="w").grid(
            row=1, column=0, padx=LABEL_PADX, pady=(20, 0), sticky="w")
        self.deck_type_menu = ctk.CTkOptionMenu(
            self, values=["Anagrams", "Leaves", "Definitions"],
            variable=self.deck_type_var, command=self.on_deck_type_change, width=250, anchor="center")
        self.deck_type_menu.set("Anagrams")
        self.deck_type_menu.grid(row=1, column=1, padx=WIDGET_PADX, pady=(20, 0), sticky="w")

        # Row 2: Checkboxes — col 1 only, stacked in a transparent frame
        self.css_checkbox_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.css_checkbox_frame.grid(row=2, column=1, padx=(0, 10), pady=(5, 0), sticky="ew")

        # Color-code checkbox (deck-type specific, shown/hidden in on_deck_type_change)
        self.anagrams_css_checkbox = ctk.CTkCheckBox(
            self.css_checkbox_frame,
            text="Color-code answers by number of anagrams",
            variable=self.use_anagrams_css_var,
            checkbox_width=18, checkbox_height=18)
        self.leaves_css_checkbox = ctk.CTkCheckBox(
            self.css_checkbox_frame,
            text="Color-code questions by leave value range",
            variable=self.use_leaves_css_var,
            checkbox_width=18, checkbox_height=18)
        self.defs_css_checkbox = ctk.CTkCheckBox(
            self.css_checkbox_frame,
            text="Color-code definitions by part of speech",
            variable=self.use_defs_css_var,
            checkbox_width=18, checkbox_height=18)

        # "Show lexicon symbols" row — checkbox with grey info text below
        self._lex_sym_row = ctk.CTkFrame(self.css_checkbox_frame, fg_color="transparent")
        self.show_lexicon_checkbox = ctk.CTkCheckBox(
            self._lex_sym_row, text="Show lexicon symbols",
            variable=self.show_lexicon_symbols_var,
            checkbox_width=18, checkbox_height=18)
        self.show_lexicon_checkbox.pack(anchor="w")
        ctk.CTkLabel(
            self._lex_sym_row,
            text="Note: This requires the lexicon_symbols column in your .db file to be pre-populated. You can use Zyzzyva to choose your preferred lexicon symbols",
            text_color="gray", anchor="w", wraplength=350, justify="left"
        ).pack(anchor="w", padx=(25, 0), pady=(1, 2))

        # Row 3: Tile Order (Anagrams only — gridded/removed in on_deck_type_change)
        self.tile_order_label = ctk.CTkLabel(self, text="Tile order:", anchor="w")
        self.tile_order_menu = ctk.CTkOptionMenu(
            self, values=["Alphabetical", "Consonant-first", "Vowel-first"],
            variable=self.tile_order_var, width=250, anchor="center")

        # Row 4: Input File — button + selected-file label stacked in col 1
        ctk.CTkLabel(self, text="Input file:", anchor="w").grid(
            row=4, column=0, padx=LABEL_PADX, pady=(14, 0), sticky="nw")
        _if_frame = ctk.CTkFrame(self, fg_color="transparent")
        _if_frame.grid(row=4, column=1, padx=WIDGET_PADX, pady=(14, 0), sticky="w")
        self.input_file_button = ctk.CTkButton(
            _if_frame, text="Select .txt File", command=self.select_input_file, width=250)
        self.input_file_button.grid(row=0, column=0, sticky="w")
        self.input_file_label = ctk.CTkLabel(
            _if_frame, text="", text_color="gray", anchor="w")
        self.input_file_label.grid(row=1, column=0, sticky="w")

        # Row 5: Lexicon Database (Anagrams/Definitions only — gridded/removed in on_deck_type_change)
        self.db_file_label_widget = ctk.CTkLabel(self, text="Lexicon database:", anchor="w")
        self._db_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.db_file_button = ctk.CTkButton(
            self._db_frame, text="Select .db File", command=self.select_db_file, width=250)
        self.db_file_button.grid(row=0, column=0, sticky="w")
        self.db_file_path_display = ctk.CTkLabel(
            self._db_frame, text="", text_color="gray", anchor="w")
        self.db_file_path_display.grid(row=1, column=0, sticky="w")

        # Row 6: Save Folder
        ctk.CTkLabel(self, text="Save folder:", anchor="w").grid(
            row=6, column=0, padx=LABEL_PADX, pady=(2, 0), sticky="nw")
        _sf_frame = ctk.CTkFrame(self, fg_color="transparent")
        _sf_frame.grid(row=6, column=1, padx=WIDGET_PADX, pady=(2, 0), sticky="w")
        self.save_folder_button = ctk.CTkButton(
            _sf_frame, text="Choose Folder", command=self.select_save_folder, width=250)
        self.save_folder_button.grid(row=0, column=0, sticky="w")
        self.save_folder_label = ctk.CTkLabel(
            _sf_frame, text=self.folder_name_display(),
            text_color="gray", anchor="w", wraplength=390, justify="left")
        self.save_folder_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        # Row 7: Output Format
        ctk.CTkLabel(self, text="Output format:", anchor="w").grid(
            row=7, column=0, padx=LABEL_PADX, pady=(20, 4), sticky="w")
        self.format_menu = ctk.CTkOptionMenu(
            self, values=["APKG (Anki deck)", "CSV", "Both"],
            variable=self.output_format_var, width=250, anchor="center")
        self.format_menu.grid(row=7, column=1, padx=WIDGET_PADX, pady=(20, 4), sticky="w")

        # Row 8: Create Deck — centered across both columns
        self.create_button = ctk.CTkButton(self, text="Create Deck", command=self.create_deck, width=180)
        self.create_button.grid(row=8, column=0, columnspan=2, pady=(30, 8))

        # Row 9: Status (spans both columns)
        self.status_label = ctk.CTkLabel(
            self, textvariable=self.status_text,
            text_color="white", wraplength=560, justify="left")
        self.status_label.grid(row=9, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        # Trigger initial state for Anagrams
        self.on_deck_type_change("Anagrams")


    def folder_name_display(self):
        if self.user_chose_folder and self.save_folder_path:
            return f"Saving to: {self.save_folder_path}"
        return "If you don't choose a folder, one labeled 'Anki Decks' will automatically be created in the working directory with your deck."

    def select_input_file(self):
        deck_type = self.deck_type_menu.get().lower()
        if deck_type == "leaves":
            filetypes = [("Leaves Data Files", "*.csv *.jqz"), ("All Files", "*.*")]
        else:
            filetypes = [("Text Files", "*.txt"), ("All Files", "*.*")]

        initial_dir = self.last_input_dir if self.last_input_dir and os.path.isdir(self.last_input_dir) else os.getcwd()

        file_path = filedialog.askopenfilename(filetypes=filetypes, initialdir=initial_dir)
        if file_path:
            self.input_file_path = file_path
            self.input_file_label.configure(text=os.path.basename(file_path))
            self.last_input_dir = os.path.dirname(file_path)
            save_last_folder(self.last_input_dir, key="input")

    def on_deck_type_change(self, selected_type):
        deck_type = selected_type.lower()

        # ── Checkboxes (col 1 frame) ──────────────────────────────────────────
        for checkbox_widget in self.css_checkbox_frame.winfo_children():
            checkbox_widget.pack_forget()

        if deck_type == "anagrams":
            self.anagrams_css_checkbox.pack(anchor="w")
            self._lex_sym_row.pack(anchor="w", pady=(4, 0))
        elif deck_type == "definitions":
            self.defs_css_checkbox.pack(anchor="w")
        elif deck_type == "leaves":
            self.leaves_css_checkbox.pack(anchor="w")

        # ── Tile order row (Anagrams only) ────────────────────────────────────
        if deck_type == "anagrams":
            self.tile_order_label.grid(row=3, column=0, padx=(15, 8), pady=(20, 15), sticky="w")
            self.tile_order_menu.grid(row=3, column=1, padx=(0, 15), pady=(20, 15), sticky="w")
        else:
            self.tile_order_label.grid_remove()
            self.tile_order_menu.grid_remove()

        # ── Input file button label ───────────────────────────────────────────
        if deck_type == "leaves":
            self.input_file_button.configure(text="Select .csv / .jqz File")
        else:
            self.input_file_button.configure(text="Select .txt File")

        # ── Lexicon DB row (Anagrams + Definitions only) ──────────────────────
        if deck_type in ("anagrams", "definitions"):
            self.db_file_label_widget.grid(row=5, column=0, padx=(15, 8), pady=2, sticky="nw")
            self._db_frame.grid(row=5, column=1, padx=(0, 15), pady=2, sticky="ew")
        else:
            self.db_file_label_widget.grid_remove()
            self._db_frame.grid_remove()
            self.db_path_var.set("")
            self.db_file_path_display.configure(text="")

        # ── Output formats ────────────────────────────────────────────────────
        formats = self._allowed_formats_for(selected_type)
        self.format_menu.configure(values=formats)
        if self.output_format_var.get() not in formats:
            self.output_format_var.set(formats[0])

    def select_db_file(self):
        # Load the last used .db folder, fallback to current directory
        initial_dir = load_last_folder("last_db_folder") or os.getcwd()

        path = filedialog.askopenfilename(
            title="Select Lexicon Database",
            filetypes=[("SQLite DB", "*.db"), ("All Files", "*.*")],
            initialdir=initial_dir
        )
        if path:
            self.db_path_var.set(path)
            self.db_file_path_display.configure(text=os.path.basename(path))
            # Save the folder where this file was selected
            save_last_folder(os.path.dirname(path), key="last_db_folder")
        
    def _allowed_formats_for(self, deck_type: str):
        deck_type = deck_type.lower()
        return ["APKG (Anki deck)", "CSV", "Both"] 

    
    def select_save_folder(self):
        initial_dir = self.save_folder_path if self.save_folder_path and os.path.isdir(self.save_folder_path) else os.getcwd()
        selected = filedialog.askdirectory(title="Select folder to save", initialdir=initial_dir)
        if selected:
            self.save_folder_path = selected
            self.user_chose_folder = True
            save_last_folder(selected)
            self.save_folder_label.configure(text=self.folder_name_display())


    def create_deck(self):
        name = self.deck_name_var.get().strip()
        deck_type = self.deck_type_var.get().lower()
        fmt = self.output_format_var.get()
              
        if not name:
            messagebox.showerror("Missing Info", "Please enter a deck name.")
            return
        if not self.input_file_path:
            messagebox.showerror("Missing Info", "Please select an input file.")
            return

        # Resolve save folder
        if self.user_chose_folder and self.save_folder_path and os.path.isdir(self.save_folder_path):
            save_path = self.save_folder_path
        else:
            default_folder = os.path.join(os.getcwd(), "Anki Decks")
            os.makedirs(default_folder, exist_ok=True)
            save_path = default_folder

        try:
            saved_files = []

            if deck_type == "anagrams":
                db_path = self.db_path_var.get()
                if not db_path:
                    messagebox.showerror("Missing Database", "Anagrams require a .db file.")
                    return

                tile_order_map = {
                    "Alphabetical": "alpha",
                    "Consonant-first": "cons",
                    "Vowel-first": "vow",
                }
                tile_order = tile_order_map.get(self.tile_order_var.get(), "alpha")

                # Build the data once
                cards = anagram_deck_builder.build_cards(self.input_file_path, db_path, tile_order=tile_order, show_lexicon_symbols=self.show_lexicon_symbols_var.get())

                # APKG?
                if fmt in ("APKG (Anki deck)", "Both"):
                    use_custom_css = self.use_anagrams_css_var.get()
                    apkg_path = anagram_deck_builder.create_anki_deck(cards, name, save_folder=save_path, use_custom_css=use_custom_css)
                    saved_files.append(apkg_path)


                # CSV?
                if fmt in ("CSV", "Both"):
                    csv_path = anagram_deck_builder.write_csv_for_anki(cards, name, save_folder=save_path)
                    saved_files.append(csv_path)

            elif deck_type == "definitions":
                db_path = self.db_path_var.get()
                if not db_path:
                    messagebox.showerror("Missing Database", "Definitions require a .db file.")
                    return
                cards = defs_deck_builder.parse_file(self.input_file_path, db_path)
                use_custom_css = self.use_defs_css_var.get()

                if fmt in ("APKG (Anki deck)", "Both"):
                    defs_deck_builder.create_anki_deck(cards, name, save_folder=save_path, use_custom_css=use_custom_css)
                    saved_files.append(os.path.join(save_path, f"{name}.apkg"))

                if fmt in ("CSV", "Both"):
                    csv_path = defs_deck_builder.write_csv_for_anki(cards, name, save_folder=save_path)
                    saved_files.append(csv_path)


            elif deck_type == "leaves":
                cards = leaves_deck_builder.parse_file(self.input_file_path)
                use_custom_css = self.use_leaves_css_var.get()

                if fmt in ("APKG (Anki deck)", "Both"):
                    leaves_deck_builder.create_anki_deck(cards, name, save_folder=save_path, use_custom_css=use_custom_css)
                    saved_files.append(os.path.join(save_path, f"{name}.apkg"))

                if fmt in ("CSV", "Both"):
                    csv_path = leaves_deck_builder.write_csv_for_anki(cards, name, save_folder=save_path)
                    saved_files.append(csv_path)



            # Report success
            if saved_files:
                msg = "Success! Generated\n" + "\n".join(saved_files)
                self.status_text.set(msg)
                self.status_label.configure(text_color="white")
            
        except Exception as e:
            self.status_text.set(f"Error: {str(e)}")
            self.status_label.configure(text_color="red")



if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue")  
    app = AnkiDeckBuilder()
    app.mainloop()
