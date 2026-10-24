import os
import sys
import argparse                         # NEU: Erlaubt das Auslesen von Terminal-Parametern (CLI Arguments)
from pathlib import Path

# =================================================================
# --- PATH ENHANCEMENT (IMPORT-REPARATUR) ---
# =================================================================
# Bestimmt den absoluten Dateipfad der aktuellen benchmark_generator.py Datei auf der Festplatte
current_file = Path(__file__).resolve()          # Ziel: .../src/benchmark_generator.py

# Ermittelt den Ordner, in dem dieses Skript liegt (der Quellcode-Ordner)
src_dir = current_file.parent                   # Ziel: .../src

# Ermittelt den übergeordneten Hauptordner des Projekts (Wurzelverzeichnis)
project_root = src_dir.parent                   # Ziel: .../Neuer Ordner

# Konstruiert den Pfad zum internen Langfuse-Verzeichnis innerhalb der Struktur
langfuse_dir = src_dir / "tracing" / "langfuse" # Ziel: .../src/tracing/langfuse

# Schleife wandert durch alle drei kritischen Ordnerpfade
for path in [project_root, src_dir, langfuse_dir]:
    # Wenn der Pfad noch nicht im Suchverzeichnis von Python registriert ist...
    if str(path) not in sys.path:
        # Füge den Pfad an Position 0 (höchste Priorität) in die Import-Suchliste ein.
        # Aufgabe: Verhindert 'ModuleNotFoundError', wenn conversation.py importiert wird.
        sys.path.insert(0, str(path))

# --- REGULÄRE IMPORTE ---
import customtkinter as ctk              # Framework für das moderne, dunkle GUI-Design
from dotenv import load_dotenv          # Lädt Umgebungsvariablen und Keys aus der .env-Datei
import json                             # Erlaubt das Lesen, Schreiben und Strukturieren von JSON-Dateien
import threading                        # Ermöglicht parallele Hintergrund-Prozesse (Multi-Threading)
import re                               # Reguläre Ausdrücke zum Durchsuchen und Filtern von Text-Strukturen
from datetime import datetime, timezone # Handhabt Zeitelemente (wichtig für Latenz- und Systemlogs)
import time                             # Stellt zeitbasierte Hilfsfunktionen (z. B. Pausen) bereit
import uuid                             # Erzeugt weltweit eindeutige IDs (z. B. für TraceIDs)

# --- LANGFUSE CLIENT IMPORT ---
from langfuse import get_client         # Importiert die offizielle Verbindungsfunktion zur Langfuse-Cloud

# --- CONVERSATION.PY FEATURES IMPORTIEREN ---
# Holt die Kernfunktionen aus deiner conversation.py, damit die GUI exakt dieselbe Logik nutzt
from conversation import call_model, build_user_message
from prepare_benchmark_data import prepare_data
from data_streamer import load_and_prepare_stream

# =================================================================
# --- KONFIGURATION & API SETUP ---
# =================================================================

# Lädt die Variablen aus der Datei '.env' in das Betriebssystem-Umfeld
load_dotenv() 

# Holt den geheimen OpenRouter-API-Key aus dem Systemspeicher
api_key_from_env = os.getenv("OPENROUTER_API_KEY")
# Sicherheitsprüfung: Wenn kein Key hinterlegt ist, breche sofort ab
if not api_key_from_env:
    raise ValueError("FEHLER: 'OPENROUTER_API_KEY' wurde in der .env-Datei nicht gefunden!")

# Initialisiert einen globalen Langfuse-Client für administrative Systemmeldungen
langfuse_global = get_client()

# NEU: Sicherheitslimit für parallele Anfragen, um Systemüberlastungen zu vermeiden
MAX_MODEL_LIMIT = 5

# =================================================================
# --- ASYNCHRONES LANGFUSE SERVER POLLING (WIE CONVERSATION.PY) ---
# =================================================================
def fetch_trace_with_retry_benchmark(trace_id: str) -> dict:
    """Fragt den Langfuse-Server so lange in einer Schleife ab, bis die Daten parat sind."""
    print(f"  [POLLING]: Warte auf Ingestion von Trace {trace_id} ", end="", flush=True)
    # Nutzt die Konfigurationswerte oder Fallback-Werte (z.B. 3 Retries, 2s Delay)
    for _ in range(5):
        try:
            trace = langfuse_global.api.trace.get(trace_id)
            observations = langfuse_global.api.observations.get_many(
                trace_id=trace_id,
                fields="core,basic,usage",
                limit=100,
            )
            print(" ✓ [Server-Daten erfolgreich geladen]")
            return {
                "trace": trace.dict(),
                "observations": [o.dict() for o in observations.data],
            }
        except Exception:
            print(".", end="", flush=True)
            time.sleep(2)

    print(" ✗ (Timeout bei Server-Abfrage)")
    return {}

# =================================================================
# --- HAUPTAPPLIKATIONS-KLASSE ---
# =================================================================
# Definiert das GUI-Fenster. Erbt von ctk.CTk (CustomTkinter Hauptfenster)
class BenchmarkApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Setzt den Fenstertitel und die Startgröße (Breite x Höhe in Pixeln)
        self.title("PflegeBench — GUI")
        self.geometry("1150x1000")
        
        # results_lock: Ein Thread-Schloss (Mutex). Verhindert Datenchaos (Race Conditions), 
        # wenn mehrere KIs exakt zeitgleich Daten in die Liste 'self.last_results' schreiben wollen.
        self.results_lock = threading.Lock()
        
        # Zähler für die aktuell im Hintergrund aktiven KI-Anfragen
        self.active_threads = 0
        
        # Der temporäre Arbeitsspeicher für alle Antworten und Tokens des aktuellen Durchlaufs
        self.last_results = []
        
        # Speichert die aktuelle Haupt-ID der Ausführung für die Export-Funktion
        self.current_trace_id = None

        # Konfiguriert das Raster-Layout (Spalte 1 dehnt sich dynamisch aus)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (LINKE SPALTE: FREIE MODELLAUSWAHL VIA TEXTFIELD) ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Label für die Format-Auswahl beim Export
        self.format_label = ctk.CTkLabel(self.sidebar, text="Export-Format für Szenarien:", font=ctk.CTkFont(weight="bold"))
        self.format_label.pack(pady=(15, 5))

        # Dropdown-Menü für JSON vs. JSONL
        self.format_option = ctk.CTkOptionMenu(self.sidebar, values=["jsonl", "json"], fg_color="#1f538d", button_color="#143963")
        self.format_option.pack(pady=5, padx=15, fill="x")
        
        # Beschriftung für die freie Modellauswahl
        self.model_label = ctk.CTkLabel(self.sidebar, text="Modell-IDs eingeben\n(Eine ID pro Zeile):", font=ctk.CTkFont(weight="bold"))
        self.model_label.pack(pady=(10, 5))

        # Kleiner Hinweistext für die OpenRouter Syntax
        self.model_hint = ctk.CTkLabel(self.sidebar, text="Format: provider/model-name\nBeispiel: openai/gpt-4o", font=ctk.CTkFont(size=10), text_color="gray")
        self.model_hint.pack(pady=(0, 10))

        # NEU: Das freie Textfeld für unbegrenzte OpenRouter Modell-Auswahlen
        self.model_input_text = ctk.CTkTextbox(self.sidebar, width=200, height=350, font=("Consolas", 11))
        self.model_input_text.pack(padx=15, pady=5, fill="both", expand=True)
        
        # Vorausgefüllte Standardwerte zur Erleichterung der Bedienung einfugen
        default_models = "openai/gpt-4o\nanthropic/claude-sonnet-4.6\ngoogle/gemini-2.5-pro"
        self.model_input_text.insert("1.0", default_models)

        # --- MAIN FRAME (RECHTE SPALTE: EINGABEN & AUSGABEN) ---
        # 1. Zuerst erstellen wir das übergeordnete main_frame, damit es existiert!
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Der dynamische Zeilen-Zähler startet bei 0
        current_row = 0

        # =================================================================
        # --- NEUE SEKTION: WORKFLOW CONTROLS (PREPARE & STREAM) ---
        # =================================================================
        self.wf_frame = ctk.CTkFrame(self.main_frame)
        self.wf_frame.grid(row=current_row, column=0, sticky="ew", padx=20, pady=(10, 5))
        self.wf_frame.grid_columnconfigure(1, weight=1)

        self.wf_title = ctk.CTkLabel(self.wf_frame, text="Prepare Data & Data-Stream", font=ctk.CTkFont(weight="bold"))
        self.wf_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")
        
        # Pfad-Felder innerhalb des wf_frame
        ctk.CTkLabel(self.wf_frame, text="Quellpfad (Prepare):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.src_path_input = ctk.CTkEntry(self.wf_frame, placeholder_text="Standard: data/benchmark/validated")
        self.src_path_input.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.wf_frame, text="Zielpfad (Prepare/Stream):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.dst_path_input = ctk.CTkEntry(self.wf_frame, placeholder_text="Standard: data/benchmark/prepared_benchmarks")
        self.dst_path_input.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # Sektions-Buttons innerhalb des wf_frame
        self.wf_btn_frame = ctk.CTkFrame(self.wf_frame, fg_color="transparent")
        self.wf_btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.gui_prepare_btn = ctk.CTkButton(self.wf_btn_frame, text="1. Prepare Data", command=self.gui_prepare_action, fg_color="#7b2cbf")
        self.gui_prepare_btn.pack(side="left", padx=5)
        
        self.gui_stream_btn = ctk.CTkButton(self.wf_btn_frame, text="2. Load to RAM (Stream)", command=self.gui_stream_action, fg_color="#3a86ff")
        self.gui_stream_btn.pack(side="left", padx=5)

        self.gui_clear_stream_btn = ctk.CTkButton(self.wf_btn_frame, text="RAM löschen", command=self.gui_clear_stream_action, fg_color="#d9534f", width=100)
        self.gui_clear_stream_btn.pack(side="left", padx=5)
        
        self.gui_stream_status_lbl = ctk.CTkLabel(self.wf_btn_frame, text="Kein RAM-Stream geladen", text_color="gray", font=ctk.CTkFont(weight="bold"))
        self.gui_stream_status_lbl.pack(side="left", padx=10)

        # Wir erhöhen current_row, da das wf_frame fertig platziert ist
        current_row += 1

        # =================================================================
        # --- PDF EINGABEFELD ---
        # =================================================================
        self.pdf_label = ctk.CTkLabel(self.main_frame, text="Optionale PDF-Dokumenten-URL (Nutzt cloudflare-ai Engine):")
        self.pdf_label.grid(row=current_row, column=0, sticky="w", padx=20, pady=(10, 0))
        current_row += 1

        self.pdf_input = ctk.CTkEntry(self.main_frame, placeholder_text="https://beispiel.de/richtlinie.pdf")
        self.pdf_input.grid(row=current_row, column=0, sticky="ew", padx=20, pady=5)
        current_row += 1

        # =================================================================
        # --- BENUTZERDEFINIERTE BENCHMARK-NUMMER / ID (JETZT DYNAMISCH) ---
        # =================================================================
        self.bench_num_label = ctk.CTkLabel(self.main_frame, text="Benchmark Nummer / Projekt-ID für den ID-Export (z.B. 1, 001, Test-M1):")
        self.bench_num_label.grid(row=current_row, column=0, sticky="w", padx=20, pady=(10, 0))
        current_row += 1

        self.bench_num_input = ctk.CTkEntry(self.main_frame, placeholder_text="Standard: Aktuelle Uhrzeit (z.B. B1830)")
        self.bench_num_input.grid(row=current_row, column=0, sticky="ew", padx=20, pady=5)
        current_row += 1

        # =================================================================
        # --- PROMPT TEXTBOX ---
        # =================================================================
        self.prompt_label = ctk.CTkLabel(self.main_frame, text="Benchmark Prompt / Anweisungen:")
        self.prompt_label.grid(row=current_row, column=0, sticky="w", padx=20, pady=(10, 0))
        current_row += 1

        self.prompt_input = ctk.CTkTextbox(self.main_frame, height=200)
        self.prompt_input.grid(row=current_row, column=0, sticky="ew", padx=20, pady=10)
        current_row += 1

        # =================================================================
        # --- OUTPUT TEXTBOX ---
        # =================================================================
        self.output_label = ctk.CTkLabel(self.main_frame, text="Antworten:")
        self.output_label.grid(row=current_row, column=0, sticky="w", padx=20)
        current_row += 1

        self.output_text = ctk.CTkTextbox(self.main_frame, font=("Consolas", 11))
        self.output_text.grid(row=current_row, column=0, sticky="nsew", padx=20, pady=10)
        
        # Das Textfeld soll sich dynamisch dehnen dürfen
        self.main_frame.grid_rowconfigure(current_row, weight=1)
        current_row += 1

        # =================================================================
        # --- BUTTONS FRAME ---
        # =================================================================
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.grid(row=current_row, column=0, pady=20)

        self.send_button = ctk.CTkButton(self.btn_frame, text="Starten", command=self.run_benchmark, fg_color="#2c6e49")
        self.send_button.pack(side="left", padx=5)
        
        self.save_button = ctk.CTkButton(self.btn_frame, text="Rohdaten Export", command=self.save_raw_json, state="disabled")
        self.save_button.pack(side="left", padx=5)

        self.extract_button = ctk.CTkButton(self.btn_frame, text="Szenarien Extrahieren", command=self.extract_scenarios, state="disabled", fg_color="#1f538d")
        self.extract_button.pack(side="left", padx=5)

        self.trace_export_button = ctk.CTkButton(self.btn_frame, text="Tracing Export", command=self.export_tracing_json, state="disabled", fg_color="#d9534f")
        self.trace_export_button.pack(side="left", padx=5)

    # =================================================================
    # --- GUI-INTEGRIERTE PIPELINE-AKTIONEN ---
    # =================================================================
    
    def gui_prepare_action(self):
        default_input = project_root / "data" / "benchmark" / "validated"
        default_output = project_root / "data" / "benchmark" / "prepared_benchmarks"
        
        user_src = self.src_path_input.get().strip()
        user_dst = self.dst_path_input.get().strip()
        
        input_path = Path(user_src).resolve() if user_src else default_input.resolve()
        output_path = Path(user_dst).resolve() if user_dst else default_output.resolve()
        
        self._append_to_output(f"\n[GUI-WORKFLOW]: Starte Datensäuberung (#65)...\n  -> Quellpfad: {input_path}\n  -> Zielpfad:  {output_path}\n")
        
        if not input_path.exists():
            self._append_to_output(f"[FEHLER]: Quellpfad existiert nicht!\n")
            return
            
        try:
            prepare_data(str(input_path), str(output_path))
            self._append_to_output(f"[SUCCESS]: Daten erfolgreich auf Festplatte bereinigt.\n")
        except Exception as e:
            self._append_to_output(f"[FEHLER bei Prepare]: {e}\n")

    def gui_stream_action(self):
        global global_jsonl_stream
        default_stream_input = project_root / "data" / "benchmark" / "prepared_benchmarks"
        
        user_dst = self.dst_path_input.get().strip()
        stream_path = Path(user_dst).resolve() if user_dst else default_stream_input.resolve()
        
        self._append_to_output(f"\n[GUI-WORKFLOW]: Starte HTTP-Stream-Vorbereitung (#66)...\n  -> Suchpfad: {stream_path}\n")
        
        if not stream_path.exists():
            self._append_to_output(f"[FEHLER]: Zielpfad existiert nicht! Bitte zuerst 'Prepare' ausführen.\n")
            return
            
        try:
            global_jsonl_stream = load_and_prepare_stream(str(stream_path))
            anzahl = len(global_jsonl_stream)
            self._append_to_output(f"[SUCCESS]: {anzahl} Szenarien im RAM bereit für den Testlauf!\n")
            self.gui_stream_status_lbl.configure(text=f"🟢 {anzahl} Szenarien im RAM", text_color="#2c6e49")
        except Exception as e:
            self._append_to_output(f"[FEHLER beim Laden des Streams]: {e}\n")
            self.gui_stream_status_lbl.configure(text="🔴 Fehler beim Laden", text_color="#d9534f")

    def gui_clear_stream_action(self):
        """Löscht den aktuellen In-Memory JSONL Stream aus dem RAM"""
        global global_jsonl_stream
        if global_jsonl_stream:
            anzahl = len(global_jsonl_stream)
            global_jsonl_stream = None
            self._append_to_output(f"\n[GUI-WORKFLOW]: {anzahl} Szenarien erfolgreich aus dem Arbeitsspeicher (RAM) gelöscht.\n")
            self.gui_stream_status_lbl.configure(text="Kein RAM-Stream geladen", text_color="gray")
        else:
            self._append_to_output("\n[HINWEIS]: Der RAM-Speicher ist bereits leer.\n")

    # =================================================================
    # --- LOGIK-FUNKTIONEN ---
    # =================================================================
    
    # Aufgabe: Bereitet die GUI vor und startet für jedes frei eingegebene Modell einen Hintergrund-Thread
    def run_benchmark(self):
        # Holt den eingegebenen Prompt-Text aus der Textbox
        prompt = self.prompt_input.get("1.0", "end-1c")
        # Holt die eingetippte PDF-URL und entfernt Leerzeichen am Rand
        pdf_url = self.pdf_input.get().strip()
        
        # Abbruch, falls das Prompt-Feld komplett leer ist
        if not prompt.strip(): return

        # NEU: Holt den rohen Text aus der Modell-Eingabe-Sidebar, splittet ihn zeilenweise auf
        raw_model_lines = self.model_input_text.get("1.0", "end-1c").split("\n")
        
        # Filtert leere Zeilen oder reine Leerzeichen aus der Liste heraus
        selected_models = [m.strip() for m in raw_model_lines if m.strip()]

        # UI-Vorbereitung: Altes Textfeld leeren und alten Speicher löschen
        self.output_text.delete("1.0", "end")
        self.last_results = []

        # Sicherheitsprüfung I: Wenn gar kein Modell eingetragen wurde
        if not selected_models:
            self._append_to_output("\n[SYSTEM-FEHLER]: Bitte mindestens ein gültiges Modell im Format 'provider/model' eintragen.\n")
            return

        # Sicherheitsprüfung II: Abfangen des Limits zur Vermeidung von Thread-Überlastung
        if len(selected_models) > MAX_MODEL_LIMIT:
            self._append_to_output(f"\n[SYSTEM-LIMIT]: Es wurden {len(selected_models)} Modelle eingegeben. "
                                   f"Das vordefinierte Maximum liegt bei {MAX_MODEL_LIMIT} Modellen gleichzeitig, "
                                   f"um API-Drosselungen zu verhindern.\n")
            return
        
        # Deaktiviert alle Buttons, damit der Benutzer während der Berechnung nicht doppelklickt
        self.send_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.extract_button.configure(state="disabled")
        self.trace_export_button.configure(state="disabled")

        # --- WEICHE FÜR DEN STREAMING-MODUS INNERHALB DER GUI ---
        if 'global_jsonl_stream' in globals() and global_jsonl_stream:
            self._append_to_output(f"[GUI-RUN]: Starte HTTP-Streaming für {len(global_jsonl_stream)} Szenarien aus dem RAM...\n")
            
            # Da HTTP-Streaming synchron/sequentiell Zeile für Zeile arbeitet, 
            # starten wir den Gesamt-Stream in einem eigenen Kontroll-Thread, damit die GUI nicht einfriert
            threading.Thread(target=self._headless_stream_loop, args=(selected_models, prompt, pdf_url)).start()
        else:
            # NORMALER MANUELLER PROMPT-MODUS
            if not prompt.strip():
                self._append_to_output("\n[FEHLER]: Bitte ein Prompt eingeben, da kein RAM-Stream aktiv ist.\n")
                self._finish_benchmark()
                return
        
        # Setzt den Zähler für aktive Threads auf die Anzahl der erkannten KIs
        self.active_threads = len(selected_models)

        # Generiert eine eindeutige, zufällige 32-stellige ID für diesen Durchlauf
        broadcast_trace_id = uuid.uuid4().hex
        self.current_trace_id = broadcast_trace_id

        # Multi-Threading Schleife: Startet für jede erkannte KI-Zeile einen eigenen Arbeiter-Thread
        for model in selected_models:
            thread = threading.Thread(
                target=self._single_model_request, 
                args=(model, prompt, pdf_url, broadcast_trace_id)
            )
            # daemon=True: Der Thread stirbt sofort automatisch mit, wenn die GUI geschlossen wird
            thread.daemon = True
            # Feuert den Thread im Hintergrund ab
            thread.start()

    def _headless_stream_loop(self, selected_models, custom_prompt, pdf_url):
        global global_jsonl_stream
        broadcast_trace_id = uuid.uuid4().hex
        self.current_trace_id = broadcast_trace_id
        
        for index, jsonl_line in enumerate(global_jsonl_stream):
            try:
                szenario_daten = json.loads(jsonl_line)
                szenario_id = szenario_daten.get("id", f"UNK_{index}")
                
                anweisung = custom_prompt.strip() if custom_prompt.strip() else "Antworte strikt im JSON-Format."
                test_frage = f"System-Anweisung: {anweisung}\n\nHier ist das Szenario:\n{jsonl_line}"
                
                self.after(0, self._append_to_output, f"\n[STREAMING] ({index+1}/{len(global_jsonl_stream)}): Sende {szenario_id}...\n")
                
                # Threads für dieses einzelne Szenario aufbauen
                self.active_threads = len(selected_models)
                threads = []
                for model in selected_models:
                    t = threading.Thread(target=self._single_model_request, args=(model, test_frage, pdf_url, broadcast_trace_id))
                    t.start()
                    threads.append(t)
                    
                for t in threads: 
                    t.join()
                    
            except Exception as e:
                self.after(0, self._append_to_output, f"[FEHLER] in Stream-Zeile {index+1}: {e}\n")
                
        self.after(0, self._append_to_output, f"\n[SYSTEM]: Alle gestreamten Szenarien beantwortet! Daten flüchtig im RAM.\n")
        self.after(0, self._finish_benchmark)

    # Aufgabe: Führt den eigentlichen Netzwerk-Aufruf zur KI isoliert im Hintergrund aus
    def _single_model_request(self, model, prompt, pdf_url, trace_id):
        try:
            # Schreibt asynchron den Start-Status in die GUI-Textbox
            self.after(0, self._append_to_output, f"\n[STARTING] {model}...\n")
            
            # REPARATUR-KERNSTÜCK: Erzeugt einen exklusiven, isolierten Langfuse-Client NUR für diesen Thread.
            thread_langfuse = get_client()
            
            # PDF-Struktur für OpenRouter zusammenbauen, falls eine URL angegeben wurde
            queued_pdf = None
            if pdf_url:
                filename = pdf_url.rstrip("/").split("/")[-1]
                if not filename.lower().endswith(".pdf"): filename += ".pdf"
                queued_pdf = {"url": pdf_url, "filename": filename, "engine": "cloudflare-ai"}
            
            # Transformiert Prompt und PDF über deine conversation.py in die offizielle API-Nachrichtenstruktur
            user_message = build_user_message(prompt, queued_pdf)
            messages_list = [user_message]
            
            # Merkt den exakten Start-Zeitpunkt in UTC (wichtig für die Latenzzeit-Berechnung)
            start_time = datetime.now(timezone.utc)
            
            # --- DIE OFFIZIELLE SDK-LÖSUNG VIA TRACE_CONTEXT ---
            clean_span_name = f"turn-1-{model.split('/')[-1]}"
            
            # Hier geben wir die trace_id über den offiziellen OpenTelemetry-Kontext des SDKs mit
            with thread_langfuse.start_as_current_observation(
                as_type="span",
                name=clean_span_name,
                trace_context={
                    "trace_id": trace_id  # Bindet den Thread fest an die übermittelte 32-stellige ID
                }
            ) as span:
                
                # Wir sichern die gemeinsame ID für den Export
                self.current_trace_id = trace_id
                
                span.update(input=prompt, metadata={"model": model})
                
                # Der physische API-Aufruf
                content, input_tok, output_tok = call_model(
                    model=model,
                    messages=messages_list,
                    pdf_engine="cloudflare-ai" if queued_pdf else None
                )
                
                # Antwort und Tokens an den Span übergeben
                span.update(output=content, usage={"input": input_tok, "output": output_tok})
            # -------------------------------------------------------------

            # Berechnet die exakte Dauer des API-Aufrufs in Sekunden
            end_time = datetime.now(timezone.utc)
            latency = (end_time - start_time).total_seconds()

            # Gibt die empfangene Antwort im GUI-Textfeld aus
            self.after(0, self._append_to_output, f"\n--- ANTWORT von {model} ---\n{content}\n")

            # Sichert die Daten thread-sicher über das Mutex-Schloss in den globalen GUI-Speicher
            with self.results_lock:
                self.last_results.append({
                    "model": model,
                    "prompt": prompt,
                    "content": content,
                    "input_tokens": input_tok,
                    "output_tokens": output_tok,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "latency": latency,
                    "trace_id": trace_id,
                    "observation_id": span.id # Nutzt die echte ID von Langfuse für das Schema
                })
            
            self.after(0, self._append_to_output, f"\n[FINISHED] {model}\n" + "="*30 + "\n")
            
            # ZWANGSLEERUNG: Schießt den Puffer dieses Threads sofort ins Internet an dein Dashboard!
            thread_langfuse.flush()
                
        except Exception as e:
            # Fängt Fehler (wie Netzwerkabbrüche) ab und zeigt sie im Textfeld an, damit die GUI nicht abstürzt
            error_msg = str(e)
            self.after(0, self._append_to_output, f"\n[FEHLER] {model}: {error_msg}\n")

        # Thread-Synchronisations-Riegel: Zählt die aktiven Threads herunter
        with self.results_lock:
            self.active_threads -= 1
            # Wenn die letzte KI fertig gerechnet hat, rufe die Abschlussfunktion auf
            if self.active_threads <= 0:
                self.after(0, self._finish_benchmark)

    # Aufgabe: Schaltet nach dem Durchlauf aller Threads die GUI wieder frei und sichert globale Daten
    def _finish_benchmark(self):
        self.send_button.configure(state="normal")
        self.save_button.configure(state="normal")
        self.extract_button.configure(state="normal")
        self.trace_export_button.configure(state="normal")
        
        # Leert vorsichtshalber den globalen Verwaltungs-Kanal
        langfuse_global.flush()
        self._append_to_output("\n[SYSTEM]: Verarbeitung abgeschlossen. Alle Daten exportbereit!\n")

    # Aufgabe: Hilfsfunktion zum sauberen Anhängen von Texten an das große GUI-Sichtfeld
    def _append_to_output(self, text):
        self.output_text.insert("end", text)
        self.output_text.see("end") # Scrollt automatisch ans Ende, damit man den Text live sieht

    # =================================================================
    # --- TRACING EXPORT METHODE ---
    # =================================================================
    def export_tracing_json(self):
        if not self.current_trace_id:
            self._append_to_output("\n[FEHLER]: Keine aktive Trace-ID für diesen Durchlauf vorhanden.\n")
            return

        filename = f"tracing_export_{datetime.now().strftime('%H%M%S')}.json"
        self._append_to_output(f"\n[SYSTEM]: Synchronisiere lokale Pipeline mit Langfuse-Server (Trace-ID: {self.current_trace_id})...\n")
        
        # 1. Puffer leeren, damit die Daten an den Server geschickt werden
        langfuse_global.flush()
        
        # 2. Server abfragen (Polling)
        try:
            server_trace_data = fetch_trace_with_retry_benchmark(self.current_trace_id)
            
            if not server_trace_data:
                self._append_to_output("[WARNUNG]: Server lieferte keine Daten. Erzeuge lokales Fallback...\n")
                # Lokales Fallback (dein alter Code), falls der Server offline ist
                return

            # 3. Exakten Server-Trace auf Festplatte schreiben
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(server_trace_data, f, indent=4, ensure_ascii=False, default=str)
                
            self._append_to_output(f"[SUCCESS]: Server-Tracing-Daten erfolgreich in '{filename}' gesichert!\n")
        except Exception as e:
            self._append_to_output(f"[FEHLER beim Server-Tracing-Export]: {e}\n")

    # Sichert die reinen Text-Antworten der KIs ungefiltert in eine Datei
    def save_raw_json(self):
        filename = f"raw_export_{datetime.now().strftime('%H%M%S')}.json"
        export_data = {
            "metadata": {"export_time": datetime.now().isoformat(), "total_models": len(self.last_results)},
            "scenarios": [{"model": r["model"], "raw_content": r["content"]} for r in self.last_results]
        }
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
            self._append_to_output(f"\n[SYSTEM]: Rohdaten in {filename} gespeichert.\n")
        except Exception as e:
            self._append_to_output(f"\n[FEHLER] beim Roh-Export: {e}\n")

    # =================================================================
    # --- DIE MODIFIZIERTE SCENARIOS EXTRAHIEREN METHODE ---
    # =================================================================
    # Aufgabe: Extrahiert JSON-Blöcke, formatiert IDs neu und speichert die Dateien nach dem neuen Namensprinzip ab.
    def extract_scenarios(self):
        user_benchmark_number = self.bench_num_input.get().strip()
        benchmark_number = user_benchmark_number if user_benchmark_number else f"B{datetime.now().strftime('%H%M')}"
        export_format = self.format_option.get()
        current_date = datetime.now().strftime('%y-%m-%d')

        scenarios_by_model = {}
        for res in self.last_results:
            model_name = res["model"].split('/')[-1].replace('.', '-')
            if model_name not in scenarios_by_model:
                scenarios_by_model[model_name] = []
            scenarios_by_model[model_name].append(res)

        for model_name, results in scenarios_by_model.items():
            filename = f"{benchmark_number}_complete-benchmark_{model_name}_{current_date}.{export_format}"
            json_array_data = []

            try:
                for idx, res in enumerate(results):
                    raw_ki_content = res["content"]
                    clean_raw = re.sub(r"```jsonl?|\n?```", "", raw_ki_content).strip()
                    
                    start_idx = clean_raw.find('{')
                    end_idx = clean_raw.rfind('}')
                    obj_extracted = None
                    
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        try:
                            obj_extracted = json.loads(clean_raw[start_idx:end_idx+1])
                        except: obj_extracted = None

                    if isinstance(obj_extracted, dict):
                        obj_extracted["id"] = f"{benchmark_number}_{model_name}_{idx+1:03d}"
                        json_array_data.append(obj_extracted)
                    else:
                        json_array_data.append({"id": f"{benchmark_number}_{model_name}_{idx+1:03d}", "raw_error_content": raw_ki_content})

                with open(filename, "w", encoding="utf-8") as f:
                    if export_format == "jsonl":
                        for item in json_array_data: f.write(json.dumps(item, ensure_ascii=False) + "\n")
                    else:
                        json.dump(json_array_data, f, indent=4, ensure_ascii=False)
                self._append_to_output(f"\n[SUCCESS]: {filename}\n")
            except Exception as e:
                self._append_to_output(f"\n[FEHLER] bei {filename}: {e}\n")

# =================================================================
# --- INTERAKTIVER TERMINAL-MODUS (SAUBERES EIGENSTÄNDIGES REPL) ---
# =================================================================
def run_pipeline_mode(args):
    global global_jsonl_stream
    global current_trace_id
    print("\n[SYSTEM]: Interaktiver CLI-Modus gestartet.")
    print("Tippe 'help' für eine Übersicht aller verfügbaren Befehle.")
    
    current_prompt = args.prompt.strip() if (args.prompt and args.prompt != "start") else ""
    current_models = [m.strip() for m in args.models.split(",") if m.strip()] if args.models else []
    
    # NEU: Wir machen die PDF-URL und die Engine als veränderbare Variablen in der Sitzung verfügbar
    current_pdf = args.pdf.strip() if args.pdf else ""
    current_engine = args.engine if args.engine else "cloudflare-ai"
    
    session_results = []
    results_lock = threading.Lock()

    # --- HILFSFUNKTION: KI-ANFRAGE ---
    def headless_model_request(model, prompt, pdf_url, trace_id, pdf_engine="cloudflare-ai"):
        try:
            print(f"\n[STARTING] {model}...\n")
            thread_langfuse = get_client()
            
            queued_pdf = None
            if pdf_url:
                filename = pdf_url.rstrip("/").split("/")[-1]
                if not filename.lower().endswith(".pdf"): filename += ".pdf"
                queued_pdf = {"url": pdf_url, "filename": filename, "engine": pdf_engine}
            
            user_message = build_user_message(prompt, queued_pdf)
            messages_list = [user_message]
            start_time = datetime.now(timezone.utc)
            
            # --- OFFIZIELLE SDK-LÖSUNG VIA TRACE_CONTEXT (CLI-EBENE) ---
            global current_trace_id
            current_trace_id = trace_id
            
            clean_span_name = f"turn-1-{model.split('/')[-1]}"
            
            # Hier geben wir die trace_id über den offiziellen OpenTelemetry-Kontext des SDKs mit
            with thread_langfuse.start_as_current_observation(
                as_type="span",
                name=clean_span_name,
                trace_context={
                    "trace_id": trace_id  # Bindet den Thread fest an die gemeinsame 32-stellige ID
                }
            ) as span:
                
                span.update(input=prompt, metadata={"model": model})
                
                content, input_tok, output_tok = call_model(
                    model=model,
                    messages=messages_list,
                    pdf_engine=pdf_engine if queued_pdf else None
                )
                
                span.update(output=content, usage={"input": input_tok, "output": output_tok})
            # -----------------------------------------------------------

            end_time = datetime.now(timezone.utc)
            latency = (end_time - start_time).total_seconds()

            print(f"\n--- ANTWORT von {model} ---\n{content}\n")

            with results_lock:
                session_results.append({
                    "model": model, "prompt": prompt, "content": content,
                    "input_tokens": input_tok, "output_tokens": output_tok,
                    "start_time": start_time.isoformat(), "end_time": end_time.isoformat(),
                    "latency": latency, "trace_id": trace_id, "observation_id": span.id # Echte Langfuse-Span-ID
                })
            print(f"\n[FINISHED] {model}\n" + "="*30 + "\n")
            thread_langfuse.flush()
        except Exception as e:
            print(f"\n[FEHLER] bei Anfrage an {model}: {e}\n")

    # --- HILFSFUNKTION: SZENARIEN-EXTRAKTION ---
    def headless_extract_scenarios(export_format="jsonl", prefix="PIPELINE"):
        current_date = datetime.now().strftime('%y-%m-%d')
        model_counters = {}
        
        for res in session_results:
            raw = res["content"]
            full_model_name = res["model"]
            clean_model_name = full_model_name.split('/')[-1].replace('.', '-')
            if clean_model_name not in model_counters:
                model_counters[clean_model_name] = 1

            filename = f"{prefix}_complete-benchmark_{clean_model_name}_{current_date}.{export_format}"
            model_extracted_data = []
            
            clean_raw = re.sub(r"```jsonl?\n?|```", "", raw).strip()
            matches = re.findall(r'\{.*?\}', clean_raw, re.DOTALL)
            
            for m in matches:
                try:
                    obj = json.loads(m)
                    if isinstance(obj, dict):
                        current_num = model_counters[clean_model_name]
                        obj["id"] = f"{prefix}_{clean_model_name}_{current_num:03d}"
                        model_extracted_data.append(obj)
                        model_counters[clean_model_name] += 1
                except: continue
                
            if not model_extracted_data:
                print(f"[HINWEIS]: Konnte keine JSON-Objekte aus dem Text filtern. Schreibe Antwort als Text-Fallback.")
                model_extracted_data = {"raw_text_response": raw}

            try:
                with open(filename, "w", encoding="utf-8") as f:
                    if export_format == "jsonl" and isinstance(model_extracted_data, list):
                        for item in model_extracted_data: 
                            f.write(json.dumps(item, ensure_ascii=False) + "\n")
                    else:
                        json.dump(model_extracted_data, f, indent=4, ensure_ascii=False)
                print(f"[EXPORT ERFOLGREICH]: Datei erstellt -> {filename}")
            except Exception as e: 
                print(f"[FEHLER beim Schreiben von {filename}]: {e}")

    # --- HILFSFUNKTION: ROHDATEN EXPORT ---
    def headless_save_raw_json():
        if not session_results: return
        filename = f"raw_export_{datetime.now().strftime('%H%M%S')}.json"
        export_data = {
            "metadata": {"export_time": datetime.now().isoformat(), "total_models": len(session_results)},
            "scenarios": [{"model": r["model"], "raw_content": r["content"]} for r in session_results]
        }
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
            print(f"[RAW EXPORT ERFOLGREICH]: Rohdaten gespeichert unter -> {filename}")
        except Exception as e:
            print(f"[FEHLER beim Rohdaten-Export]: {e}")

    # --- HILFSFUNKTION: TRACING-EXPORT ---
    # --- HILFSFUNKTION: TRACING-EXPORT (SERVER-POLLING MODUS) ---
    def headless_export_tracing():
        global current_trace_id
        if not current_trace_id: 
            print("[FEHLER]: Keine aktive Trace-ID vorhanden.")
            return
            
        filename = f"tracing_export_{datetime.now().strftime('%H%M%S')}.json"
        print(f"\n[SYSTEM]: Erzwinge Server-Synchronisation für Trace: {current_trace_id}")
        
        # Puffer absenden
        langfuse_global.flush()
        
        # Server-Abfrage starten
        try:
            server_trace_data = fetch_trace_with_retry_benchmark(current_trace_id)
            if server_trace_data:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(server_trace_data, f, indent=4, ensure_ascii=False, default=str)
                print(f"[TRACING ERFOLGREICH]: Original Server-Trace exportiert -> {filename}")
            else:
                print("[FEHLER]: Server-Daten konnten nicht abgerufen werden (Timeout).")
        except Exception as e:
            print(f"[FEHLER beim Tracing-Export]: {e}")

    # --- AUTOMATISCHER ERSTDURCHLAUF ---
    if current_prompt and current_models:
        print(f"\n[START]: Starte automatischen Erstdurchlauf...")
        current_trace_id = uuid.uuid4().hex
        threads = []
        for model in current_models:
            t = threading.Thread(target=headless_model_request, args=(model, current_prompt, current_pdf, current_trace_id, current_engine))
            t.start()
            threads.append(t)
        for t in threads: t.join()
        print("\n[SYSTEM]: Erstdurchlauf beendet. Führe automatischen Export aus...")
        headless_extract_scenarios(args.format, args.prefix)
        headless_export_tracing()
        
    # --- INTERAKTIVE SCHLEIFE (REPL) ---
    while True:
        try:
            user_input = input("\nPflegeBench> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[SYSTEM]: Programm beendet."); sys.exit(0)
        if not user_input: continue

        cmd_parts = user_input.split(maxsplit=1)
        base_cmd = cmd_parts[0].lower()
        cmd_arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

        if base_cmd == "help":
            print("""
┌──────────────────────────────────────────────────────────────────────────────────┐
│  PflegeBench — Pipeline & Interaktive CLI Commands                               │
├──────────────────────────────────────────────────────────────────────────────────┤
│  START-ARGUMENTE (Beim Aufruf von python benchmark.py ...):                      │
│  --cli                     Aktiviert direkt den interaktiven Terminal-Modus      │
│  --prompt <pfad/text>      Dateipfad (.txt) ODER direkter Prompt-Text            │
│  --models <id1,id2>        Kommagetrennte OpenRouter-Modelle                     │
│  --prefix <name>           Präfix für Szenarien-IDs (Standard: PIPELINE)         │
│  --format <json/jsonl>     Ausgabeformat für Szenarien (Standard: jsonl)         │
│  --pdf <url>               Optionale URL zu einem PDF-Dokument                   │
│  --engine cloudflare-ai    Nutzt die standardmäßige Cloudflare-AI Engine         │
│  --engine mistral-ocr      Nutzt die hochpräzise Mistral-OCR Engine              │
│  --engine native           Nutzt die native OpenRouter-Engine (Direktübergabe)   │
│  -h, --help                Zeigt diese Hilfeübersicht an                         │
├──────────────────────────────────────────────────────────────────────────────────┤
│  INTERAKTIVE BEFEHLE (Innerhalb der "PflegeBench>" Konsole):                     │
│  help                      Zeigt diese Übersicht an                              │
│  prepare [pfad]            Säubert Validierungsdaten auf Festplatte              │
│                            (Nutzt Default-Pfad, falls kein Pfad angegeben wird)  │
│  stream [pfad]             Lädt bereinigte Daten unbestechlich in den RAM        │
|                            (Nutzt Default-Pfad, falls kein Pfad angegeben wird)  |
│  prompt <text/pfad>        Überschreibt oder setzt den aktuellen System-Prompt   │
│  models <id1,id2>          Setzt ein oder mehrere Modelle (kommagetrennt)        │
│  run                       Startet Abfrage (In-Memory Stream ODER Einzelprompt)  │
│  export [json/jsonl]       Extrahiert tiefe JSON-Strukturen aus dem RAM-Ergebnis │
│  raw                       Exportiert die unstrukturierten KI-Antworten (JSON)   │
│  tracing                   Exportiert das Langfuse-Tracing-Protokoll (JSON)      │
│  reset                     Verwirft RAM-Stream & Sitzungsdaten für Neustart      │
│  done                      Beendet das Programm vollständig                      │
├──────────────────────────────────────────────────────────────────────────────────┤
│  HINWEISE ZUM STREAMING-WORKFLOW:                                                │
│  1. Nutze 'prepare' und danach 'stream', um Testdaten in den RAM zu laden.       │
│  2. 'run' erkennt den RAM-Stream automatisch und schaltet auf HTTP-Streaming.    │
│  3. Erst durch 'export' wird die finale Gesamtdatei auf Festplatte erzeugt.      │
│  4. Wird das Skript ohne Argumente gestartet, öffnet sich die Desktop-GUI.       │
└──────────────────────────────────────────────────────────────────────────────────┘""")

        elif base_cmd == "done":
            print("[SYSTEM]: Programm beendet. Auf Wiedersehen!"); sys.exit(0)

        elif base_cmd == "reset":
            # REPARATUR: Wir greifen auf die globale Stream-Variable zu und leeren sie
            global global_jsonl_stream
            global_jsonl_stream = None  # Verwirft die In-Memory JSONL-Zeilen vollständig im RAM
            
            # Die restlichen Sitzungsvariablen zurücksetzen
            current_prompt = ""
            current_models = []
            current_pdf = ""
            current_engine = "cloudflare-ai"
            session_results = []
            
            print("[SYSTEM]: Sitzung komplett zurückgesetzt (inklusive PDF, Engine und In-Memory Stream Daten).")

        elif base_cmd == "prompt":
            if not cmd_arg: print("[FEHLER]: Prompt fehlt."); continue
            if os.path.exists(cmd_arg):
                try:
                    with open(cmd_arg, "r", encoding="utf-8") as f: current_prompt = f.read().strip()
                    print(f"[SYSTEM]: Prompt erfolgreich aus Datei geladen.")
                except Exception as e: print(f"[FEHLER]: {e}")
            else:
                current_prompt = cmd_arg; print("[SYSTEM]: Direkt-Text als Prompt gespeichert.")

        elif base_cmd == "models":
            if not cmd_arg: print("[FEHLER]: Modell-ID fehlt."); continue
            current_models = [m.strip() for m in cmd_arg.split(",") if m.strip()]
            print(f"[SYSTEM]: Modelle gesetzt: {current_models}")

        # INTEGRIERTER BEFEHL FÜR PDF-ÜBERGABE IM SELECTION MODUS ---
        elif base_cmd == "pdf":
            if not cmd_arg:
                print("[FEHLER]: Bitte gib eine gültige PDF-URL an (z.B. pdf https://beispiel.de/datei.pdf).")
                continue
            
            pdf_parts = cmd_arg.split()
            current_pdf = pdf_parts[0].strip()
            
            # Prüft, ob nach der URL auch eine gewünschte Engine mitgegeben wurde
            if len(pdf_parts) > 1:
                chosen_engine = pdf_parts[1].lower().strip()
                if chosen_engine in ["cloudflare-ai", "mistral-ocr", "native"]:
                    current_engine = chosen_engine
                else:
                    print(f"[HINWEIS]: Ungültige Engine '{chosen_engine}'. Nutze Standard: cloudflare-ai")
                    current_engine = "cloudflare-ai"
            else:
                current_engine = "cloudflare-ai"
                
            print(f"[SYSTEM]: PDF erfolgreich geladen.")
            print(f"  -> URL: {current_pdf}")
            print(f"  -> Engine: {current_engine}")
        
        # REINE DATEN-SÄUBERUNG 
        elif base_cmd == "prepare":
            # bei default Rot 
            default_input = project_root / "data" / "benchmark" / "validated"
            default_output = project_root / "data" / "benchmark" / "prepared_benchmarks"
            
            if cmd_arg:
                given_path = Path(cmd_arg)
                input_path = given_path.resolve() if given_path.is_absolute() else (project_root / given_path).resolve()
            else:
                input_path = default_input.resolve()
            
            output_path = default_output.resolve()
            
            print(f"\n[WORKFLOW]: Starte Datensäuberung (#65)...")
            print(f"  -> Quellpfad: {input_path}")
            print(f"  -> Zielpfad:  {output_path}")
            
            if not input_path.exists():
                print(f"[FEHLER]: Der Pfad '{input_path}' existiert nicht! Bitte überprüfe die Eingabe.")
                continue
            
            print("\n[PROZESS]: Bereinige Validierungsdaten auf der Festplatte...")
            try:
                prepare_data(str(input_path), str(output_path))
            except Exception as e:
                print(f"[FEHLER bei der Säuberung]: {e}")

        # REINES IN-MEMORY HTTP-STREAMING (#66)
        elif base_cmd == "stream":
            
            default_stream_input = project_root / "data" / "benchmark" / "prepared_benchmarks"
            
            if cmd_arg:
                given_path = Path(cmd_arg)
                stream_path = given_path.resolve() if given_path.is_absolute() else (project_root / given_path).resolve()
            else:
                stream_path = default_stream_input.resolve()
                
            print(f"\n[WORKFLOW]: Starte HTTP-Stream-Vorbereitung (#66)...")
            print(f"  -> Suchpfad: {stream_path}")
            
            if not stream_path.exists():
                print(f"[FEHLER]: Der Pfad '{stream_path}' existiert nicht! Bitte zuerst 'prepare' ausführen.")
                continue
                
            print("\n[PROZESS]: Lade bereinigte Daten unbestechlich sortiert in den RAM...")
            try:
                global_jsonl_stream = load_and_prepare_stream(str(stream_path))
                print(f"\n[SUCCESS]: {len(global_jsonl_stream)} Szenarien stehen im Arbeitsspeicher bereit für den Testlauf ('run')!")
            except Exception as e:
                print(f"[FEHLER beim Laden des Streams]: {e}")

        elif base_cmd == "run":
            if not current_models:
                model_retry = input("Keine Modelle definiert. Bitte jetzt eingeben (kommagetrennt): ").strip()
                if not model_retry: continue
                current_models = [m.strip() for m in model_retry.split(",") if m.strip()]
            
            # FALL A) Es liegen gestreamte Szenarien im RAM vor
            if 'global_jsonl_stream' in globals() and global_jsonl_stream:
                print(f"\n[BENCHMARK-RUN]: Starte HTTP-Streaming für {len(global_jsonl_stream)} Szenarien...")
                session_results = [] 
                current_trace_id = uuid.uuid4().hex

                # Wir gehen jedes Szenario einzeln durch (Reines RAM-Streaming)
                for index, jsonl_line in enumerate(global_jsonl_stream):
                    try:
                        szenario_daten = json.loads(jsonl_line)
                        szenario_id = szenario_daten.get("id", f"UNK_{index}")
                        
                        # Auslesen des Systemprompts und Verknüpfung
                        anweisung = current_prompt if current_prompt else "Antworte strikt im JSON-Format."
                        test_frage = (
                            f"System-Anweisung: {anweisung}\n\n"
                            f"Hier ist das zu bearbeitende Szenario als JSON-Daten:\n"
                            f"{jsonl_line}"
                        )
                        
                        print(f"\n[STREAMING] ({index+1}/{len(global_jsonl_stream)}): Sende Szenario {szenario_id} an KIs...")
                        
                        threads = []
                        for model in current_models:
                            t = threading.Thread(
                                target=headless_model_request, 
                                args=(model, test_frage, current_pdf, current_trace_id, current_engine)
                            )
                            t.start()
                            threads.append(t)
                        
                        for t in threads: 
                            t.join() # Warten, bis alle Modelle dieses Szenario beantwortet haben
                            
                    except Exception as e:
                        print(f"[FEHLER] beim Streamen von Szenario-Zeile {index+1}: {e}")
                        
                print("\n[SYSTEM]: Alle gestreamten Szenarien wurden erfolgreich von OpenRouter beantwortet!")
                print("[HINWEIS]: Die Antworten liegen flüchtig im RAM. Nutze 'export', um sie dauerhaft zu speichern.")

            # FALL B) Normaler manueller Prompt-Modus
            else:
                if not current_prompt: 
                    print("[FEHLER]: Kein Prompt und keine Stream-Daten hinterlegt! Nutze: prompt <Inhalt> oder stream"); 
                    continue
                
                print(f"\n[START]: Sende Standard-Prompt.")
                session_results = [] 
                current_trace_id = uuid.uuid4().hex
                threads = []
                for model in current_models:
                    t = threading.Thread(target=headless_model_request, args=(model, current_prompt, current_pdf, current_trace_id, current_engine))
                    t.start()
                    threads.append(t)
                for t in threads: t.join()
                print("[SYSTEM]: KI-Antwort für Standard-Prompt erfolgreich verarbeitet!")

        elif base_cmd == "export":
            if not session_results: 
                print("[FEHLER]: Keine Daten zum Exportieren im Arbeitsspeicher vorhanden. Bitte erst 'run' ausführen.")
                continue
            
            # Wunschformat auswerten (Standard: jsonl)
            export_format = cmd_arg.lower().strip() if cmd_arg else "jsonl"
            if export_format not in ["json", "jsonl"]:
                print(f"[HINWEIS]: Ungültiges Format '{export_format}'. Nutze Standard: jsonl")
                export_format = "jsonl"
                
            print(f"\n[WORKFLOW]: Starte Szenarien-Export mit tiefer JSON-Struktur-Extraktion ({export_format.upper()})...")
            current_date = datetime.now().strftime('%y-%m-%d')
            
            # Ergebnisse nach Modell gruppieren
            scenarios_by_model = {}
            for res in session_results:
                model_name = res["model"].split('/')[-1].replace('.', '-')
                if model_name not in scenarios_by_model:
                    scenarios_by_model[model_name] = []
                scenarios_by_model[model_name].append(res)
                
            for model_name, results in scenarios_by_model.items():
                prefix = args.prefix if 'args' in locals() and args.prefix else "PIPELINE"
                filename = f"{prefix}_complete-benchmark_{model_name}_{current_date}.{export_format}"
                
                print(f"[EXPORT]: Extrahiere JSON-Strukturen für Modell '{model_name}'...")
                json_array_data = []
                
                try:
                    for idx, res in enumerate(results):
                        raw_ki_content = res["content"]
                        
                        # Schritt A: Markdown-Blöcke wegschneiden
                        clean_raw = re.sub(r"```jsonl?|\n?```", "", raw_ki_content).strip()
                        
                        # Schritt B: Finde die ALLERERSTE öffnende Klammer '{' und die ALLERLETZTE schließende Klammer '}'
                        # Das garantiert, dass auch tief verschachtelte JSONs komplett erfasst werden!
                        start_idx = clean_raw.find('{')
                        end_idx = clean_raw.rfind('}')
                        
                        obj_extracted = None
                        
                        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                            potential_json = clean_raw[start_idx:end_idx+1]
                            try:
                                # Versuche das von der KI generierte JSON-Objekt direkt zu parsen
                                obj_extracted = json.loads(potential_json)
                            except Exception:
                                obj_extracted = None

                        # Schritt C: Strukturierung der Ausgabe
                        if isinstance(obj_extracted, dict):
                            # Wenn das extrahierte Objekt bereits ein 'id'-Feld hat, behalten wir es oder überschreiben es sauber
                            if "id" not in obj_extracted:
                                obj_extracted["id"] = f"{prefix}_{model_name}_{idx+1:03d}"
                            
                            json_array_data.append(obj_extracted)
                        else:
                            # Sicheres Fallback NUR, wenn absolut kein JSON extrahiert werden konnte
                            fallback_obj = {
                                "id": f"{prefix}_{model_name}_{idx+1:03d}",
                                "raw_error_content": raw_ki_content
                            }
                            json_array_data.append(fallback_obj)
                    
                    # --- SCHREIBEN DER EXTRAHIERTEN STRUKTUR ---
                    with open(filename, "w", encoding="utf-8") as f:
                        if export_format == "jsonl":
                            for item in json_array_data:
                                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                        else:
                            json.dump(json_array_data, f, indent=4, ensure_ascii=False)
                            
                    print(f"[SUCCESS]: JSON-Struktur extrahiert und gespeichert in -> {filename}")
                    
                except Exception as file_err:
                    print(f"[FEHLER]: Konnte Datei {filename} nicht schreiben: {file_err}")

        elif base_cmd == "raw":
            if not session_results: print("[FEHLER]: Keine Rohdaten vorhanden. Bitte erst 'run' ausführen."); continue
            headless_save_raw_json()

        elif base_cmd == "tracing":
            if not session_results: print("[FEHLER]: Keine Tracing-Daten vorhanden."); continue
            headless_export_tracing()
            
        else:
            print(f"[FEHLER]: Unbekannter Befehl '{base_cmd}'.")

# =================================================================
# --- REINER PROGRAMM-STARTPUNKT (MAIN-BLOCK) ---
# =================================================================
if __name__ == "__main__":
    HELP_TEXT = """
┌──────────────────────────────────────────────────────────────────────────────────┐
│  PflegeBench — Pipeline & Interaktive CLI Commands                               │
├──────────────────────────────────────────────────────────────────────────────────┤
│  START-ARGUMENTE (Beim Aufruf von python benchmark.py ...):                      │
│  --cli                     Aktiviert direkt den interaktiven Terminal-Modus      │
│  --prompt <pfad/text>      Dateipfad (.txt) ODER direkter Prompt-Text            │
│  --models <id1,id2>        Kommagetrennte OpenRouter-Modelle                     │
│  --prefix <name>           Präfix für Szenarien-IDs (Standard: PIPELINE)         │
│  --format <json/jsonl>     Ausgabeformat für Szenarien (Standard: jsonl)         │
│  --pdf <url>               Optionale URL zu einem PDF-Dokument                   │
│  --engine cloudflare-ai    Nutzt die standardmäßige Cloudflare-AI Engine         │
│  --engine mistral-ocr      Nutzt die hochpräzise Mistral-OCR Engine              │
│  --engine native           Nutzt die native OpenRouter-Engine (Direktübergabe)   │
│  -h, --help                Zeigt diese Hilfeübersicht an                         │
├──────────────────────────────────────────────────────────────────────────────────┤
│  INTERAKTIVE BEFEHLE (Innerhalb der "PflegeBench>" Konsole):                     │
│  help                      Zeigt diese Übersicht an                              │
│  prepare [pfad]            Säubert Validierungsdaten auf Festplatte              │
│                            (Nutzt Default-Pfad, falls kein Pfad angegeben wird)  │
│  stream [pfad]             Lädt bereinigte Daten unbestechlich in den RAM        │
|                            (Nutzt Default-Pfad, falls kein Pfad angegeben wird)  |
│  prompt <text/pfad>        Überschreibt oder setzt den aktuellen System-Prompt   │
│  models <id1,id2>          Setzt ein oder mehrere Modelle (kommagetrennt)        │
│  run                       Startet Abfrage (In-Memory Stream ODER Einzelprompt)  │
│  export [json/jsonl]       Extrahiert tiefe JSON-Strukturen aus dem RAM-Ergebnis │
│  raw                       Exportiert die unstrukturierten KI-Antworten (JSON)   │
│  tracing                   Exportiert das Langfuse-Tracing-Protokoll (JSON)      │
│  reset                     Verwirft RAM-Stream & Sitzungsdaten für Neustart      │
│  done                      Beendet das Programm vollständig                      │
├──────────────────────────────────────────────────────────────────────────────────┤
│  HINWEISE ZUM STREAMING-WORKFLOW:                                                │
│  1. Nutze 'prepare' und danach 'stream', um Testdaten in den RAM zu laden.       │
│  2. 'run' erkennt den RAM-Stream automatisch und schaltet auf HTTP-Streaming.    │
│  3. Erst durch 'export' wird die finale Gesamtdatei auf Festplatte erzeugt.      │
│  4. Wird das Skript ohne Argumente gestartet, öffnet sich die Desktop-GUI.       │
└──────────────────────────────────────────────────────────────────────────────────┘
"""

    parser = argparse.ArgumentParser(description="PflegeBench Pipeline & GUI", add_help=False)
    # NEU: Das saubere CLI-Flag (action="store_true" bedeutet: Ein/Aus-Schalter)
    parser.add_argument("--cli", action="store_true", help="Startet direkt den Terminal-Modus")
    parser.add_argument("--prompt", type=str)
    parser.add_argument("--models", type=str)
    parser.add_argument("--prefix", type=str, default="PIPELINE")
    parser.add_argument("--format", type=str, choices=["json", "jsonl"], default="jsonl")
    parser.add_argument("--pdf", type=str, default="")
    parser.add_argument("--engine", type=str, choices=["cloudflare-ai", "mistral-ocr", "native"], default="cloudflare-ai")
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    if args.help:
        print(HELP_TEXT)
        sys.exit(0)

    # DIE NEUE, SAUBERE WEICHE:
    # Wenn entweder das neue --cli Flag gesetzt ist ODER Pipeline-Parameter übergeben wurden,
    # starten wir direkt das Headless Terminal. Nur wenn alles leer ist, kommt die GUI.
    if args.cli or args.prompt or args.models or args.pdf:
        run_pipeline_mode(args)
    else:
        app = BenchmarkApp()
        app.mainloop()