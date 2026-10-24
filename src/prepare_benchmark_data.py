import os
import sys
import argparse
import json
from pathlib import Path

def sanitize_benchmark_item(item):
    """
    Bereinigt ein Benchmark-Szenario basierend auf zwei Konfigurationslisten:
    1. Komplett löschen (Struktur + Inhalt weg)
    2. Inhalt leeren (Struktur bleibt als leerer String erhalten)
    """
    # Liste A: Diese Felder werden KOMPLETT aus dem JSON gelöscht
    fields_to_remove = [
        "point_scale_id",
        "point_value",
        "_validation",
        "point_scale_options",
        "model",
        "model_version",
        "temperature"
    ]
    
    # Liste B: Diese Felder bleiben im JSON, aber ihr INHALT wird auf "" gesetzt
    fields_to_clear = [
        "answer_idx",
        "rationale_id"
    ]
    
    # Kopie erstellen, um das Originalobjekt nicht direkt zu verändern
    sanitized_item = item.copy()
    
    # 1. Felder aus der Löschliste komplett entfernen
    for field in fields_to_remove:
        if field in sanitized_item:
            del sanitized_item[field]
            
    # 2. Inhalt der Felder aus der Clear-Liste leeren (Struktur bleibt)
    for field in fields_to_clear:
        if field in sanitized_item:
            sanitized_item[field] = ""
            
    return sanitized_item

def prepare_data(input_path, output_path):
    input_base = Path(input_path).resolve()
    output_base = Path(output_path).resolve()
    
    # KORRIGIERTE LOGIK: Prüfen, ob der Input eine Datei oder ein Ordner ist
    if input_base.is_file():
        # Wenn es eine Datei ist, packen wir sie als einziges Element in unsere Liste
        all_files = [input_base]
        # Für den relativen Pfad nehmen wir den übergeordneten Ordner als Basis
        search_base = input_base.parent
        print(f"\n[SYSTEM]: Einzelne Datei als Input erkannt.")
    else:
        # Wenn es ein Ordner ist, suchen wir wie gewohnt nach allen JSONs
        all_files = list(input_base.rglob("*.json"))
        search_base = input_base
        print(f"\n[SYSTEM]: Ordner als Input erkannt. Starte Datensuche in: {input_base}")
    
    if not all_files:
        print(f"\n[⚠️ WARNUNG]: Keine .json Dateien gefunden!")
        return

    print(f"[START]: {len(all_files)} Datei(en) wird/werden bereinigt...\n")
    
    for json_file in all_files:
        # Nutzt die dynamische search_base für die korrekte Strukturierung im Zielordner
        relative_path = json_file.relative_to(search_base)
        target_file_path = output_base / relative_path
        
        print(f"[PROZESS]: Verarbeite Datei: {json_file.name}")
        
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, list):
                sanitized_data = []
                for item in data:
                    validation_state = item.get("_validation", {}).get("status", "validated")
                    if validation_state == "rejected":
                        continue
                    sanitized_item = sanitize_benchmark_item(item)
                    sanitized_data.append(sanitized_item)
            else:
                sanitized_data = sanitize_benchmark_item(data)
                
            target_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_file_path, "w", encoding="utf-8") as f:
                json.dump(sanitized_data, f, indent=4, ensure_ascii=False)
                
            print(f"  ➔ ERFOLG: Gespeichert unter: {target_file_path}")
            
        except Exception as e:
            print(f"  ➔ [FEHLER] beim Verarbeiten von {json_file.name}: {e}")

    print(f"\n[SYSTEM]: Verarbeitung erfolgreich abgeschlossen!")

if __name__ == "__main__":
    HELP_TEXT = """
┌────────────────────────────────────────────────────────────────────────────────┐
│  PflegeBench — Data Preparation Tool                                           │
├────────────────────────────────────────────────────────────────────────────────┤
│  PROJEKT-ERKLÄRUNG:                                                            │
│  Bereitet validierte Experten-Daten für den unvoreingenommenen KI-Testlauf vor.│
│  Entfernt alle Lösungen (answer_idx), Punktwerte und logische Hinweise.        │
├────────────────────────────────────────────────────────────────────────────────┤
│  REQUIRED PARAMETERS (Müssen beim Aufruf übergeben werden):                    │
│  --input_path <pfad>       Pfad zur validierten .json ODER dem gesamten Ordner │
│  --output_path <pfad>      Zielordner für die bereinigten Benchmark-Dateien    │
├────────────────────────────────────────────────────────────────────────────────┤
│  SYSTEM-COMMANDS:                                                              │
│  -h, --help                Zeigt diese Übersichtstabelle an                    │
├────────────────────────────────────────────────────────────────────────────────┤
│  BEISPIEL-AUFRUF:                                                              │
│  python src/prepare_benchmark_data.py \\                                       │
│     --input_path "./data/benchmark/validated" \\                               │
│     --output_path "./data/benchmark/prepared_benchmarks"                       │
└────────────────────────────────────────────────────────────────────────────────┘
"""

    parser = argparse.ArgumentParser(description="PflegeBench Data Prep", add_help=False)
    parser.add_argument("--input_path", type=str)
    parser.add_argument("--output_path", type=str)
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    if args.help:
        print(HELP_TEXT)
        sys.exit(0)

    if not args.input_path or not args.output_path:
        print(HELP_TEXT)
        print("[FEHLER]: Bitte gib sowohl --input_path als auch --output_path an!")
        sys.exit(1)

    if not os.path.exists(args.input_path):
        print(f"[FEHLER]: Der angegebene Quellpfad '{args.input_path}' existiert nicht!")
        sys.exit(1)
        
    prepare_data(args.input_path, args.output_path)