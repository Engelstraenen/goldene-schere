#!/usr/bin/env python3
"""Lädt fertige sjinn-Bilder, legt Originale in assets-roh/img/ und baut Web-Fassungen.

Start: python3 tools/assets.py GS-H1=https://...jpg GS-S1=https://...jpg ...
Desktop: <key>.jpg 3840 breit (nie hochskaliert). Handy: <key>-m.jpg
  - Vollbild-Bilder (FULL): Hochkant-Ausschnitt in voller Höhe um den Fokus x, auf 2000 px Höhe
  - sonst: 1800 breit
Schreibt site/assets/js/media.js (Versionsstempel, vorhandene Schlüssel).
"""
import json
import os
import sys
import time
import urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets-roh", "img")
IMG = os.path.join(ROOT, "site", "assets", "img")
KEY = {"GS-H1": "hero", "GS-H2": "clipper", "GS-K1": "karriere", "GS-S1": "sHaar", "GS-S2": "sBart", "GS-S3": "sKind",
       "GS-E1": "fassade", "GS-E2": "gInnen", "GS-G1": "gRasur", "GS-G2": "gWerkzeug", "GS-G3": "gBart", "GS-F1": "fadeStart"}
FULL = {"hero": .62, "karriere": .22, "fadeStart": .4}   # Fokus x für Handy-Hochkant
os.makedirs(RAW, exist_ok=True)


def build(key, src):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    d = im if w <= 3840 else im.resize((3840, round(h * 3840 / w)), Image.LANCZOS)
    d.save(os.path.join(IMG, key + ".jpg"), quality=84, optimize=True, progressive=True)
    if key in FULL:
        cw = round(h * .6); x = int(min(max(FULL[key] * w - cw / 2, 0), w - cw))
        m = im.crop((x, 0, x + cw, h)); m = m.resize((round(cw * 2000 / h), 2000), Image.LANCZOS) if h > 2000 else m
    else:
        m = im if w <= 1800 else im.resize((1800, round(h * 1800 / w)), Image.LANCZOS)
    m.save(os.path.join(IMG, key + "-m.jpg"), quality=82, optimize=True, progressive=True)
    print(key, im.size, "->", d.size, m.size)


for arg in sys.argv[1:]:
    jid, url = arg.split("=", 1)
    key = KEY[jid]
    raw = os.path.join(RAW, jid + ".jpg")
    if url.startswith("http"):
        import subprocess
        subprocess.check_call(['curl', '-sSf', '-A', 'Mozilla/5.0', '-o', raw, url])
    build(key, raw)

have = {k: 2 for k in KEY.values() if os.path.exists(os.path.join(IMG, k + ".jpg"))}
mj = os.path.join(ROOT, "site", "assets", "js", "media.js")
vid = {}
for v in ("fade", "karriere"):
    if os.path.exists(os.path.join(ROOT, "site", "assets", "vid", v + ".mp4")):
        vid[v] = 1
open(mj, "w").write("window.GS=" + json.dumps({"v": str(int(time.time())), "img": have, "vid": vid}) + ";\n")
print("media.js:", sorted(have), vid)
