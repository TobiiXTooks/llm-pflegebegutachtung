import customtkinter as ctk
from customtkinter import filedialog
import duckdb
import os

# Globale Konfiguration für das Erscheinungsbild der App (Nutzt das System-Theme)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AdvancedBenchmarkApp(ctk.CTk):
    """
    Hauptklasse für die Pflegegutachten AI-Benchmark Editor Applikation.
    Erstellt das UI-Fenster und verwaltet die DuckDB In-Memory-Datenbank für das Multi-File-Handling.
    """
    def __init__(self):
        super().__init__()
        self.title("Pflegegutachten AI-Benchmark Editor - Multi-File Pro")
        self.geometry("1400x1050")
        
        # Liste zur Speicherung aller aktuell geladenen .jsonl Dateipfade
        self.loaded_files = []
        # Datenbank-Verbindungsobjekt (wird beim Laden der ersten Datei initialisiert)
        self.con = None
        # Enthält die Datensätze, die den aktuell gesetzten Suchfiltern entsprechen
        self.filtered_records = []
        # Der Index des aktuell im Editor (Bereich 3) angezeigten Datensatzes
        self.current_index = 0
        
        # Haupt-Scroll-Container: Erlaubt das Scrollen der gesamten UI bei kleineren Bildschirmen
        self.main_container = ctk.CTkScrollableFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # =====================================================================
        # INITIALISIERUNG DER EINZELNEN UI-BEREICHE
        # =====================================================================
        
        # BEREICH 1: Pfadauswahl und Laden der Dateien
        self.build_path_selection_area()
        
        # Arbeits-Container: Umfasst alle nachfolgenden Bearbeitungs-Bereiche.
        # Wird standardmäßig deaktiviert, bis mindestens eine Datei erfolgreich geladen wurde.
        self.work_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.work_container.pack(fill="both", expand=True)
        
        # BEREICH 2: Die Such- und Filtermaske
        self.build_filter_area()
        # BEREICH 3: Die detaillierte Maske zum Editieren des aktuellen Datensatzes
        self.build_editor_area()
        # BEREICH 4: Die tabellarische Live-Vorschau der ersten 10 Treffer
        self.build_table_area()
        # BEREICH 5: Das Eingabeformular für das Hinzufügen komplett neuer Einträge
        self.build_insert_area()
        
        # Initialer Zustand: Sperrt alle Felder im Arbeitsbereich
        self.toggle_ui_state("disabled")

    # =========================================================================
    # BEREICH 1: MULTI-PFADAUSWAHL & DATENBANK-INITIALISIERUNG
    # =========================================================================
    def build_path_selection_area(self):
        """Erstellt die Widgets für die Dateiauswahl und das Laden der JSONL-Dateien."""
        path_frame = ctk.CTkFrame(self.main_container, corner_radius=10, border_width=2, border_color="#1f538d")
        path_frame.pack(fill="x", padx=10, pady=5)
        
        lbl = ctk.CTkLabel(path_frame, text="📂 JSONL DATEIEN LADEN (Mehrfachauswahl möglich)", font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        
        self.entry_path = ctk.CTkEntry(path_frame, placeholder_text="Wähle eine oder mehrere benchmarks.jsonl Dateien...")
        self.entry_path.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        btn_browse = ctk.CTkButton(path_frame, text="Durchsuchen...", width=100, command=self.browse_files)
        btn_browse.grid(row=1, column=1, padx=5, pady=10)
        
        self.btn_load = ctk.CTkButton(path_frame, text="Datei(en) hinzufügen 🔓", width=150, fg_color="green", hover_color="darkgreen", command=self.load_jsonl_files)
        self.btn_load.grid(row=1, column=2, padx=10, pady=10)
        
        self.lbl_file_status = ctk.CTkLabel(path_frame, text="Keine Dateien geladen", text_color="gray")
        self.lbl_file_status.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        
        path_frame.grid_columnconfigure(0, weight=1)

    def browse_files(self):
        """Öffnet den nativen Betriebssystem-Dialog zur Auswahl mehrerer JSONL-Dateien."""
        chosen_paths = filedialog.askopenfilenames(title="Wähle deine JSONL-Datei(en) aus", filetypes=[("JSON Lines", "*.jsonl")])
        if chosen_paths:
            self.entry_path.delete(0, "end")
            # Verbindet die ausgewählten Pfade mit einem Semikolon zur Anzeige im Entry-Feld
            self.entry_path.insert(0, "; ".join(chosen_paths))

    def load_jsonl_files(self):
        """
        Liest die eingetragenen Pfade aus, initialisiert bei Bedarf die DuckDB-Instanz
        mit dem festen Zielschema und importiert die JSONL-Inhalte in die SQL-Tabelle.
        """
        raw_paths = self.entry_path.get().strip()
        if not raw_paths:
            return
            
        # Zerlegt den String anhand der Semikolons und prüft, ob die Dateien existieren
        paths = [p.strip() for p in raw_paths.split(";") if os.path.exists(p.strip())]
        if not paths:
            return
            
        try:
            # Datenbank und Tabellenstruktur generieren, falls noch nicht geschehen
            if not self.con:
                self.con = duckdb.connect()
                # HINWEIS: Die Spalte _source_file speichert den Dateipfad, um Multi-File-Support zu ermöglichen
                self.con.execute("""
                    CREATE TABLE runs (
                        id VARCHAR, module VARCHAR, criterion VARCHAR, scale_type VARCHAR, stem VARCHAR,
                        options VARCHAR[], answer_idx INT, rationale_options VARCHAR[], rationale_id INT,
                        point_scale_options VARCHAR[], point_scale_id INT, point_value INT,
                        split VARCHAR, model VARCHAR, model_version VARCHAR, temperature DOUBLE,
                        _source_file VARCHAR
                    );
                """)
            
            for path in paths:
                # Verhindert, dass dieselbe Datei doppelt in die DB importiert wird
                if path not in self.loaded_files:
                    self.loaded_files.append(path)
                    # DuckDB liest das JSONL automatisch und setzt den Dateipfad als statischen Wert für alle Zeilen dieser Datei ein
                    self.con.execute(f"""
                        INSERT INTO runs 
                        SELECT *, '{path}' as _source_file 
                        FROM read_json_auto('{path}');
                    """)
            
            # Dateinamens-Vorschau in der UI aktualisieren (zeigt nur die Dateinamen ohne den kompletten Pfad)
            short_names = [os.path.basename(f) for f in self.loaded_files]
            self.lbl_file_status.configure(text=f"Geladene Quell-Dateien: {', '.join(short_names)}", text_color="white")
            self.entry_path.delete(0, "end")
            
            # Das Dropdown-Menü im Einfüge-Bereich (Bereich 5) mit den aktuell geladenen Dateien befüllen
            self.i_target_file.configure(values=self.loaded_files)
            self.i_target_file.set(self.loaded_files[0])
            
            # UI freischalten und die Filter triggern, um erste Daten anzuzeigen
            self.toggle_ui_state("normal")
            self.apply_filters()
        except Exception as e:
            print(f"Fehler beim Laden: {e}")

    def toggle_ui_state(self, state):
        """Schaltet den Zustand ('normal' oder 'disabled') des kompletten Arbeitsbereichs um."""
        for child in self.work_container.winfo_children():
            self.set_state_recursive(child, state)

    def set_state_recursive(self, widget, state):
        """Rekursive Hilfsfunktion, um alle verschachtelten Sub-Widgets zu aktivieren/deaktivieren."""
        try: widget.configure(state=state)
        except: pass
        for child in widget.winfo_children(): self.set_state_recursive(child, state)

    # =========================================================================
    # BEREICH 2: FILTER AREA (Echtzeit-Suche)
    # =========================================================================
    def build_filter_area(self):
        """Erstellt die Eingabefelder und Dropdowns zur Einschränkung des Suchbestands."""
        self.filter_frame = ctk.CTkFrame(self.work_container, corner_radius=10)
        self.filter_frame.pack(fill="x", padx=10, pady=5)
        
        lbl = ctk.CTkLabel(self.filter_frame, text="🔍 GEFILTERTE SUCHE (id, module, criterion, split, model, temperature)", font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="w")
        
        # ID-Filter mit Event-Bind bei Tastatureingabe für direkten Filtereffekt
        self.f_id = ctk.CTkEntry(self.filter_frame, placeholder_text="Filter ID...")
        self.f_id.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.f_id.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        # Modul-Auswahldropdown
        self.f_mod = ctk.CTkComboBox(self.filter_frame, values=["ALLE", "M1", "M2", "M4"], command=lambda v: self.apply_filters())
        self.f_mod.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Kriterium-Textfilter
        self.f_crit = ctk.CTkEntry(self.filter_frame, placeholder_text="Filter Kriterium...")
        self.f_crit.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        self.f_crit.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        # Split-Auswahldropdown
        self.f_split = ctk.CTkComboBox(self.filter_frame, values=["ALLE", "train", "test", "val"], command=lambda v: self.apply_filters())
        self.f_split.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        
        # Modell-Auswahldropdown
        self.f_model = ctk.CTkComboBox(self.filter_frame, values=["ALLE", "Gemini", "ChatGPT"], command=lambda v: self.apply_filters())
        self.f_model.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # Temperatur-Textfilter
        self.f_temp = ctk.CTkEntry(self.filter_frame, placeholder_text="Filter Temp (z.B. 0.0)...")
        self.f_temp.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.f_temp.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        self.filter_frame.grid_columnconfigure((0,1,2,3), weight=1)

    # =========================================================================
    # BEREICH 3: EDITOR AREA (Datensatz-Ansicht & Mutation)
    # =========================================================================
    def build_editor_area(self):
        """Erstellt die Detailmaske zur Manipulation des aktuell ausgewählten Tabelleneintrags."""
        self.edit_frame = ctk.CTkFrame(self.work_container, corner_radius=10, border_width=1, border_color="gray")
        self.edit_frame.pack(fill="x", padx=10, pady=5)
        
        # Sub-Frame für die Navigations-Leiste (Zurück, Zähler, Weiter)
        nav_frame = ctk.CTkFrame(self.edit_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10, pady=5)
        
        self.btn_prev = ctk.CTkButton(nav_frame, text="◀ Zurück", width=80, command=self.prev_record)
        self.btn_prev.pack(side="left", padx=5)
        
        self.lbl_counter = ctk.CTkLabel(nav_frame, text="0 / 0 Einträge", font=ctk.CTkFont(weight="bold"))
        self.lbl_counter.pack(side="left", expand=True)
        
        self.btn_next = ctk.CTkButton(nav_frame, text="Weiter ▶", width=80, command=self.next_record)
        self.btn_next.pack(side="right", padx=5)
        
        # Grid-Formular für die einzelnen Datenfelder
        form = ctk.CTkFrame(self.edit_frame, fg_color="transparent")
        form.pack(fill="x", padx=10, pady=5)
        
        # Zeile 0: Szenariotext / Stem (Große Textbox)
        ctk.CTkLabel(form, text="Stem (Szenariotext):").grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.e_stem = ctk.CTkTextbox(form, height=70)
        self.e_stem.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Zeile 1: ID (Schreibgeschützt, da Primärschlüssel-Komponente) & Module
        ctk.CTkLabel(form, text="ID:").grid(row=1, column=0, sticky="w", padx=5)
        self.e_id = ctk.CTkEntry(form, state="disabled")
        self.e_id.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        ctk.CTkLabel(form, text="Module:").grid(row=1, column=2, sticky="w", padx=5)
        self.e_mod = ctk.CTkEntry(form)
        self.e_mod.grid(row=1, column=3, sticky="ew", padx=5, pady=2)
        
        # Zeile 2: Kriterium & Scale Type
        ctk.CTkLabel(form, text="Kriterium:").grid(row=2, column=0, sticky="w", padx=5)
        self.e_crit = ctk.CTkEntry(form)
        self.e_crit.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        ctk.CTkLabel(form, text="Scale Type:").grid(row=2, column=2, sticky="w", padx=5)
        self.e_scale = ctk.CTkEntry(form)
        self.e_scale.grid(row=2, column=3, sticky="ew", padx=5, pady=2)
        
        # Zeile 3: Options (Als Textbox umgesetzt gegen Textabschneidung) & Answer Index
        ctk.CTkLabel(form, text="Options (kommasep.):").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.e_opt = ctk.CTkTextbox(form, height=50)
        self.e_opt.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
        ctk.CTkLabel(form, text="Answer Idx (0-3):").grid(row=3, column=2, sticky="w", padx=5)
        self.e_ans = ctk.CTkEntry(form)
        self.e_ans.grid(row=3, column=3, sticky="ew", padx=5, pady=2)
        
        # Zeile 4: Rationale Options (Als Textbox umgesetzt) & Rationale ID
        ctk.CTkLabel(form, text="Rationale Opts (\\n sep):").grid(row=4, column=0, sticky="nw", padx=5, pady=5)
        self.e_rat_opts = ctk.CTkTextbox(form, height=50)
        self.e_rat_opts.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        
        ctk.CTkLabel(form, text="Rationale ID:").grid(row=4, column=2, sticky="w", padx=5)
        self.e_rat_id = ctk.CTkEntry(form)
        self.e_rat_id.grid(row=4, column=3, sticky="ew", padx=5, pady=2)
        
        # Zeile 5: Point Scale Options & Point Scale ID
        ctk.CTkLabel(form, text="Point Scale Opts:").grid(row=5, column=0, sticky="w", padx=5)
        self.e_pts_opts = ctk.CTkEntry(form)
        self.e_pts_opts.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        
        ctk.CTkLabel(form, text="Point Scale ID:").grid(row=5, column=2, sticky="w", padx=5)
        self.e_pts_id = ctk.CTkEntry(form)
        self.e_pts_id.grid(row=5, column=3, sticky="ew", padx=5, pady=2)
        
        # Zeile 6: Point Value & Data-Split (test/train/val)
        ctk.CTkLabel(form, text="Point Value:").grid(row=6, column=0, sticky="w", padx=5)
        self.e_pts_val = ctk.CTkEntry(form)
        self.e_pts_val.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        
        ctk.CTkLabel(form, text="Split:").grid(row=6, column=2, sticky="w", padx=5)
        self.e_split = ctk.CTkEntry(form)
        self.e_split.grid(row=6, column=3, sticky="ew", padx=5, pady=2)
        
        # Zeile 7: KI-Modellname & Version
        ctk.CTkLabel(form, text="Model Name:").grid(row=7, column=0, sticky="w", padx=5)
        self.e_model = ctk.CTkEntry(form)
        self.e_model.grid(row=7, column=1, sticky="ew", padx=5, pady=2)
        
        ctk.CTkLabel(form, text="Model Version:").grid(row=7, column=2, sticky="w", padx=5)
        self.e_version = ctk.CTkEntry(form)
        self.e_version.grid(row=7, column=3, sticky="ew", padx=5, pady=2)
        
        # Zeile 8: Generierungs-Temperatur & Label zur Herkunfts-Info der Datei
        ctk.CTkLabel(form, text="Temperature:").grid(row=8, column=0, sticky="w", padx=5)
        self.e_temp = ctk.CTkEntry(form)
        self.e_temp.grid(row=8, column=1, sticky="ew", padx=5, pady=2)
        
        ctk.CTkLabel(form, text="Herkunft (Datei):").grid(row=8, column=2, sticky="w", padx=5)
        self.e_source_info = ctk.CTkLabel(form, text="-", anchor="w", text_color="orange")
        self.e_source_info.grid(row=8, column=3, sticky="ew", padx=5, pady=2)
        
        form.grid_columnconfigure((1,3), weight=1)

        # Geteilter Button-Aktionsbereich ganz unten in der Editor-Sektion
        action_frame = ctk.CTkFrame(self.edit_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=10)
        
        # Roter Löschen-Button (Nimmt exakt 50% der Breite ein)
        self.btn_delete = ctk.CTkButton(action_frame, text="🗑️ Eintrag löschen", fg_color="#a83232", hover_color="#7a2222", command=self.delete_record)
        self.btn_delete.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Grüner Überschreiben-Button (Nimmt ebenfalls 50% der Breite ein)
        self.btn_save = ctk.CTkButton(action_frame, text="💾 Änderungen in ursprüngliche JSONL überschreiben", fg_color="green", hover_color="darkgreen", command=self.save_changes)
        self.btn_save.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        action_frame.grid_columnconfigure((0, 1), weight=1)

    # =========================================================================
    # BEREICH 4: LIVE-TABELLE (Visualisierungskomponente)
    # =========================================================================
    def build_table_area(self):
        """Erstellt den Rahmen für die horizontale und vertikale Live-Grid-Tabelle."""
        self.table_frame = ctk.CTkFrame(self.work_container, corner_radius=10)
        self.table_frame.pack(fill="x", padx=10, pady=5)
        
        lbl_title = ctk.CTkLabel(self.table_frame, text="📊 Live-Tabelle (Erste 10 Treffer mit erweitertem JSON-Mapping)", font=ctk.CTkFont(weight="bold"))
        lbl_title.pack(anchor="w", padx=10, pady=5)
        
        # Horizontaler Scrollbalken, da die Zeilenstruktur breiter als das Fenster ist
        self.table_scroll = ctk.CTkScrollableFrame(self.table_frame, orientation="horizontal", height=280)
        self.table_scroll.pack(fill="x", padx=10, pady=5)
        
        self.grid_container = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True)

    def refresh_table(self, records):
        """
        Löscht das alte Grid und zeichnet die ersten 10 Treffer der gefilterten
        Menge mitsamt allen geforderten Spalten (inkl. Rationale und Point Scales) neu.
        """
        # Vorherige Zellen-Widgets zerstören, um Memory-Leaks zu verhindern
        for widget in self.grid_container.winfo_children(): widget.destroy()
        if not records: return
        
        # Spalten-Header Definition
        headers = ["ID", "Module", "Criterion", "Scale Type", "Rat ID", "Pt Scale Opts", "Pt Scale ID", "Model", "Version", "Split", "Ans Idx", "Temp", "Quelle"]
        for col_idx, h in enumerate(headers):
            header_lbl = ctk.CTkLabel(self.grid_container, text=h, font=ctk.CTkFont(weight="bold"), fg_color="gray30", text_color="white", width=120)
            header_lbl.grid(row=0, column=col_idx, sticky="ew", padx=1, pady=2)
            
        # Zeichnet maximal die ersten 10 Treffer der Ergebnisliste
        for row_idx, r in enumerate(records[:10]):
            # Indizes entsprechen exakt dem DuckDB SQL-Tabellenschema
            vals = [
                str(r[0]), str(r[1]), str(r[2]), str(r[3]), 
                str(r[8]), str(r[9]), str(r[10]), 
                str(r[13]), str(r[14]), str(r[12]), str(r[6]), str(r[15]),
                os.path.basename(str(r[16])) # Extrahiert nur den Dateinamen aus dem vollständigen Pfad
            ]
            # Alternierender Hintergrund zur besseren Lesbarkeit (Zebramuster)
            bg = "gray20" if row_idx % 2 == 0 else "gray25"
            for col_idx, val in enumerate(vals):
                cell = ctk.CTkLabel(self.grid_container, text=val, fg_color=bg, anchor="w", width=120)
                cell.grid(row=row_idx+1, column=col_idx, sticky="ew", padx=1, pady=1)

    # =========================================================================
    # BEREICH 5: INSERT AREA (Formular zur Neuanlage mit Speicher-Routing)
    # =========================================================================
    def build_insert_area(self):
        """Erstellt das Eingaberaster für ein absolut vollständiges neues Antragsobjekt."""
        self.ins_frame = ctk.CTkFrame(self.work_container, corner_radius=10, border_width=1, border_color="green")
        self.ins_frame.pack(fill="x", padx=10, pady=10)
        
        lbl = ctk.CTkLabel(self.ins_frame, text="➕ NEUEN IN DIE JSONL EINZUFÜGENDEN ANTRAGS-BENCHMARK EINTRAGEN (ALLE FELDER)", font=ctk.CTkFont(weight="bold"), text_color="green")
        lbl.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="w")
        
        # Zeile 1: ID, Module, Criterion, Scale Type
        self.i_id = ctk.CTkEntry(self.ins_frame, placeholder_text="ID...")
        self.i_id.grid(row=1, column=0, padx=5, pady=3, sticky="ew")
        self.i_mod = ctk.CTkEntry(self.ins_frame, placeholder_text="Module (z.B. M1)...")
        self.i_mod.grid(row=1, column=1, padx=5, pady=3, sticky="ew")
        self.i_crit = ctk.CTkEntry(self.ins_frame, placeholder_text="Criterion...")
        self.i_crit.grid(row=1, column=2, padx=5, pady=3, sticky="ew")
        self.i_scale = ctk.CTkEntry(self.ins_frame, placeholder_text="Scale Type...")
        self.i_scale.grid(row=1, column=3, padx=5, pady=3, sticky="ew")
        
        # Zeile 2: Stem (Über alle Spalten)
        self.i_stem = ctk.CTkEntry(self.ins_frame, placeholder_text="Stem (Szenariotext)...")
        self.i_stem.grid(row=2, column=0, columnspan=4, padx=5, pady=3, sticky="ew")
        
        # Zeile 3: Options, Answer Idx, Rationale Opts, Rationale ID
        self.i_options = ctk.CTkEntry(self.ins_frame, placeholder_text="Options (Kommasep.)...")
        self.i_options.grid(row=3, column=0, padx=5, pady=3, sticky="ew")
        self.i_ans_idx = ctk.CTkEntry(self.ins_frame, placeholder_text="Answer Idx (Integer)...")
        self.i_ans_idx.grid(row=3, column=1, padx=5, pady=3, sticky="ew")
        self.i_rat_opts = ctk.CTkEntry(self.ins_frame, placeholder_text="Rationale Opts (Kommasep.)...")
        self.i_rat_opts.grid(row=3, column=2, padx=5, pady=3, sticky="ew")
        self.i_rat_id = ctk.CTkEntry(self.ins_frame, placeholder_text="Rationale ID (Integer)...")
        self.i_rat_id.grid(row=3, column=3, padx=5, pady=3, sticky="ew")
        
        # Zeile 4: Point Scale Opts, Point Scale ID, Point Value, Split
        self.i_pts_opts = ctk.CTkEntry(self.ins_frame, placeholder_text="Point Scale Opts (Kommasep.)...")
        self.i_pts_opts.grid(row=4, column=0, padx=5, pady=3, sticky="ew")
        self.i_pts_id = ctk.CTkEntry(self.ins_frame, placeholder_text="Point Scale ID (Integer)...")
        self.i_pts_id.grid(row=4, column=1, padx=5, pady=3, sticky="ew")
        self.i_pts_val = ctk.CTkEntry(self.ins_frame, placeholder_text="Point Value (Integer)...")
        self.i_pts_val.grid(row=4, column=2, padx=5, pady=3, sticky="ew")
        self.i_split = ctk.CTkEntry(self.ins_frame, placeholder_text="Split (test/train)...")
        self.i_split.grid(row=4, column=3, padx=5, pady=3, sticky="ew")
        
        # Zeile 5: Model, Version, Temperature & Dropdown für Zieldatei-Routing
        self.i_model = ctk.CTkEntry(self.ins_frame, placeholder_text="Model (z.B. Gemini)...")
        self.i_model.grid(row=5, column=0, padx=5, pady=3, sticky="ew")
        self.i_ver = ctk.CTkEntry(self.ins_frame, placeholder_text="Model Version...")
        self.i_ver.grid(row=5, column=1, padx=5, pady=3, sticky="ew")
        self.i_temp = ctk.CTkEntry(self.ins_frame, placeholder_text="Temperature (0.0)...")
        self.i_temp.grid(row=5, column=2, padx=5, pady=3, sticky="ew")
        
        # OptionMenu: Ermöglicht dem Benutzer die Auswahl, in welche der geladenen Dateien gespeichert wird
        self.i_target_file = ctk.CTkOptionMenu(self.ins_frame, values=["Erst Datei laden..."], fg_color="#1f538d")
        self.i_target_file.grid(row=5, column=3, padx=5, pady=3, sticky="ew")
        
        btn_insert = ctk.CTkButton(self.ins_frame, text="➕ In ausgewählte JSONL Datei einfügen und validieren", fg_color="green", hover_color="darkgreen", command=self.insert_record)
        btn_insert.grid(row=6, column=0, columnspan=4, padx=5, pady=10, sticky="ew")
        self.ins_frame.grid_columnconfigure((0,1,2,3), weight=1)

    # =========================================================================
    # DATENBANK-PIPELINE & GESCHÄFTSLOGIK (DuckDB Operations)
    # =========================================================================
    def apply_filters(self):
        """Generiert ein dynamisches SQL-Query basierend auf den UI-Suchfiltern und fragt DuckDB ab."""
        if not self.con: return
        query = "SELECT * FROM runs WHERE 1=1"
        
        # String-Filter nutzen ILIKE für Case-Insensitive (Groß-/Kleinschreibung ignorieren) Suchen
        if self.f_id.get(): query += f" AND id ILIKE '%{self.f_id.get()}%'"
        if self.f_mod.get() != "ALLE": query += f" AND module = '{self.f_mod.get()}'"
        if self.f_crit.get(): query += f" AND criterion ILIKE '%{self.f_crit.get()}%'"
        if self.f_split.get() != "ALLE": query += f" AND split = '{self.f_split.get()}'"
        if self.f_model.get() != "ALLE": query += f" AND model = '{self.f_model.get()}'"
        if self.f_temp.get(): query += f" AND CAST(temperature AS VARCHAR) ILIKE '{self.f_temp.get()}%'"
            
        # Holt alle zutreffenden Records als Tupel-Liste ab
        self.filtered_records = self.con.execute(query).fetchall()
        self.current_index = 0
        
        # Aktualisiert die Benutzeroberfläche basierend auf dem neuen Datensatz-Zustand
        self.update_editor_fields()
        self.refresh_table(self.filtered_records)

    def update_editor_fields(self):
        """Befüllt alle Eingabefelder im Editor-Bereich mit den Werten des aktuellen Index."""
        total = len(self.filtered_records)
        if total == 0:
            # Falls kein Treffer vorliegt: Alle Masken leeren
            self.lbl_counter.configure(text="0 / 0 Einträge")
            self.e_id.configure(state="normal"); self.e_id.delete(0, "end"); self.e_id.configure(state="disabled")
            self.e_mod.delete(0, "end")
            self.e_crit.delete(0, "end"); self.e_scale.delete(0, "end")
            self.e_stem.delete("1.0", "end"); self.e_opt.delete("1.0", "end")
            self.e_ans.delete(0, "end"); self.e_rat_opts.delete("1.0", "end")
            self.e_rat_id.delete(0, "end"); self.e_pts_opts.delete(0, "end")
            self.e_pts_id.delete(0, "end"); self.e_pts_val.delete(0, "end")
            self.e_split.delete(0, "end"); self.e_model.delete(0, "end")
            self.e_version.delete(0, "end"); self.e_temp.delete(0, "end")
            self.e_source_info.configure(text="-")
            return
            
        self.lbl_counter.configure(text=f"{self.current_index + 1} / {total} Einträge")
        r = self.filtered_records[self.current_index]
        
        # Befüllen der Felder (Sonderlogik für schreibgeschützte ID und Textboxen)
        self.e_id.configure(state="normal"); self.e_id.delete(0, "end"); self.e_id.insert(0, str(r[0])); self.e_id.configure(state="disabled")
        self.e_mod.delete(0, "end"); self.e_mod.insert(0, str(r[1]))
        self.add_val(self.e_crit, r[2]); self.add_val(self.e_scale, r[3])
        
        self.e_stem.delete("1.0", "end"); self.e_stem.insert("1.0", str(r[4]))
        self.e_opt.delete("1.0", "end"); self.e_opt.insert("1.0", str(r[5]))
        self.add_val(self.e_ans, r[6])
        
        self.e_rat_opts.delete("1.0", "end"); self.e_rat_opts.insert("1.0", str(r[7]))
        self.add_val(self.e_rat_id, r[8])
        
        self.add_val(self.e_pts_opts, r[9]); self.add_val(self.e_pts_id, r[10])
        self.add_val(self.e_pts_val, r[11]); self.add_val(self.e_split, r[12])
        self.add_val(self.e_model, r[13]); self.add_val(self.e_version, r[14])
        self.add_val(self.e_temp, r[15])
        
        # Zeigt dem Nutzer die exakte Dateiquelle des aktiven Elements
        self.e_source_info.configure(text=os.path.basename(str(r[16])))

    def add_val(self, field, value):
        """Kleine Hilfsmethode, um Standard-Entry-Felder sicher zu leeren und zu befüllen."""
        field.delete(0, "end")
        if value is not None: field.insert(0, str(value))

    def next_record(self):
        """Navigiert einen Schritt vorwärts im gefilterten Suchergebnis."""
        if self.current_index < len(self.filtered_records) - 1:
            self.current_index += 1; self.update_editor_fields()

    def prev_record(self):
        """Navigiert einen Schritt rückwärts im gefilterten Suchergebnis."""
        if self.current_index > 0:
            self.current_index -= 1; self.update_editor_fields()

    def delete_record(self):
        """Entfernt den aktiven Datensatz über ID und Dateizuordnung aus der DB und schreibt die Datei neu."""
        if not self.filtered_records or not self.con: return
        current_id = self.filtered_records[self.current_index][0]
        source_file = self.filtered_records[self.current_index][16] # Ziel-Pfad aus Spalte 16 extrahieren
        
        # SQL-Query führt ein präzises Deleting aus
        self.con.execute("DELETE FROM runs WHERE id = ? AND _source_file = ?", (current_id, source_file))
        
        # EXCLUDE wirft die interne Hilfsspalte beim Schreiben aus der Datei, um die Originalstruktur sauber zu halten
        self.con.execute(f"COPY (SELECT * EXCLUDE (_source_file) FROM runs WHERE _source_file = '{source_file}') TO '{source_file}' (FORMAT JSON);")
        self.apply_filters()

    def save_changes(self):
        """
        Liest alle mutierten Werte aus der Editor-Maske aus, aktualisiert die Zeile 
        über ein SQL UPDATE-Statement und exportiert den aktualisierten Stand in die Quell-JSONL.
        """
        if not self.filtered_records or not self.con: return
        current_id = self.filtered_records[self.current_index][0]
        source_file = self.filtered_records[self.current_index][16]
        
        # Hilfsfunktion: Konvertiert kommagetrennte Strings aus der GUI in echte Python-Listen für DuckDB Arrays
        def to_arr(txt): return [x.strip().replace("'", "").replace('"', '') for x in txt.replace("[", "").replace("]", "").split(",") if x.strip()]
        
        self.con.execute("""
            UPDATE runs SET 
                module = ?, criterion = ?, scale_type = ?, stem = ?, options = ?, answer_idx = ?, 
                rationale_options = ?, rationale_id = ?, point_scale_options = ?, point_scale_id = ?, 
                point_value = ?, split = ?, model = ?, model_version = ?, temperature = ?
            WHERE id = ? AND _source_file = ?
        """, (
            self.e_mod.get(), self.e_crit.get(), self.e_scale.get(), self.e_stem.get("1.0", "end-1c"),
            to_arr(self.e_opt.get("1.0", "end-1c")), int(self.e_ans.get()) if self.e_ans.get() else 0,
            to_arr(self.e_rat_opts.get("1.0", "end-1c")), int(self.e_rat_id.get()) if self.e_rat_id.get() else 0,
            to_arr(self.e_pts_opts.get()), int(self.e_pts_id.get()) if self.e_pts_id.get() else 0,
            int(self.e_pts_val.get()) if self.e_pts_val.get() else 0, self.e_split.get(),
            self.e_model.get(), self.e_version.get(), float(self.e_temp.get()) if self.e_temp.get() else None,
            current_id, source_file
        ))
        
        # Schreibe nur den Datenanteil der modifizierten Datei auf die Festplatte zurück
        self.con.execute(f"COPY (SELECT * EXCLUDE (_source_file) FROM runs WHERE _source_file = '{source_file}') TO '{source_file}' (FORMAT JSON);")
        self.apply_filters()

    def insert_record(self):
        """
        Validiert und parst die Daten aus dem Neuanlage-Formular, fügt sie mit 
        korrektem Datei-Routing in DuckDB ein und aktualisiert die gewählte JSONL-Datei.
        """
        if not self.con: return
        if not self.i_id.get() or not self.i_stem.get(): return
        
        # Holt den ausgewählten Zielpfad aus dem OptionMenu
        target_file = self.i_target_file.get()
        if target_file == "Erst Datei laden...": return
        
        def to_arr(txt): return [x.strip().replace("'", "").replace('"', '') for x in txt.replace("[", "").replace("]", "").split(",") if x.strip()]
        
        # Typkonvertierungen vor der SQL-Injektion durchführen (Sicherheit gegen Casting-Fehler)
        t = float(self.i_temp.get()) if self.i_temp.get() else None
        ans_idx = int(self.i_ans_idx.get()) if self.i_ans_idx.get() else 0
        rat_id = int(self.i_rat_id.get()) if self.i_rat_id.get() else 0
        pts_id = int(self.i_pts_id.get()) if self.i_pts_id.get() else 0
        pts_val = int(self.i_pts_val.get()) if self.i_pts_val.get() else 0
        
        # Intelligente Fallbacks für M1 Pflegegutachten-Kriterien, falls leergelassen
        opts = to_arr(self.i_options.get()) if self.i_options.get() else (["selbständig", "überwiegend selbständig", "überwiegend unselbständig", "unselbständig"] if self.i_mod.get() == "M1" else ["vorhanden/unbeeinträchtigt", "größtenteils vorhanden", "gering vorhanden", "nicht vorhanden"])
        rat_opts = to_arr(self.i_rat_opts.get())
        pts_opts = to_arr(self.i_pts_opts.get()) if self.i_pts_opts.get() else ["0", "1", "2", "3"]

        # Insert Statement, das target_file als Routing-Spaltenwert übergibt
        self.con.execute("INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            self.i_id.get(), self.i_mod.get(), self.i_crit.get(), self.i_scale.get(), self.i_stem.get(),
            opts, ans_idx, rat_opts, rat_id, pts_opts, pts_id, pts_val,
            self.i_split.get(), self.i_model.get(), self.i_ver.get(), t, target_file
        ))
        
        # Aktualisiert die modifizierte Datei
        self.con.execute(f"COPY (SELECT * EXCLUDE (_source_file) FROM runs WHERE _source_file = '{target_file}') TO '{target_file}' (FORMAT JSON);")
        
        # Alle Formularfelder leeren, um direkt für die nächste Eingabe bereit zu sein
        fields_to_clear = [
            self.i_id, self.i_mod, self.i_crit, self.i_scale, self.i_stem,
            self.i_options, self.i_ans_idx, self.i_rat_opts, self.i_rat_id,
            self.i_pts_opts, self.i_pts_id, self.i_pts_val, self.i_split,
            self.i_model, self.i_ver, self.i_temp
        ]
        for f in fields_to_clear: f.delete(0, "end")
        
        self.apply_filters()

# =============================================================================
# ANWENDUNGS-STARTPUNKT
# =============================================================================
if __name__ == "__main__":
    app = AdvancedBenchmarkApp()
    app.mainloop()