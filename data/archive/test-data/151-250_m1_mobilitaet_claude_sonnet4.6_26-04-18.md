Du bist ein Experte für Benchmark-Design und Datensatzerstellung für Large Language Models (LLMs), insbesondere im Bereich Pflegebegutachtung.

Aufgabe:
Erstelle einen hochwertigen Benchmark-Datensatz im JSONL-Format und JSON-FORMAT, der verwendet werden kann, um ein LLM systematisch zu evaluieren.
Beziehe dich hierfür zunächst nur auf das Modul "Mobilität"

Ziel:
Der Benchmark soll:

realistische, praxisnahe Fälle enthalten

klare, überprüfbare Antworten haben

für quantitative Auswertung geeignet sein

den Begutachtungsrichtlinien entsprechen

Kontext:
Der Benchmark wird für ein Forschungsprojekt verwendet (Paper).
Er dient dazu, ein LLM vor und nach Finetuning zu vergleichen.
Struktur pro Datenpunkt:
Jeder Eintrag soll folgende Felder enthalten (als Beispiel orientiere dich daran):

  "id": "M1_012",
  "case_id": "CASE_004",
  "module": "M1",
  "criterion": "treppensteigen",
  "scale_type": "selbststaendigkeit",
  "stem": "Der Versicherte schafft wenige Stufen allein, über eine Etage muss er gestützt werden.",
  "options": ["selbständig","überwiegend selbständig","überwiegend unselbständig","unselbständig"],
  "answer_idx": 2,
  "rationale": "F4.1.5: nur mit Stütze möglich = überwiegend unselbständig",
  "tags": ["pflegegutachten","mobilität","treppensteigen"],
  "difficulty": "mittel",
  "source": "pflegegutachten_poc_v0_1",
  "lang": "de"
  "split": "test"0

Wichtige Anforderungen:
- Keine Mehrdeutigkeiten in den Antworten
- Antwort muss eindeutig aus dem Text ableitbar sein
- Sprache: Deutsch
- Fachlich korrekt (orientiert an realen Richtlinien)
- Keine unnötigen Ausschmückungen

Erstelle:
- mindestens 10–20 Datenpunkte
- verschiedene Schwierigkeitsgrade
- Mischung aus einfachen und komplexen Fällen

Zusätzliche Anforderungen:
- Variiere die Formulierungen (kein Copy-Paste-Stil)
- Nutze realistische Szenarien (keine künstlichen Beispiele)
- Erweitere deine Datenpunkte auf 100 (id: M1_001 - M1_100). Teile diese auf in 70 Trainingsdaten und 30 Testdaten
- Verzichte auf direkte Wiederholungen von Beispielen

Format:
Gib ausschließlich gültiges JSONL und JSON aus (ein JSON-Objekt pro Zeile, keine Kommentare, keine Erklärungen außerhalb).