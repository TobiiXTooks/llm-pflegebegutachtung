
# Benchmark-Daten Schema

## Naming files

moduleNumber_moduleName_modelName_modelVersion_YY-MM-DD_HH-MM.json
moduleNumber_moduleName_modelName_modelVersion_YY-MM-DD_HH-MM.jsonl
moduleNumber_moduleName_modelName_modelVersion_YY-MM-DD_HH-MM.md (optional answers of the model/ clarifications of the model)

## Prompting

- **Step 1**: Define the AI's ROLE
- **Step 2**: Cleary State the TASK
- **Step 3**: FORCE the OUTPUT FORMAT (JSON bzw. JSONL)
- **Step 4**: SHOW the JSON-SCHEMA
- **Step 5**: Add STRICT RULES

## JSON-Schema Beispiel MODUL 1

```json
{
  "id": "benchmarknumber_modelname_001",
  "module": "M1",
  "criterion": [
    "positionwechsel im bett", 
    "halten einer stabilen sitzposition", 
    "umsetzen", 
    "fortbewegung innerhalb des wohnbereichs", 
    "treppensteigen"
    ],
  "scale_type": "selbststaendigkeit",
  "stem": "Die versicherte Person schafft wenige Stufen allein, über eine Etage muss sie gestützt werden.",
  "options": [
    "selbständig", 
    "überwiegend selbständig", 
    "überwiegend unselbständig", 
    "unselbständig"
    ],
  "answer_idx": 1,
  "rationale_options": [
    "F4.1.1: mit Hilfsmitteln allein = selbständig",
    "F4.1.1: nach Anreichen eines Hilfsmittels = überwiegend selbständig",
    "F4.1.1: nur wenig mithelfen = überwiegend unselbständig",
    "F4.1.1: nicht beteiligen = unselbständig",
    "F4.1.2: sicher sitzen ohne Unterstützung = selbständig",
    "F4.1.2: nur minimale Unterstützung = überwiegend selbständig",
    "F4.1.2: erhebliche Unterstützung = überwiegend unselbständig",
    "F4.1.2: nicht selbständig sitzen = unselbständig",
    "F4.1.3: eigenständig umsetzen = selbständig",
    "F4.1.3: nach minimaler Hilfe = überwiegend selbständig",
    "F4.1.3: nur wenig mithelfen = überwiegend unselbständig",
    "F4.1.3: nicht umsetzen können = unselbständig",
    "F4.1.4: ohne Hilfe gehen = selbständig",
    "F4.1.4: nur gelegentliche Unterstützung = überwiegend selbständig",
    "F4.1.4: ständige Begleitung/erhebliche Hilfe = überwiegend unselbständig",
    "F4.1.4: nicht gehen können = unselbständig",
    "F4.1.5: ohne Hilfe Treppen steigen = selbständig",
    "F4.1.5: mit geringer Unterstützung = überwiegend selbständig",
    "F4.1.5: erhebliche Hilfe/Stützen = überwiegend unselbständig",
    "F4.1.5: keine Treppen steigen können = unselbständig"
  ],
  "rationale_id": 0 - 19,
  "point_scale_options": [
    "selbständig = 0 Punkte",
    "überwiegend selbständig = 1 Punkt",
    "überwiegend unselbständig = 2 Punkte",
    "unselbständig = 3 Punkte"
  ],
  "point_scale_id": 1,
  "point_value": 1,
  "split": "test",
  "model": "ChatGPT",
  "model_version": "5.4",
  "temperature": null
}
```


## Kriterien Mapping M1

### F4.1.1 - Positionswechsel im Bett
Einnehmen von verschiedenen Positionen im Bett, Drehen um die Längsachse, Aufrichten aus dem Liegen. Hilfen beim Aufstehen oder Zubettgehen sind unter F 4.6.2 „Ruhen und Schlafen" zu berücksichtigen.

- **Selbständig**: Auch eine Person, die ihre Position unter Nutzung von Hilfsmitteln (Aufrichthilfe, Bettseitenteil, Strickleiter, elektrisch verstellbares Bett) allein verändern kann.
- **Überwiegend selbständig**: Person kann nach Anreichen eines Hilfsmittels oder Reichen der Hand ihre Lage im Bett verändern.
- **Überwiegend unselbständig**: Person kann beim Positionswechsel nur wenig mithelfen, z. B. auf den Rücken rollen, am Bettgestell festhalten, oder zum Lagern die Arme vor der Brust verschränken und den Kopf auf die Brust legen.
- **Unselbständig**: Person kann sich beim Positionswechsel nicht oder nur minimal beteiligen.

### F4.1.2 - Halten einer stabilen Sitzposition
Aufrechtes Sitzen im Bett, auf einem Stuhl oder Rollstuhl.

- **Selbständig**: Person sitzt sicher und kann das Gleichgewicht ohne Unterstützung halten.
- **Überwiegend selbständig**: Person benötigt nur minimale Unterstützung (z. B. gelegentliches Festhalten).
- **Überwiegend unselbständig**: Person benötigt erhebliche Unterstützung, um die Sitzposition zu halten.
- **Unselbständig**: Person kann nicht selbständig sitzen.

### F4.1.3 - Umsetzen
Von liegender Position zum Sitzen, vom Bett auf einen Stuhl/Rollstuhl.

- **Selbständig**: Person kann eigenständig umsetzen.
- **Überwiegend selbständig**: Person kann nach minimaler Hilfe (z. B. Stütze an der Armlehre) selbst umsetzen.
- **Überwiegend unselbständig**: Person kann nur wenig mithelfen.
- **Unselbständig**: Person kann nicht umsetzen.

### F4.1.4 - Fortbewegung innerhalb des Wohnbereichs
Gehen im Wohnbereich, ggf. mit Hilfsmitteln.

- **Selbständig**: Person kann ohne Hilfe gehen, ggf. mit Hilfsmitteln (Rollator, Stock).
- **Überwiegend selbständig**: Person benötigt nur gelegentliche Unterstützung.
- **Überwiegend unselbständig**: Person benötigt ständige Begleitung oder erhebliche Hilfe.
- **Unselbständig**: Person kann nicht gehen.

### F4.1.5 - Treppensteigen
Treppen steigen (innerhalb und außerhalb der Wohnung).

- **Selbständig**: Person kann Treppen ohne Hilfe steigen.
- **Überwiegend selbständig**: Person kann mit geringer Unterstützung (z. B. Geländer) Treppen steigen.
- **Überwiegend unselbständig**: Person benötigt erhebliche Hilfe (z. B. Stützen durch eine Person).
- **Unselbständig**: Person kann keine Treppen steigen.


---

## JSON-Schema Beispiel M2

```json
{
  "id": "XXX",
  "module": "M2",
  "criterion": [
    "erkennen_von_personen_aus_dem_naeheren_umfeld",
    "oertliche_orientierung",
    "zeitliche_orientierung",
    "erinnern_an_wesentliche_ereignisse_oder_beobachtungen",
    "steuern_von_mehrschrittigen_alltagshandlungen",
    "treffen_von_entscheidungen_im_alltag",
    "verstehen_von_sachverhalten_und_informationen",
    "erkennen_von_risiken_und_gefahren",
    "mitteilen_von_elementaren_beduerfnissen",
    "verstehen_von_aufforderungen",
    "beteiligen_an_einem_gespraech"
  ],
  "scale_type": "faehigkeit",
  "stem": "Die versicherte Person erkennt ihre Tochter erst nach längerer Ansprache, kann sie dann aber korrekt zuordnen.",
  "options": [
    "vorhanden",
    "größtenteils vorhanden",
    "in geringem Maße vorhanden",
    "nicht vorhanden"
  ],
  "answer_idx": 0,
  "rationale_options": [
    "F4.2.1: erkennt nahe Bezugspersonen unmittelbar = vorhanden",
    "F4.2.1: erkennt bekannte Personen erst nach längerem Kontakt oder nicht immer zuverlässig = größtenteils vorhanden",
    "F4.2.1: erkennt Personen aus dem näheren Umfeld nur selten oder stark tagesformabhängig = in geringem Maße vorhanden",
    "F4.2.1: erkennt auch Familienmitglieder nicht oder nur ausnahmsweise = nicht vorhanden",

    "F4.2.2: findet sich in Wohnung, Einrichtung und näherer außerhäuslicher Umgebung zurecht = vorhanden",
    "F4.2.2: Orientierung in eigenen Räumen vorhanden, außerhäuslich erschwert = größtenteils vorhanden",
    "F4.2.2: Orientierung auch in gewohnter Wohnumgebung unsicher = in geringem Maße vorhanden",
    "F4.2.2: benötigt selbst in eigener Wohnumgebung regelmäßig Unterstützung = nicht vorhanden",

    "F4.2.3: zeitliche Orientierung ohne wesentliche Beeinträchtigung = vorhanden",
    "F4.2.3: meist zeitlich orientiert, aber nicht durchgängig = größtenteils vorhanden",
    "F4.2.3: zeitliche Orientierung meist nur ansatzweise vorhanden = in geringem Maße vorhanden",
    "F4.2.3: Verständnis für zeitliche Strukturen kaum oder nicht vorhanden = nicht vorhanden",

    "F4.2.4: erinnert sich an kurz zurückliegende und wesentliche biografische Ereignisse = vorhanden",
    "F4.2.4: erinnert sich überwiegend, hat aber einzelne relevante Lücken = größtenteils vorhanden",
    "F4.2.4: vergisst kurz zurückliegende Ereignisse häufig, wichtige biografische Ereignisse teils vorhanden = in geringem Maße vorhanden",
    "F4.2.4: Erinnerung an Ereignisse, Dinge oder Personen der eigenen Lebensgeschichte kaum vorhanden = nicht vorhanden",

    "F4.2.5: kann mehrschrittige Alltagshandlungen in richtiger Reihenfolge steuern = vorhanden",
    "F4.2.5: verliert manchmal den Faden, kann mit Erinnerung fortsetzen = größtenteils vorhanden",
    "F4.2.5: verwechselt oder vergisst regelmäßig notwendige Handlungsschritte = in geringem Maße vorhanden",
    "F4.2.5: beginnt mehrschrittige Alltagshandlungen kaum oder bricht sie ab = nicht vorhanden",

    "F4.2.6: trifft im Alltag folgerichtige und geeignete Entscheidungen = vorhanden",
    "F4.2.6: trifft einfache Alltagsentscheidungen meist selbst, benötigt bei komplexeren Situationen Unterstützung = größtenteils vorhanden",
    "F4.2.6: Entscheidungen sind häufig ungeeignet oder nur mit erheblicher Unterstützung möglich = in geringem Maße vorhanden",
    "F4.2.6: kann Entscheidungen kaum treffen oder Zustimmung/Ablehnung kaum ausdrücken = nicht vorhanden",

    "F4.2.7: versteht Sachverhalte und Informationen des Alltags = vorhanden",
    "F4.2.7: versteht einfache Informationen, komplexere Inhalte nur eingeschränkt = größtenteils vorhanden",
    "F4.2.7: versteht nur sehr einfache oder stark reduzierte Informationen = in geringem Maße vorhanden",
    "F4.2.7: versteht Sachverhalte und Informationen kaum oder nicht = nicht vorhanden",

    "F4.2.8: erkennt Risiken und Gefahren im Alltag angemessen = vorhanden",
    "F4.2.8: erkennt naheliegende Risiken meist, unbekannte oder komplexe Risiken eingeschränkt = größtenteils vorhanden",
    "F4.2.8: erkennt Risiken nur in einfachen oder unmittelbar erfahrbaren Situationen = in geringem Maße vorhanden",
    "F4.2.8: erkennt Risiken und Gefahren kaum oder nicht = nicht vorhanden",

    "F4.2.9: kann elementare Bedürfnisse eindeutig verbal oder nonverbal mitteilen = vorhanden",
    "F4.2.9: teilt Bedürfnisse nicht immer spontan oder eindeutig mit, kann sie auf Nachfrage verdeutlichen = größtenteils vorhanden",
    "F4.2.9: Bedürfnisse sind nur aus uneindeutigem Verhalten ableitbar = in geringem Maße vorhanden",
    "F4.2.9: äußert Bedürfnisse kaum oder nicht, Zustimmung/Ablehnung nicht erkennbar = nicht vorhanden",

    "F4.2.10: versteht Aufforderungen zu alltäglichen Grundbedürfnissen = vorhanden",
    "F4.2.10: versteht einfache Aufforderungen, komplexere müssen erklärt werden = größtenteils vorhanden",
    "F4.2.10: versteht Aufforderungen meist nur nach Wiederholung oder Erläuterung = in geringem Maße vorhanden",
    "F4.2.10: versteht Anleitungen und Aufforderungen kaum oder nicht = nicht vorhanden",

    "F4.2.11: kann Gesprächsinhalte aufnehmen, passend antworten und Gespräch fortführen = vorhanden",
    "F4.2.11: beteiligt sich an einfachen Gesprächen, bei komplexen Gesprächen eingeschränkt = größtenteils vorhanden",
    "F4.2.11: beteiligt sich nur geringfügig, stark verlangsamt oder überwiegend nonverbal = in geringem Maße vorhanden",
    "F4.2.11: Gesprächsbeteiligung kaum oder nicht möglich = nicht vorhanden"
  ],
  "rationale_id": 1,
  "point_scale_options": [
    "vorhanden = 0 Punkte",
    "größtenteils vorhanden = 1 Punkt",
    "in geringem Maße vorhanden = 2 Punkte",
    "nicht vorhanden = 3 Punkte"
  ],
  "point_scale_id": 0,
  "point_value": 0,
  "split": "test",
  "model": "ChatGPT",
  "model_version": "5.4",
  "temperature": null
}
```


## Kriterien Mapping M2

### F4.2.1 - Erkennen von Personen aus dem näheren Umfeld
Fähigkeit, vertraute Personen aus dem näheren Umfeld wiederzuerkennen, also Personen, zu denen im Alltag regelmäßig direkter Kontakt besteht.

- **Fähigkeit vorhanden**: Person erkennt Personen aus dem näheren Umfeld unmittelbar.
- **Fähigkeit größtenteils vorhanden**: Person erkennt vertraute Personen erst nach längerem Kontakt oder hat regelmäßig, aber nicht täglich, Schwierigkeiten beim Erkennen.
- **Fähigkeit in geringem Maße vorhanden**: Personen aus dem näheren Umfeld werden nur selten erkannt oder die Fähigkeit schwankt stark je nach Tagesform.
- **Fähigkeit nicht vorhanden**: Auch Familienmitglieder werden nicht oder nur ausnahmsweise erkannt.

### F4.2.2 - Örtliche Orientierung
Fähigkeit, sich in der räumlichen Umgebung zurechtzufinden, Orte gezielt anzusteuern und zu wissen, wo man sich befindet.

- **Fähigkeit vorhanden**: Person weiß, wo sie sich befindet, kennt sich in regelmäßig genutzten Räumen aus und findet sich auch in der näheren Umgebung zurecht.
- **Fähigkeit größtenteils vorhanden**: Person ist in den eigenen Wohnräumen orientiert, hat aber Schwierigkeiten außerhalb der Wohnung oder Einrichtung.
- **Fähigkeit in geringem Maße vorhanden**: Person hat auch in gewohnter Wohnumgebung Schwierigkeiten, Räume und Wege zuverlässig zu erkennen.
- **Fähigkeit nicht vorhanden**: Person ist selbst in der eigenen Wohnumgebung regelmäßig auf Unterstützung angewiesen.

### F4.2.3 - Zeitliche Orientierung
Fähigkeit, zeitliche Strukturen wie Uhrzeit, Tagesabschnitte, Wochentag, Monat, Jahreszeit oder zeitliche Abläufe zu erkennen.

- **Fähigkeit vorhanden**: Zeitliche Orientierung ist ohne nennenswerte Beeinträchtigung vorhanden.
- **Fähigkeit größtenteils vorhanden**: Person ist meist zeitlich orientiert, aber nicht durchgängig, z. B. bei Tagesabschnitten ohne äußere Orientierungshilfen.
- **Fähigkeit in geringem Maße vorhanden**: Zeitliche Orientierung ist meist nur ansatzweise vorhanden, auch mit Orientierungshilfen.
- **Fähigkeit nicht vorhanden**: Verständnis für zeitliche Strukturen und Abläufe ist kaum oder nicht vorhanden.

### F4.2.4 - Erinnern an wesentliche Ereignisse oder Beobachtungen
Fähigkeit, sich an kurz zurückliegende und länger zurückliegende Ereignisse oder Beobachtungen zu erinnern.

- **Fähigkeit vorhanden**: Person kann über kurz zurückliegende Ereignisse Auskunft geben oder durch Verhalten zeigen, dass sie sich erinnert.
- **Fähigkeit größtenteils vorhanden**: Person hat Schwierigkeiten mit manchen kurz zurückliegenden Ereignissen, erinnert sich aber an wichtige biografische Ereignisse.
- **Fähigkeit in geringem Maße vorhanden**: Kurz zurückliegende Ereignisse werden häufig vergessen, wichtige biografische Ereignisse sind teilweise noch präsent.
- **Fähigkeit nicht vorhanden**: Person kann sich nicht oder nur selten an Ereignisse, Dinge oder Personen aus der eigenen Lebensgeschichte erinnern.

### F4.2.5 - Steuern von mehrschrittigen Alltagshandlungen
Fähigkeit, vertraute Alltagshandlungen mit mehreren Teilschritten zielgerichtet und in richtiger Reihenfolge durchzuführen oder zu steuern.

- **Fähigkeit vorhanden**: Person kann die notwendigen Handlungsschritte selbständig in der richtigen Reihenfolge ausführen oder steuern.
- **Fähigkeit größtenteils vorhanden**: Person verliert manchmal den Faden, kann die Handlung nach Erinnerungshilfe aber selbständig fortsetzen.
- **Fähigkeit in geringem Maße vorhanden**: Person verwechselt regelmäßig Handlungsschritte oder vergisst notwendige Teilschritte.
- **Fähigkeit nicht vorhanden**: Mehrschrittige Alltagshandlungen werden nicht begonnen oder nach ersten Versuchen aufgegeben.

### F4.2.6 - Treffen von Entscheidungen im Alltag
Fähigkeit, folgerichtige und geeignete Entscheidungen im Alltag zu treffen, z. B. bei Kleidung, Aktivitäten oder Kontakten.

- **Fähigkeit vorhanden**: Person kann auch in unbekannten Situationen folgerichtige Entscheidungen treffen.
- **Fähigkeit größtenteils vorhanden**: Entscheidungen gelingen im Rahmen von Alltagsroutinen oder vorher besprochenen Situationen, aber nicht zuverlässig in unbekannten Situationen.
- **Fähigkeit in geringem Maße vorhanden**: Person trifft Entscheidungen, diese sind aber meist nicht geeignet, das Ziel zu erreichen, oder nur mit Anleitung möglich.
- **Fähigkeit nicht vorhanden**: Person kann auch mit Unterstützung keine oder nur selten Entscheidungen treffen.

### F4.2.7 - Verstehen von Sachverhalten und Informationen
Fähigkeit, Sachverhalte und Informationen aus dem Alltagsleben aufzunehmen, zu verstehen und einzuordnen.

- **Fähigkeit vorhanden**: Person kann Sachverhalte und Informationen aus dem Alltag ohne nennenswerte Probleme verstehen.
- **Fähigkeit größtenteils vorhanden**: Einfache Sachverhalte werden verstanden, bei komplizierteren Informationen bestehen Schwierigkeiten.
- **Fähigkeit in geringem Maße vorhanden**: Auch einfache Informationen werden häufig nur nach wiederholter Erklärung verstanden.
- **Fähigkeit nicht vorhanden**: Person zeigt weder verbal noch nonverbal, dass sie Situationen oder Informationen versteht.

### F4.2.8 - Erkennen von Risiken und Gefahren
Fähigkeit, alltägliche Risiken und Gefahren zu erkennen, z. B. Strom, Feuer, Hindernisse, Glätte, Straßenverkehr oder Baustellen.

- **Fähigkeit vorhanden**: Person kann Risiken und Gefahren im Alltag ohne Weiteres erkennen.
- **Fähigkeit größtenteils vorhanden**: Person erkennt meist Gefahren in vertrauter Wohnumgebung, hat aber Schwierigkeiten in ungewohnter Umgebung oder im Straßenverkehr.
- **Fähigkeit in geringem Maße vorhanden**: Person erkennt häufig auch Risiken in der eigenen Wohnumgebung nicht.
- **Fähigkeit nicht vorhanden**: Person kann Risiken und Gefahren so gut wie gar nicht erkennen.

### F4.2.9 - Mitteilen von elementaren Bedürfnissen
Fähigkeit, elementare Bedürfnisse wie Schmerzen, Frieren, Hunger, Durst oder Ausscheidungsbedürfnisse verbal oder nonverbal mitzuteilen.

- **Fähigkeit vorhanden**: Person kann elementare Bedürfnisse benennen oder durch Laute, Gestik, Mimik oder Hilfsmittel deutlich machen.
- **Fähigkeit größtenteils vorhanden**: Person äußert Bedürfnisse nicht immer von sich aus oder nicht eindeutig, kann sie aber auf Nachfrage mitteilen.
- **Fähigkeit in geringem Maße vorhanden**: Bedürfnisse sind nur aus uneindeutigem Verhalten ableitbar und müssen durch Pflegepersonen eruiert werden.
- **Fähigkeit nicht vorhanden**: Person äußert Bedürfnisse nicht oder nur sehr selten, auch nicht nonverbal.

### F4.2.10 - Verstehen von Aufforderungen
Fähigkeit, Aufforderungen zu alltäglichen Grundbedürfnissen wie Essen, Trinken, Anziehen oder Beschäftigung zu verstehen.

- **Fähigkeit vorhanden**: Aufforderungen und Bitten zu alltäglichen Grundbedürfnissen werden ohne Weiteres verstanden.
- **Fähigkeit größtenteils vorhanden**: Einfache Aufforderungen werden verstanden; komplexere Handlungen müssen erklärt oder besonders deutlich vermittelt werden.
- **Fähigkeit in geringem Maße vorhanden**: Aufforderungen werden meist nur nach Wiederholung und Erläuterung verstanden; nonverbale Zustimmung oder Ablehnung ist aber möglich.
- **Fähigkeit nicht vorhanden**: Person kann Anleitungen und Aufforderungen kaum oder nicht verstehen.

### F4.2.11 - Beteiligen an einem Gespräch
Fähigkeit, Gesprächsinhalte aufzunehmen, sinngerecht zu antworten und eigene Inhalte einzubringen.

- **Fähigkeit vorhanden**: Person kommt in Einzelgesprächen und kleinen Gruppen zurecht und beteiligt sich passend am Gespräch.
- **Fähigkeit größtenteils vorhanden**: Einzelgespräche gelingen meist, in Gruppen ist die Person überfordert oder benötigt langsame, deutliche und wiederholte Kommunikation.
- **Fähigkeit in geringem Maße vorhanden**: Person kann Gesprächen kaum folgen, beteiligt sich nur mit wenigen Worten oder weicht häufig vom Inhalt ab.
- **Fähigkeit nicht vorhanden**: Ein Gespräch über einfache Mitteilungen hinaus ist auch mit nonverbaler Kommunikation kaum oder nicht möglich.

---

## JSON-Schema Beispiel M4

```json
{
  "id": "XXX",
  "module": "M4",
  "criterion": [
    "waschen_des_vorderen_oberkoerpers",
    "koerperpflege_im_bereich_des_kopfes",
    "waschen_des_intimbereichs",
    "duschen_und_baden_einschliesslich_waschen_der_haare",
    "an_und_auskleiden_des_oberkoerpers",
    "an_und_auskleiden_des_unterkoerpers",
    "mundgerechtes_zubereiten_der_nahrung_und_eingiessen_von_getraenken",
    "essen",
    "trinken",
    "benutzen_einer_toilette_oder_eines_toilettenstuhls",
    "bewaeltigen_der_folgen_einer_harninkontinenz_und_umgang_mit_dauerkatheter_und_urostoma",
    "bewaeltigen_der_folgen_einer_stuhlinkontinenz_und_umgang_mit_stoma",
    "ernaehrung_parenteral_oder_ueber_sonde"
  ],
  "scale_type": "selbststaendigkeit",
  "stem": "Die versicherte Person kann essen, benötigt aber bei fast jeder Mahlzeit Motivation und teilweise das Reichen der Nahrung.",
  "options": [
    "selbständig",
    "überwiegend selbständig",
    "überwiegend unselbständig",
    "unselbständig"
  ],
  "answer_idx": 2,
  "rationale_options": [
    "F4.4.1: wäscht vorderen Oberkörper ohne personelle Hilfe = selbständig",
    "F4.4.1: benötigt Bereitstellen, Aufforderung oder punktuelle Teilhilfe = überwiegend selbständig",
    "F4.4.1: kann nur geringe Anteile übernehmen oder braucht umfassende Anleitung = überwiegend unselbständig",
    "F4.4.1: beteiligt sich nicht oder nur minimal = unselbständig",

    "F4.4.2: führt Kopfpflege ohne personelle Hilfe durch = selbständig",
    "F4.4.2: benötigt Bereitlegen/Richten von Gegenständen oder punktuelle Nachhilfe = überwiegend selbständig",
    "F4.4.2: beginnt Teilhandlungen, führt sie aber nicht ausreichend zu Ende = überwiegend unselbständig",
    "F4.4.2: beteiligt sich nicht oder nur minimal = unselbständig",

    "F4.4.3: wäscht und trocknet Intimbereich ohne personelle Hilfe = selbständig",
    "F4.4.3: benötigt Utensilien, Aufforderung oder punktuelle Teilhilfe = überwiegend selbständig",
    "F4.4.3: kann nur geringe Anteile übernehmen = überwiegend unselbständig",
    "F4.4.3: beteiligt sich nicht oder nur minimal = unselbständig",

    "F4.4.4: duscht/badet einschließlich Haare ohne personelle Hilfe = selbständig",
    "F4.4.4: benötigt Vorbereitung, einzelne Handreichungen oder Sicherheitsanwesenheit = überwiegend selbständig",
    "F4.4.4: kann nur geringe Anteile wie Waschen des vorderen Oberkörpers übernehmen = überwiegend unselbständig",
    "F4.4.4: beteiligt sich nicht oder nur minimal = unselbständig",

    "F4.4.5: kleidet Oberkörper ohne personelle Hilfe an/aus = selbständig",
    "F4.4.5: benötigt Anreichen/Halten der Kleidung, Hilfe bei Verschlüssen oder Sitzkontrolle = überwiegend selbständig",
    "F4.4.5: kann nur kleine Teilhandlungen übernehmen = überwiegend unselbständig",
    "F4.4.5: beteiligt sich nicht oder nur minimal = unselbständig",

    "F4.4.6: kleidet Unterkörper ohne personelle Hilfe an/aus = selbständig",
    "F4.4.6: benötigt Anreichen/Halten, Einstiegshilfe, Hilfe bei Verschlüssen oder Sitzkontrolle = überwiegend selbständig",
    "F4.4.6: kann nur geringe Teilhandlungen übernehmen = überwiegend unselbständig",
    "F4.4.6: beteiligt sich nicht oder nur minimal = unselbständig",

    "F4.4.7: zerteilt Nahrung und gießt Getränke ohne personelle Hilfe ein = selbständig",
    "F4.4.7: benötigt Vorbereitung, Bereitstellung oder punktuelle Hilfe = überwiegend selbständig",
    "F4.4.7: Nahrung/Getränke müssen überwiegend mundgerecht vorbereitet werden = überwiegend unselbständig",
    "F4.4.7: beteiligt sich nicht oder nur minimal = unselbständig",

    "F4.4.8: isst ohne personelle Hilfe = selbständig",
    "F4.4.8: benötigt punktuelle Anleitung oder einzelne Hilfen beim Essen = überwiegend selbständig",
    "F4.4.8: muss aufwendig motiviert werden oder Nahrung wird größtenteils gereicht = überwiegend unselbständig",
    "F4.4.8: Nahrung muss nahezu komplett gereicht werden oder Schlucken ist nicht möglich = unselbständig",

    "F4.4.9: trinkt ohne personelle Hilfe = selbständig",
    "F4.4.9: benötigt Positionieren des Trinkgefäßes oder Erinnerung = überwiegend selbständig",
    "F4.4.9: Trinkgefäß muss gegeben werden oder zu fast jedem Schluck motiviert werden = überwiegend unselbständig",
    "F4.4.9: Getränke müssen nahezu komplett gereicht werden oder Schlucken ist nicht möglich = unselbständig",

    "F4.4.10: nutzt Toilette/Toilettenstuhl ohne personelle Hilfe = selbständig",
    "F4.4.10: erledigt größten Anteil selbst, benötigt nur einzelne Hilfen = überwiegend selbständig",
    "F4.4.10: erledigt nur geringe Anteile selbst = überwiegend unselbständig",
    "F4.4.10: beteiligt sich nicht oder nur minimal = unselbständig",

    "F4.4.11: nutzt Hilfsmittel bei Harninkontinenz/Katheter/Urostoma selbständig = selbständig",
    "F4.4.11: benötigt Anreichen, Entsorgung oder Erinnerung = überwiegend selbständig",
    "F4.4.11: beteiligt sich nur teilweise am Wechsel der Systeme = überwiegend unselbständig",
    "F4.4.11: Beteiligung nicht oder nur minimal möglich = unselbständig",

    "F4.4.12: nutzt Inkontinenz- oder Stomasysteme selbständig = selbständig",
    "F4.4.12: benötigt Bereitlegen, Entsorgung oder Erinnerung = überwiegend selbständig",
    "F4.4.12: beteiligt sich nur teilweise am Wechsel der Systeme = überwiegend unselbständig",
    "F4.4.12: Beteiligung nicht oder nur minimal möglich = unselbständig"
  ],
  "rationale_id": 30,
  "point_scale_options": [
    "F4.4.1-F4.4.7, F4.4.11-F4.4.12 + selbständig = 0 Punkte",
    "F4.4.1-F4.4.7, F4.4.11-F4.4.12 + überwiegend selbständig = 1 Punkt",
    "F4.4.1-F4.4.7, F4.4.11-F4.4.12 + überwiegend unselbständig = 2 Punkte",
    "F4.4.1-F4.4.7, F4.4.11-F4.4.12 + unselbständig = 3 Punkte",
    "F4.4.8 Essen + selbständig = 0 Punkte",
    "F4.4.8 Essen + überwiegend selbständig = 3 Punkte",
    "F4.4.8 Essen + überwiegend unselbständig = 6 Punkte",
    "F4.4.8 Essen + unselbständig = 9 Punkte",
    "F4.4.9 Trinken oder F4.4.10 Benutzen einer Toilette/eines Toilettenstuhls + selbständig = 0 Punkte",
    "F4.4.9 Trinken oder F4.4.10 Benutzen einer Toilette/eines Toilettenstuhls + überwiegend selbständig = 2 Punkte",
    "F4.4.9 Trinken oder F4.4.10 Benutzen einer Toilette/eines Toilettenstuhls + überwiegend unselbständig = 4 Punkte",
    "F4.4.9 Trinken oder F4.4.10 Benutzen einer Toilette/eines Toilettenstuhls + unselbständig = 6 Punkte"
  ],
  "point_scale_id": 6,
  "point_value": 6,
  "split": "test",
  "model": "ChatGPT",
  "model_version": "5.4",
  "temperature": null
}
```


## Zusatzschema M4.4.13: Ernährung parenteral oder über Sonde

```json
{
  "id": "XXX",
  "module": "M4",
  "criterion": "ernaehrung_parenteral_oder_ueber_sonde",
  "scale_type": "sonden_oder_parenterale_ernaehrung",
  "stem": "Die versicherte Person erhält täglich zusätzlich zur oralen Nahrung Sondennahrung und benötigt dabei Hilfe.",
  "options": [
    "selbständig oder keine/nicht tägliche/nicht dauerhafte künstliche Ernährung",
    "mit Hilfe: täglich zusätzlich zu oraler Ernährung",
    "mit Hilfe: ausschließlich oder nahezu ausschließlich"
  ],
  "answer_idx": 1,
  "rationale_options": [
    "F4.4.13: keine, nicht tägliche, nicht dauerhafte oder selbständig durchgeführte künstliche Ernährung",
    "F4.4.13: mit Hilfe täglich zusätzlich zu oraler Ernährung",
    "F4.4.13: mit Hilfe ausschließlich oder nahezu ausschließlich künstliche Ernährung"
  ],
  "rationale_id": 1,
  "point_scale_options": [
    "selbständig oder keine, nicht tägliche oder nicht dauerhafte künstliche Ernährung = 0 Punkte",
    "mit Hilfe: täglich zusätzlich zu oraler Ernährung = 6 Punkte",
    "mit Hilfe: ausschließlich oder nahezu ausschließlich künstliche Ernährung = 3 Punkte"
  ],
  "point_scale_id": 1,
  "point_value": 6,
  "split": "test",
  "model": "ChatGPT",
  "model_version": "5.4",
  "temperature": null
}
```


## Kriterien Mapping M4

### F4.4.1 - Waschen des vorderen Oberkörpers
Hände, Gesicht, Arme, Achselhöhlen sowie vorderen Hals- und Brustbereich waschen und abtrocknen.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person kann die Aktivität durchführen, wenn Gegenstände bereitgelegt werden oder punktuelle Hilfen bzw. Aufforderungen erfolgen.
- **Überwiegend unselbständig**: Person kann nur geringe Anteile selbständig durchführen, z. B. nur Hände oder Gesicht waschen.
- **Unselbständig**: Person kann sich an der Aktivität nicht oder nur minimal beteiligen.

### F4.4.2 - Körperpflege im Bereich des Kopfes
Kämmen, Zahnpflege, Prothesenreinigung und Rasieren.

- **Selbständig**: Person kann die Aktivitäten ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person benötigt Bereitstellen oder Richten von Gegenständen oder punktuelle Hilfen, z. B. Zahnpasta auftragen, Rasierer anreichen oder Nachkorrekturen.
- **Überwiegend unselbständig**: Person beginnt einzelne Tätigkeiten, führt sie aber nicht vollständig zu Ende.
- **Unselbständig**: Person kann sich an den Aktivitäten nicht oder nur minimal beteiligen.

### F4.4.3 - Waschen des Intimbereichs
Intimbereich waschen und abtrocknen.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person kann die Aktivität durchführen, wenn Utensilien bereitgelegt werden oder punktuelle Hilfen bzw. Aufforderungen erfolgen.
- **Überwiegend unselbständig**: Person kann nur geringe Anteile selbständig durchführen, z. B. nur den vorderen Intimbereich waschen.
- **Unselbständig**: Person kann sich an der Aktivität nicht oder nur minimal beteiligen.

### F4.4.4 - Duschen und Baden einschließlich Waschen der Haare
Durchführung des Dusch- oder Wannenbades einschließlich Haarewaschen, Abtrocknen, Föhnen und Sicherheitsaspekten.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person benötigt vorbereitete Utensilien, einzelne Handreichungen, Hilfe beim Ein- oder Aussteigen, beim Haarewaschen, Föhnen, Abtrocknen oder Anwesenheit aus Sicherheitsgründen.
- **Überwiegend unselbständig**: Person kann nur geringe Anteile durchführen, z. B. Waschen des vorderen Oberkörpers.
- **Unselbständig**: Person kann sich an der Aktivität nicht oder nur minimal beteiligen.

### F4.4.5 - An- und Auskleiden des Oberkörpers
Bereitliegende Oberkörperkleidung wie Unterhemd, T-Shirt, Hemd, Bluse, Pullover, Jacke, BH oder Schlafanzugoberteil an- und ausziehen.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person benötigt Hilfe beim Anreichen oder Halten von Kleidung, bei Verschlüssen, Kontrolle des Sitzes oder Aufforderung zur Vervollständigung.
- **Überwiegend unselbständig**: Person kann nur geringe Anteile übernehmen, z. B. Hände in die Ärmel eines bereitgehaltenen T-Shirts schieben.
- **Unselbständig**: Person kann sich an der Aktivität nicht oder nur minimal beteiligen.

### F4.4.6 - An- und Auskleiden des Unterkörpers
Bereitliegende Unterkörperkleidung wie Unterwäsche, Hose, Rock, Strümpfe und Schuhe an- und ausziehen.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person benötigt Hilfe beim Anreichen oder Halten von Kleidung, bei Verschlüssen, Schuhen, Kontrolle des Sitzes oder Aufforderung.
- **Überwiegend unselbständig**: Person kann nur geringe Anteile durchführen, z. B. Hose oder Rock vom Oberschenkel zur Taille hochziehen.
- **Unselbständig**: Person kann sich an der Aktivität nicht oder nur minimal beteiligen.

### F4.4.7 - Mundgerechtes Zubereiten der Nahrung und Eingießen von Getränken
Nahrung in mundgerechte Stücke zerteilen und Getränke öffnen bzw. eingießen.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person benötigt punktuelle Hilfe, z. B. beim Öffnen einer Flasche oder Schneiden harter Nahrungsmittel.
- **Überwiegend unselbständig**: Person kann nur geringe Teile übernehmen, z. B. schneiden, aber keine mundgerechten Stücke herstellen oder keine Getränke eingießen.
- **Unselbständig**: Person kann sich an der Aktivität nicht oder nur minimal beteiligen.

### F4.4.8 - Essen
Bereitgestellte, mundgerecht zubereitete Speisen aufnehmen, zum Mund führen, abbeißen, kauen und schlucken.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person benötigt punktuelle Anleitung oder Hilfe, z. B. Aufforderung zum Beginn oder Weiteressen, Besteck in die Hand geben.
- **Überwiegend unselbständig**: Person muss aufwendig motiviert werden, Nahrung muss größtenteils gereicht werden oder ständige Eingreifbereitschaft wegen Aspirationsgefahr ist nötig.
- **Unselbständig**: Nahrung muss nahezu vollständig gereicht werden oder Person kann nicht schlucken.

### F4.4.9 - Trinken
Bereitstehende Getränke aufnehmen, gegebenenfalls mit Hilfsmitteln wie Strohhalm oder Spezialbecher.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person kann trinken, wenn das Getränk in den Aktionsradius gestellt oder an das Trinken erinnert wird.
- **Überwiegend unselbständig**: Trinkgefäß muss in die Hand gegeben werden, Person muss zu fast jedem Schluck motiviert werden oder ständige Eingreifbereitschaft ist wegen Aspirationsgefahr nötig.
- **Unselbständig**: Getränke müssen nahezu vollständig gereicht werden oder Person kann nicht schlucken.

### F4.4.10 - Benutzen einer Toilette oder eines Toilettenstuhls
Zur Toilette gehen, Hinsetzen und Aufstehen, Sitzen während der Blasen- oder Darmentleerung, Intimhygiene und Kleidung richten.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person kann den größten Anteil selbständig durchführen; Hilfe beschränkt sich auf einzelne Schritte, z. B. Toilettenstuhl leeren, Orientierung, Hinsetzen, Aufstehen, Toilettenpapier anreichen oder Kleidung richten.
- **Überwiegend unselbständig**: Person kann nur geringe Anteile durchführen, z. B. nur Kleidung richten oder Intimhygiene nach Wasserlassen.
- **Unselbständig**: Person kann sich nicht oder nur minimal beteiligen.

### F4.4.11 - Bewältigen der Folgen einer Harninkontinenz und Umgang mit Dauerkatheter und Urostoma
Inkontinenz- und Stomasysteme sachgerecht verwenden, wechseln, entleeren und entsorgen.

- **Selbständig**: Person kann Hilfsmittel selbständig benutzen.
- **Überwiegend selbständig**: Person kann die Aktivität überwiegend selbständig durchführen, wenn Inkontinenzsysteme angereicht, entsorgt oder Wechsel erinnert wird.
- **Überwiegend unselbständig**: Person kann sich am Wechsel beteiligen, z. B. Vorlagen einlegen oder Inkontinenzhosen entfernen.
- **Unselbständig**: Beteiligung ist nicht oder nur minimal möglich.

### F4.4.12 - Bewältigen der Folgen einer Stuhlinkontinenz und Umgang mit Stoma
Inkontinenz- und Stomasysteme sachgerecht verwenden, wechseln, entleeren und entsorgen.

- **Selbständig**: Person kann Hilfsmittel selbständig benutzen.
- **Überwiegend selbständig**: Person kann die Aktivität überwiegend selbständig durchführen, wenn Inkontinenzsysteme bereitgelegt, entsorgt oder Wechsel erinnert wird.
- **Überwiegend unselbständig**: Person kann sich am Wechsel beteiligen, z. B. beim Wechsel eines Stomabeutels mithelfen.
- **Unselbständig**: Beteiligung ist nicht oder nur minimal möglich.

### F4.4.13 - Ernährung parenteral oder über Sonde
Ernährung über parenteralen Zugang, z. B. Port, oder über Zugang in Magen oder Dünndarm, z. B. PEG oder PEJ.

- **Selbständig**: Person führt die Versorgung ohne Fremdhilfe durch.
- **Nicht täglich, nicht auf Dauer**: Person erhält zusätzlich zur oralen Ernährung gelegentlich oder vorübergehend Nahrung oder Flüssigkeit parenteral oder über Sonde.
- **Täglich, zusätzlich zu oraler Ernährung**: Person erhält täglich Nahrung oder Flüssigkeit parenteral oder über Sonde zusätzlich zur oralen Aufnahme.
- **Ausschließlich oder nahezu ausschließlich**: Person erhält Nahrung und Flüssigkeit ausschließlich oder nahezu ausschließlich parenteral oder über Sonde.

---

## JSON-Schema Beispiel M5 für F4.5.1 bis F4.5.15

```json
{
  "id": "XXX",
  "module": "M5",
  "criterion": [
    "medikation",
    "injektionen",
    "versorgung_intravenoeser_zugaenge",
    "absaugen_und_sauerstoffgabe",
    "einreibungen_oder_kaelte_und_waermeanwendungen",
    "messung_und_deutung_von_koerperzustaenden",
    "koerpernahe_hilfsmittel",
    "verbandswechsel_und_wundversorgung",
    "versorgung_mit_stoma",
    "regelmaessige_einmalkatheterisierung_und_nutzung_von_abfuehrmethoden",
    "therapiemassnahmen_in_haeuslicher_umgebung",
    "zeit_und_technikintensive_massnahmen_in_haeuslicher_umgebung",
    "arztbesuche",
    "besuche_anderer_medizinischer_oder_therapeutischer_einrichtungen_bis_drei_stunden",
    "zeitlich_ausgedehnte_besuche_anderer_medizinischer_oder_therapeutischer_einrichtungen_mehr_als_drei_stunden"
  ],
  "scale_type": "haeufigkeit_der_hilfe",
  "stem": "Die versicherte Person benötigt morgens und abends Hilfe beim Bereitstellen und Einnehmen der Medikamente.",
  "options": [
    "entfällt oder nicht erforderlich",
    "selbständig",
    "Hilfe erforderlich"
  ],
  "answer_idx": 2,
  "frequency_unit_options": ["pro_tag", "pro_woche", "pro_monat", null],
  "frequency_count": 2,
  "frequency_unit": "pro_tag",
  "point_scale_options": [
    "F4.5.1-F4.5.7: keine oder seltener als einmal täglich = 0 Punkte",
    "F4.5.1-F4.5.7: mindestens einmal bis maximal dreimal täglich = 1 Punkt",
    "F4.5.1-F4.5.7: mehr als dreimal bis maximal achtmal täglich = 2 Punkte",
    "F4.5.1-F4.5.7: mehr als achtmal täglich = 3 Punkte",
    "F4.5.8-F4.5.11: nie oder seltener als einmal wöchentlich = 0 Punkte",
    "F4.5.8-F4.5.11: ein- bis mehrmals wöchentlich = 1 Punkt",
    "F4.5.8-F4.5.11: ein- bis unter dreimal täglich = 2 Punkte",
    "F4.5.8-F4.5.11: mindestens dreimal täglich = 3 Punkte",
    "F4.5.12: entfällt/selbständig = 0 Punkte; tägliche Häufigkeit × 60; wöchentliche Häufigkeit × 8,6; monatliche Häufigkeit × 2",
    "F4.5.13-F4.5.14: entfällt/selbständig = 0 Punkte; wöchentliche Häufigkeit × 4,3; monatliche Häufigkeit × 1",
    "F4.5.15: entfällt/selbständig = 0 Punkte; wöchentliche Häufigkeit × 8,6; monatliche Häufigkeit × 2"
  ],
  "point_scale_id": 1,
  "point_value": 1,
  "split": "test",
  "model": "ChatGPT",
  "model_version": "5.4",
  "temperature": null
}
```


## JSON-Schema Beispiel M5 für F4.5.16

```json
{
  "id": "XXX",
  "module": "M5",
  "criterion": "einhalten_einer_diaet_oder_anderer_krankheits_oder_therapiebedingter_verhaltensvorschriften",
  "scale_type": "selbststaendigkeit",
  "stem": "Die versicherte Person muss an die Einhaltung einer ärztlich angeordneten Diät mehrmals täglich erinnert und beaufsichtigt werden.",
  "options": [
    "entfällt, nicht erforderlich oder selbständig",
    "überwiegend selbständig",
    "überwiegend unselbständig",
    "unselbständig"
  ],
  "answer_idx": 2,
  "rationale_options": [
    "F4.5.16: keine Vorschrift, nicht erforderlich oder selbständig eingehalten = selbständig",
    "F4.5.16: Erinnerung oder Anleitung maximal einmal täglich erforderlich = überwiegend selbständig",
    "F4.5.16: Anleitung oder Beaufsichtigung mehrmals täglich erforderlich = überwiegend unselbständig",
    "F4.5.16: Anleitung oder Beaufsichtigung fast durchgehend erforderlich = unselbständig"
  ],
  "rationale_id": 2,
  "point_scale_options": [
    "entfällt, nicht erforderlich oder selbständig = 0 Punkte",
    "überwiegend selbständig = 1 Punkt",
    "überwiegend unselbständig = 2 Punkte",
    "unselbständig = 3 Punkte"
  ],
  "point_scale_id": 2,
  "point_value": 2,
  "split": "test",
  "model": "ChatGPT",
  "model_version": "5.4",
  "temperature": null
}
```


## Kriterien Mapping M5

### Allgemeine Bewertungslogik für F4.5.1 bis F4.5.15
In Modul 5 geht es um ärztlich angeordnete Maßnahmen, die auf eine bestehende Erkrankung ausgerichtet und voraussichtlich mindestens sechs Monate erforderlich sind.

- **Entfällt**: Maßnahme ist nicht erforderlich oder liegt nicht vor.
- **Selbständig**: Person kann die Maßnahme selbständig durchführen.
- **Hilfe erforderlich**: Person kann die Maßnahme nicht selbständig durchführen; dokumentiert wird die Häufigkeit der Hilfe durch andere Personen.
- **Häufigkeit**: Hilfe wird als Anzahl pro Tag, pro Woche oder pro Monat erfasst.

### F4.5.1 - Medikation
Orale Medikation, Augen- oder Ohrentropfen, Dosieraerosole, Pulverinhalatoren, Zäpfchen, Medikamentenpflaster und vergleichbare Arzneimittelanwendungen.

- **Entfällt**: Keine entsprechende ärztlich angeordnete Medikation erforderlich.
- **Selbständig**: Person kann Medikamente selbständig richten, dosieren und einnehmen bzw. anwenden.
- **Hilfe erforderlich**: Person benötigt Hilfe beim Stellen, Verabreichen oder Anwenden der Medikamente.
- **Häufigkeit**: Erfasst wird die Häufigkeit der Hilfe, z. B. pro Tag, Woche oder Monat.

### F4.5.2 - Injektionen
Subkutane und intramuskuläre Injektionen sowie subkutane Infusionen, z. B. Insulin oder Medikamentenpumpen.

- **Entfällt**: Keine Injektionen oder subkutanen Infusionen erforderlich.
- **Selbständig**: Person kann die Injektion oder Infusion selbständig vorbereiten und durchführen.
- **Hilfe erforderlich**: Person benötigt Hilfe beim Vorbereiten, Durchführen oder Überwachen.
- **Häufigkeit**: Erfasst wird die Anzahl der notwendigen Hilfen pro Tag, Woche oder Monat.

### F4.5.3 - Versorgung intravenöser Zugänge
Versorgung und Verbände venöser Zugänge, z. B. Port, Shaldon- oder Broviac-Katheter, einschließlich Einbringen von Medikamenten.

- **Entfällt**: Kein entsprechender intravenöser oder vergleichbarer Zugang vorhanden.
- **Selbständig**: Person kann den Zugang selbständig versorgen.
- **Hilfe erforderlich**: Person benötigt Hilfe bei Versorgung, Verband, Hygiene oder Medikamentengabe über den Zugang.
- **Häufigkeit**: Erfasst wird die Anzahl der Hilfen pro Tag, Woche oder Monat.

### F4.5.4 - Absaugen und Sauerstoffgabe
Absaugen, Sauerstoffgabe über Brille oder Maske, Atemmasken, Inhalationsgerät bereitstellen und reinigen.

- **Entfällt**: Keine entsprechende Maßnahme erforderlich.
- **Selbständig**: Person kann Absaugen, Sauerstoffgabe oder Gerätemanagement selbständig durchführen.
- **Hilfe erforderlich**: Person benötigt Hilfe beim Absaugen, Anlegen, Ablegen, Bereitstellen, Reinigen oder Überwachen.
- **Häufigkeit**: Erfasst wird der durchschnittliche Hilfebedarf pro Tag, Woche oder Monat.

### F4.5.5 - Einreibungen oder Kälte- und Wärmeanwendungen
Ärztlich angeordnete Salben, Cremes, Emulsionen, Kälte- oder Wärmeanwendungen.

- **Entfällt**: Keine ärztlich angeordnete externe Anwendung erforderlich.
- **Selbständig**: Person kann die Anwendung selbständig durchführen.
- **Hilfe erforderlich**: Person benötigt Hilfe beim Auftragen, Anwenden, Vorbereiten oder Entfernen.
- **Häufigkeit**: Erfasst wird die Anzahl der Hilfen pro Tag, Woche oder Monat.

### F4.5.6 - Messung und Deutung von Körperzuständen
Ärztlich angeordnete Messungen wie Blutdruck, Puls, Blutzucker, Temperatur, Gewicht oder Flüssigkeitshaushalt einschließlich notwendiger Schlussfolgerungen.

- **Entfällt**: Keine krankheitsbezogene ärztlich angeordnete Messung erforderlich.
- **Selbständig**: Person kann Messung und Deutung selbständig durchführen und passende Konsequenzen ableiten.
- **Hilfe erforderlich**: Person benötigt Hilfe beim Messen, Interpretieren oder beim Ableiten notwendiger Maßnahmen.
- **Häufigkeit**: Erfasst wird die Anzahl der Hilfen pro Tag, Woche oder Monat.

### F4.5.7 - Körpernahe Hilfsmittel
An- und Ablegen von Prothesen, Orthesen, Epithesen, Sehhilfen, Hörgeräten, kieferorthopädischen Apparaturen und Kompressionsstrümpfen.

- **Entfällt**: Kein entsprechendes körpernahes Hilfsmittel erforderlich.
- **Selbständig**: Person kann das Hilfsmittel selbständig anlegen, ablegen und sachgerecht handhaben.
- **Hilfe erforderlich**: Person benötigt Hilfe beim Anlegen, Ablegen oder Reinigen im Zusammenhang mit der Nutzung.
- **Häufigkeit**: Erfasst wird die Anzahl der Hilfen pro Tag, Woche oder Monat.

### F4.5.8 - Verbandswechsel und Wundversorgung
Versorgung chronischer Wunden, z. B. Ulcus cruris oder Dekubitus.

- **Entfällt**: Keine chronische Wundversorgung erforderlich.
- **Selbständig**: Person kann Verbandswechsel und Wundversorgung selbständig durchführen.
- **Hilfe erforderlich**: Person benötigt Hilfe bei Reinigung, Verband, Wundkontrolle oder Materialhandhabung.
- **Häufigkeit**: Erfasst wird die Anzahl der Hilfen pro Tag, Woche oder Monat.

### F4.5.9 - Versorgung mit Stoma
Pflege künstlicher Körperöffnungen, z. B. Tracheostoma, PEG, suprapubischer Blasenkatheter, Urostoma, Colo- oder Ileostoma.

- **Entfällt**: Kein entsprechendes Stoma oder keine künstliche Körperöffnung vorhanden.
- **Selbständig**: Person kann die Stomaversorgung selbständig durchführen.
- **Hilfe erforderlich**: Person benötigt Hilfe bei Reinigung, Desinfektion, Verbandswechsel, Basisplattenwechsel oder vergleichbaren Versorgungsschritten.
- **Häufigkeit**: Erfasst wird die Anzahl der Hilfen pro Tag, Woche oder Monat.

### F4.5.10 - Regelmäßige Einmalkatheterisierung und Nutzung von Abführmethoden
Regelmäßige Einmalkatheterisierung sowie Abführmethoden wie Klistier, Einlauf oder digitale Ausräumung.

- **Entfällt**: Keine regelmäßige Einmalkatheterisierung oder Abführmethode erforderlich.
- **Selbständig**: Person kann die Maßnahme selbständig durchführen.
- **Hilfe erforderlich**: Person benötigt Hilfe bei Vorbereitung, Durchführung, Hygiene oder Nachbereitung.
- **Häufigkeit**: Erfasst wird die Anzahl der Hilfen pro Tag, Woche oder Monat.

### F4.5.11 - Therapiemaßnahmen in häuslicher Umgebung
Eigenübungen aus Heilmitteltherapie, therapeutische Maßnahmen zur Sekretelimination, Peritonealdialyse und vergleichbare Maßnahmen.

- **Entfällt**: Keine entsprechende häusliche Therapiemaßnahme erforderlich.
- **Selbständig**: Person kann die Maßnahme selbständig durchführen.
- **Hilfe erforderlich**: Person benötigt Anleitung, Motivation, Beaufsichtigung oder praktische Hilfe.
- **Häufigkeit**: Erfasst wird die Anzahl der Hilfen pro Tag, Woche oder Monat.

### F4.5.12 - Zeit- und technikintensive Maßnahmen in häuslicher Umgebung
Zeit- und technikintensive Maßnahmen wie Heimbeatmung oder Hämodialyse, die geschulte Überwachung erfordern.

- **Entfällt**: Keine zeit- und technikintensive Maßnahme erforderlich.
- **Selbständig**: Person kann die Maßnahme selbständig bewältigen.
- **Hilfe erforderlich**: Person benötigt geschulte Hilfe, Überwachung oder technische Unterstützung.
- **Häufigkeit**: Erfasst wird die Anzahl der Hilfen pro Tag, Woche oder Monat.

### F4.5.13 - Arztbesuche
Regelmäßige Besuche bei Hausärztinnen, Hausärzten oder Fachärztinnen und Fachärzten zu diagnostischen oder therapeutischen Zwecken.

- **Entfällt**: Keine regelmäßigen Arztbesuche mit Unterstützungsbedarf erforderlich.
- **Selbständig**: Person kann Arztbesuche selbständig organisieren und aufsuchen.
- **Hilfe erforderlich**: Person benötigt Unterstützung auf dem Weg, bei der Begleitung oder während des Arztbesuchs.
- **Häufigkeit**: Erfasst wird die durchschnittliche Häufigkeit der erforderlichen Hilfe pro Monat oder Woche.

### F4.5.14 - Besuche anderer medizinischer oder therapeutischer Einrichtungen bis zu drei Stunden
Besuche bei therapeutischen oder medizinischen Einrichtungen, z. B. Physiotherapie, Ergotherapie, Logopädie, Psychotherapie oder ambulante Diagnostik, mit Gesamtaufwand bis zu drei Stunden.

- **Entfällt**: Keine entsprechenden Besuche mit Unterstützungsbedarf erforderlich.
- **Selbständig**: Person kann die Einrichtung selbständig aufsuchen.
- **Hilfe erforderlich**: Person benötigt Begleitung, Wegeunterstützung oder Unterstützung während des Besuchs.
- **Häufigkeit**: Erfasst wird die durchschnittliche Häufigkeit der erforderlichen Hilfe pro Woche oder Monat.

### F4.5.15 - Zeitlich ausgedehnte Besuche anderer medizinischer oder therapeutischer Einrichtungen über drei Stunden
Besuche medizinischer oder therapeutischer Einrichtungen mit Gesamtaufwand für die Pflegeperson von mehr als drei Stunden, z. B. Dialyse oder onkologische Behandlung.

- **Entfällt**: Keine zeitlich ausgedehnten Besuche mit Unterstützungsbedarf erforderlich.
- **Selbständig**: Person kann die Besuche selbständig bewältigen.
- **Hilfe erforderlich**: Person benötigt Begleitung oder Unterstützung über einen längeren Zeitraum.
- **Häufigkeit**: Erfasst wird die durchschnittliche Häufigkeit der erforderlichen Hilfe pro Woche oder Monat.

### F4.5.16 - Einhalten einer Diät oder anderer krankheits- oder therapiebedingter Verhaltensvorschriften
Fähigkeit, die Notwendigkeit ärztlich angeordneter Diäten oder Verhaltensvorschriften zu erkennen und einzuhalten.

- **Selbständig**: Person kann Vorschriften selbständig einhalten; das Bereitstellen einer Diät reicht aus.
- **Überwiegend selbständig**: Person benötigt Erinnerung oder Anleitung; darüber hinausgehendes Eingreifen ist maximal einmal täglich erforderlich.
- **Überwiegend unselbständig**: Person benötigt meistens Anleitung oder Beaufsichtigung; Eingreifen ist mehrmals täglich erforderlich.
- **Unselbständig**: Person benötigt immer Anleitung oder Beaufsichtigung; Eingreifen ist fast durchgehend erforderlich.

---

## JSON-Schema Beispiel M6

```json
{
  "id": "XXX",
  "module": "M6",
  "criterion": [
    "gestaltung_des_tagesablaufs_und_anpassung_an_veraenderungen",
    "ruhen_und_schlafen",
    "sichbeschaeftigen",
    "vornehmen_von_in_die_zukunft_gerichteten_planungen",
    "interaktion_mit_personen_im_direkten_kontakt",
    "kontaktpflege_zu_personen_ausserhalb_des_direkten_umfelds"
  ],
  "scale_type": "selbststaendigkeit",
  "stem": "Die versicherte Person kann ihren gewohnten Tagesablauf weitgehend selbst planen, benötigt aber bei ungewohnten Änderungen Erinnerung und Unterstützung.",
  "options": [
    "selbständig",
    "überwiegend selbständig",
    "überwiegend unselbständig",
    "unselbständig"
  ],
  "answer_idx": 1,
  "rationale_options": [
    "F4.6.1: Tagesablauf kann ohne personelle Hilfe geplant und angepasst werden = selbständig",
    "F4.6.1: Routineabläufe gelingen, bei ungewohnten Veränderungen ist Unterstützung nötig = überwiegend selbständig",
    "F4.6.1: Hilfe bei Planung des Routinetagesablaufs oder häufige Erinnerung über den Tag nötig = überwiegend unselbständig",
    "F4.6.1: Mitwirkung an Tagesstrukturierung kaum oder nicht möglich = unselbständig",

    "F4.6.2: Tag-Nacht-Rhythmus und Ruhephasen ohne personelle Hilfe möglich = selbständig",
    "F4.6.2: Hilfe beim Aufstehen/Zubettgehen oder gelegentlicher nächtlicher Hilfebedarf = überwiegend selbständig",
    "F4.6.2: nahezu jede Nacht erhebliche Hilfe bei Unruhe, Einschlafen, Lagewechsel oder Toilettengang nötig = überwiegend unselbständig",
    "F4.6.2: kein oder deutlich gestörter Schlaf-Wach-Rhythmus = unselbständig",

    "F4.6.3: Beschäftigung kann ohne personelle Hilfe gewählt und durchgeführt werden = selbständig",
    "F4.6.3: geringe Hilfe wie Vorbereitung, Zurechtlegen, Erinnerung oder Motivation nötig = überwiegend selbständig",
    "F4.6.3: Beschäftigung nur mit umfassender Anleitung, Begleitung oder motorischer Unterstützung möglich = überwiegend unselbständig",
    "F4.6.3: keine nennenswerte Mitwirkung an Entscheidung oder Durchführung = unselbständig",

    "F4.6.4: Zukunftsplanung über den Tag hinaus ohne personelle Hilfe möglich = selbständig",
    "F4.6.4: plant etwas, muss aber an Umsetzung erinnert werden oder braucht Abstimmungshilfe = überwiegend selbständig",
    "F4.6.4: plant kaum selbst, entscheidet aber mit Unterstützung oder braucht umfassende Umsetzungshilfe = überwiegend unselbständig",
    "F4.6.4: keine Zeitvorstellung für Planungen oder keine erkennbare Zustimmung/Ablehnung = unselbständig",

    "F4.6.5: direkte Interaktion mit anderen Personen ohne personelle Hilfe möglich = selbständig",
    "F4.6.5: Interaktion mit vertrauten Personen gelingt, bei fremden Personen oder Kommunikationsproblemen punktuelle Hilfe nötig = überwiegend selbständig",
    "F4.6.5: kaum Eigeninitiative, reagiert aber auf Ansprache oder braucht umfassende Kommunikationsunterstützung = überwiegend unselbständig",
    "F4.6.5: reagiert nicht oder kaum auf Ansprache oder nonverbale Kontaktversuche = unselbständig",

    "F4.6.6: Kontakte außerhalb des direkten Umfelds ohne personelle Hilfe pflegen = selbständig",
    "F4.6.6: kann Kontakt planen, benötigt aber Hilfe bei Umsetzung, Erinnerung oder Technik = überwiegend selbständig",
    "F4.6.6: Kontaktgestaltung ist überwiegend reaktiv, Mitwirkung nur bei Initiative anderer = überwiegend unselbständig",
    "F4.6.6: Kontaktpflege außerhalb des direkten Umfelds kaum oder nicht möglich = unselbständig"
  ],
  "rationale_id": 1,
  "point_scale_options": [
    "selbständig = 0 Punkte",
    "überwiegend selbständig = 1 Punkt",
    "überwiegend unselbständig = 2 Punkte",
    "unselbständig = 3 Punkte"
  ],
  "point_scale_id": 1,
  "point_value": 1,
  "split": "test",
  "model": "ChatGPT",
  "model_version": "5.4",
  "temperature": null
}
```


## Kriterien Mapping M6

### F4.6.1 - Gestaltung des Tagesablaufs und Anpassung an Veränderungen
Den Tagesablauf nach individuellen Gewohnheiten und Vorlieben einteilen, bewusst gestalten und bei Veränderungen anpassen.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Routineabläufe können weitgehend selbständig gestaltet werden; bei ungewohnten Veränderungen sind Erinnerungshilfen oder Unterstützung nötig.
- **Überwiegend unselbständig**: Person benötigt Hilfe beim Planen des Routinetagesablaufs und über den Tag hinweg Erinnerung oder Aufforderung.
- **Unselbständig**: Mitwirkung an der Tagesplanung oder Orientierung an vorgegebenen Strukturen ist nicht oder nur minimal möglich.

### F4.6.2 - Ruhen und Schlafen
Einen Tag-Nacht-Rhythmus einhalten, ausreichend Ruhe- und Schlafphasen finden und mit Schlafproblemen umgehen.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person benötigt Hilfe beim Aufstehen oder Zubettgehen, zeitliche Orientierungshilfen oder gelegentlich nächtliche Hilfe.
- **Überwiegend unselbständig**: Person hat nahezu jede Nacht Einschlafprobleme, nächtliche Unruhe oder benötigt regelmäßig Hilfe, um weiterzuschlafen.
- **Unselbständig**: Person hat keinen oder stark gestörten Schlaf-Wach-Rhythmus oder benötigt regelmäßig mindestens dreimal nachts personelle Unterstützung.

### F4.6.3 - Sichbeschäftigen
Verfügbare freie Zeit nutzen, um Aktivitäten nach eigenen Vorlieben und Interessen auszuwählen und durchzuführen.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person benötigt nur geringe Hilfe, z. B. Vorbereiten von Gegenständen, Erinnerung, Motivation oder Entscheidungshilfe.
- **Überwiegend unselbständig**: Person kann sich beteiligen, benötigt aber umfassende Anleitung, Begleitung oder motorische Unterstützung.
- **Unselbständig**: Person kann an Auswahl oder Durchführung nicht nennenswert mitwirken und beteiligt sich nicht oder nur minimal.

### F4.6.4 - Vornehmen von in die Zukunft gerichteten Planungen
Über den Tag hinaus planen, Zeitabschnitte überblicken und zukünftige Vorhaben einordnen.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person nimmt sich etwas vor, muss aber an die Durchführung erinnert werden oder benötigt Hilfe bei der Abstimmung mit anderen.
- **Überwiegend unselbständig**: Person plant nicht selbständig, kann aber mit Unterstützung entscheiden und benötigt Erinnerung, emotionale oder körperliche Unterstützung bei der Umsetzung.
- **Unselbständig**: Person hat keine ausreichenden Zeitvorstellungen für Planungen über den Tag hinaus und signalisiert auch bei Auswahloptionen keine Zustimmung oder Ablehnung.

### F4.6.5 - Interaktion mit Personen im direkten Kontakt
Im direkten Kontakt mit Angehörigen, Pflegepersonen, Mitbewohnern oder Besuchern umgehen, Kontakt aufnehmen und auf Ansprache reagieren.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Interaktion mit vertrauten Personen gelingt selbständig; bei fremden Personen oder Kommunikationsproblemen ist punktuelle Unterstützung nötig.
- **Überwiegend unselbständig**: Person ergreift kaum Initiative, reagiert aber nach Ansprache oder Motivation verbal oder nonverbal erkennbar.
- **Unselbständig**: Person reagiert nicht nennenswert auf Ansprache oder nonverbale Kontaktversuche.

### F4.6.6 - Kontaktpflege zu Personen außerhalb des direkten Umfelds
Bestehende Kontakte zu Freunden, Bekannten oder Nachbarn aufrechterhalten, beenden oder zeitweise ablehnen, auch über Telefon, Briefe oder digitale Kommunikation.

- **Selbständig**: Person kann die Aktivität ohne personelle Hilfe durchführen.
- **Überwiegend selbständig**: Person kann Kontakte planen, benötigt aber Hilfe bei Umsetzung, Erinnerung, Telefonnummern, Terminabsprachen oder beim Herstellen des Kontakts.
- **Überwiegend unselbständig**: Kontaktgestaltung ist reaktiv; Person wirkt mit, wenn andere die Initiative ergreifen oder bei der Kontaktaufnahme unterstützen.
- **Unselbständig**: Person nimmt keinen Kontakt außerhalb des direkten Umfelds auf und reagiert nicht auf Anregungen zur Kontaktaufnahme.

---

## Feld-Erklärungen

- **id**: Eindeutige Kennzeichnung für jedes Benchmark-Item, z. B. "M1_012", zur Identifizierung und Referenzierung.
- **module**: Gibt das Modul an (z. B. "M1" für Mobilität), das sich in Inhalt, Bewertungssystem und Gewichtung unterscheidet.
- **criterion**: Beschreibt das konkrete Kriterium, das bewertet wird, z. B. "treppensteigen"; ermöglicht Unterscheidung ähnlicher Items mit unterschiedlicher Bedeutung (z. B. Treppensteigen vs. Fortbewegung in der Wohnung).
- **scale_type**: Definiert die Antwortskala, z. B. "selbststaendigkeit" (für M1); unterscheidet sich zwischen Modulen (z. B. "selbständig" in M1 vs. "täglich" in M2).
- **stem**: Der Text der Frage oder Aussage, die bewertet wird, z. B. „Die versicherte Person schafft wenige Stufen allein, über eine Etage muss sie gestützt werden.“.
- **options**: Liste der möglichen Antwortoptionen, z. B. ["selbständig", "überwiegend selbständig", "überwiegend unselbständig", "unselbständig"]; definiert die Skala für die Bewertung.
- **answer_idx**: Index der korrekten Antwort in der Optionsliste, z. B. 2 (für "überwiegend unselbständig").
- **frequency_count**: Nur Modul 5: Anzahl der erforderlichen Hilfen/Maßnahmen. 
- **frequency_unit**: Nur Modul 5: Einheit der Häufigkeit, z. B. pro_tag, pro_woche, pro_monat. 
- **rationale_options**: Liste der möglichen Begründungen im Format "F4.x.x: Beschreibung = Antwortstufe", z. B. ["F4.1.1: mit Hilfsmitteln allein = selbständig", "F4.1.5: erhebliche Hilfe/Stützen = überwiegend unselbständig"]. Jeder Eintrag entspricht einer Kombination aus Referenz, Bedingung und Antwortstufe.
- **rationale_id**: Index der korrekten Begründung in der rationale_options-Liste, z. B. 18 (für "F4.1.5: erhebliche Hilfe/Stützen = überwiegend unselbständig"). Ermöglicht die Zuordnung der Antwort zur passenden Referenz.
- **point_scale_options**: Liste der möglichen Punktzuordnungen aus der Begutachtungsrichtlinie. Bei Standard-Skalen entspricht jeder Eintrag einer Antwortstufe; bei Sonderregeln, z. B. Modul 4 Essen/Trinken/Toilette/Sondenernährung oder Modul 5 Häufigkeiten, beschreibt jeder Eintrag die passende Bewertungslogik.
- **point_scale_id**: Index des passenden Eintrags in der point_scale_options-Liste.
- **point_value**: Einzelpunktwert bzw. Zwischenergebnis-Punktwert, der sich aus Antwort, Kriterium und ggf. Häufigkeit ergibt.
- **split**: Zuordnung zu Train/Test-Split, z. B. "test".
- **model**: Bezeichnet die Modellfamilie oder den Modellnamen, mit dem das Item beantwortet oder ausgewertet wurde, z. B. "ChatGPT", "Claude" oder "Gemini".
- **model_version**: Gibt die genaue Modellversion an, um Ergebnisse eindeutig einer konkreten Modellvariante zuordnen zu können, z. B. "5.4", "Sonnet 4.6" oder "2.5 Pro".
- **temperature**: Gibt den beim Modelllauf verwendeten Temperature-Wert an. Der Wert kann null sein, wenn er nicht bekannt oder nicht dokumentiert ist, oder als numerischer Wert zwischen 0.1 und 2 gespeichert werden. Niedrigere Werte stehen in der Regel für deterministischere, höhere Werte für variablere Antworten.