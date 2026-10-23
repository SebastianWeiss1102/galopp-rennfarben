#!/usr/bin/env python3
"""Besitzer oder DG-Rennfarben-ID in der einen Trikot-Datenbank finden.

    python3 werkzeug/suche.py "Gestüt Brümmerhof"
    python3 werkzeug/suche.py "Team Valor/England" 23096897

Regel: Steht ein Besitzer hier, wird dieses Trikot verwendet. Neu gezeichnet wird nur, wenn nichts gefunden wird,
und dann HIER eingetragen (siehe README.md). Der Länderzusatz von Deutscher Galopp („/England“) wird ignoriert.
"""
import json, os, re, sys, unicodedata
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WURZEL)
import trikot

LAND = re.compile(r"\s*/\s*(England|Frankreich|Irland|Italien|Belgien|Niederlande|Holland|Schweden|Norwegen|Dänemark|"
                  r"Tschechien|Polen|Ungarn|Österreich|Schweiz|USA|Japan|Spanien|Katar|VAE|Deutschland|Slowakei|"
                  r"Australien|Hongkong|Saudi-Arabien|Bahrain)\s*$")

def ohne_land(name):
    return LAND.sub("", (name or "").strip())

def schreibweise(name):
    v = unicodedata.normalize("NFKD", ohne_land(name)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", v)

_DB = None
def db():
    global _DB
    if _DB is None:
        trikot.laden(os.path.join(WURZEL, "rennfarben.json"))
        dg = json.load(open(os.path.join(WURZEL, "rennfarben-dg.json"), encoding="utf-8"))["dg"]
        idx = {}
        for k, v in trikot.FARBEN.items():
            idx.setdefault(schreibweise(k), (k, v))
        _DB = (idx, dg)
    return _DB

def besitzer(name):
    """(Name in der Datenbank, Eintrag) oder None. Genaue Schreibweise, dann ohne Länderzusatz/Sonderzeichen,
    dann die Namenslogik von trikot.py (Titel, Firmenendungen, Reihenfolge von Gemeinschaften)."""
    idx, _ = db()
    if name in trikot.FARBEN:
        return name, trikot.FARBEN[name]
    t = idx.get(schreibweise(name))
    if t:
        return t
    f = trikot._finden(ohne_land(name))
    return (ohne_land(name), f) if f else None

def _absolut(e):
    if e and e.get("svg_override") and not os.path.isabs(e["svg_override"]):
        e = dict(e, svg_override=os.path.join(WURZEL, e["svg_override"]))
    return e

def dg_zeichnung(dg_id):
    return _absolut(db()[1].get(str(dg_id)))

_VOR = None
def vorlage(pruefsumme):
    """Zeichnung zu einer Bildvorlage (z. B. frühere Renntage), unverändert so, wie sie geprüft wurde."""
    global _VOR
    if _VOR is None:
        _VOR = json.load(open(os.path.join(WURZEL, "rennfarben-vorlagen.json"), encoding="utf-8"))["vorlagen"]
    return _absolut(_VOR.get(pruefsumme))

def trikot_fuer(name, dg_id=None):
    """Was ein Projekt fuer einen Starter verwenden soll.
    Mit amtlicher Farbnummer (deutsche Rennen): zuerst die Zeichnung dieser Farbnummer, denn Besitzernamen sind
    weltweit nicht eindeutig (es gibt z. B. eine andere „ACE Racing“ im Ausland). Sonst der Besitzer.
    "bestaetigt": Besitzer und Farbnummer sind gegeneinander geprüft (dg_ids) bzw. es ist die amtliche Farbnummer."""
    if dg_id and dg_zeichnung(dg_id):
        return {"quelle": "dg", "name": str(dg_id), "eintrag": dg_zeichnung(dg_id), "bestaetigt": True}
    t = besitzer(name)
    if t:
        ok = bool(dg_id) and str(dg_id) in (t[1].get("dg_ids") or [])
        return {"quelle": "besitzer", "name": t[0], "eintrag": t[1], "bestaetigt": ok or not dg_id}
    return None

if __name__ == "__main__":
    r = trikot_fuer(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps(r, ensure_ascii=False, indent=1) if r else "nicht gefunden: neu zeichnen und hier eintragen")
