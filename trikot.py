# -*- coding: utf-8 -*-
"""Rennfarben als eigene Zeichnung.

Aus der Beschreibung einer Besitzerfarbe (Grundfarbe, Muster, Zweitfarbe je
fuer Koerper und Aermel, dazu die Kappe als Angabe) wird ein Trikot als SVG
gezeichnet. Vorlage (16.09.2026): flaches Hemd ohne Glanz und ohne Kappe,
Stehkragen mit Kerbe oben und unten, gerader Koerper, zwei lange, leicht
abgespreizte Aermel, kraeftige schwarze Kontur. Nichts davon ist fremdes Material.

Liegen fuer einen Besitzer keine Farben vor, wird dieselbe Form neutral in
Hellgrau gezeichnet (Entscheidung 16.09.2026). Erfunden wird dabei nichts.
"""
import json, os, math, re, unicodedata

# Das EINE Zeichenprogramm aller Galopp-Projekte (seit 23.10.2026 im Repo galopp-rennfarben).
# G1Stars, GaloppFacts, ClassicWinners, Meetings, YearlingStars, SireStars und Fantasy Galopp nutzen nur dieses.

HIER = os.path.dirname(os.path.realpath(__file__))

# ---------------------------------------------------------------- Umriss
# Zeichenflaeche ca. 101 x 103, Mittelachse x = 50.5
KRAGEN = "M39,1.2 L50.5,6.8 L62,1.2 L62,11.1 L50.5,16.1 L39,11.1 Z"
KRAGEN_MITTE = "M50.5,6.8 L50.5,16.1"
KOERPER = "M25.5,17.8 L39,11.1 L50.5,16.1 L62,11.1 L75.5,17.8 L73.3,102.2 L27.7,102.2 Z"
ARM_L = "M25.5,17.8 L13.9,20.6 L1.2,97.8 L16.1,102.2 L27,51 Z"
ARM_R = "M75.5,17.8 L87.1,20.6 L99.8,97.8 L84.9,102.2 L74,51 Z"
KONTUR = "#111111"
STRICH = "2.3"
KONTUR_DUNKEL = "#6B7480"   # auf sehr dunklen Trikots bleibt die Form so erkennbar
NEUTRAL = {"grund": "#E9ECEF", "kontur": "#A7AFB8"}

# Flaechen, in denen gemustert wird (x, y, Breite, Hoehe); sie ueberdecken den Umriss
FELD = {"koerper": (25, 10, 51, 93), "arm_l": (0, 17, 28, 86.5), "arm_r": (73, 17, 28, 86.5),
        "kragen": (38.5, 0.5, 24, 16)}


def _rect(x, y, b, h, farbe):
    return "<rect x='%s' y='%s' width='%s' height='%s' fill='%s'/>" % (
        round(x, 2), round(y, 2), round(b, 2), round(h, 2), farbe)


def _poly(punkte, farbe):
    return "<polygon points='%s' fill='%s'/>" % (" ".join("%.1f,%.1f" % p for p in punkte), farbe)


def _stern(cx, cy, r, farbe):
    p = []
    for i in range(10):
        w = math.pi / 5 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.42
        p.append((cx + rr * math.cos(w), cy + rr * math.sin(w)))
    return _poly(p, farbe)


def muster(art, teil, grund, zweit, dritt=None):
    """Die Fuellung eines Teils: Grundfarbe, darueber das Muster."""
    x, y, b, h = FELD[teil]
    z = zweit or "#FFFFFF"
    d3 = dritt or z
    arm = teil.startswith("arm")
    # 23.10.2026: Musternamen aus den Daten, die bisher kein Zeichenprogramm kannte (wurden still einfarbig)
    art = {"kreuzband_r2": "kreuzband_r", "drei_scheiben": "drei_punkte", "drei_schraeg_r": "drei_schraeg",
           "fenster": "quadrat"}.get(art, art)
    if art and "+" in art:                         # zwei Muster uebereinander: erstes in Zweit-, zweites in Drittfarbe
        erst, dann = art.split("+", 1)
        grundflaeche = _rect(x, y, b, h, grund)
        oben = muster(dann, teil, grund, dritt or zweit)
        if oben.startswith(grundflaeche):
            oben = oben[len(grundflaeche):]
        return muster(erst, teil, grund, zweit) + oben
    if art == "everest_208893":
        return _rect(x,y,b,h,grund)+_poly([(25,40),(38,30),(51,40),(64,30),(77,40),(77,54),(64,44),(51,54),(38,44),(25,54)],z)
    if art == "everest_211246":
        return (muster('epauletten',teil,grund,z)+
                "<text x='50.5' y='65' text-anchor='middle' fill='#FFFFFF' font-family='serif' font-size='13'>Inglis</text>")
    if art == "everest_211247":
        return _rect(x,y,b,h,grund)+''.join(_rect(x,y+h*f,b,h*.17,z) for f in (.15,.48,.81))
    if art == "zwei_baender_historisch":
        return _rect(x,y,b,h,grund)+_rect(x,y+h*.32,b,h*.12,z)+_rect(x,y+h*.60,b,h*.12,z)
    if art == "drei_punkte_historisch":
        return _rect(x,y,b,h,grund)+"".join("<circle cx='%s' cy='%s' r='8' fill='%s'/>"%(cx,cy,z) for cx,cy in ((42,34),(60,57),(42,80)))
    if art == "diagonal_quartiert_historisch":
        return _rect(x,y,b,h,grund)+_poly([(x,y),(x+b,y),(x+b/2,y+h/2)],z)+_poly([(x,y+h),(x+b,y+h),(x+b/2,y+h/2)],z)
    if art == "blitz_historisch":
        return _rect(x,y,b,h,grund)+_poly([(x+b*.6,y+8),(x+b*.2,y+h*.55),(x+b*.48,y+h*.5),(x+b*.3,y+h-5),(x+b*.83,y+h*.36),(x+b*.53,y+h*.42)],z)
    if art == "paulson_ap":
        return _rect(x,y,b,h,grund)+_rect(x,y,b,20,z)+"<text x='50.5' y='72' text-anchor='middle' font-family='Arial,sans-serif' font-size='25' font-weight='bold'><tspan fill='#D6242C'>A</tspan><tspan fill='#2058A5'>P</tspan></text>"
    if art == "winx_m":
        return muster("epauletten",teil,grund,z)+"<text x='50.5' y='73' text-anchor='middle' fill='white' font-family='Arial,sans-serif' font-size='36' font-weight='bold'>M</text>"
    if art == "melody_belle":
        return muster("sterne",teil,grund,z)+_poly([(x,y),(x+9,y),(x+b,y+h-13),(x+b,y+h),(x+b-9,y+h),(x,y+13)],"#FFFFFF")
    aus = [_rect(x, y, b, h, grund)]
    if art in ("einfarbig", "", None):
        return "".join(aus)
    if art == "querstreifen":                      # hoops
        n = 6 if teil == "koerper" else 7
        s = h / (n * 2.0)
        for i in range(n):
            aus.append(_rect(x, y + (2 * i + 1) * s, b, s, z))
    elif art in ("zwei_baender", "drei_querstreifen"):  # zwei bzw. drei Querstreifen (23.10.2026)
        n = 2 if art == "zwei_baender" else 3
        for i in range(n):
            aus.append(_rect(x, y + h * (0.28 + i * (0.36 if n == 2 else 0.2)), b, h * 0.085, z))
    elif art == "laengsstreifen":                  # stripes
        n = 5 if teil == "koerper" else 3
        s = b / (n * 2.0)
        for i in range(n):
            aus.append(_rect(x + (2 * i + 1) * s, y, s, h, z))
    elif art == "armringe":                        # armlets
        for f in (0.52, 0.66):
            aus.append(_rect(x, y + h * f, b, h * 0.075, z))
    elif art == "armbinde":                        # armband: eine breite Binde (z. B. Gestuet Ittlingen)
        aus.append(_rect(x, y + h * 0.55, b, h * 0.12, z))
    elif art == "karo":                            # checks: quadratische Felder wie auf der Vorlage
        s = b / 8.0 if teil == "koerper" else b / 4.0
        for i in range(int(b / s) + 1):
            for j in range(int(h / s) + 1):
                if (i + j) % 2:
                    aus.append(_rect(x + i * s, y + j * s, s, s, z))
    elif art == "kreuzband":                       # sash, linke Schulter zur rechten Huefte
        aus.append(_poly([(x - 2, y + 18), (x + 12, y + 3), (x + b + 2, y + h - 12), (x + b - 12, y + h + 3)], z))
    elif art == "kreuzband_r":                     # sash, rechte Schulter zur linken Huefte (Drittfarbe: zweifarbig)
        aus.append(_poly([(x + b + 2, y + 18), (x + b - 12, y + 3), (x - 2, y + h - 12), (x + 12, y + h + 3)], z))
        if dritt:
            aus.append(_poly([(x + b + 2, y + 18), (x + b - 5, y + 10.5), (x + 5, y + h - 4.5), (x + 12, y + h + 3)], dritt))
    elif art == "kreuzbaender":                    # crossed sashes
        aus.append(_poly([(x - 2, y + 18), (x + 12, y + 3), (x + b + 2, y + h - 12), (x + b - 12, y + h + 3)], z))
        aus.append(_poly([(x + b + 2, y + 18), (x + b - 12, y + 3), (x - 2, y + h - 12), (x + 12, y + h + 3)], z))
    elif art == "scheibe":                         # disc
        aus.append("<circle cx='%.1f' cy='%.1f' r='%.1f' fill='%s'/>" % (x + b / 2.0, y + h * 0.45, b * 0.32, z))
    elif art == "stern":                           # star
        aus.append(_stern(x + b / 2.0, y + h * 0.45, b * 0.32, z))
    elif art == "sterne":                          # stars
        for cx, cy in ((0.3, 0.3), (0.7, 0.3), (0.5, 0.52), (0.3, 0.74), (0.7, 0.74)) if not arm else ((0.5, 0.35), (0.5, 0.7)):
            aus.append(_stern(x + b * cx, y + h * cy, b * (0.11 if not arm else 0.2), z))
    elif art == "quartiert":                       # quartered
        aus.append(_rect(x + b / 2.0, y, b / 2.0, h / 2.0, z))
        aus.append(_rect(x, y + h / 2.0, b / 2.0, h / 2.0, z))
    elif art == "gespalten":                       # halved (vertikal)
        aus.append(_rect(x + b / 2.0, y, b / 2.0, h, z))
    elif art == "diagonal_gespalten":              # diagonal halves (mit Drittfarbe: Schaerpe auf der Teilung)
        aus.append(_poly([(x + b, y), (x + b, y + h), (x, y + h)], z))
        if dritt:
            aus.append(_poly([(x + b + 4, y - 2), (x + b + 4, y + 12), (x + 8, y + h + 4), (x - 6, y + h + 4)], dritt))
    elif art == "epauletten":                      # epaulets
        if teil == "koerper":
            aus.append(_poly([(25, 16), (39, 9), (41, 20), (27, 27)], z))
            aus.append(_poly([(76, 16), (62, 9), (60, 20), (74, 27)], z))
    elif art == "breite_epauletten":
        if teil == "koerper":
            aus.append(_poly([(27, 18), (36, 13), (43, 30), (41, 37), (35, 35)], z))
            aus.append(_poly([(74, 18), (65, 13), (58, 30), (60, 37), (66, 35)], z))
    elif art == "joch":                            # yoke
        aus.append(_rect(x, y, b, 20, z))
    elif art == "naht":                            # seams: schmale Linien auf Schulter- und Seitennaehten
        if teil == "koerper":
            aus.append("<path d='M26.5,19 L39.5,12.6 M74.5,19 L61.5,12.6 M28.2,20 L29.6,102 M72.8,20 L71.4,102' stroke='%s' stroke-width='3.2' fill='none'/>" % z)
        else:
            aus.append("<path d='M%s' stroke='%s' stroke-width='3' fill='none'/>" % ("14.5,21 L2.5,97" if teil == "arm_l" else "86.5,21 L98.5,97", z))
    elif art == "streifen":                        # stripe (ein Laengsstreifen in der Mitte)
        aus.append(_rect(x + b / 2.0 - b * 0.1, y, b * 0.2, h, z))
    elif art == "kreuz_durchgehend":               # schmales Kreuz ueber die ganze Vorderseite
        if teil == "koerper":
            aus.append(_rect(x + b * 0.44, y, b * 0.12, h, z))
            aus.append(_rect(x, y + h * 0.31, b, h * 0.09, z))
    elif art == "breites_band":                    # breites mittiges Querband
        aus.append(_rect(x, y + h * 0.35, b, h * 0.29, z))
    elif art == "vier_scheiben_mit_mitte":         # Jimmysstar: four yellow discs and green chest panel
        if teil == "koerper":
            for cx, cy in ((.25,.23),(.75,.23),(.25,.64),(.75,.64)):
                aus.append("<circle cx='%.1f' cy='%.1f' r='5.7' fill='%s'/>" %
                           (x+b*cx,y+h*cy,z))
            aus.append(_rect(x+b*.30,y+h*.34,b*.40,h*.20,d3))
            aus.append(_rect(x+b*.36,y+h*.41,b*.28,h*.06,"#FFFFFF"))
    elif art == "karo_vier":                       # four broad checked columns
        cols, rows = 4, 5
        for col in range(cols):
            for row in range(rows):
                if (col + row) % 2:
                    aus.append(_rect(x+col*b/cols,y+row*h/rows,b/cols,h/rows,z))
    elif art == "kreuz_breit":                    # broad full-body cross
        if teil == "koerper":
            aus.append(_rect(x+b*.39,y,b*.22,h,z))
            aus.append(_rect(x,y+h*.36,b,h*.20,z))
    elif art == "oberarm_gross":                  # broad upper-sleeve colour panel
        aus.append(_rect(x,y+h*.11,b,h*.37,z))
    elif art == "pink_schulter":                  # pink shoulder on blue sleeve
        aus.append(_rect(x,y,b,h*.29,z))
    elif art == "rauten_netze":                   # outlined two-colour diamonds
        if teil == "koerper":
            for row in range(-1,5):
                cy=y+row*h/3.5
                for col in range(-1,4):
                    cx=x+(col+(row%2)*.5)*b/2.5
                    colour=z if (row+col)%2 else grund
                    aus.append("<polygon points='%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f' fill='%s' stroke='#132334' stroke-width='1.5'/>" %
                               (cx,cy-h/7,cx+b/5,cy,cx,cy+h/7,cx-b/5,cy,colour))
        else:
            for cy in (.32,.56,.80):
                px,py=x+b*.5,y+h*cy
                aus.append("<polygon points='%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f' fill='%s' stroke='#132334' stroke-width='1.5'/>" %
                           (px,py-7,px+7,py,px,py+7,px-7,py,z))
    elif art == "pink_zackenjoch":               # Japanese yellow body with pink jagged yoke
        if teil == "koerper":
            aus.append(_poly([(x,y),(x+b,y),(x+b,y+h*.29),
                              (x+b*.83,y+h*.18),(x+b*.66,y+h*.37),
                              (x+b*.50,y+h*.18),(x+b*.34,y+h*.37),
                              (x+b*.17,y+h*.18),(x,y+h*.29)],z))
    elif art == "regenbogen_mandala":            # reviewed multicolour circular racing pattern
        if teil == "koerper":
            cx,cy=x+b*.5,y+h*.50
            palette=[(30,"#69DDE6"),(26,"#1E614B"),(22,"#E6B82F"),
                     (18,"#873597"),(13,"#64DAE8"),(8,"#299456"),(4,"#D8B32A")]
            for radius,colour in palette:
                points=[]
                for i in range(32):
                    angle=2*math.pi*i/32-math.pi/2
                    rr=radius*(1 if i%2==0 else .82)
                    points.append((cx+rr*math.cos(angle),cy+rr*math.sin(angle)))
                aus.append(_poly(points,colour))
        else:
            for pos,colour in ((.10,"#E4B529"),(.30,"#66D7E6"),(.49,"#249454"),
                               (.68,"#E4B529"),(.84,"#66D7E6")):
                aus.append(_rect(x,y+h*pos,b,h*.10,colour))
    elif art == "drei_schraeg":                    # reviewed Stall Grafenberg drawing (DG 3196004)
        for offset in (0, 22, 44):
            aus.append(_poly([(-5 + offset, 107), (3 + offset, 107),
                              (104 + offset, 6), (96 + offset, 6)], z))
    elif art == "chevron":                         # chevron (ein Winkel)
        y0 = y + h * 0.3
        aus.append(_poly([(x - 2, y0), (x + b / 2.0, y0 + 22), (x + b + 2, y0), (x + b + 2, y0 + 12), (x + b / 2.0, y0 + 34), (x - 2, y0 + 12)], z))
    elif art in ("spitzen", "chevrons"):           # chevrons
        n = 3 if teil == "koerper" else 4
        for i in range(n):
            y0 = y + 12 + i * (h - 14) / n
            d = 8.0 if teil == "koerper" else 5.0
            aus.append(_poly([(x, y0), (x + b / 2.0, y0 + d * 1.6), (x + b, y0), (x + b, y0 + d), (x + b / 2.0, y0 + d * 2.6), (x, y0 + d)], z))
    elif art == "raute":                           # diamond
        cx, cy = x + b / 2.0, y + h * 0.45
        aus.append(_poly([(cx, cy - 20), (cx + 15, cy), (cx, cy + 20), (cx - 15, cy)], z))
    elif art == "drei_laengsstreifen":
        for pos in (.12,.44,.76): aus.append(_rect(x+b*pos,y,b*.12,h,z))
    elif art == "rautenflaeche":
        rx,ry=b/6,h/6
        for i in range(3):
            for j in range(3):
                cx,cy=x+(2*i+1)*rx,y+(2*j+1)*ry
                aus.append(_poly([(cx,cy-ry),(cx+rx,cy),(cx,cy+ry),(cx-rx,cy)],z))
    elif art == "lange_epauletten":
        aus.append(_poly([(25,16),(34,12),(39,37),(34,41)],z))
        aus.append(_poly([(76,16),(67,12),(62,37),(67,41)],z))
    elif art == "kreuzbaender_schmal":
        aus.append("<path d='M25,12 L76,103 M76,12 L25,103' stroke='%s' stroke-width='9' fill='none'/>" % z)
    elif art == "panelnaehte":
        aus.append("<path d='M28,21 L47,15 L47,97 L30,97 Z M54,15 L73,21 L71,97 L54,97 Z' fill='none' stroke='%s' stroke-width='2'/>" % z)
    elif art == "drei_baender":
        for pos in (0.08, 0.38, 0.68):
            aus.append(_rect(x, y + h*pos, b, h*.15, z))
    elif art == "drei_armpunkte":
        for pos in (.33,.57,.81):
            aus.append("<circle cx='%.1f' cy='%.1f' r='4.6' fill='%s'/>" % (x+b*.5,y+h*pos,z))
    elif art == "karo_grob":
        size=b/2
        for i in range(2):
            for j in range(int(h/size)+1):
                if (i+j)%2: aus.append(_rect(x+i*size,y+j*size,size,size,z))
    elif art == "oberarmband":
        aus.append(_rect(x,y+h*.20,b,h*.17,z))
    elif art == "zwei_armbaender":
        for pos in (.20,.65): aus.append(_rect(x,y+h*pos,b,h*.17,z))
    elif art == "grosses_joch":
        aus.append(_poly([(x,y),(x+b,y),(x+b-8,y+h*.23),(x+8,y+h*.23)],z))
    elif art in ("acht_punkte","acht_sterne"):
        for cx,cy in ((.25,.2),(.75,.2),(.5,.34),(.25,.48),(.75,.48),(.5,.62),(.25,.76),(.75,.76)):
            if art == "acht_sterne": aus.append(_stern(x+b*cx,y+h*cy,8,z))
            else: aus.append("<circle cx='%.1f' cy='%.1f' r='4.5' fill='%s'/>" % (x+b*cx,y+h*cy,z))
    elif art == "drei_armsterne":
        for cy in (.33,.57,.81): aus.append(_stern(x+b*.5,y+h*cy,6,z))
    elif art == "hufeisen":
        aus.append("<path d='M39,35 C20,82 34,92 50,92 C70,92 79,76 63,35' fill='none' stroke='%s' stroke-width='8'/>" % z)
        for cx,cy in ((35,49),(32,63),(36,79),(47,87),(60,84),(67,72),(67,56),(63,44)):
            aus.append("<circle cx='%s' cy='%s' r='1.2' fill='%s'/>" % (cx,cy,grund))
    elif art == "pferdekopf":
        # Own vector drawing of the documented purple horse-head emblem.
        aus.append("<path d='M34,87 L35,48 Q39,39 48,40 L56,41 L61,26 L63,43 L70,51 L69,61 L75,72 Q77,79 70,81 L61,77 L56,67 L50,65 L45,71 L40,83 Z' fill='%s'/>" % z)
    elif art == "drei_verbundene_rauten":
        cy=y+h*.46
        for pos in (1/6,.5,5/6):
            cx=x+b*pos;aus.append(_poly([(cx,cy-11),(cx+b/6,cy),(cx,cy+11),(cx-b/6,cy)],z))
    elif art == "drei_aermelrauten":
        # Three diamonds along each sleeve; Conover's verified race-day colours.
        for cy in (0.33, 0.57, 0.81):
            px, py = x + b * (0.60 if teil == "arm_l" else 0.40), y + h * cy
            aus.append(_poly([(px, py - 6), (px + 5, py), (px, py + 6), (px - 5, py)], z))
    elif art == "unterarm":
        aus.append(_rect(x, y + h * 0.50, b, h * 0.50, z))
    elif art == "rauten":                          # diamonds
        for cx, cy in ((0.3, 0.27), (0.7, 0.27), (0.5, 0.5), (0.3, 0.73), (0.7, 0.73)):
            px, py = x + b * cx, y + h * cy
            aus.append(_poly([(px, py - 7), (px + 5.5, py), (px, py + 7), (px - 5.5, py)], z))
    elif art == "punkte":                          # spots
        r = b * (0.065 if teil == "koerper" else 0.12)
        cols = (0.22, 0.5, 0.78) if teil == "koerper" else (0.5,)
        rows = 6 if teil == "koerper" else 5
        for j in range(rows):
            # versetzte Reihen mittig (01.10.2026): gerade Reihen drei Punkte, ungerade zwei dazwischen
            reihe = (0.36, 0.64) if (teil == "koerper" and j % 2) else cols
            for cx in reihe:
                aus.append("<circle cx='%.1f' cy='%.1f' r='%.1f' fill='%s'/>" % (
                    x + b * cx, y + h * (0.16 + 0.14 * j), r, z))
    elif art == "diagonalstreifen":                # diagonal stripes
        w = 7.0
        for k in range(-12, 14):
            o = k * 2 * w
            aus.append(_poly([(x + o, y + h + 4), (x + o + w, y + h + 4), (x + o + w + h + 8, y - 4), (x + o + h + 8, y - 4)], z))
    elif art == "band":                            # hoop / band quer
        aus.append(_rect(x, y + h * 0.42, b, h * 0.14, z))
    elif art == "manschetten":                     # cuffs
        aus.append(_rect(x, y + h * 0.84, b, h * 0.2, z))
    elif art == "dreieck":                         # triangle (Spitze oben)
        cx, cy = x + b / 2.0, y + h * 0.45
        aus.append(_poly([(cx, cy - 18), (cx + 17, cy + 13), (cx - 17, cy + 13)], z))
    elif art == "ring":                            # hollow disc
        aus.append("<circle cx='%.1f' cy='%.1f' r='%.1f' fill='none' stroke='%s' stroke-width='3.2'/>" % (
            x + b / 2.0, y + h * 0.45, b * 0.27, z))
    elif art == "raute_rahmen":                    # hollow diamond
        cx, cy = x + b / 2.0, y + h * 0.45
        aus.append("<polygon points='%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f' fill='none' stroke='%s' stroke-width='3'/>" % (
            cx, cy - 19, cx + 15, cy, cx, cy + 19, cx - 15, cy, z))
    elif art == "rautenband":                      # a row of diamonds across the chest
        for cx in ((0.2, 0.5, 0.8) if teil == "koerper" else (0.5,)):
            px, py = x + b * cx, y + h * 0.36
            aus.append(_poly([(px, py - 8), (px + 7, py), (px, py + 8), (px - 7, py)], z))
    elif art == "harlekin":                        # diamonds all over (harlequin)
        s = b / 3.4
        for j in range(-1, int(h / s) + 2):
            for i in range(-1, 5):
                if (i + j) % 2:
                    px, py = x + i * s + s / 2.0, y + j * s + s / 2.0
                    aus.append(_poly([(px, py - s / 2.0), (px + s / 2.0, py), (px, py + s / 2.0), (px - s / 2.0, py)], z))
    elif art == "zacken_unten":                    # a row of triangles on the hem
        n = 4
        for i in range(n):
            px = x + 6 + i * (b - 12) / float(n)
            w = (b - 12) / float(n)
            aus.append(_poly([(px, y + h), (px + w / 2.0, y + h - 14), (px + w, y + h)], z))
    elif art == "kreuz":                           # cross (Tatzenkreuz vereinfacht)
        cx, cy = x + b / 2.0, y + h * 0.45
        aus.append(_rect(cx - 4, cy - 15, 8, 30, z))
        aus.append(_rect(cx - 15, cy - 4, 30, 8, z))
    elif art == "zwei_streifen":                   # two stripes, wide centre panel
        aus.append(_rect(x + b * 0.28, y, b * 0.08, h, z))
        aus.append(_rect(x + b * 0.64, y, b * 0.08, h, z))
    elif art == "dreieck_unten":                   # inverted triangle (Spitze unten)
        cx, cy = x + b / 2.0, y + h * 0.4
        aus.append(_poly([(cx - 17, cy - 13), (cx + 17, cy - 13), (cx, cy + 18)], z))
    elif art == "harlekin_fein":                   # kleine Rauten ueberall
        s = b / 5.2 if teil == "koerper" else b / 2.6
        for j in range(-1, int(h / s) + 2):
            for i in range(-1, int(b / s) + 2):
                if (i + j) % 2:
                    px, py = x + i * s + s / 2.0, y + j * s * 1.25 + s / 2.0
                    aus.append(_poly([(px, py - s * 0.62), (px + s / 2.0, py), (px, py + s * 0.62), (px - s / 2.0, py)], z))
    elif art == "aermelstreifen":                  # ein Streifen laengs auf dem Aermel
        if teil != "koerper":
            aus.append("<path d='M%s' stroke='%s' stroke-width='3.4' fill='none'/>" % ("19.8,21 L7.8,99" if teil == "arm_l" else "81.2,21 L93.2,99", z))
    elif art == "kasten":                          # box: schmaler Rechteckrahmen
        cx, cy = x + b / 2.0, y + h * 0.42
        aus.append("<rect x='%.1f' y='%.1f' width='30' height='22' fill='none' stroke='%s' stroke-width='3.4'/>" % (cx - 15, cy - 11, z))
    elif art == "zickzackband":                    # zigzag hoop
        y0, a, t = y + h * 0.44, 5.0, 9.0
        oben = [(x - 2 + i * b / 6.0, y0 - (a if i % 2 else 0)) for i in range(8)]
        unten = [(px, py + t) for px, py in reversed(oben)]
        aus.append(_poly(oben + unten, z))
    elif art == "quadrat_rahmen":                  # hollow square
        cx, cy = x + b / 2.0, y + h * 0.42
        aus.append(_rect(cx - 13, cy - 13, 26, 26, z))
        aus.append(_rect(cx - 6.5, cy - 6.5, 13, 13, d3 if dritt else grund))
    elif art == "quer_gespalten":                  # halved horizontally (untere Haelfte Zweitfarbe)
        aus.append(_rect(x, y + h * 0.5, b, h * 0.5 + 1, z))
        if dritt:                                  # Drittfarbe = Band auf der Trennlinie
            aus.append(_rect(x, y + h * 0.43, b, h * 0.14, dritt))
    elif art == "quer_gespalten_scheibe":          # halved horizontally, Scheibe in Drittfarbe darueber
        aus.append(_rect(x, y + h * 0.5, b, h * 0.5 + 1, z))
        aus.append("<circle cx='%.1f' cy='%.1f' r='%.1f' fill='%s'/>" % (x + b / 2.0, y + h * 0.5, b * 0.3, d3))
    elif art == "oval":                            # emblem / oval badge
        aus.append("<ellipse cx='%.1f' cy='%.1f' rx='%.1f' ry='%.1f' fill='%s' stroke='%s' stroke-width='1.6'/>" % (
            x + b / 2.0, y + h * 0.5, b * 0.36, h * 0.13, z, d3))
    elif art == "band_gesaeumt":                   # hoop mit schmalem Mittelstreifen
        aus.append(_rect(x, y + h * 0.4, b, h * 0.09, z))
        aus.append(_rect(x, y + h * 0.425, b, h * 0.04, d3))
    elif art == "rauten_schraeg":                  # diamond sash, linke Huefte zur rechten Schulter
        for i in range(6):
            t = i / 5.0
            px, py = x + b * (0.14 + 0.72 * t), y + h * (0.92 - 0.72 * t)
            aus.append(_poly([(px, py - 6), (px + 4, py), (px, py + 6), (px - 4, py)], z))
    elif art == "saltire":                         # breites Andreaskreuz
        aus.append(_poly([(x, y + 10), (x + b / 2.0, y + h * 0.5), (x, y + h)], z))
        aus.append(_poly([(x + b, y + 10), (x + b / 2.0, y + h * 0.5), (x + b, y + h)], z))
    elif art == "wuerfel":                         # Naehte plus zwei Wuerfel auf der Brust
        if teil == "koerper":
            aus.append("<path d='M28.2,20 L29.6,102 M72.8,20 L71.4,102 M50.5,16 L50.5,102' stroke='%s' stroke-width='2.6' fill='none'/>" % z)
            for wx in (34.5, 51.5):
                aus.append(_rect(wx, 30, 14, 14, z))
                for dx, dy in ((3.5, 3.5), (10.5, 3.5), (7, 7), (3.5, 10.5), (10.5, 10.5)):
                    aus.append("<circle cx='%.1f' cy='%.1f' r='1.3' fill='%s'/>" % (wx + dx, 30 + dy, d3))
        else:
            aus.append("<path d='M%s' stroke='%s' stroke-width='2.6' fill='none'/>" % ("14.5,21 L2.5,97" if teil == "arm_l" else "86.5,21 L98.5,97", z))
    elif art == "karo_viertel":                    # zwei karierte Viertel (oben rechts, unten links)
        s = b / 8.0
        for qx, qy in ((x + b / 2.0, y), (x, y + h / 2.0)):
            for i in range(4):
                for j in range(int(h / 2.0 / s) + 1):
                    if (i + j) % 2:
                        aus.append(_rect(qx + i * s, qy + j * s, s, min(s, qy + h / 2.0 - (qy + j * s)), z))
    elif art == "grosskaro":                       # large checks
        s = b / 4.0 if teil == "koerper" else b / 2.0
        for i in range(int(b / s) + 1):
            for j in range(int(h / s) + 1):
                if (i + j) % 2:
                    aus.append(_rect(x + i * s, y + j * s, s, s, z))
    elif art.startswith("buchstabe_"):             # ein Buchstabe auf der Brust
        if teil == "koerper":
            aus.append("<text x='%.1f' y='%.1f' text-anchor='middle' font-family='Arial,Helvetica,sans-serif' font-weight='700' font-size='34' fill='%s'>%s</text>" % (
                x + b / 2.0, y + h * 0.58, z, art.split("_", 1)[1][:2]))
    elif art == "kleeblatt":                       # shamrock / Kleeblatt
        if teil == "koerper":
            cx, cy = x + b / 2.0, y + h * 0.42
            for dx, dy in ((0, -7), (-7, 0), (7, 0), (0, 7)):
                aus.append("<circle cx='%.1f' cy='%.1f' r='6.2' fill='%s'/>" % (cx + dx, cy + dy, z))
            aus.append("<path d='M%.1f,%.1f L%.1f,%.1f' stroke='%s' stroke-width='2.4'/>" % (cx, cy + 8, cx + 4, cy + 20, z))
    elif art == "v_gross":                         # grosses V von den Schultern zur Mitte
        if teil == "koerper":
            aus.append(_poly([(x, y + 6), (x + 10, y + 6), (x + b / 2.0, y + h * 0.52), (x + b - 10, y + 6), (x + b, y + 6),
                              (x + b / 2.0, y + h * 0.66)], z))
    elif art == "spitze_oben":                     # grosser Winkel mit der Spitze nach oben
        if teil == "koerper":
            aus.append(_poly([(x - 2, y + h), (x + b / 2.0, y + h * 0.28), (x + b + 2, y + h), (x + b - 12, y + h),
                              (x + b / 2.0, y + h * 0.5), (x + 12, y + h)], z))
    elif art == "zackenjoch":                      # Schulterteil mit Zackenkante (japanisches Yamagata)
        if teil == "koerper":
            y0, zacke, n = y + h * 0.3, 8.0, 5
            pkt = [(x - 2, y - 2), (x + b + 2, y - 2), (x + b + 2, y0)]
            for i in range(n, 0, -1):
                pkt += [(x + b * (i - 0.5) / n, y0 + zacke), (x + b * (i - 1) / n, y0)]
            aus.append(_poly(pkt, z))
        else:
            aus.append(_rect(x, y, b, 18, z))
    # 23.10.2026: weitere Muster aus dem woechentlichen Nachzeichnen (G1Stars-Trikotlauf)
    elif art in ("drei_scheiben_ro", "drei_scheiben_lo"):   # drei grosse Punkte schraeg
        if teil == "koerper":
            lage = ((0.7, 0.3), (0.48, 0.52), (0.26, 0.74)) if art.endswith("ro") else ((0.3, 0.3), (0.5, 0.52), (0.7, 0.74))
            r = b * (0.13 if art.endswith("ro") else 0.11)
            for cx, cy in lage:
                aus.append("<circle cx='%.1f' cy='%.1f' r='%.1f' fill='%s'/>" % (x + b * cx, y + h * cy, r, z))
    elif art == "diabolo":                         # Sanduhr: Dreiecke oben und unten
        cx = 14.5 if teil == "arm_l" else 86.5 if teil == "arm_r" else x + b / 2.0
        ym = y + h * 0.5
        aus.append(_poly([(x - 2, y - 2), (x + b + 2, y - 2), (cx, ym)], z))
        aus.append(_poly([(x - 2, y + h + 2), (x + b + 2, y + h + 2), (cx, ym)], z))
    elif art == "pferd":                           # galoppierendes Pferd (eigene Zeichnung)
        if teil == "koerper":
            aus.append("<path d='M36,80 L40,64 L38,53 Q40,45 48,45 L59,45 L65,35 L63,28 L69,27 L74,34 L70,38 L67,48 L67,57 L73,67 L70,69 L63,59 L57,61 L59,73 L56,75 L52,62 L46,62 L42,71 L39,81 Z' fill='%s'/>" % z)
    elif art == "davidstern":                      # Hexagramm als Umriss
        if teil == "koerper":
            cx, cy, r = x + b / 2.0, y + h * 0.45, 15.0
            for w0 in (-90, 90):
                pk = " ".join("%.1f,%.1f" % (cx + r * math.cos(math.radians(w0 + 120 * i)), cy + r * math.sin(math.radians(w0 + 120 * i))) for i in range(3))
                aus.append("<polygon points='%s' fill='none' stroke='%s' stroke-width='2.6'/>" % (pk, z))
    elif art == "farn":                            # Farnblatt schraeg
        if teil == "koerper":
            aus.append("<path d='M40,77 Q42,53 65,32 Q63,57 40,77 Z' fill='%s'/>" % z)
            aus.append("<path d='M38,80 L64,34' stroke='%s' stroke-width='0.9'/>" % grund)
    elif art == "querstreifen3":                   # Ringe abwechselnd in Zweit- und Drittfarbe
        n = 6 if teil == "koerper" else 7
        s = h / (n * 2.0)
        for i in range(n):
            aus.append(_rect(x, y + (2 * i + 1) * s, b, s, z if i % 2 == 0 else d3))
    elif art == "lothringerkreuz":                 # Kreuz mit zwei Querbalken
        if teil == "koerper":
            cx, cy = x + b / 2.0, y + h * 0.45
            aus.append(_rect(cx - 3.5, cy - 20, 7, 40, z))
            aus.append(_rect(cx - 10, cy - 12, 20, 6, z))
            aus.append(_rect(cx - 14, cy - 1, 28, 6, z))
    elif art == "grosse_zacken_unten":             # grosse Zacken vom Saum aufwaerts
        if teil == "koerper":
            aus.append(_poly([(x - 2, y + h + 2), (x - 2, y + h * 0.78), (x + b / 6.0, y + h * 0.5), (x + b / 3.0, y + h * 0.8),
                              (x + b / 2.0, y + h * 0.5), (x + b * 2 / 3.0, y + h * 0.8), (x + b * 5 / 6.0, y + h * 0.5),
                              (x + b + 2, y + h * 0.78), (x + b + 2, y + h + 2)], z))
    elif art == "saum":                            # breiter Saum unten
        aus.append(_rect(x, y + h * 0.82, b, h * 0.2, z))
    elif art == "band_zweifarbig":                 # Querband aus zwei Farben uebereinander
        aus.append(_rect(x, y + h * 0.4, b, h * 0.08, z))
        aus.append(_rect(x, y + h * 0.48, b, h * 0.08, d3))
    elif art == "chevrons_oben":                   # Winkel mit der Spitze nach oben
        n = 3 if teil == "koerper" else 4
        for i in range(n):
            y0 = y + 12 + i * (h - 14) / n
            d = 8.0 if teil == "koerper" else 5.0
            aus.append(_poly([(x, y0 + d * 1.6), (x + b / 2.0, y0), (x + b, y0 + d * 1.6), (x + b, y0 + d * 2.6), (x + b / 2.0, y0 + d), (x, y0 + d * 2.6)], z))
    elif art == "malteserkreuz":                   # Malteserkreuz: vier spitze Arme zur Mitte
        if teil == "koerper":
            cx, cy, r, w = x + b / 2.0, y + h * 0.45, 19.0, 10.0
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                ex, ey = cx + dx * r, cy + dy * r
                aus.append(_poly([(cx, cy), (ex + dy * w, ey + dx * w), (ex - dy * w, ey - dx * w)], z))
    elif art == "sechs_punkte":                    # sechs grosse Punkte in zwei Reihen
        if teil == "koerper":
            for cx in (0.33, 0.67):
                for cy in (0.25, 0.47, 0.69):
                    aus.append("<circle cx='%.1f' cy='%.1f' r='%.1f' fill='%s'/>" % (x + b * cx, y + h * cy, b * 0.085, z))
    elif art == "punkte_schraeg":                  # Punkte als Schaerpe, rechte Schulter zur linken Huefte
        if teil == "koerper":
            for i in range(5):
                t = i / 4.0
                aus.append("<circle cx='%.1f' cy='%.1f' r='4.3' fill='%s'/>" % (x + b * (0.8 - 0.6 * t), y + h * (0.2 + 0.66 * t), z))
    elif art in ("fuenf_punkte", "hufeisen_klein"):   # fuenf grosse Punkte bzw. kleine Hufeisen wie eine Fuenf beim Wuerfel
        if teil == "koerper":
            for cx, cy in ((0.3, 0.27), (0.7, 0.27), (0.5, 0.48), (0.3, 0.7), (0.7, 0.7)):
                px, py = x + b * cx, y + h * cy
                if art == "fuenf_punkte":
                    aus.append("<circle cx='%.1f' cy='%.1f' r='%.1f' fill='%s'/>" % (px, py, b * 0.09, z))
                else:
                    aus.append("<path d='M%.1f,%.1f L%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Q%.1f,%.1f %.1f,%.1f L%.1f,%.1f' fill='none' stroke='%s' stroke-width='1.9'/>" % (
                        px - 4, py - 5, px - 4, py + 1, px - 4, py + 5, px, py + 5, px + 4, py + 5, px + 4, py + 1, px + 4, py - 5, z))
    # --- aus GaloppFacts uebernommen (23.10.2026: ein Zeichenprogramm fuer alle Galopp-Projekte).
    # Varianten mit Endung _gf: gleicher Name wie bei G1Stars, aber anders gezeichnet; bleiben getrennt.
    if art == "kreuzband_dreifarbig":            # three parallel bands, white in the middle
        left = [(x - 2, y + 18), (x + b - 12, y + h + 3)]
        right = [(x + 12, y + 3), (x + b + 2, y + h - 12)]
        def edge(i, t): return tuple(left[i][j] + t * (right[i][j] - left[i][j]) for j in (0, 1))
        for i, color in enumerate((z, "#FFFFFF", d3)):
            aus.append(_poly([edge(0,i/3),edge(0,(i+1)/3),edge(1,(i+1)/3),edge(1,i/3)],color))
    if art == "kreuzband_r_gf":                     # sash, rechte Schulter zur linken Huefte
        aus.append(_poly([(x + b + 2, y + 18), (x + b - 12, y + 3), (x - 2, y + h - 12), (x + 12, y + h + 3)], z))
    if art == "diagonal_gespalten_gf":              # diagonal halves
        aus.append(_poly([(x + b, y), (x + b, y + h), (x, y + h)], z))
    if art == "punkte_gf":                          # spots
        r = b * (0.065 if teil == "koerper" else 0.12)
        cols = (0.22, 0.5, 0.78) if teil == "koerper" else (0.5,)
        rows = 6 if teil == "koerper" else 5
        for j in range(rows):
            for i, cx in enumerate(cols):
                off = 0.14 if (teil == "koerper" and j % 2) else 0.0
                aus.append("<circle cx='%.1f' cy='%.1f' r='%.1f' fill='%s'/>" % (
                    x + b * min(cx + off, 0.86), y + h * (0.16 + 0.14 * j), r, z))
    if art == "punkte_viermalvier" and teil == "koerper":
        for row in range(4):
            for col in range(4):
                aus.append("<circle cx='%.1f' cy='%.1f' r='3.7' fill='%s'/>" % (
                    x + b * (0.16 + col * 0.22), y + h * (0.2 + row * 0.17), z))
    if art == "diagonal_gespalten_l":            # schraeg geteilt, untere linke Haelfte Zweitfarbe (26.09.2026)
        aus.append(_poly([(x, y), (x + b, y + h), (x, y + h)], z))
    if art == "harlekin_bunt":                   # vielfarbig gerautet: Rauten reihum zweit/dritt auf Grund (26.09.2026)
        s = b / 5.2 if teil == "koerper" else b / 2.6
        for j in range(-1, int(h / s) + 2):
            for i in range(-1, int(b / s) + 2):
                if (i + j) % 2:
                    px, py = x + i * s + s / 2.0, y + j * s * 1.25 + s / 2.0
                    aus.append(_poly([(px, py - s * 0.62), (px + s / 2.0, py), (px, py + s * 0.62), (px - s / 2.0, py)], z if (i + 2 * j) % 4 in (0, 1) else d3))
    if art == "krone":                           # Krone auf der Brust (26.09.2026)
        if teil == "koerper":
            cx, cy = x + b / 2.0, y + h * 0.36
            aus.append(_poly([(cx - 13, cy + 10), (cx - 14, cy - 6), (cx - 7, cy + 1), (cx, cy - 9), (cx + 7, cy + 1), (cx + 14, cy - 6), (cx + 13, cy + 10)], z))
            aus.append(_rect(cx - 13, cy + 11.5, 26, 3.5, z))
    if art == "drei_punkte":                     # drei grosse Punkte schraeg von links oben nach rechts unten (26.09.2026)
        if teil == "koerper":
            for cx, cy in ((0.3, 0.3), (0.52, 0.52), (0.74, 0.74)):
                aus.append("<circle cx='%.1f' cy='%.1f' r='%.1f' fill='%s'/>" % (x + b * cx, y + h * cy, b * 0.1, z))
    if art == "quer_gespalten_gf":                  # halved horizontally (untere Haelfte Zweitfarbe)
        aus.append(_rect(x, y + h * 0.5, b, h * 0.5 + 1, z))
    if art == "armband":                         # ein einzelner Ring am Aermel (25.09.2026, GaloppFacts)
        if teil != "koerper":
            aus.append(_rect(x, y + h * 0.42, b, h * 0.09, z))
    if art == "streifen_gesaeumt":               # Mittelstreifen (dritt) mit schmalem Saum (zweit)
        aus.append(_rect(x + b / 2.0 - b * 0.15, y, b * 0.3, h, z))
        aus.append(_rect(x + b / 2.0 - b * 0.09, y, b * 0.18, h, d3))
    if art == "litzen":                          # Schnuere quer ueber die Brust (Husarenjacke)
        if teil == "koerper":
            for j in range(4):
                yy = y + h * (0.2 + 0.13 * j)
                aus.append(_rect(x + b * 0.3, yy - 1.3, b * 0.4, 2.6, z))
                for cx in (0.3, 0.7):
                    aus.append("<circle cx='%.1f' cy='%.1f' r='2.8' fill='%s'/>" % (x + b * cx, yy, z))
    if art == "quadrat":                         # gefuelltes Quadrat auf der Brust
        cx, cy = x + b / 2.0, y + h * 0.42
        aus.append(_rect(cx - 13, cy - 13, 26, 26, z))
    if art == "band_zwei":                       # zwei Querbaender uebereinander (zweit, dann dritt)
        aus.append(_rect(x, y + h * 0.36, b, h * 0.09, z))
        aus.append(_rect(x, y + h * 0.45, b, h * 0.09, d3))
    if art == "spitze_unten":                    # untere Haelfte in Zweitfarbe mit Spitze nach oben
        aus.append(_poly([(x - 2, y + h * 0.72), (x + b / 2.0, y + h * 0.42), (x + b + 2, y + h * 0.72), (x + b + 2, y + h + 2), (x - 2, y + h + 2)], z))
    if art == "streifen_breit":                  # breiter Mittelstreifen
        aus.append(_rect(x + b / 2.0 - b * 0.16, y, b * 0.32, h, z))
    if art == "v":                               # grosses V von den Schultern zur Brustmitte
        aus.append(_poly([(x - 2, y + 4), (x + 9, y + 4), (x + b / 2.0, y + h * 0.42), (x + b - 9, y + 4), (x + b + 2, y + 4), (x + b / 2.0, y + h * 0.58)], z))
    if art == "gespalten_quadrat":               # gespalten, dazu ein Quadrat ueber der Mitte
        aus.append(_rect(x + b / 2.0, y, b / 2.0, h, z))
        if teil == "koerper":
            aus.append(_rect(x + b / 2.0 - 14, y + h * 0.3, 20, 20, z))
    if art == "punkte_gross":                    # wenige grosse Punkte
        for cx, cy in ((0.3, 0.3), (0.7, 0.4), (0.35, 0.62), (0.68, 0.78)) if teil == "koerper" else ((0.5, 0.35), (0.5, 0.7)):
            aus.append("<circle cx='%.1f' cy='%.1f' r='%.1f' fill='%s'/>" % (x + b * cx, y + h * cy, b * (0.13 if teil == "koerper" else 0.22), z))
    if art == "karostreifen":                    # ein senkrechter Streifen aus Karos (zweit/dritt) links der Mitte
        if teil == "koerper":
            s = 7.0
            for j in range(int(h / s) + 1):
                for i in range(2):
                    aus.append(_rect(x + b * 0.2 + i * s, y + j * s, s, s, z if (i + j) % 2 else d3))
    if art == "kleeblatt_gf":                       # Kleeblatt auf der Brust
        if teil == "koerper":
            cx, cy = x + b / 2.0, y + h * 0.42
            for dx, dy in ((0, -8), (-8, 3), (8, 3)):
                aus.append("<circle cx='%.1f' cy='%.1f' r='7.5' fill='%s'/>" % (cx + dx, cy + dy, z))
            aus.append(_poly([(cx - 1.5, cy + 2), (cx + 1.5, cy + 2), (cx + 4, cy + 20), (cx + 1, cy + 20)], z))
    if art == "schmetterling":                   # Schmetterling auf der Brust
        if teil == "koerper":
            cx, cy = x + b / 2.0, y + h * 0.42
            for dx, dy, rx, ry in ((-8, -6, 8, 9), (8, -6, 8, 9), (-6, 8, 6, 7), (6, 8, 6, 7)):
                aus.append("<ellipse cx='%.1f' cy='%.1f' rx='%s' ry='%s' fill='%s'/>" % (cx + dx, cy + dy, rx, ry, z))
    if art == "halbmond":                        # Halbmond mit Stern
        if teil == "koerper":
            cx, cy = x + b / 2.0 - 3, y + h * 0.42
            aus.append("<circle cx='%.1f' cy='%.1f' r='13' fill='%s'/>" % (cx, cy, z))
            aus.append("<circle cx='%.1f' cy='%.1f' r='11' fill='%s'/>" % (cx + 5, cy - 1, grund))
            aus.append(_stern(cx + 9, cy, 5, z))
    if art == "lilie":                           # Lilie (Fleur-de-lis), vereinfacht
        cx, cy = x + b / 2.0, y + h * 0.42
        f = 1.0 if teil == "koerper" else 0.55
        if teil != "koerper": cy = y + h * 0.4
        aus.append(_poly([(cx, cy - 16 * f), (cx + 5 * f, cy - 4 * f), (cx, cy + 6 * f), (cx - 5 * f, cy - 4 * f)], z))
        aus.append(_poly([(cx - 3 * f, cy + 2 * f), (cx - 14 * f, cy - 8 * f), (cx - 12 * f, cy + 4 * f), (cx - 4 * f, cy + 10 * f)], z))
        aus.append(_poly([(cx + 3 * f, cy + 2 * f), (cx + 14 * f, cy - 8 * f), (cx + 12 * f, cy + 4 * f), (cx + 4 * f, cy + 10 * f)], z))
        aus.append(_rect(cx - 9 * f, cy + 5 * f, 18 * f, 3 * f, z))
    if art == "dreieck_unten_gross":             # grosses Dreieck von den Schultern bis tief in den Koerper
        if teil == "koerper":
            aus.append(_poly([(x - 2, y + 4), (x + b + 2, y + 4), (x + b / 2.0, y + h * 0.72)], z))
    if art == "diagonalstreifen_r":              # diagonal stripes, andere Richtung (links oben nach rechts unten)
        w = 7.0
        for k in range(-12, 14):
            o = k * 2 * w
            aus.append(_poly([(x + o, y - 4), (x + o + w, y - 4), (x + o + w + h + 8, y + h + 4), (x + o + h + 8, y + h + 4)], z))
    if art == "sanduhr":                         # zwei Dreiecke oben und unten, Spitzen in der Mitte
        if teil == "koerper":
            aus.append(_poly([(x - 2, y + 4), (x + b + 2, y + 4), (x + b / 2.0, y + h * 0.5)], z))
            aus.append(_poly([(x - 2, y + h + 2), (x + b + 2, y + h + 2), (x + b / 2.0, y + h * 0.5)], z))
    if art == "dreifarbig_quer":                 # drei Querfelder: oben zweit, Mitte Grund, unten dritt
        aus.append(_rect(x, y, b, h * 0.36, z))
        aus.append(_rect(x, y + h * 0.66, b, h * 0.36, d3))
    if art == "herz":                            # Herz auf der Brust
        if teil == "koerper":
            cx, cy = x + b / 2.0, y + h * 0.4
            aus.append("<path d='M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f Z' fill='%s'/>" % (
                cx, cy + 16, cx - 22, cy + 2, cx - 10, cy - 18, cx, cy - 6, cx + 10, cy - 18, cx + 22, cy + 2, cx, cy + 16, z))
    if art == "winkel_oben":                     # umgekehrter Winkel (Spitze oben)
        if teil == "koerper":
            y0 = y + h * 0.25
            aus.append(_poly([(x + 6, y0 + 40), (x + b / 2.0, y0), (x + b - 6, y0 + 40), (x + b - 13, y0 + 40), (x + b / 2.0, y0 + 13), (x + 13, y0 + 40)], z))
    if art == "traube":                          # Weintraube (Beeren im Dreieck)
        if teil == "koerper":
            cx, cy = x + b / 2.0, y + h * 0.36
            for r_, n in enumerate((4, 3, 2, 1)):
                for i in range(n):
                    aus.append("<circle cx='%.1f' cy='%.1f' r='3.6' fill='%s'/>" % (cx + (i - (n - 1) / 2.0) * 7, cy + r_ * 6.5, z))
    if art == "wappen":                          # Wappenschild: oben zweit, unten dritt
        if teil == "koerper":
            cx, cy = x + b / 2.0, y + h * 0.3
            aus.append(_poly([(cx - 12, cy), (cx + 12, cy), (cx + 12, cy + 14), (cx, cy + 28), (cx - 12, cy + 14)], z))
            aus.append(_poly([(cx - 12, cy + 12), (cx + 12, cy + 12), (cx + 12, cy + 14), (cx, cy + 28), (cx - 12, cy + 14)], d3))
    if art == "regenbogen":                      # Regenbogen quer ueber die Brust
        if teil == "koerper":
            for i, fa in enumerate(("#E3202A", "#F47B20", "#F6E21B", "#1E9A3C", "#1F55A8", "#6A1B9A")):
                aus.append("<path d='M%.1f,%.1f A40,40 0 0 1 %.1f,%.1f' stroke='%s' stroke-width='3.2' fill='none'/>" % (x + 8 + i * 3, y + h * 0.75, x + b + 4, y + 18 + i * 3, fa))

    return "".join(aus)


def _hell(farbe):
    """Relative Helligkeit 0..1 einer #RRGGBB-Farbe."""
    try:
        r, g, b = (int(farbe[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    except Exception:
        return 1.0
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _teil(pfad, kennung, art, grund, zweit, feld, kontur=KONTUR, dritt=None):
    x, y, b, h = FELD[feld]
    return ("<clipPath id='%s'><path d='%s'/></clipPath>"
            "<g clip-path='url(#%s)'>%s</g>"
            "<path d='%s' fill='none' stroke='%s' stroke-width='%s' stroke-linejoin='round'/>") % (
        kennung, pfad, kennung, muster(art, feld, grund, zweit, dritt), pfad, kontur, STRICH)


def _schrift(f):
    """Optionaler Schriftzug auf der Brust (Feld 'text', Farbe 'text_farbe'), z. B. SAUREN oder 66."""
    t = f.get("text")
    if not t: return ""
    gr = 34 if len(t) <= 2 else max(9, 60 / len(t))
    return "<text x='50.5' y='%.1f' text-anchor='middle' font-family='Arial,Helvetica,sans-serif' font-weight='700' font-size='%.1f' fill='%s'>%s</text>" % (
        40 if len(t) > 2 else 58, gr, f.get("text_farbe", "#FFFFFF"), t)


def zeichnen(f, kennung, klasse="trikot"):
    """f ist ein Eintrag aus rennfarben.json (Kappe wird gespeichert, aber nicht gezeichnet)."""
    kb = f.get("koerper_grund") or "#FFFFFF"
    ab = f.get("aermel_grund") or kb
    kr = f.get("kragen_grund") or kb
    kontur = f.get("_kontur") or (KONTUR_DUNKEL if (_hell(kb) < 0.02 or _hell(ab) < 0.02) else KONTUR)
    teile = [
        _teil(ARM_L, kennung + "al", f.get("aermel_muster"), ab, f.get("aermel_zweit"), "arm_l", kontur, f.get("aermel_dritt")),
        _teil(ARM_R, kennung + "ar", f.get("aermel_muster"), ab, f.get("aermel_zweit"), "arm_r", kontur, f.get("aermel_dritt")),
        _teil(KOERPER, kennung + "k", f.get("koerper_muster"), kb, f.get("koerper_zweit"), "koerper", kontur, f.get("koerper_dritt")),
        _schrift(f),
        "<path d='%s' fill='%s' stroke='%s' stroke-width='%s' stroke-linejoin='round'/>" % (KRAGEN, kr, kontur, STRICH),
        "<path d='%s' fill='none' stroke='%s' stroke-width='%s'/>" % (KRAGEN_MITTE, kontur, STRICH),
    ]
    return ("<svg class='%s' viewBox='-1.5 -0.5 104 105' aria-hidden='true'>%s</svg>"
            % (klasse, "".join(teile)))


def neutral(kennung, klasse="trikot"):
    """Dieselbe Form ohne Farben, fuer Besitzer ohne belegte Rennfarben."""
    f = {"koerper_grund": NEUTRAL["grund"], "aermel_grund": NEUTRAL["grund"], "_kontur": NEUTRAL["kontur"]}
    return zeichnen(f, kennung, klasse + " trikotneutral")


# ---------------------------------------------------------------- Daten
FARBEN = {}


def laden(pfad=None, quellen=None):
    """Laedt die eine Trikot-Datenbank (galopp-rennfarben/rennfarben.json).
    Ohne Pfad: Datei neben diesem Programm. Altes flaches Format (Besitzer direkt auf oberster Ebene) wird
    ebenfalls gelesen. quellen: optionale private Datei mit Vorlage-Adressen je Besitzer (nur G1Stars)."""
    pfad = pfad or os.path.join(HIER, "rennfarben.json")
    if not os.path.exists(pfad):
        return FARBEN
    roh = json.load(open(pfad, encoding="utf-8"))
    roh = roh.get("besitzer", roh)
    zusatz = json.load(open(quellen, encoding="utf-8")) if quellen and os.path.exists(quellen) else {}
    for k, v in roh.items():
        if not k.startswith("_") and isinstance(v, dict):
            if k in zusatz:
                v = dict(v, **zusatz[k])
            if v.get("svg_override") and not os.path.isabs(v["svg_override"]):
                v = dict(v, svg_override=os.path.join(os.path.dirname(os.path.abspath(pfad)), v["svg_override"]))
            FARBEN[k] = v
            for a in v.get("aliase") or []:
                FARBEN.setdefault(a, v)
    NORM.clear(); NORM_OHNE_ANTEILE.clear()
    for k, v in FARBEN.items():
        if freigegeben(v):
            NORM.setdefault(schluessel(k), []).append(v)
            NORM_OHNE_ANTEILE.setdefault(schluessel(ohne_anteile(k)), []).append(v)
    return FARBEN


# Besitzer in anderer Schreibweise (26.09.2026): "Michael Tabor & Derrick Smith & Mrs John Magnier" ist
# dieselbe Gemeinschaft wie "Mrs John Magnier & Michael Tabor & Derrick Smith", "Pinecliff Racing (Mgr: J B Munz)"
# derselbe Besitzer wie "Pinecliff Racing". Nur wenn alle Treffer dieselbe Zeichnung haben, sonst neutral.
NORM = {}
# 18.10.2026: japanische Besitzer kommen als "Carrot Farm Co. Ltd. Syndicated For 1 Share: ¥90,000/ 400 Shares".
# Der Zusatz beschreibt nur Anteile. Nur wenn der genaue Name keinen Treffer hat, zaehlt der Name ohne Zusatz,
# und auch dann nur bei eindeutiger Zeichnung (Garnet Flare, Shuka Sho 2026, stand sonst mit neutralem Trikot).
NORM_OHNE_ANTEILE = {}


def ohne_anteile(name):
    return re.sub(r"\s+Syndicated For\b.*$", "", name or "", flags=re.I).strip()
_TITEL = {"mr", "mrs", "ms", "miss", "dr", "sir", "hh", "the", "sheikh", "lord", "lady", "hon", "prince", "princess"}
_SUFFIX = {"ltd", "limited", "co", "pty", "llc", "inc", "plc", "gmbh", "sa", "snc", "sarl", "ag", "corp",
           "corporation", "company", "kg", "pl"}
_FIRMA = {"racing", "stable", "stables", "farm", "farms", "stud", "bloodstock", "syndicate", "partners",
          "partnership", "thoroughbreds", "investments", "group", "management", "holdings", "family"}
_ZEICHNUNG = ("koerper_grund", "koerper_muster", "koerper_zweit", "aermel_grund", "aermel_muster", "aermel_zweit")


def _namensteil(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[.'`]", "", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    w = [x for x in t.split() if x not in _TITEL]
    if w[:2] == ["h", "h"]:
        w = w[2:]
    while w and w[-1] in _SUFFIX:
        w.pop()
    if not w:
        return ""
    if 2 <= len(w) <= 4 and all(x.isalpha() for x in w) and not any(x in _FIRMA for x in w):
        return w[0][0] + " " + w[-1]
    return " ".join("farm" if x == "farms" else "stable" if x == "stables" else x for x in w)


def schluessel(name):
    s = re.sub(r"\([^)]*\)", "", name or "")
    s = re.sub(r"\bet al\b\.?", "", s, flags=re.I)
    return "|".join(sorted({x for x in (_namensteil(y) for y in re.split(r",|&|/|\band\b|\bund\b", s)) if x}))


def freigegeben(f):
    return bool(f and f.get("koerper_grund") and f.get("status") not in
                ("entwurf", "abgelehnt", "requires_visual_review"))


def _finden(besitzer):
    f = FARBEN.get(besitzer)
    if freigegeben(f):
        return f
    if not besitzer:
        return None
    treffer = NORM.get(schluessel(besitzer)) or []
    if treffer and len({tuple(t.get(k) for k in _ZEICHNUNG) for t in treffer}) == 1:
        return treffer[0]
    if not treffer and ohne_anteile(besitzer) != besitzer:
        treffer = NORM_OHNE_ANTEILE.get(schluessel(ohne_anteile(besitzer))) or []
        if treffer and len({tuple(t.get(k) for k in _ZEICHNUNG) for t in treffer}) == 1:
            return treffer[0]
    return None


_ZAEHLER = [0]


def trikot(besitzer, klasse="trikot"):
    """Das Trikot eines Besitzers; ohne belegte Farben das neutrale Trikot."""
    _ZAEHLER[0] += 1
    f = _finden(besitzer)
    if not f:
        return neutral("t%d" % _ZAEHLER[0], klasse)
    return zeichnen(f, "t%d" % _ZAEHLER[0], klasse)


def hat_farben(besitzer):
    return bool(_finden(besitzer))


def beschreibung(besitzer):
    f = _finden(besitzer) or {}
    return f.get("beschreibung", "")


def reference_owner(url):
    """Match the exact source or an unambiguous racing.com silk image ID."""
    reference = (url or '').split('?')[0]
    if not reference:
        return None
    for name, drawing in FARBEN.items():
        urls = [u.rstrip('.,;') for u in re.findall(r"https?://[^\s)]+", str(drawing.get('quelle', '')))]
        if reference in urls and freigegeben(drawing):
            return name
    # racing.com distributes the same numbered template through its CDN and
    # the older racevic.silks host. The image ID is the exact template key,
    # but only if every approved match has the same drawing.
    match = re.search(r"(?:silks\.racing\.com|racevic\.silks)/bb/(\d+)\.png$", reference)
    if match:
        image_id = match.group(1)
        matches = [(name, drawing) for name, drawing in FARBEN.items()
                   if freigegeben(drawing) and re.search(
                       r"(?:silks\.racing\.com|racevic\.silks)/bb/%s\.png(?:\b|$)" % image_id,
                       str(drawing.get('quelle', '')))]
        if matches and len({tuple(drawing.get(key) for key in _ZEICHNUNG)
                            for _, drawing in matches}) == 1:
            return matches[0][0]
    return None


def runner_colours(runner, klasse="trikot"):
    """An exact archived race reference takes priority over ambiguous owner colours."""
    return trikot(reference_owner(runner.get('silk_vorlage')) or runner.get('besitzer', ''), klasse)
