"""Offizielle deutsche Farbbeschreibung (Deutscher Galopp) -> Trikot-Eintrag (25.09.2026).

    from wortlaut import lesen
    e = lesen("rot, weißer Stern, Ärmel u. Kappe weiß, rote Sterne")

Liefert einen Eintrag im Format von rennfarben.json (koerper_grund, koerper_muster, ...),
dazu '_unsicher' mit allem, was nicht gelesen werden konnte (z. B. Embleme, Logos).
Die Kappe wird nicht gezeichnet; alles ab der Kappe wird ignoriert.
"""
import re

FARBE = {
    "weiß": "#FFFFFF", "weiss": "#FFFFFF", "schwarz": "#111111", "rot": "#EE1C25", "hellrot": "#FF6670", "dunkelrot": "#B00010",
    "bordeauxrot": "#A0103E", "weinrot": "#A01040", "purpurrot": "#9B1B4E", "rotbraun": "#8A2A10", "kirschrot": "#B0102A",
    "blau": "#2A86E8", "königsblau": "#2A6AE0", "dunkelblau": "#1A2FB8", "hellblau": "#A8DAF8", "himmelblau": "#8CC8F0",
    "marineblau": "#16284F", "türkis": "#33D8B4", "petrol": "#1A6A7A",
    "grün": "#36B94A", "dunkelgrün": "#0E7A2C", "hellgrün": "#B4F07A", "olivgrün": "#5A9100", "smaragdgrün": "#2FB060", "lindgrün": "#B4E05A",
    "gelb": "#FAEC1A", "hellgelb": "#FBF08A", "gold": "#F0C818", "altgold": "#D8B800", "orange": "#FF7A1E", "hellorange": "#F8B060",
    "braun": "#7A4214", "dunkelbraun": "#5A2E0C", "hellbraun": "#B08050", "goldbraun": "#9A6A1F", "beige": "#E8C79A", "champagnerfarben": "#F2E4C8",
    "grau": "#888888", "silbergrau": "#B4B4B4", "silber": "#B4B4B4", "hellgrau": "#C8C8C8", "dunkelgrau": "#5A5A5A", "anthrazit": "#3A3A3A",
    "lila": "#A87DF0", "helllila": "#C4A4F4", "dunkellila": "#6632B2", "violett": "#7A4AE0", "mauve": "#B48CE6", "flieder": "#C8A8F0",
    "rosa": "#F78CD8", "braunrot": "#8A2A10", "kardinalrot": "#C0102A", "bronzebraun": "#8A5A2A", "hellbau": "#8CC8F0", "dunkelviolett": "#4A1A7A", "hellviolett": "#A07AD8", "kobaldblau": "#1F3AB0", "kobaltblau": "#1F3AB0", "azurblau": "#2A8AE0", "silberggrau": "#B4B4B4", "dunkelgelb": "#E8C000", "zitronengelb": "#FBF03A", "moosgrün": "#4A6A2A", "tannengrün": "#0E4A2C", "maisgelb": "#F8D040", "golden": "#F0C818", "altgolden": "#D8B800", "silbern": "#B4B4B4", "hellgolden": "#E8C860", "cremefarben": "#FBF3DC", "altrosa": "#E0A8A8", "pink": "#E83CA0", "magenta": "#D01E8A", "cremefarben": "#FBF3DC", "creme": "#FBF3DC",
}
KURZ = {"schw": "schwarz", "dbl": "dunkelblau", "sgr": "silbergrau", "dgr": "dunkelgrün", "hbl": "hellblau", "hgr": "hellgrün",
        "bl": "blau", "w": "weiß", "g": "gold", "r": "rot", "gr": "grün", "o": "orange", "b.rote": "bordeauxrot", "b.rot": "bordeauxrot",
        "dkl.bl": "dunkelblau", "dkl.rot": "dunkelrot", "dkl.rote": "dunkelrot", "gold": "gold", "gelbe": "gelb", "borrdeaur": "bordeauxrot",
        "bordeauxr": "bordeauxrot", "or": "orange", "hellor": "hellorange", "hellor.": "hellorange", "vio": "violett", "türk": "türkis", "gel": "gelb", "ro": "rot"}


def farbe(wort):
    """'rote' -> '#E3202A'; None, wenn kein Farbwort."""
    w = wort.lower().strip(" .")
    w = KURZ.get(w, w)
    if w in FARBE: return FARBE[w]
    for end in ("en", "er", "es", "em", "e"):
        if w.endswith(end) and w[:-len(end)] in FARBE: return FARBE[w[:-len(end)]]
        if w.endswith(end) and KURZ.get(w[:-len(end)]) in FARBE: return FARBE[KURZ[w[:-len(end)]]]
    if w + "e" in FARBE: return FARBE[w + "e"]
    for end in ("r", "s", "n", "m"):   # oranger, beiger, rosas
        if w.endswith(end) and w[:-1] in FARBE: return FARBE[w[:-1]]
    return None


def farben(wort):
    """'blau-weiß' -> ['#..', '#..']; leere Liste, wenn kein Farbwort."""
    teile = [farbe(x) for x in wort.split("-")]
    return teile if teile and all(teile) else []


# Musterwoerter fuer zweifarbige Flaechen: "blau-gelb gevierteilt"
FLAECHE = [("diag. gev", "sanduhr"), ("diagonal gevierteilt", "sanduhr"), ("diag. geviert", "sanduhr"),
           ("schräg geteilt", "diagonal_gespalten"), ("schräg gestreift", "diagonalstreifen"), ("schräg gestr", "diagonalstreifen"),
           ("quer gestreift", "querstreifen"), ("quer geteilt", "quer_gespalten"), ("quer get", "quer_gespalten"),
           ("längs geteilt", "gespalten"), ("gevierteilt", "quartiert"), ("geviert", "quartiert"), ("gev", "quartiert"),
           ("gestreift", "laengsstreifen"), ("gestr", "laengsstreifen"), ("kariert", "karo"), ("gerautet", "harlekin"),
           ("geringelt", "querstreifen"), ("geteilt", "gespalten"), ("gewürfelt", "karo")]
AERMEL_FLAECHE = {"querstreifen": "querstreifen", "laengsstreifen": "laengsstreifen", "karo": "karo", "harlekin": "harlekin",
                  "quartiert": "manschetten", "quer_gespalten": "manschetten", "gespalten": "laengsstreifen", "sanduhr": "manschetten",
                  "diagonal_gespalten": "manschetten", "diagonalstreifen": "querstreifen"}

# Koerper-Elemente: Substantiv -> Muster (Einzahl, Mehrzahl)
KOERPER = [("andreaskreuz", "kreuzbaender"), ("schärpen über kreuz", "kreuzbaender"), ("regenbogenfarbende schärpe", "regenbogen"), ("regenbogen", "regenbogen"), ("schärpen ü. kr", "kreuzbaender"), ("schärpen", "kreuzbaender"),
           ("schärpe", "kreuzband_r"), ("schrägstrich", "kreuzband_r"), ("schrägstreifen", "drei_schraeg"), ("querstreifen", "band"), ("gürtel", "band"),
           ("malteserkreuz", "kreuz"), ("lothringer kreuz", "kreuz"), ("kreuz", "kreuz"),
           ("streifen", "streifen_breit"), ("sterne", "sterne"), ("stern", "stern"), ("punkte", "punkte"), ("punkt", "scheibe"),
           ("rauten", "rauten"), ("raute", "raute"), ("diamant", "raute"), ("karo", "raute"), ("winkel", "spitzen"), ("v-einsatz", "dreieck_unten_gross"),
           ("v", "v"), ("schultern", "epauletten"), ("schulterstück", "joch"), ("nähte", "naht"), ("schnüre", "litzen"), ("ring", "ring"),
           ("kleeblatt", "kleeblatt"), ("herz", "herz"), ("halbmond", "halbmond"), ("hufeisen", "buchstabe_U"), ("lilie", "lilie"),
           ("dreieck", "dreieck"), ("quadrat", "quadrat"), ("keil", "dreieck_unten"), ("wappen", "wappen"), ("sonne", "scheibe"),
           ("kreis", "ring"), ("scheibe", "scheibe"), ("schmetterling", "schmetterling"), ("sterne", "sterne")]
AERMEL = [("armbinden", "armringe"), ("armb", "armringe"), ("armringe", "armringe"), ("armring", "armband"), ("armbinde", "armband"),
          ("aufschläge", "manschetten"), ("aufschl", "manschetten"), ("sterne", "sterne"), ("stern", "sterne"), ("punkte", "punkte"),
          ("streifen", "aermelstreifen"), ("rauten", "rauten"), ("nähte", "naht"), ("winkel", "spitzen"), ("str", "aermelstreifen")]
ZAHL = {"zwei": 2, "drei": 3, "vier": 4, "fünf": 5}


def _norm(t):
    t = t.replace(" ", " ")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def lesen(text):
    e = {"_unsicher": []}
    if not text or text.lower().startswith("keine"):
        return None
    segs = [_norm(s) for s in _norm(text).split(",")]
    koerper_elemente = []      # (muster, farbe, [dritt])
    aermel_gesehen = False
    zuletzt_farbe = None
    for i, seg in enumerate(segs):
        s = seg.lower()
        if not s: continue
        # Kappe erreicht: Rest gehoert zur Kappe
        kappe = re.search(r"(?:^|\s)(kappe|k\.|k$|quaste|schirm)(?=\s|$|,)", s)
        vor_kappe = s[:kappe.start()].strip() if kappe else s
        vor_kappe = re.sub(r"\b(u\.|und)$", "", vor_kappe).strip()
        if kappe and i > 0 and not re.search(r"(?:^|\s)(ärmel|armb\S*|armr\S*|aufschl\S*|schärpe\S*|stern\S*|punkt\S*|streifen|raute|rauten|gürtel|schulter\S*|naht|nähte|kreuz|v|winkel|ring)(?=\s|$)", vor_kappe):
            break
        if i == 0:
            # Grund: "rot" oder "blau-gelb gevierteilt" oder "schwarz-weiß gestreift"
            m = re.match(r"([a-zäöüß.\-]+)(?:\s+(.*))?$", vor_kappe)
            fs = farben(m.group(1)) if m else []
            rest = (m.group(2) or "") if m else ""
            if not fs:
                e["_unsicher"].append(seg); continue
            e["koerper_grund"] = fs[0]
            if len(fs) >= 2:
                art = next((a for k, a in FLAECHE if rest.startswith(k)), None)
                if art:
                    e["koerper_muster"] = art; e["koerper_zweit"] = fs[1]
                    if art == "sanduhr": e["koerper_grund"], e["koerper_zweit"] = fs[1], fs[0]
                    if len(fs) >= 3 and art in ("laengsstreifen", "querstreifen", "quer_gespalten"):
                        if art != "quer_gespalten": e["_unsicher"].append("dreifarbig: " + seg)
                        if art == "quer_gespalten": e["koerper_muster"] = "dreifarbig_quer"; e["koerper_dritt"] = fs[2]; e["koerper_zweit"] = fs[0]; e["koerper_grund"] = fs[1]
                else:
                    e["_unsicher"].append(seg)
            elif rest:
                e["_unsicher"].append(seg)
            if kappe: break
            continue
        # "Ärmel u. Kappe weiß" (Farbe nachgestellt)
        m = re.match(r"ärmel (?:u\.|und) kappe ([a-zäöüß.]+)", s)
        if m and farbe(m.group(1)):
            e["aermel_grund"] = farbe(m.group(1)); aermel_gesehen = True; break
        # Aufzaehlung "gelbe Schärpe u. Ärmel", "rote Schärpe, Armbinden und Kappe"
        woerter = vor_kappe.split(" ")
        anzahl = None
        if woerter and woerter[0] in ZAHL:
            anzahl = ZAHL[woerter[0]]; woerter = woerter[1:]
        fs = farben(woerter[0]) if woerter else []
        if fs:
            zuletzt_farbe = fs; woerter = woerter[1:]
        elif woerter and woerter[0] in ("ein", "eine", "einen"):
            woerter = woerter[1:]
        nomen = " ".join(woerter)
        # Nomen koennen mit u./und verbunden sein
        glieder = [g.strip() for g in re.split(r"\s+(?:u\.|und)\s+|\s+u\.$", nomen) if g.strip()]
        if not glieder and kappe and fs:
            break
        f = zuletzt_farbe or []
        for g in glieder:
            gl = g.lower()
            if gl.startswith("ärmel") or gl.endswith("ärmel") or " ärmel" in gl:
                aermel_gesehen = True
                vor = gl.replace("ärmel", "").strip()
                art = next((a for k, a in FLAECHE if vor.startswith(k)), None) if vor else None
                if vor.startswith("gewinkelt"):
                    art = "spitzen"
                if art:
                    if len(f) >= 2:
                        e["aermel_grund"], e["aermel_zweit"] = f[0], f[1]
                    else:
                        e["aermel_grund"] = e.get("koerper_grund"); e["aermel_zweit"] = e.get("koerper_zweit") or (f[0] if f else None)
                        if not e["aermel_zweit"]: e["_unsicher"].append(seg)
                    e["aermel_muster"] = AERMEL_FLAECHE.get(art, art)
                    if len(f) >= 3: e["aermel_dritt"] = f[2]
                elif f:
                    e["aermel_grund"] = f[0]
                    if len(f) >= 2: e["aermel_muster"] = "manschetten"; e["aermel_zweit"] = f[1]
                elif vor:
                    e["_unsicher"].append(seg)
                continue
            art = None
            if aermel_gesehen or gl.startswith(("armb", "armr", "aufschl")):
                art = next((a for k, a in AERMEL if gl.startswith(k)), None)
                if art:
                    if not f: e["_unsicher"].append(seg); continue
                    if gl.startswith(("armb", "armr")) and len(f) >= 2:
                        if len(f) == 3: e["aermel_muster"] = "band_gesaeumt"; e["aermel_zweit"], e["aermel_dritt"] = f[0], f[1]
                        else: e["aermel_muster"] = "band_zwei"; e["aermel_zweit"], e["aermel_dritt"] = f[0], f[1]
                        e.setdefault("aermel_grund", e.get("koerper_grund"))
                    else:
                        e.setdefault("aermel_grund", e.get("koerper_grund"))
                        if e.get("aermel_muster") in (None, "einfarbig") or art in ("armringe", "manschetten"):
                            e["aermel_muster"] = art; e["aermel_zweit"] = f[0]
                        else:
                            e["_unsicher"].append("zweites Aermelmuster: " + seg)
                    continue
            # Buchstaben: "weißes W", "schwarzes H"
            if re.fullmatch(r"[a-zäöü&]{1,3}", g) and not g in ("v",) and f:
                e["text"] = g.upper() if len(g) > 1 or g.islower() else g
                e["text"] = seg.split()[-1] if len(seg.split()[-1]) <= 3 else g.upper()
                e["text_farbe"] = f[0]; continue
            m = re.match(r"(.+) in ([a-zäöüß]+)$", seg.strip(), flags=re.I)
            if m and farbe(m.group(2)) and len(m.group(1)) <= 4:
                e["text"] = m.group(1); e["text_farbe"] = farbe(m.group(2)); continue
            art = next((a for k, a in KOERPER if gl == k or gl.startswith(k + " ") or gl.startswith(k)), None)
            if art == "regenbogen" and not f: f = ["#FFFFFF"]
            if art and f:
                if art == "band" and anzahl == 2: art = "zwei_baender"
                if art == "band" and anzahl == 3: art = "drei_querstreifen"
                if art == "streifen_breit" and anzahl == 2: art = "zwei_streifen"; f = f[:1]
                if art == "streifen_breit" and anzahl and anzahl >= 3: art = "laengsstreifen"
                if art == "streifen_breit" and len(f) >= 2: art = "streifen_gesaeumt"
                if art == "drei_schraeg" and anzahl == 1: art = "kreuzband_r"
                if art in ("punkte", "scheibe") and anzahl == 3: art = "drei_scheiben"
                if art in ("raute", "rauten") and anzahl == 3: art = "rautenband"
                if art == "spitzen" and re.match(r"[a-zäöü.\-]+er$", " ".join(vor_kappe.split(" ")[:1])): art = "winkel_oben"
                if art == "sterne" and e.get("koerper_muster") not in (None, "einfarbig") and e.get("koerper_muster") != "sterne":
                    e["_unsicher"].append("zweites Koerpermuster: " + seg); continue
                koerper_elemente.append((art, f))
            else:
                e["_unsicher"].append(seg)
        if kappe:
            break
    # Koerperelemente eintragen: erstes zaehlt, weitere als unsicher
    for n, (art, f) in enumerate(koerper_elemente):
        if n == 0 and e.get("koerper_muster") in (None, "einfarbig"):
            e["koerper_muster"] = art
            if art == "streifen_gesaeumt":
                e["koerper_zweit"], e["koerper_dritt"] = f[0], f[1] if len(f) > 1 else f[0]
                if len(f) >= 3: e["koerper_zweit"], e["koerper_dritt"] = f[0], f[1]
            elif art == "kreuzbaender" and len(f) >= 2:
                e["koerper_zweit"] = f[0]
            elif art == "v" and len(f) >= 2:
                e["koerper_zweit"] = f[0]
            else:
                e["koerper_zweit"] = f[0]
                if len(f) >= 2 and art == "kreuzband_r": e["koerper_muster"] = "kreuzband_r2"; e["koerper_zweit"], e["koerper_dritt"] = f[0], f[1]
                elif len(f) >= 2 and art == "band": e["koerper_muster"] = "band_zwei"; e["koerper_zweit"], e["koerper_dritt"] = f[0], f[1]
                elif len(f) >= 2 and art == "v": e["koerper_zweit"] = f[0]
                elif len(f) >= 2: e["_unsicher"].append("mehrfarbig: " + art)
        elif n == 1 and not e.get("koerper_muster2") and e.get("koerper_muster") not in ("einfarbig",) and art != e.get("koerper_muster"):
            e["koerper_muster2"] = art; e["koerper_zweit2"] = f[0]
        else:
            e["_unsicher"].append("weiteres Element: " + art)
    e.setdefault("koerper_muster", "einfarbig")
    e.setdefault("aermel_grund", e.get("koerper_grund"))
    e.setdefault("aermel_muster", "einfarbig")
    if not e.get("koerper_grund"):
        return None
    return e


if __name__ == "__main__":
    import sys
    for t in sys.argv[1:]:
        print(t, "->", lesen(t))
