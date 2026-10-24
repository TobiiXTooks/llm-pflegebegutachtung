# Pflegebegutachtung – MC (Module F4.1–F4.6)

Format je Zeile (JSONL):
```
{
  "id": "M1_012",
  "stem": "Der Versicherte schafft wenige Stufen allein, über eine Etage muss er gestützt werden.",
  "options": ["selbständig","überwiegend selbständig","überwiegend unselbständig","unselbständig"],
  "answer_idx": 2,
  "rationale": "F4.1.5: nur mit Stütze möglich = überwiegend unselbständig",
  "tags": ["pflegegutachten","mobilität","treppensteigen"],
  "difficulty": "mittel",
  "source": "pflegegutachten_poc_v0_1",
  "lang": "de"
}
```

Vorhersagen (JSONL):
```
{"id": "M1_012", "pred_idx": 2}
```
