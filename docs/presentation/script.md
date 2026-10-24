# Präsentationsablauf – PflegeBench

## 1. Einstieg

**Präsentiert von:** Tobias

- Projekttitel nennen: PflegeBench
- Kurz erklären, worum es im Projekt geht
- Ziel der Präsentation nennen:
  - Workflow zeigen
  - konkrete Ergebnisse zeigen
  - Tool-Ausgaben nachvollziehbar darstellen

---

## 2. Ausgangslage / Problem

**Präsentiert von:** Tobias

- KI-Antworten im Pflegekontext müssen überprüfbar sein
- Einzelne Modellantworten reichen nicht aus
- Es braucht:
  - strukturierte Datengrundlage
  - menschliche Prüfung
  - Vergleichbarkeit
  - nachvollziehbare Ergebnisdokumentation

---

## 3. Ziel des Projekts

**Präsentiert von:** Tobias

- Aufbau eines wiederholbaren Workflows
- Vergleich von Modellantworten mit validierten Referenzen
- Erzeugung von Reports, Fehlerdateien und Dashboard
- Vorbereitung einer abgabefähigen Ergebnisdokumentation

---

## 4. Gesamtworkflow zeigen

**Präsentiert von:** Tobias

Ablauf:

1. Projektumgebung prüfen
2. Modellantworten erzeugen
3. Antworten prüfen und validieren
4. Ergebnisse vergleichen
5. Reports und Fehlerdateien erzeugen
6. Dashboard erstellen
7. Ergebnisdokumentation abgeben

---

## 5. Projektumgebung und Basisbefehle

**Präsentiert von:** Tobias

Tools kurz zeigen:

- `python -m pflegebench overview`
- `python -m pflegebench doctor`
- `python -m pflegebench check`

Ergebnis zeigen:

- installierte Umgebung
- erkannte Projektpfade
- vorhandene Pakete
- erfolgreiche Projektprüfung

---

## 6. Toolgruppe: Antwortgenerierung

**Präsentiert von:** Alaa

Tools kurz im Detail zeigen:

- `python -m pflegebench gui-benchmark`
- `python -m pflegebench trace --model <openrouter-model-id>`
- `python -m pflegebench trace-smoke`

Zuordnung:

| Tool | Zweck | Ergebnis |
|---|---|---|
| `gui-benchmark` | Modellantworten erzeugen | Dateien in `to_validate` |
| `trace` | Modelllauf nachvollziehbar machen | getrackte Modellinteraktion |
| `trace-smoke` | Modellanbindung testen | Funktionsprüfung der API |

---

## 7. Toolgruppe: Prüfung und Validierung

**Präsentiert von:** Marius

Tools kurz im Detail zeigen:

- `python -m pflegebench gui-editor`

Zuordnung:

| Tool | Zweck | Ergebnis |
|---|---|---|
| `gui-editor` | JSON/JSONL-Dateien bearbeiten | korrigierte Dateien |

---

## 8. Konkrete Ergebnisdokumentation zeigen

**Präsentiert von:** Tobias

Zeigen:

- HTML-Ergebnisdokumentation
- konkrete Vergleichsergebnisse
- erzeugte Reports
- Fehlerbeispiele
- Dashboard-Ausgabe
- Befehle zu den jeweiligen Ergebnissen

Fokus:

- keine theoretische Demo
- reale Ausgaben aus dem Projekt
- abgabefähige Darstellung

---

## 9. Ergebnisinterpretation

**Präsentiert von:** Tobias

- Vergleich der Modellleistungen
- Einordnung der Ergebniswerte
- Auffälligkeiten aus Fehlerbeispielen
- Nutzen der Reports und CSV-Dateien
- Bedeutung des Dashboards für die Auswertung

---

## 10. Nutzen des Projekts

**Präsentiert von:** Tobias

Kernaussagen:

- strukturierter Workflow
- wiederholbare Auswertung
- Vergleichbarkeit zwischen Modellen
- menschliche Validierung eingebunden
- automatische Ergebnisaufbereitung
- abgabefähige Dokumentation

---
