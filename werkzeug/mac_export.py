#!/usr/bin/env python3
"""Kopie der Datenbank für den Mac-Ordner „Galopp Projekte/Bilder/Rennfarben/Datenbank“ (zum Ansehen, Katalog,
ältere Mac-Werkzeuge). Format wie bisher: Rennfarben.json {besitzer: {name: {..., svg}}}, SVG/, Katalog.html,
LIESMICH.md. Nur eine KOPIE: gepflegt wird ausschließlich im Repo galopp-rennfarben.

    python3 werkzeug/mac_export.py "<Zielordner>"
"""
import json, os, shutil, sys
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WURZEL, "werkzeug"))
import export

def main(ziel):
    roh = json.load(open(os.path.join(WURZEL, "rennfarben.json"), encoding="utf-8"))
    index = json.load(open(os.path.join(WURZEL, "index.json"), encoding="utf-8"))["besitzer"]
    os.makedirs(os.path.join(ziel, "SVG"), exist_ok=True)
    db = {}
    for name, v in roh["besitzer"].items():
        quelle = index.get(name)
        if not quelle:
            continue
        datei = os.path.basename(quelle)
        shutil.copyfile(os.path.join(WURZEL, quelle), os.path.join(ziel, "SVG", datei))
        db[name] = dict(v, svg="SVG/" + datei)
        db[name].pop("svg_override", None)
    json.dump({"_stand": roh.get("_stand"), "_anzahl": len(db), "besitzer": db},
              open(os.path.join(ziel, "Rennfarben.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    shutil.copyfile(os.path.join(WURZEL, "katalog.html"), os.path.join(ziel, "Katalog.html"))
    open(os.path.join(ziel, "LIESMICH.md"), "w", encoding="utf-8").write(
        "# Rennfarben-Datenbank (Kopie)\n\nDies ist nur eine KOPIE der einen Trikot-Datenbank aller Galopp-Projekte.\n"
        "Gepflegt wird ausschließlich im Repo https://github.com/SebastianWeiss1102/galopp-rennfarben (Regeln im README dort).\n"
        "Hier nichts von Hand ändern: wird mit `werkzeug/mac_export.py` neu erzeugt.\n\n%d Besitzer, Stand %s.\n" % (len(db), roh.get("_stand")))
    print(len(db), "Besitzer nach", ziel)

if __name__ == "__main__":
    main(sys.argv[1])
