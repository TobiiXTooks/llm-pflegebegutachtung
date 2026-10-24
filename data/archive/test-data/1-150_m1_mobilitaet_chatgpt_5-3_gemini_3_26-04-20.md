# Erzeugung von Szenarien für Benchmark
bei der Erzeugung von Szenarien werden folgende Punkte berücksichtigt:
1. **Eindeutige regelbasierte Grundlage**
    - Die Szenarien basieren auf offiziellen Richtlinien. hier(Richtlinien des Medizinischen Dienstes Bund zur Feststellung der Pflegebedürftigkeit nach dem XI. Buch des Sozialgesetzbuches)
    - Vermeidung von Grauzonen (ein deutige Einordnung)
2. **Herausforderung einbauen**
    - Initial-Aussage (Unvollständige Aussagen)
    - Notwendigkeit auf Rückfragen
3. **Definierte Schlüsselkriterien für die Bewertung**
4. **Trennung von Hilfsmitteln und personeller Hilfe** Fokus auf personelle Hilfe

---
# Prompt
Du bist ein erfahrener Pflegegutachter. Dein Aufgabe ist Szenarien für Benchmark von LLM zuerstellen. Beachte folgendes:
 1. Eindeutige Regelbasierte Szenarien aus beigefügten Begutachtungsrichtlinien Datien 
 2. Herausforderung einbauen 
 3. Definierte die Schlüsselkriterien für die Bewertung. 
Bilde die Beispiel analog zu meinem Szenarien in beigefügten Datien. achte darauf, dass du andere Herausforderung bilden zu meinen Beispielen aber die Regel halte sie fest und gib sie in anderen Ausdruck. Zum Beispiel Art den Hilfamitteln statt Gehestück Rollator. 
Meine Beispiel sind aus dem Modul 1 (Mobilität). Bilde zu jedem Beispiel 5 analoge Beispiele. ändere die id zu M1-AI-[nummer] damit ich weiß, welche durch LLM erzeugt ist. Schreib deine Szenarien in jsonl-Format

## Gemini:
**Antwort:**

Als erfahrener Pflegegutachter habe ich die Begutachtungsrichtlinien (BRi) analysiert, um hochwertige Benchmark-Szenarien für LLMs zu erstellen. In der Pflegebegutachtung ist die zentrale Regel für Modul 1 (Mobilität), dass nur die motorischen Aspekte (Kraft, Balance, Koordination) und die benötigte personelle Hilfe zählen. Hilfsmittel, Schmerzen oder eine langsame Ausführung führen nicht zu einer Abwertung der Selbständigkeit, solange keine Person physisch eingreifen oder beaufsichtigen muss.

Hier sind jeweils drei analoge Beispiele zu deinen Szenarien, die gezielte Herausforderungen (z. B. Zeitaufwand, irrelevante Umgebungsfaktoren oder Ablenkungen) einbauen: $siehe m1_mobilitaet.jsonl$

Schlüsselkriterien für die Bewertung:Personenneutralität: Hilfsmittel (Rollator, Geländer, Strickleiter) werden wie die eigene Körperkraft gewertet.Hypothetische Durchführung: Die Fähigkeit wird auch bewertet, wenn die Umgebung (z. B. keine Treppen) sie aktuell nicht erfordert.Abgrenzung zu Modul 6: Hilfe bei der Haushaltsführung (Taschen tragen) oder Planung (Termine) beeinflusst die motorische Mobilität in Modul 1 nicht.Sicherheitsaspekt: Bloße Anwesenheit zur Abwendung von Gefahren (ohne physische Hilfe) führt bereits zur Einstufung "überwiegend selbständig".

Wegen Rechenkapazität des Modell wird jedes Mal 25 Beispiele erzeugt daher wird das Modell immer gefordert weitere 25 Beispiele. 

## ChatGPT
Hier sind LLM-generierte Benchmark-Szenarien für Modul 1 (Mobilität) basierend auf den Begutachtungsrichtlinien.
Ich habe:

Regelbindung strikt eingehalten (nur motorische Aspekte, keine kognitiven Einflüsse )
Bewertungslogik (0–3 Punkte) integriert
Herausforderungen eingebaut (Hilfsmittel, Grenzfälle, Teilselbständigkeit)
Schlüsselkriterien explizit definiert
jeweils 3 analoge Varianten pro Szenariotyp erzeugt
neue IDs: M1-AI-* 
$siehe m1_mobilitaet.jsonl$

---

Die generiete Benschmark-Daten durch Gemini ist Umfangreicher und bildet komplexe Herausförderungen als GhatGpt daher wir die Daten mit Gemini generiet.

Für jede Abstufung der fünf Kriterien in Modul 1 wird ein Beispiel erstellt. Analog zu diesen Szenarien wird mit Gemini weitere Szenarien erzeugt.

---
## Modul 1
### Szenario 1
| Komponente | Beschreibung |
| ---------- | ------------ |
| Modul / Frage | Modul 1: Mobilität - Positionswechsel im Bett  |
| Patienten-Beschreibung | Nach Bandscheibe-OP kann der Patient sein Postion wechsel, in dem er auf den Bettseitenteil schtütz. Wenn jemand in sein Zimmer Abwiesend, hilft der Petient in der sache an |
| Initial-Aussage (Vage) | 3 Monate nach der Operation kann ich mein Position im Bett wechseln, denoch leide ich unter Schmerzen. Wenn jemand mir in dieser Sache hilft, ist die Bewegung leichter |
| Die „Falle“ (Challenge) | Das Modell muss heraußfinden, dass ob die Zeitraum und Schmerzen keine Rolle für die Einordnung spielen, und die Bewegung im Bett ohne hilfe möglich ist |
| Korrekte Einstufung | selbstständigkeit |

Evaluation der Argumentationsqualität
- Kriterium 1: Das Model muss nachfragen, ob die Bewegung ohne hilfe möglich ist
- Kriterium 2: Das Model muss erkenn das die Schmerzen und Zeit nach Operation für die Bewertung nicht wichtig. sobald die Bewegung ohne hilfe möglich ist.

### Szenario 2
| Komponente | Beschreibung |
| ---------- | ------------ |
| Modul / Frage | Modul 1: Mobilität - Halten einer stabilen Sitzposition|
| Patienten-Beschreibung | Der Patient kann auf dauer sein Sitzposition stabiel halten aber bei Position wechsel, schützt er sich auf in der nähe stehende Gegenstände |
| Initial-Aussage (Vage) | ich kann meine Sitzposition ändern aber leide ich von Schmerzen|
| Die „Falle“ (Challenge) | um richtig zu Bewerten muss das Modell heraußfinden, ob der Patient sein setzt Position für lange Zeit die Sitzposition halten kann |
| Korrekte Einstufung | selbstständigkeit |

Evaluation der Argumentationsqualität
- Kriterium 1: Das Modell muss nachfragen, ob der Patient seine Sitzpostion für lange Zeit halten kann.
- Kriterium 2: Dannach muss das Modell fragen ob er hilfe braucht. (denn es kann sein, das der Patient auf Kriterium 1 mit nein Antworten, aber braucht er kein Hilfe. Kriterium 1 allein ist nicht ausreichend für Bewertung)

### Szenario 3
| Komponente | Beschreibung |
| ---------- | ------------ |
| Modul / Frage | Modul 1: Mobilität - Umsetzen |
| Patienten-Beschreibung | Der Patient kann von übliche Sitzhöhe etwa 45 cm ohne Hilfe aufstehen aber er stützte sich auf eine Krücke. manschmal bietet der Enkel Hilfe auch|
| Initial-Aussage (Vage) | beim Aufstehen vom Boden benötig ich hilfe. |
| Die „Falle“ (Challenge) | Das Modell muss heraußfinden ob beim Aufstehen vom üblichen Höhe (45 cm) auch hilfe braucht und ob es geht mit Hilfsmittel |
| Korrekte Einstufung | selbstständigkeit |

Evaluation der Argumentationsqualität
- Kriterium 1: das Modell muss klären, ob beim Aufstehen von 45 cm Höhe hilfe benötigt.
- Kriterium 2: Das Modell muss erkennen, ob die Aufstehen von diese Höhe durch Hilfsmittel allein möglich

### Szenario 4
| Komponente | Beschreibung |
| ---------- | ------------ |
| Modul / Frage | Modul 1: Mobilität - Fortbewegen innerhalb des Wohnbereichs |
| Patienten-Beschreibung | Der Patient leidet unter Gleichgewichtsstörungen. Innerhalb der Wohnung nutzt er einen Rollator, mit dem er sicher von Zimmer zu Zimmer kommt. Seine Tochter ist jedoch oft besorgt und hält ihn zusätzlich am Unterarm, wenn sie zu Besuch ist. |
| Initial-Aussage (Vage) | Ich bewege mich in der Wohnung mit meinem Rollator. Wenn meine Tochter da ist, stützt sie mich aber immer, damit ich nicht umkippe. |
| Die „Falle“ (Challenge) | Das KI muss erkennen, ob die Hilfe der Tochter notwendig ist (weil der Rollator allein nicht reicht) oder ob es sich um eine reine Vorsichtsmaßnahme handelt. |
| Korrekte Einstufung | selbstständigkeit |

Evaluation der Argumentationsqualität
- Kriterium 1: Das Modell muss nachfragen, ob der Patient die Fortbewegung auch dann sicher bewältigt, wenn die Tochter nicht anwesend ist.
- Kriterium 2: Das Modell muss korrekt interpretieren, dass die Nutzung des Rollators die Selbstständigkeit nicht mindert

### Szenario 5
| Komponente | Beschreibung |
| ---------- | ------------ |
| Modul / Frage | Modul 1: Mobilität - Treppensteigen |
| Patienten-Beschreibung | Der Patient kann die Treppen zwischen zwei Etagen komplett alein über wenden aber er nutzt ein Gehstuck. Erkann die Treppe leichter Überwenden wenn jemand ihm Hilfe bietet |
| Initial-Aussage (Vage) | beim Treppensteigen nutzte ich ein Gehstück. Wenn jemand mir hilfe bietet kann ich die Trappe schneller Steigen|
| Die „Falle“ (Challenge) | Das Modell muss ermitteln, der Patient zwei Etagen Treppe ohne hilfe steigen kann und das Hilfsmittel und wie schnell beim hilfe steigen kann, keine einschränkung für Selbstständigkeit ist |
| Korrekte Einstufung | selbstständig |

Evaluation der Argumentationsqualität
- Kriterium 1: Das Modell muss Fragen ob er dabei hilfe braucht
- Kriterium 2: Das Modell muss Fragen nach Treppenlänge

### Szenario 6
| Komponente | Beschreibung |
| ---------- | ------------ |
| Modul / Frage |   |
| Patienten-Beschreibung |  |
| Initial-Aussage (Vage) | |
| Die „Falle“ (Challenge) |  |
| Korrekte Einstufung |  |
Evaluation der Argumentationsqualität
Kriterium 1: 
Kriterium 2: 