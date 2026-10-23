#!/usr/bin/env python3
"""Erzeugt aus der Datenbank die fertigen Bilder (laeuft automatisch bei jedem Push, Workflow „Pruefen“).

  svg/<Besitzer>.svg     ein Trikot je Besitzer
  svg-dg/<DG-ID>.svg     ein Trikot je amtlicher Rennfarben-ID von Deutscher Galopp
  index.json             Besitzer und DG-ID -> Bilddatei (fuer Projekte, die nur Bilder brauchen)
  katalog.html           alle Trikots auf einer Seite, mit Suche

Von Hand nichts in svg/, svg-dg/, index.json oder katalog.html aendern: wird neu erzeugt.
"""
import html, json, os, re, shutil, sys
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WURZEL)
import trikot

def dateiname(name):
    return (re.sub(r'[\\/:*?"<>|]+', "-", name).strip(" .")[:120] or "ohne-name") + ".svg"

def svg_von(v, kennung):
    if v.get("svg_override"):
        return open(os.path.join(WURZEL, v["svg_override"]), encoding="utf-8").read()
    return trikot.zeichnen(v, kennung).replace("<svg class='trikot'", "<svg xmlns='http://www.w3.org/2000/svg' class='trikot'", 1)

def main():
    roh = json.load(open(os.path.join(WURZEL, "rennfarben.json"), encoding="utf-8"))["besitzer"]
    dg = json.load(open(os.path.join(WURZEL, "rennfarben-dg.json"), encoding="utf-8"))["dg"]
    for o in ("svg", "svg-dg"):
        shutil.rmtree(os.path.join(WURZEL, o), ignore_errors=True); os.makedirs(os.path.join(WURZEL, o))
    index, karten, vergeben = {"besitzer": {}, "dg": {}}, [], set()
    for n, (name, v) in enumerate(roh.items()):
        if not v.get("koerper_grund") and not v.get("svg_override"):
            continue
        datei = dateiname(name); z = 2
        while datei.lower() in vergeben:
            datei = dateiname(name)[:-4] + " (%d).svg" % z; z += 1
        vergeben.add(datei.lower())
        svg = svg_von(v, "b%d" % n)
        open(os.path.join(WURZEL, "svg", datei), "w", encoding="utf-8").write(svg)
        index["besitzer"][name] = "svg/" + datei
        for a in v.get("aliase") or []:
            index["besitzer"].setdefault(a, "svg/" + datei)
        such = " ".join([name] + (v.get("aliase") or []) + (v.get("dg_ids") or [])).lower()
        karten.append("<figure data-such='%s'>%s<figcaption><b>%s</b><span>%s</span></figcaption></figure>" % (
            html.escape(such, True), svg, html.escape(name), html.escape(v.get("beschreibung") or v.get("farben_offiziell") or "")))
    for i, v in dg.items():
        open(os.path.join(WURZEL, "svg-dg", i + ".svg"), "w", encoding="utf-8").write(svg_von(v, "d" + i))
        index["dg"][i] = "svg-dg/%s.svg" % i
    json.dump(index, open(os.path.join(WURZEL, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    open(os.path.join(WURZEL, "katalog.html"), "w", encoding="utf-8").write(
        "<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
        "<title>Galopp-Rennfarben</title><style>body{font:14px system-ui,sans-serif;margin:24px;color:#1b3b55}"
        "input{font:inherit;padding:8px 12px;width:min(320px,100%%);margin:14px 0;border:1px solid #cdddeb;border-radius:8px}"
        "main{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}"
        "figure{margin:0;padding:10px;border:1px solid #e3ebf2;border-radius:10px;text-align:center}"
        "figure svg{width:80px;height:80px}figcaption b{display:block;font-size:12.5px;margin-top:6px}"
        "figcaption span{display:block;font-size:11px;color:#617180}</style>"
        "<h1>Galopp-Rennfarben</h1><p>%d Besitzer, %d amtliche Farbnummern.</p>"
        "<input placeholder='Besitzer oder DG-Nummer suchen' oninput=\"for(const f of document.querySelectorAll('figure'))"
        "f.hidden=!f.dataset.such.includes(this.value.toLowerCase())\"><main>%s</main>" % (len(index["besitzer"]), len(dg), "".join(karten)))
    print(len(index["besitzer"]), "Besitzer-Eintraege,", len(dg), "DG-Farbnummern exportiert")

if __name__ == "__main__":
    main()
