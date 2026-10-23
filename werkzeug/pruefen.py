#!/usr/bin/env python3
"""Pruefung der Trikot-Datenbank (laeuft bei jedem Push, Workflow „Pruefen“).

- jede Zeichnung nutzt nur Muster, die trikot.py kennt (unbekannte Muster wuerden still einfarbig)
- keine zwei Eintraege mit gleicher Schreibweise und verschiedener Zeichnung
- jede DG-Farbnummer hoechstens bei einem Besitzer; Sonderzeichnungen vorhanden
- keine internen Quellenangaben im oeffentlichen Repo
"""
import json, os, re, sys
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WURZEL); sys.path.insert(0, os.path.join(WURZEL, "werkzeug"))
import trikot, suche

def bekannte_muster():
    s = open(os.path.join(WURZEL, "trikot.py"), encoding="utf-8").read()
    teil = s[s.index("def muster("):]
    return set(re.findall(r'art (?:==|in)\s*\(?([^:]+)', teil) and
               re.findall(r'"([a-z0-9_]+)"', " ".join(re.findall(r'art (?:==|in) ([^:]+):', teil)))) | {"einfarbig", None, ""}

def main():
    fehler = []
    roh = json.load(open(os.path.join(WURZEL, "rennfarben.json"), encoding="utf-8"))["besitzer"]
    dg = json.load(open(os.path.join(WURZEL, "rennfarben-dg.json"), encoding="utf-8"))["dg"]
    m = bekannte_muster() | {"kreuzband_r2", "drei_scheiben", "drei_schraeg_r", "fenster"}
    for quelle, daten in (("Besitzer", roh), ("DG", dg)):
        for k, v in daten.items():
            for t in ("koerper_muster", "aermel_muster"):
                if v.get(t) not in m and not str(v.get(t)).startswith("buchstabe_"):
                    fehler.append(f"{quelle} {k}: unbekanntes Muster {v.get(t)}")
            for verboten in ("quelle", "quellen", "lokale_vorlage", "vorlage"):
                if verboten in v:
                    fehler.append(f"{quelle} {k}: interne Angabe '{verboten}' gehoert nicht ins oeffentliche Repo")
            if v.get("svg_override") and not os.path.exists(os.path.join(WURZEL, v["svg_override"])):
                fehler.append(f"{k}: Sonderzeichnung fehlt {v['svg_override']}")
    for k, v in roh.items():
        for i in v.get("dg_ids") or []:
            if i in dg and dg[i].get("svg_override") and v.get("svg_override") != dg[i]["svg_override"]:
                fehler.append(f"{k}: bestätigt für DG {i}, zeigt aber eine andere Zeichnung (ein Trikot je Farbnummer)")
    vor = json.load(open(os.path.join(WURZEL, "rennfarben-vorlagen.json"), encoding="utf-8"))["vorlagen"]
    for md5, v in vor.items():
        if not os.path.exists(os.path.join(WURZEL, v["svg_override"])):
            fehler.append(f"Vorlage {md5}: Zeichnung fehlt")
    for i, v in dg.items():
        if v.get("svg_override") and not os.path.exists(os.path.join(WURZEL, v["svg_override"])):
            fehler.append(f"DG {i}: Zeichnung fehlt")
    dg_bei = {}
    for k, v in roh.items():
        for i in v.get("dg_ids") or []:
            dg_bei.setdefault(i, []).append(k)
    fehler += [f"DG-Farbnummer {i} bei mehreren Besitzern: {n}" for i, n in dg_bei.items() if len(n) > 1]
    gruppen = {}
    for k, v in roh.items():
        gruppen.setdefault(suche.schreibweise(k), []).append((k, tuple(v.get(x) for x in trikot._ZEICHNUNG)))
    for s, liste in gruppen.items():
        if len({z for _, z in liste}) > 1:
            print("Hinweis, gleiche Schreibweise mit verschiedenen Zeichnungen:", [n for n, _ in liste])
    for f in fehler:
        print("FEHLER", f)
    print(len(roh), "Besitzer,", len(dg), "DG-Farbnummern,", len(fehler), "Fehler")
    return 1 if fehler else 0

if __name__ == "__main__":
    sys.exit(main())
