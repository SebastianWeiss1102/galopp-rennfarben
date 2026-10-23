# Galopp-Rennfarben · die eine Trikot-Datenbank aller Galopp-Projekte

Seit 23.10.2026 die **einzige** Quelle für Trikots (Rennfarben) in allen Galopp-Projekten von Sebastian Weiss:
G1Stars, GaloppFacts, ClassicWinners, Meetings, YearlingStars, SireStars und Fantasy Galopp.
Kein Projekt führt eine eigene Trikot-Sammlung oder ein eigenes Zeichenprogramm.

Das Repo ist öffentlich lesbar: Jedes Projekt, jeder Programmierer und jede Automatik kommt ohne Schlüssel dran.
Interne Angaben (woher eine Vorlage stammt) stehen nicht hier, sondern privat im G1Stars-Repo
(`daten/gemeinsam/rennfarben_quellen.json`).

## Inhalt

| Datei | Was |
|---|---|
| `rennfarben.json` | je Besitzer die Zeichenangaben (Grundfarbe, Muster, Zweit-/Drittfarbe für Körper und Ärmel, ggf. Schriftzug), Schreibweisen (`aliase`), amtliche Beschreibung (`farben_offiziell`), amtliche Farbnummern (`dg_ids`) |
| `rennfarben-dg.json` | Zeichnungen je amtlicher Rennfarben-ID von Deutscher Galopp (`dg_silk`), für Starter, deren Besitzer noch nicht unter `besitzer` steht |
| `trikot.py` | **das eine Zeichenprogramm**: `trikot.laden()`, `trikot.trikot(besitzer)`, `trikot.zeichnen(eintrag, kennung)` |
| `zeichnungen/` | handgezeichnete Sondertrikots (`svg_override`) |
| `werkzeug/suche.py` | Besitzer/DG-Nummer finden: `python3 werkzeug/suche.py "Team Valor/England" 23096897` |
| `werkzeug/pruefen.py` | Prüfung (läuft bei jedem Push) |
| `werkzeug/export.py` | erzeugt `svg/`, `svg-dg/`, `index.json`, `katalog.html` (läuft bei jedem Push) |
| `katalog.html` | alle Trikots auf einer Seite mit Suche |

## So nutzt ein Projekt die Datenbank

In GitHub Actions (öffentlich, kein Schlüssel):

```yaml
- uses: actions/checkout@v4
  with:
    repository: SebastianWeiss1102/galopp-rennfarben
    path: rennfarben
```

Im Code:

```python
import sys; sys.path.insert(0, "rennfarben"); sys.path.insert(0, "rennfarben/werkzeug")
import trikot, suche
trikot.laden("rennfarben/rennfarben.json")
treffer = suche.trikot_fuer("Gestüt Brümmerhof", dg_id="1594762")   # zuerst Besitzer, dann DG-Nummer
svg = trikot.zeichnen(treffer["eintrag"], "k1")
```

Nur Bilder: `index.json` zeigt je Besitzer und DG-Nummer auf die Datei in `svg/` bzw. `svg-dg/`, abrufbar über
`https://raw.githubusercontent.com/SebastianWeiss1102/galopp-rennfarben/main/<Pfad>`.

## Regeln (verbindlich für alle Projekte)

1. **Erst suchen, nie zuerst zeichnen.** `werkzeug/suche.py` findet Besitzer auch mit Länderzusatz von Deutscher
   Galopp („/England“), anderer Schreibweise, Titeln und Firmenendungen. Steht der Besitzer hier, wird **dieses**
   Trikot verwendet.
2. **Fehlt ein Trikot:** aus der amtlichen Beschreibung bzw. Bildvorlage (Deutscher Galopp, sonst der zuständige
   Verband) mit `trikot.py` zeichnen, mit der Vorlage vergleichen und **hier** eintragen (Besitzer mit `dg_ids`,
   Schreibweisen in `aliase`). Nie im Projekt selbst ablegen. Keine neutralen Ersatztrikots, keine fremden Bilder.
3. **Fehler werden hier korrigiert**, nicht im Projekt. Danach ziehen alle Projekte die Korrektur beim nächsten Lauf.
4. **Pro Besitzer bzw. pro DG-Farbnummer genau eine Zeichnung.** Bewusste historische Farben eines Besitzers stehen
   als eigener Eintrag mit `historisch`.
5. **Neue Muster** nur in `trikot.py` ergänzen. `werkzeug/pruefen.py` schlägt fehl, wenn Daten ein Muster benutzen,
   das `trikot.py` nicht kennt (früher wurden solche Trikots still einfarbig).
6. Sichtvergleich: Muster müssen dasselbe Element zeigen (Schnüre sind keine Punkte, ein Winkel ist kein dreifacher
   Winkel). Farbtöne derselben Farbfamilie gelten als gleich.

## Schreiben

Lesen ist frei. Schreiben dürfen Sebastian, eingeladene Programmierer und die Automatiken von G1Stars und
GaloppFacts (über das Secret `RENNFARBEN_TOKEN` in deren Repos). Jede Änderung läuft durch `werkzeug/pruefen.py`.

## Geschichte

Bis 23.10.2026 lag der Master im G1Stars-Repo (`daten/gemeinsam/rennfarben.json`), GaloppFacts hatte zusätzlich
eigene Sammlungen und ein abweichendes Zeichenprogramm. Folge: derselbe Besitzer sah je nach Seite verschieden aus
(Gestüt Brümmerhof mit Punkten statt Schnüren), und vorhandene Besitzer wurden neu gezeichnet (Team Valor). Beim
Zusammenführen wurden beide Zeichenprogramme vereint (alle Muster beider Projekte; gleichnamige, aber verschieden
gezeichnete GaloppFacts-Muster tragen die Endung `_gf`), 431 GaloppFacts-Besitzer und 3.782 DG-Farbnummern
übernommen und die am 23.10. gegen die DG-Vorlagen geprüften Korrekturen eingetragen.
