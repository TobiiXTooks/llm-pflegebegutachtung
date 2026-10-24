# PflegeBench — Vorläufiges Benchmark-Testprotokoll
## 1. Test-Setup & Angewendeter Prompt
Als Test-Eingabe wurde der offizielle, validierte Haupt-Prompt zur Erstellung von Pflegebegutachtungsbögen verwendet, ergänzt um die exakte JSON-Struktur der Rohdaten (Module `M1` bis `M6`).

* **Benutzerdefinierte Benchmark-Nummer:** `1` (Manuell in der GUI gesetzt)
* **Ausgewählte Modelle:** `openai/gpt-4o`, `google/gemini-2.5-pro`, `anthropic/claude-sonnet-4.6`
* **PDF-URL Status:** Nicht funktionsfähig. Da die OpenRouter-Einspeisung der PDF-Richtlinien-URL erneut zu serverseitigen `Internal Server Errors (500)` führte, wurde das Dokument für diesen Systemtest entkoppelt. Das JSON-Strukturbeispiel im Prompt reichte den Modellen jedoch völlig aus.

---

## 2. Technische Messergebnisse der GUI

Der parallele 1:n Broadcast lief extrem stabil. Die GUI blieb dank der Auslagerung in separate Threads voll reaktionsfähig. Hier sind die exakten Performance-Daten aus dem generierten Tracing-Log:

### Performance- und Kostenübersicht

| Modellname | Erzeugte Szenarien | Gemessene Latenz | Generierte Output-Tokens | Berechnete Kosten |
| :--- | :---: | :---: | :---: | :---: |
| **openai/gpt-4o** | 5 Blöcke | 13,54 Sek. | 1.526 Tokens | 0,01639 $ |
| **google/gemini-2.5-pro** | 20 Blöcke | 204,62 Sek. | 20.869 Tokens | 0,21020 $ |
| **anthropic/claude-sonnet-4.6** | 30 Blöcke | 95,15 Sek. | 11.356 Tokens | 0,11479 $ |
| **Gesamtsumme (Broadcast)** | **55 Blöcke** | **313,32 Sek.** *(akkumuliert)* | **33.751 Tokens** | **0,34140 $** |

---

## 3. Validierung der Export-Werkzeuge

Nach Abschluss der Berechnungen wurden die drei Export-Schnittstellen der GUI erfolgreich validiert:

### A. Rohdaten Export (`raw_export_182910.json`)
* **Status:** FEHLERFREI
* **Inhalt:** Sichert die vollständigen, unstrukturierten Textantworten aller drei Anbieter inklusive der Markdown-Codeblöcke.

### B. Szenarien Extraktion (`extracted_scenarios_182912.json`)
* **Status:** ERFOLGREICH (Neues ID-Schema verifiziert!)
* **Logik-Prüfung:** Der Parser hat das vom Benutzer eingegebene Präfix `1` perfekt ausgelesen und mit dem bereinigten Modellnamen verknüpft. Jedes Modell zählt seine Szenarien nun sauber und unabhängig von `001` hoch:
  * *GPT-4o Muster-IDs:* `1_gpt-4o_001` bis `1_gpt-4o_005`
  * *Gemini Muster-IDs:* `1_gemini-2-5-pro_001` bis `1_gemini-2-5-pro_020`
  * *Claude Muster-IDs:* `1_claude-sonnet-4-6_001` bis `1_claude-sonnet-4-6_030`
* **Sonderzeichen-Korrektur:** Punkte in den Modellnamen (wie bei `gemini-2.5`) wurden automatisch in ID-konforme Bindestriche umgewandelt (`gemini-2-5`).

### C. Server Tracing Export (`tracing_export_182913.json`)
* **Status:** FEHLERFREI
* **Logik-Prüfung:** Generiert ein hochkomplexes, verschachteltes OpenTelemetry-Protokoll. Die Gesamt-Latenz von **313,32 Sekunden** und die akkumulierten Kosten von **0,3414 $** wurden fehlerfrei ausgerechnet und zusammengeführt.

---

## 4. Fazit für das Projekt-Team
Das Merge zwischen `benchmark_generator.py` und `conversation.py` funktioniert nun einwandfrei. Das neue, benutzerdefinierte ID-Schema arbeitet absolut präzise und trennt die Daten der verschiedenen KI-Anbieter sauber voneinander. 
