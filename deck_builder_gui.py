import customtkinter as ctk
from tkinter import filedialog, messagebox
from deck_builder import anagram_deck_builder, leaves_deck_builder, defs_deck_builder
from utils import save_last_folder, load_last_folder
import os


class AnkiDeckBuilder(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Anki Deck Builder")
        self.geometry("400x700")
        self.resizable(True, True)

        # State variables
        self.deck_name_var = ctk.StringVar()
        self.deck_type_var = ctk.StringVar(value="Anagrams")
        self.db_path_var = ctk.StringVar()
        self.use_anagrams_css_var = ctk.BooleanVar(value=False)     # Anagrams
        self.use_leaves_css_var = ctk.BooleanVar(value=False)  # Leaves
        self.use_defs_css_var = ctk.BooleanVar(value=False)    # Definitions
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
        # Deck Name
        ctk.CTkLabel(self, text="Deck Name:", anchor="w").pack(padx=20, pady=(15, 5), fill="x")
        self.deck_name_entry = ctk.CTkEntry(self, placeholder_text="Create a deck name", textvariable=self.deck_name_var)
        self.deck_name_entry.pack(padx=20, fill="x")

        # Deck Type
        ctk.CTkLabel(self, text="Deck Type:", anchor="w").pack(padx=20, pady=(15, 0), fill="x")
        self.deck_type_menu = ctk.CTkOptionMenu(self, values=["Anagrams", "Leaves", "Definitions"], variable=self.deck_type_var, command=self.on_deck_type_change)
        self.deck_type_menu.set("Anagrams")
        self.deck_type_menu.pack(padx=20, fill="x")

        # Frame to hold dynamic checkboxes based on deck type
        self.css_checkbox_frame = ctk.CTkFrame(self)
        self.css_checkbox_frame.pack(padx=20, pady=(8, 0), fill="x")

        # Input File
        ctk.CTkLabel(self, text="Input File:", anchor="w").pack(padx=20, pady=(15, 0), fill="x")
        self.input_file_button = ctk.CTkButton(self, text="Select File", command=self.select_input_file)
        self.input_file_button.pack(padx=20, fill="x")
        self.input_file_label = ctk.CTkLabel(self, text="", text_color="gray", anchor="w")
        self.input_file_label.pack(padx=20, pady=(0, 7), fill="x")

        # Database File Picker (hidden if not Anagrams or Definitions type)
        self.db_file_label_widget = ctk.CTkLabel(self, text="Lexicon Database:", anchor="w")
        self.db_file_button = ctk.CTkButton(self, text="Select .db File", command=self.select_db_file)
        self.db_file_path_display = ctk.CTkLabel(self, text="", text_color="gray", anchor="w")

        # Save Folder
        self.save_folder_label_widget = ctk.CTkLabel(self, text="Select Folder to Save Anki Deck:", anchor="w")
        self.save_folder_label_widget.pack(padx=17, fill="x")
        self.save_folder_button = ctk.CTkButton(self, text="Choose Folder", command=self.select_save_folder)
        self.save_folder_button.pack(padx=20, fill="x")
        self.save_folder_label = ctk.CTkLabel(
            self, 
            text=self.folder_name_display(), text_color="gray", anchor="w", wraplength=365,  # Set wrap width (pixels)
            justify="left"   
        ) # Align multi-line text to the left
        self.save_folder_label.pack(padx=20, pady=(7, 5), fill="x")

        # Output format
        ctk.CTkLabel(self, text="Output format:", anchor="w").pack(padx=20, pady=(15, 0), fill="x")
        self.format_menu = ctk.CTkOptionMenu(
            self,
            values=["APKG (Anki deck)", "CSV", "Both"],
            variable=self.output_format_var
        )
        self.format_menu.pack(padx=20, fill="x")


        # Create Deck
        self.create_button = ctk.CTkButton(self, text="Create Deck", command=self.create_deck)
        self.create_button.pack(padx=50, pady=(45, 15), fill="x")

        # Status
        self.status_label = ctk.CTkLabel(
            self, 
            textvariable=self.status_text, 
            text_color="white", 
            wraplength=360, 
            justify="left"
        )
        self.status_label.pack(padx=20, fill="x")

        # Checkbox for CSS
        self.anagrams_css_checkbox = ctk.CTkCheckBox(self.css_checkbox_frame, text="Color-code answers by number of anagrams", variable=self.use_anagrams_css_var)
        self.leaves_css_checkbox = ctk.CTkCheckBox(self.css_checkbox_frame, text="Color-code questions by leave value range", variable=self.use_leaves_css_var)
        self.defs_css_checkbox = ctk.CTkCheckBox(self.css_checkbox_frame, text="Color-code definitions by part of speech", variable=self.use_defs_css_var)

        # Hide DB widgets initially if not needed
        self.db_file_label_widget.pack_forget()
        self.db_file_button.pack_forget()
        self.db_file_path_display.pack_forget()


        # Since Anagrams is the default, show the DB file selector
        self.on_deck_type_change("Anagrams")


    def folder_name_display(self):
        if self.user_chose_folder and self.save_folder_path:
            return f"Saving to: {self.save_folder_path}"
        return "If you don't choose a folder, one labeled 'Anki Decks' will automatically be created in the directory with your deck."

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

        for widget in self.css_checkbox_frame.winfo_children():
            widget.pack_forget()

        # Show only the relevant one
        if selected_type.lower() == "anagrams":
            self.anagrams_css_checkbox.pack(anchor="w")
        elif selected_type.lower() == "definitions":
            self.defs_css_checkbox.pack(anchor="w")
        elif selected_type.lower() == "leaves":
            self.leaves_css_checkbox.pack(anchor="w")
        
        if selected_type.lower() in ["anagrams", "definitions"]:
            self.db_file_label_widget.pack(padx=20, fill="x", before=self.save_folder_label_widget)
            self.db_file_button.pack(padx=20, fill="x", before=self.save_folder_label_widget)
            self.db_file_path_display.pack(padx=20, pady=(0,7), fill="x", before=self.save_folder_label_widget)
        else:
            self.db_file_label_widget.pack_forget()
            self.db_file_button.pack_forget()
            self.db_file_path_display.pack_forget()

            self.db_path_var.set("")  # Clear the stored DB path
            self.db_file_path_display.configure(text="")

        # Restrict output formats based on deck type
        formats = self._allowed_formats_for(selected_type)
        self.format_menu.configure(values=formats)
        if self.output_format_var.get() not in formats:
            self.output_format_var.set(formats[0])  # snap to a valid choice


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

                # Build the data once
                cards = anagram_deck_builder.build_cards(self.input_file_path, db_path)

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
