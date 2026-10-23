#!/usr/bin/env python3
"""Lokale Kopie der Trikot-Datenbank auf den neuesten Stand bringen, ohne Git (z. B. auf Sebastians Mac, wo Git in
den Dokumenten-Ordnern nicht löschen darf). Lädt das Paket des aktuellen Stands von GitHub und entpackt es über
diesen Ordner.

    python3 werkzeug/aktualisieren.py
"""
import io, json, os, sys, tarfile, urllib.request
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.github.com/repos/SebastianWeiss1102/galopp-rennfarben/commits/main"

def main():
    sha = json.load(urllib.request.urlopen(urllib.request.Request(API, headers={"Accept": "application/vnd.github+json"}), timeout=60))["sha"]
    stand = os.path.join(WURZEL, ".stand")
    if os.path.exists(stand) and open(stand).read().strip() == sha:
        print("aktuell:", sha[:7]); return 0
    daten = urllib.request.urlopen("https://codeload.github.com/SebastianWeiss1102/galopp-rennfarben/tar.gz/" + sha, timeout=300).read()
    with tarfile.open(fileobj=io.BytesIO(daten)) as t:
        for m in t.getmembers():
            teile = m.name.split("/", 1)
            if len(teile) < 2 or not teile[1] or not m.isfile():
                continue
            ziel = os.path.join(WURZEL, teile[1])
            os.makedirs(os.path.dirname(ziel), exist_ok=True)
            with open(ziel, "wb") as f:
                f.write(t.extractfile(m).read())
    open(stand, "w").write(sha)
    print("aktualisiert auf", sha[:7]); return 0

if __name__ == "__main__":
    sys.exit(main())
