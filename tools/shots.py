#!/usr/bin/env python3
"""Headless-Prüfung Goldene Schere: Konsolenfehler, Querscroll, Kopfzeilen-Kante, kleine Schrift, Screenshots je Kapitel.

Start: python3 tools/shots.py [url] [ausgabe] [größen]   größen z. B. 1440x900,390x844
Stellen: id:anteil (Anteil der Sticky-Strecke bzw. Oberkante der Sektion).
"""
import os
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4390/"
out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/gs-shots"
sizes = (sys.argv[3] if len(sys.argv) > 3 else "1440x900,1280x800,1100x800,390x844,360x740,430x932,844x390").split(",")
spots = (sys.argv[4] if len(sys.argv) > 4 else
         "hero:0,hero:.45,hero:.8,fade:.05,fade:.35,fade:.62,fade:.9,preise:0,preise:.6,live:0,warum:.3,warum:.95,laden:.1,laden:.9,bewertungen:0,bewertungen:.5,karriere:.2,karriere:.9,kontakt:0,kontakt:.9").split(",")
os.makedirs(out, exist_ok=True)
problems = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for s in sizes:
        w, h = (int(x) for x in s.split("x"))
        mob = w < 900 and h > w or w < 600
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1, is_mobile=mob, has_touch=mob)
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(1500)
        for sp in spots:
            sid, frac = sp.split(":")
            y = pg.evaluate("""([id,f]) => { const el=document.getElementById(id); if(!el||!el.offsetHeight) return -1;
              const top=el.getBoundingClientRect().top+scrollY; const run=Math.max(0, el.offsetHeight-innerHeight);
              return run>0 ? top+run*f : top+el.offsetHeight*f - (f>0? innerHeight*.5:0); }""", [sid, float(frac)])
            if y < 0:
                continue
            pg.evaluate(f"scrollTo(0,{y})"); pg.wait_for_timeout(700)
            pg.screenshot(path=f"{out}/{w}x{h}_{sid}_{frac}.jpg", type="jpeg", quality=70)
        info = pg.evaluate("""() => {
          const sw=document.documentElement.scrollWidth, iw=innerWidth;
          const nav=[...document.querySelectorAll('.nav > *')].filter(e=>e.offsetParent).map(e=>Math.round(e.getBoundingClientRect().right));
          const small=[...document.querySelectorAll('p,li,a,span,td,button,label,cite')].filter(e=>e.offsetParent&&e.innerText&&e.innerText.trim()&&e.children.length===0)
            .filter(e=>parseFloat(getComputedStyle(e).fontSize)<12).map(e=>e.innerText.trim().slice(0,30));
          const taps=[...document.querySelectorAll('a,button')].filter(e=>e.offsetParent&&!e.closest('dialog')).filter(e=>{const r=e.getBoundingClientRect();return r.width&&(r.height<40)}).map(e=>(e.innerText||e.getAttribute('aria-label')||'').trim().slice(0,24)+':'+Math.round(e.getBoundingClientRect().height));
          return {sw, iw, navMax:Math.max(...nav), small:small.slice(0,8), taps:taps.slice(0,12)};
        }""")
        line = f"{s}: querscroll={'JA' if info['sw']>info['iw'] else 'nein'} navRechts={info['navMax']}/{info['iw']} fehler={len(errs)}"
        print(line, "| klein:", info["small"], "| tap<40:", info["taps"])
        for e in errs[:5]:
            print("   ERR", e)
        pg.close()
    b.close()
