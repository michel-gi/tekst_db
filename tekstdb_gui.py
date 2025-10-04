#!/usr/bin/env python3
"""
Een GUI-applicatie voor het bewerken van tekst-databases.
Gebaseerd op tekstdb_bewerk.py.
"""

import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from database import TextDatabase


class TextEntryDialog(tk.Toplevel):
    """Een modaal dialoogvenster voor het invoeren van meerdere regels tekst."""

    def __init__(self, parent, title=None, prompt=None, initial_text=""):
        """Initialiseert het dialoogvenster."""
        super().__init__(parent)
        self.transient(parent)  # Blijf boven het hoofdvenster
        self.parent = parent
        self.result = None

        if title:
            self.title(title)

        # Frame voor de inhoud
        body = ttk.Frame(self, padding="10")
        self.initial_focus = self.body(body, prompt, initial_text)
        body.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.buttonbox()

        self.grab_set()  # Maak modaal

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")
        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master, prompt, initial_text):
        """Creëert de inhoud van het dialoogvenster."""
        if prompt:
            ttk.Label(master, text=prompt).pack(pady=5, anchor=tk.W)

        text_frame = ttk.Frame(master, borderwidth=1, relief="sunken")
        self.text = tk.Text(text_frame, width=60, height=15, wrap=tk.WORD)
        self.text.insert("1.0", initial_text)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
        self.text["yscrollcommand"] = scrollbar.set

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_frame.pack(fill=tk.BOTH, expand=True)

        return self.text  # Geef focus aan het tekstveld

    def buttonbox(self):
        """Creëert de OK en Annuleren knoppen."""
        box = ttk.Frame(self)
        ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(box, text="Annuleren", width=10, command=self.cancel).pack(side=tk.LEFT, padx=5, pady=5)
        # De onderstaande regel is verwijderd omdat deze het venster bij elke Enter-toetsdruk sloot,
        # wat ongewenst is in een multi-line Text widget.
        # self.bind("<Return>", self.ok)
        # Gebruik Ctrl+Enter om op te slaan, dit is een gangbare conventie die niet conflicteert met typen.
        self.bind("<Control-Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def ok(self, event=None):
        """Verwerkt de OK-knop."""
        self.result = self.text.get("1.0", tk.END).strip()
        self.parent.focus_set()
        self.destroy()

    def cancel(self, event=None):
        """Verwerkt de Annuleren-knop."""
        self.parent.focus_set()
        self.destroy()


class TekstDbGuiApp:
    """De Tkinter GUI voor de TekstDB bewerker."""

    DATABASE_FILETYPES = (
        ("Databasebestanden", "*.txt *.TXT *.dat *.DAT"),
        ("Tekstbestanden", "*.txt"),
        ("Alle bestanden", "*.*"),
    )

    def __init__(self, master, filepath=None):
        """Initialiseert de applicatie."""
        self.master = master
        master.geometry("800x600")  # Startgrootte (iets groter voor de preview)

        # Variabele voor de zoekbalk
        self.search_var = tk.StringVar()
        self.preview_text = None  # Placeholder voor de preview widget
        self._search_debounce_job = None  # Voor de zoek-debounce
        # Variabelen voor drag-and-drop
        self._clipboard_item = None
        self._drag_source_index = None
        self._drop_indicator = None

        # --- Database initialisatie ---
        db_file = filepath or "mijn_tekstdatabase.txt"
        self.db = TextDatabase(db_file)
        self._update_title()

        # Hoofdframe
        self.main_frame = ttk.Frame(master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Statusbalk onderaan het venster
        self.status_bar = ttk.Label(master, text="", relief=tk.SUNKEN, anchor=tk.W, padding=2)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.create_menu()
        self.create_widgets()
        self.bind_keys()
        # Laad de data in de lijst bij het opstarten
        self.refresh_item_list()
        self._update_ui_state()

    def _update_title(self):
        """Updates the window title with the current database filename."""
        dirty_marker = "*" if self.db.dirty else ""
        self.master.title(f"TekstDB Bewerker - {self.db.bestandsnaam}{dirty_marker}")

    def create_menu(self):
        """Maakt de menubalk voor de applicatie."""
        menubar = tk.Menu(self.master)
        self.master["menu"] = menubar

        # Bestand menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Bestand", menu=file_menu, underline=0)
        file_menu.add_command(label="Nieuwe database...", command=self.new_database, underline=0)
        file_menu.add_command(label="Open...", command=self.open_database, accelerator="Ctrl+O", underline=0)
        file_menu.add_separator()
        file_menu.add_command(label="Opslaan", command=self.save_database, accelerator="Ctrl+S", underline=0)
        file_menu.add_command(
            label="Opslaan als...", command=self.save_database_as, accelerator="Ctrl+Shift+S", underline=1
        )
        file_menu.add_separator()
        file_menu.add_command(label="Sluiten", command=self.sluit_applicatie, accelerator="Ctrl+Q", underline=0)

        # Bewerken menu
        self.edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Bewerken", menu=self.edit_menu, underline=1)
        self.edit_menu.add_command(label="Nieuw item...", command=self.nieuw_item, accelerator="Ctrl+N", underline=0)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Wijzig item...", command=self.wijzig_item, accelerator="Ctrl+W", underline=0)
        self.edit_menu.add_command(
            label="Verwijder item...", command=self.verwijder_item, accelerator="Del", underline=0
        )
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Knippen", command=self.cut_item, accelerator="Ctrl+X", underline=2)
        self.edit_menu.add_command(
            label="Plakken", command=self.paste_item, accelerator="Ctrl+V", underline=1, state=tk.DISABLED
        )
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Zoek...", command=self.focus_search, accelerator="Ctrl+F", underline=0)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu, underline=0)
        help_menu.add_command(label="Over...", command=self.show_about, underline=0)

    def create_widgets(self):
        """Maakt de widgets (knoppen, etc.) in het hoofdvenster."""
        # Frame voor de knoppen, onderaan geplaatst
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # Knoppen
        self.btn_nieuw = ttk.Button(button_frame, text="Nieuw", command=self.nieuw_item)
        self.btn_nieuw.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_wijzig = ttk.Button(button_frame, text="Wijzig", command=self.wijzig_item)
        self.btn_wijzig.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_verwijder = ttk.Button(button_frame, text="Verwijder", command=self.verwijder_item)
        self.btn_verwijder.pack(side=tk.LEFT, padx=5, pady=5)

        # Een 'spacer' om de sluiten-knop naar rechts te duwen
        spacer = ttk.Frame(button_frame)
        spacer.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.btn_sluiten = ttk.Button(button_frame, text="Sluiten", command=self.sluit_applicatie)
        self.btn_sluiten.pack(side=tk.RIGHT, padx=5, pady=5)

        # --- Frame voor de zoekbalk ---
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(pady=5, padx=0, fill=tk.X, side=tk.TOP)

        ttk.Label(search_frame, text="Zoek:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Gebruik debouncing voor live zoeken om UI-vertraging te voorkomen
        self.search_var.trace_add("write", self._on_search_change)

        ttk.Button(search_frame, text="Wissen", command=self.clear_search).pack(side=tk.LEFT, padx=(5, 0))

        # --- PanedWindow voor een resizable scheiding tussen lijst en preview ---
        paned_window = ttk.PanedWindow(self.main_frame, orient=tk.VERTICAL)
        paned_window.pack(pady=5, padx=0, fill=tk.BOTH, expand=True, side=tk.TOP)

        # --- Frame voor de lijst en scrollbar (bovenste paneel) ---
        list_frame = ttk.Frame(paned_window)
        paned_window.add(list_frame, weight=4)

        # Configureer grid layout voor de list_frame om beide scrollbars te plaatsen
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Verticale Scrollbar
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        # Horizontale Scrollbar
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Listbox voor de items
        self.item_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            exportselection=False,
            height=25,  # Stel een initiële hoogte in (in tekstregels)
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
        )
        self.item_listbox.grid(row=0, column=0, sticky="nsew")

        # --- Frame voor de preview (onderste paneel) ---
        preview_frame = ttk.Frame(paned_window)
        paned_window.add(preview_frame, weight=1)  # Geef de preview minder gewicht bij resizen

        preview_scrollbar = ttk.Scrollbar(preview_frame)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.preview_text = tk.Text(
            preview_frame,
            yscrollcommand=preview_scrollbar.set,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=8,  # Stel een initiële hoogte in (in tekstregels)
        )
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Koppel scrollbars aan widgets
        v_scrollbar["command"] = self.item_listbox.yview
        h_scrollbar["command"] = self.item_listbox.xview
        preview_scrollbar["command"] = self.preview_text.yview  # pyright: ignore[reportOptionalMemberAccess]

        # Voeg dubbelklik-event toe om een item te wijzigen
        self.item_listbox.bind("<Double-1>", lambda event: self.wijzig_item())

        # Update de knopstatus en preview wanneer de selectie verandert.
        # <<ListboxSelect>> wordt geactiveerd door zowel muisklikken als pijltjestoetsen.
        # <<ListboxSelect>> wordt geactiveerd door zowel muisklikken als pijltjestoetsen.
        self.item_listbox.bind("<<ListboxSelect>>", self._on_selection_change)
        self.item_listbox.bind("<KeyRelease-Up>", self._force_selection_on_arrow)
        self.item_listbox.bind("<KeyRelease-Down>", self._force_selection_on_arrow)

    def bind_keys(self):
        """Bindt toetsen aan de commando's."""
        # Sneltoetsen met Ctrl
        self.master.bind("<Control-f>", lambda event: self.focus_search())
        self.master.bind("<Control-o>", lambda event: self.open_database())
        self.master.bind("<Control-s>", lambda event: self.save_database())
        self.master.bind("<Control-S>", lambda event: self.save_database_as())  # Control-Shift-S
        self.master.bind("<Control-n>", lambda event: self.nieuw_item())
        self.master.bind("<Control-w>", lambda event: self.wijzig_item())
        self.master.bind("<Control-x>", lambda event: self.cut_item())
        self.master.bind("<Control-v>", lambda event: self.paste_item())
        self.master.bind("<Control-q>", lambda event: self.sluit_applicatie())

        # Bind de Delete-toets aan de verwijder-functie voor extra gebruiksgemak
        self.master.bind("<Delete>", lambda event: self.verwijder_item())

        # Bind drag-and-drop events
        self.item_listbox.bind("<Button-1>", self._on_drag_start)
        self.item_listbox.bind("<B1-Motion>", self._on_drag_motion)
        self.item_listbox.bind("<ButtonRelease-1>", self._on_drag_release)

    # --- Data-operaties ---

    def refresh_item_list(self):
        """Leest de data uit de database en vult de listbox."""
        # Zorgt ervoor dat de zoekbalk leeg is en de volledige lijst wordt getoond.
        self.clear_search()

    def _populate_listbox(self, items_to_display):
        """Hulpfunctie om de listbox te vullen met een gegeven set items."""
        # Maak de lijst leeg
        self.item_listbox.delete(0, tk.END)

        if not items_to_display:
            self.item_listbox.insert(tk.END, "Database is leeg. Gebruik 'Nieuw' om een item toe te voegen.")
            self.item_listbox["fg"] = "gray"  # Maak de tekst grijs
        else:
            self.item_listbox["fg"] = "black"  # Zet de kleur terug naar standaard
            # Sorteer op index en vul de lijst
            for index, tekst in sorted(items_to_display.items()):
                preview = tekst.replace("\n", " ").strip()
                self.item_listbox.insert(tk.END, f"{index: >3}: {preview}")

        self._update_button_states()
        self._update_preview_pane()
        self._update_status_bar()

    def perform_search(self, *args):
        """Filtert de lijst op basis van de zoekterm in de tekst of het indexnummer."""
        search_term = self.search_var.get()

        if not search_term:
            items_to_show = self.db.data
        else:
            search_term_lower = search_term.lower()
            items_to_show = {
                index: text
                for index, text in self.db.data.items()
                if search_term_lower in text.lower() or str(index).startswith(search_term)
            }

        self._populate_listbox(items_to_show)

    def _on_search_change(self, *args):
        """
        Handelt een wijziging in het zoekveld af met debouncing.
        De zoekopdracht wordt pas uitgevoerd nadat de gebruiker 300ms is gestopt met typen.
        """
        if self._search_debounce_job:
            self.master.after_cancel(self._search_debounce_job)

        # Plan de zoekopdracht om na 300ms te worden uitgevoerd
        self._search_debounce_job = self.master.after(300, self.perform_search)

    def _get_selected_index(self):
        """Haalt het indexnummer op van het geselecteerde item in de listbox."""
        selection = self.item_listbox.curselection()
        if not selection:
            return None

        selected_line = self.item_listbox.get(selection[0])
        try:
            # De lijn is opgebouwd als "   1: Preview van de tekst..."
            index_str = selected_line.split(":")[0].strip()
            return int(index_str)
        except (ValueError, IndexError):
            return None  # Mocht er iets misgaan met de parsing

    def _get_db_index_from_list_index(self, list_index):
        """Haalt het database-indexnummer op van een item op een gegeven listbox-index."""
        if list_index < 0 or list_index >= self.item_listbox.size():
            return None
        line = self.item_listbox.get(list_index)
        try:
            index_str = line.split(":", 1)[0].strip()
            return int(index_str)
        except (ValueError, IndexError):
            return None

    def _force_selection_on_arrow(self, event=None):
        """
        Werkt de selectie bij om overeen te komen met het actieve item (focus met stippellijn).

        Dit wordt aangeroepen na een pijltjestoets-event. De standaard `Listbox`
        verandert alleen het 'actieve' item, niet de 'selectie'. Deze methode
        synchroniseert de twee, wat er vervolgens voor zorgt dat het
        `<<ListboxSelect>>` event wordt geactiveerd.
        """
        try:
            # Haal de index op van het item dat de focus heeft (stippellijn)
            active_index = self.item_listbox.index(tk.ACTIVE)
            current_selection = self.item_listbox.curselection()

            # Voer alleen uit als de selectie niet al overeenkomt met het actieve item
            if not current_selection or current_selection[0] != active_index:
                self.item_listbox.selection_clear(0, tk.END)
                self.item_listbox.selection_set(active_index)
                # Genereer het event handmatig om de update-keten te starten
                self.item_listbox.event_generate("<<ListboxSelect>>")

        except tk.TclError:
            # Dit kan gebeuren als er geen items in de lijst zijn of geen actief item is.
            pass

    def _on_selection_change(self, event=None):
        """
        Plant de UI-update in om te draaien nadat het huidige event is verwerkt.

        Dit lost potentiële timing-problemen op waarbij de selectie-status nog niet
        volledig is bijgewerkt op het exacte moment dat het event wordt geactiveerd.
        De `after_idle` methode zorgt ervoor dat de update-logica wordt uitgevoerd
        zodra Tkinter klaar is met de huidige taken, wat garandeert dat de
        selectie in de listbox correct is.
        """
        self.master.after_idle(self._perform_selection_update)

    def _perform_selection_update(self):
        """Voert de daadwerkelijke UI-updates uit na een selectiewijziging."""
        self._update_button_states()
        self._update_preview_pane()

    def _update_preview_pane(self):
        """Werkt het preview-paneel bij met de tekst van het geselecteerde item."""
        # Maak de preview eerst leeg
        self.preview_text["state"] = tk.NORMAL  # pyright: ignore[reportOptionalSubscript]
        self.preview_text.delete("1.0", tk.END)  # pyright: ignore[reportOptionalMemberAccess]

        index_nummer = self._get_selected_index()
        if index_nummer:
            tekst = self.db.get_tekst(index_nummer)
            if tekst is not None:
                self.preview_text.insert(tk.END, tekst)  # pyright: ignore[reportOptionalMemberAccess]

        # Maak het tekstveld weer read-only om onbedoelde wijzigingen te voorkomen
        self.preview_text["state"] = tk.DISABLED  # pyright: ignore[reportOptionalSubscript]

    def _update_button_states(self, event=None):
        """Updates de status van knoppen en menu-items op basis van de selectie."""
        if self.item_listbox.curselection():
            new_state = tk.NORMAL
        else:
            new_state = tk.DISABLED

        # Update knoppen
        self.btn_wijzig["state"] = new_state
        self.btn_verwijder["state"] = new_state

        # Update menu-items
        self.edit_menu.entryconfig("Wijzig item...", state=new_state)
        self.edit_menu.entryconfig("Verwijder item...", state=new_state)

    def _update_status_bar(self):
        """Updates de tekst in de statusbalk."""
        aantal_items = len(self.db.data)
        status_text = f"  Totaal: {aantal_items} items"
        self.status_bar["text"] = status_text

    def focus_search(self, event=None):
        """Zet de focus op de zoekbalk."""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)

    def clear_search(self):
        """Maakt de zoekbalk leeg en toont de volledige lijst."""
        self.search_var.set("")
        # Annuleer een eventuele lopende debounce-taak en voer de zoekopdracht direct uit
        if self._search_debounce_job:
            self.master.after_cancel(self._search_debounce_job)
        self.perform_search()

    # --- Commando's (Bestand) ---
    # --- Commando's (Bestand) ---

    def new_database(self):
        """Vraagt om een bestandsnaam en creëert een nieuwe, lege database."""
        filepath = filedialog.asksaveasfilename(
            title="Nieuwe database aanmaken",
            filetypes=self.DATABASE_FILETYPES,
            defaultextension=".txt",
        )
        if not filepath:
            return  # Gebruiker heeft geannuleerd

        try:
            # Maak een nieuw, leeg database object aan.
            # Het bestand zelf wordt pas aangemaakt bij de eerste schrijf-actie.
            self.db = TextDatabase(filepath, create_new=True)
            self._update_title()
            self.refresh_item_list()  # Toont de lege staat in de GUI

            # Vraag direct om het eerste item in te voeren, zoals gevraagd.
            self.nieuw_item()
        except Exception as e:
            messagebox.showerror("Fout bij aanmaken", f"Kon de nieuwe database niet initialiseren.\nFout: {e}")

    def open_database(self):
        """Opent een bestandsdialoog om een nieuwe database te laden."""
        if not self._check_unsaved_changes():
            return

        filepath = filedialog.askopenfilename(
            title="Open databasebestand",
            filetypes=self.DATABASE_FILETYPES,
            defaultextension=".txt",
        )
        if not filepath:
            return  # Gebruiker heeft geannuleerd

        try:
            self.db = TextDatabase(filepath)
            self.refresh_item_list()
            messagebox.showinfo("Succes", f"Database '{filepath}' succesvol geladen.")
        except Exception as e:
            messagebox.showerror("Fout bij openen", f"Kon het bestand niet laden.\nFout: {e}")

    def save_database(self):
        """Slaat de huidige database op naar het huidige bestand."""
        if self.db.save():
            messagebox.showinfo("Succes", f"Wijzigingen opgeslagen in '{self.db.bestandsnaam}'.")
            self._update_ui_state()
            return True
        else:
            messagebox.showerror("Fout bij opslaan", f"Kon de database niet opslaan naar '{self.db.bestandsnaam}'.")
            return False

    def save_database_as(self):
        """Opent een bestandsdialoog om de database onder een nieuwe naam op te slaan."""
        filepath = filedialog.asksaveasfilename(
            title="Database opslaan als...",
            filetypes=self.DATABASE_FILETYPES,
            defaultextension=".txt",
            initialfile=self.db.bestandsnaam,
        )
        if not filepath:
            return  # Gebruiker heeft geannuleerd

        # Update de bestandsnaam in het database-object en sla het op
        self.db.bestandsnaam = filepath
        if self.db.save():
            messagebox.showinfo("Succes", f"Database succesvol opgeslagen als '{filepath}'.")
            self._update_ui_state()
        else:
            messagebox.showerror("Fout bij opslaan", f"Kon de database niet opslaan naar '{filepath}'.")

    def nieuw_item(self):
        """Opent een dialoogvenster om een nieuw item toe te voegen."""
        dialog = TextEntryDialog(self.master, title="Nieuw Item", prompt="Voer de nieuwe tekst in:")
        nieuwe_tekst = dialog.result

        if nieuwe_tekst:  # Controleer of er tekst is ingevoerd
            if self.db.voeg_tekst_toe(nieuwe_tekst):
                messagebox.showinfo("Succes", "Nieuw item succesvol toegevoegd.")
                self.refresh_item_list()
                self._update_ui_state()
            else:
                messagebox.showerror("Fout", "Kon het nieuwe item niet opslaan in het bestand.")
        # Geen bericht nodig bij annuleren; de gebruiker weet dit.

    def wijzig_item(self):
        """Opent een dialoogvenster om een geselecteerd item te wijzigen."""
        index_nummer = self._get_selected_index()
        if index_nummer is None:
            messagebox.showwarning("Geen selectie", "Selecteer eerst een item om te wijzigen.")
            return

        huidige_tekst = self.db.get_tekst(index_nummer)
        if huidige_tekst is None:
            # Dit zou niet moeten gebeuren als de lijst synchroon is met de db
            messagebox.showerror("Fout", f"Kon de tekst voor index {index_nummer} niet vinden.")
            return

        dialog = TextEntryDialog(
            self.master,
            title=f"Wijzig Item {index_nummer}",
            prompt=f"Wijzig de tekst voor item {index_nummer}:",
            initial_text=huidige_tekst,
        )
        nieuwe_tekst = dialog.result

        # Controleer of de gebruiker heeft geannuleerd (result is None)
        if nieuwe_tekst is None:
            return  # Doe niets

        # Controleer of de resulterende tekst leeg is.
        if not nieuwe_tekst:
            messagebox.showwarning("Ongeldige invoer", "Een item mag niet leeg zijn. De wijziging is niet opgeslagen.")
            return

        if self.db.wijzig_tekst(index_nummer, nieuwe_tekst):
            messagebox.showinfo("Succes", f"Item {index_nummer} succesvol gewijzigd.")
            self.refresh_item_list()
            self._update_ui_state()
        else:
            messagebox.showerror("Fout", f"Kon item {index_nummer} niet wijzigen.")

    def verwijder_item(self):
        """Verwijdert het geselecteerde item na bevestiging."""
        index_nummer = self._get_selected_index()
        if index_nummer is None:
            messagebox.showwarning("Geen selectie", "Selecteer eerst een item om te verwijderen.")
            return

        bevestiging = messagebox.askyesno(
            "Bevestig Verwijdering",
            f"Weet u zeker dat u item {index_nummer} wilt verwijderen?\nDeze actie kan niet ongedaan worden gemaakt.",
        )

        if bevestiging:
            if self.db.verwijder_tekst(index_nummer):
                messagebox.showinfo(
                    "Succes", f"Item {index_nummer} succesvol verwijderd.\nDe database is geherindexeerd."
                )
                self.refresh_item_list()
                self._update_ui_state()
            else:
                messagebox.showerror("Fout", f"Kon item {index_nummer} niet verwijderen.")

    def cut_item(self, event=None):
        """Knipt het geselecteerde item naar het klembord."""
        index_nummer = self._get_selected_index()
        if index_nummer is None:
            return

        # Sla de data van het te knippen item op
        tekst = self.db.get_tekst(index_nummer)
        self._clipboard_item = {"text": tekst}

        # Verwijder het item uit de database
        if self.db.verwijder_tekst(index_nummer):
            self.refresh_item_list()
            self._update_ui_state()
        else:
            # Dit zou niet moeten gebeuren als we net de index hebben gekregen
            messagebox.showerror("Fout", f"Kon item {index_nummer} niet knippen.")
            self._clipboard_item = None  # Maak klembord leeg bij fout
            self._update_ui_state()

    def paste_item(self, event=None):
        """Plakt het geknipte item op de geselecteerde positie."""
        if not self._clipboard_item:
            return

        selection = self.item_listbox.curselection()
        if selection:
            # Plak voor het geselecteerde item
            list_index = selection[0]
            dest_db_index = self._get_db_index_from_list_index(list_index)
            if dest_db_index is None:  # Mocht er iets misgaan
                dest_db_index = len(self.db.data) + 1
        else:
            # Plak aan het einde als er niets is geselecteerd
            dest_db_index = len(self.db.data) + 1

        tekst_to_paste = self._clipboard_item["text"]
        if self.db.voeg_tekst_op_index_toe(dest_db_index, tekst_to_paste):
            self._clipboard_item = None  # Maak klembord leeg na plakken
            self.refresh_item_list()
            self.item_listbox.selection_set(dest_db_index - 1)
            self.item_listbox.see(dest_db_index - 1)
            self._update_ui_state()
        else:
            messagebox.showerror("Fout", "Kon het item niet plakken.")

    def _on_drag_start(self, event):
        """Start van een drag-and-drop operatie."""
        list_index = self.item_listbox.nearest(event.y)
        if list_index != -1:
            self._drag_source_index = list_index
            self.item_listbox.selection_clear(0, tk.END)
            self.item_listbox.selection_set(list_index)
            self.item_listbox.activate(list_index)

    def _on_drag_motion(self, event):
        """Handelt de beweging tijdens drag-and-drop af."""
        if self._drag_source_index is None:
            return

        dest_list_index = self.item_listbox.nearest(event.y)
        if dest_list_index == -1:
            if self._drop_indicator:
                self._drop_indicator.place_forget()
            return

        if not self._drop_indicator:
            self._drop_indicator = tk.Frame(self.item_listbox, height=2, bg="blue", relief=tk.SOLID)

        item_bbox = self.item_listbox.bbox(dest_list_index)
        if item_bbox:
            indicator_y = item_bbox[1]
            midpoint = indicator_y + item_bbox[3] / 2
            if event.y > midpoint:
                indicator_y += item_bbox[3]

            self._drop_indicator.place(x=0, y=indicator_y - 1, width=self.item_listbox.winfo_width(), height=2)

    def _on_drag_release(self, event):
        """Handelt het loslaten van de muisknop na drag-and-drop af."""
        if self._drag_source_index is None:
            return

        if self._drop_indicator:
            self._drop_indicator.place_forget()

        source_list_index = self._drag_source_index
        self._drag_source_index = None  # Reset drag state

        dest_list_index = self.item_listbox.nearest(event.y)
        if dest_list_index == -1 or dest_list_index == source_list_index:
            return  # Geen verplaatsing nodig

        source_db_index = self._get_db_index_from_list_index(source_list_index)
        if source_db_index is None:
            return

        # Bepaal de uiteindelijke positie in de lijst (0-gebaseerd)
        item_bbox = self.item_listbox.bbox(dest_list_index)
        final_list_index = dest_list_index
        if item_bbox and event.y > (item_bbox[1] + item_bbox[3] / 2):
            final_list_index += 1

        # Corrigeer de doel-index voor de `pop` operatie in `move_item`
        if source_list_index < final_list_index:
            target_insert_index = final_list_index - 1
        else:
            target_insert_index = final_list_index

        dest_db_index = target_insert_index + 1

        if self.db.move_item(source_db_index, dest_db_index):
            self.refresh_item_list()
            self.item_listbox.selection_set(target_insert_index)
            self.item_listbox.see(target_insert_index)
            self._update_ui_state()

    def sluit_applicatie(self):
        """Sluit de applicatie."""
        if self._check_unsaved_changes():
            self.master.quit()

    def _check_unsaved_changes(self):
        """
        Controleert op niet-opgeslagen wijzigingen en vraagt de gebruiker wat te doen.
        Geeft True terug als de actie mag doorgaan, False als de gebruiker annuleert.
        """
        if not self.db.dirty:
            return True  # Veilig om door te gaan

        response = messagebox.askyesnocancel(
            "Niet-opgeslagen wijzigingen",
            f"Er zijn niet-opgeslagen wijzigingen in '{self.db.bestandsnaam}'.\n"
            "Wilt u de wijzigingen opslaan voordat u doorgaat?",
            parent=self.master,
        )

        if response is True:  # Ja
            return self.save_database()
        return response is not None  # True voor Nee (doorgaan), False voor Annuleren

    def show_about(self):
        """Toont het 'Over' dialoogvenster."""
        messagebox.showinfo(
            "Over TekstDB Bewerker", "TekstDB Bewerker v0.1\n\nEen GUI voor het beheren van tekst-databases."
        )

    def _update_ui_state(self):
        """Werkt alle UI-elementen bij die de databasestatus weerspiegelen."""
        self._update_title()
        self._update_status_bar()
        self._update_button_states()
        paste_state = tk.NORMAL if self._clipboard_item else tk.DISABLED
        self.edit_menu.entryconfig("Plakken", state=paste_state)


def main():
    """Start de applicatie."""
    parser = argparse.ArgumentParser(description="Een GUI-applicatie voor het bewerken van tekst-databases.")
    parser.add_argument(
        "-f",
        "--file",
        dest="filepath",
        help="Pad naar het te openen databasebestand.",
    )
    args = parser.parse_args()

    root = tk.Tk()
    TekstDbGuiApp(root, filepath=args.filepath)
    root.mainloop()


if __name__ == "__main__":
    main()
