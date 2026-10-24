import os
import sys
import argparse
import json
from pathlib import Path

def load_and_prepare_stream(input_path):
    """
    Lädt JSON-Dateien, sortiert die Szenarien reproduzierbar nach ID
    und konvertiert sie im RAM in das JSON-Lines (JSONL) Format.
    """
    input_base = Path(input_path).resolve()
    all_scenarios = []

    # 1. Daten einlesen (Unterstützt Datei oder Ordner)
    if input_base.is_file():
        files_to_read = [input_base]
    elif input_base.is_dir():
        files_to_read = list(input_base.rglob("*.json"))
    else:
        print(f"[FEHLER]: Pfad existiert nicht: {input_base}")
        return []

    for file_path in files_to_read:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_scenarios.extend(data)
                elif isinstance(data, dict):
                    all_scenarios.append(data)
        except Exception as e:
            print(f"[WARNUNG] Konnte {file_path.name} nicht lesen: {e}")

    if not all_scenarios:
        print("[⚠️ WARNUNG]: Keine Szenarien zum Streamen gefunden.")
        return []

    # 2. STRIKTE SORTIERUNG (Sorgt für die reproduzierbare Reihenfolge)
    # Wir sortieren nach der 'id' des Szenarios (z.B. 16_claude_002, 16_claude_003)
    all_scenarios.sort(key=lambda x: x.get("id", ""))
    print(f"[STREAMER]: {len(all_scenarios)} Szenarien erfolgreich geladen und nach ID sortiert.")

    # 3. IN-MEMORY CONVERSION TO JSONL (Kein Speichern auf Festplatte!)
    # Wir erstellen eine Liste von validen JSON-Strings, wobei jedes Element eine Zeile darstellt
    jsonl_stream = [json.dumps(scen, ensure_ascii=False) for scen in all_scenarios]
    
    return jsonl_stream

if __name__ == "__main__":
    HELP_TEXT = """
┌────────────────────────────────────────────────────────────────────────────────┐
│  PflegeBench — HTTP Streaming Data Loader (Ticket #66)                         │
├────────────────────────────────────────────────────────────────────────────────┤
│  PROJEKT-ERKLÄRUNG:                                                            │
│  Lädt bereinigte Daten, sortiert sie strikt nach ID für Reproduzierbarkeit    │
│  und stellt sie als In-Memory JSONL-Stream für OpenRouter bereit.              │
├────────────────────────────────────────────────────────────────────────────────┤
│  PARAMETERS:                                                                   │
│  --input_path <pfad>       Standard: ./ai-project/data/benchmark/prepared_benchmarks
├────────────────────────────────────────────────────────────────────────────────┤
│  SYSTEM-COMMANDS:                                                              │
│  -h, --help                Zeigt diese Übersichtstabelle an                    │
└────────────────────────────────────────────────────────────────────────────────┘
"""

    parser = argparse.ArgumentParser(description="PflegeBench Streamer", add_help=False)
    parser.add_argument(
        "--input_path", 
        type=str, 
        default="./ai-project/data/benchmark/prepared_benchmarks"
    )
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args()

    if args.help:
        print(HELP_TEXT)
        sys.exit(0)

    print("[TESTLAUF]: Starte den Streamer im Standalone-Modus...")
    stream = load_and_prepare_stream(args.input_path)
    
    if stream:
        print("\n[VORSCHAU des In-Memory JSONL-Streams (Erste 2 Zeilen)]:")
        for i, line in enumerate(stream[:2]):
            print(f"Zeile {i+1}: {line[:120]}...")
        print("\n[ERFOLG]: Daten stehen bereit für das HTTP-Streaming via benchmark.py!")