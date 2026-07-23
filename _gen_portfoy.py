#!/usr/bin/env python3
# Portföy paneli üretici — danışman/çarpanlara (tekil oteli olmayanlara).
import re, pathlib
from urllib.parse import quote
BASE = pathlib.Path(__file__).parent
TPL = (BASE / "_portfoy_template.html").read_text(encoding="utf-8")
WA = "https://wa.me/905344318734?text="

# slug, portföy adı, hitap, tesis sayısı, tesis başı oda, ortalama ADR, upsell/oda
CARPAN = [
 ("erdal-dalkilic","Yönettiğiniz portföy","Erdal Bey",6,150,5000,90),
 ("anil-sonmez","Accor Leased Türkiye portföyü","Anıl Bey",8,160,4500,85),
 ("burak-yurdakan","Cluster portföyünüz","Burak Bey",5,170,4500,85),
 ("murat-kiran","Cluster operasyonunuz","Murat Bey",5,170,4000,80),
 ("burak-riza-hakan","Danışmanlık portföyünüz","Burak Bey",6,150,4500,90),
 ("hakan-sezgin","Danışmanlık portföyünüz","Hakan Bey",6,150,4500,90),
 ("hamit-topaloglu","Danışmanlık verdiğiniz portföy","Hamit Bey",7,180,6000,120),
 ("ercument-ulucer","Akcan turizm yatırım portföyü","Ercüment Bey",5,180,5500,110),
]
CFG_RE = re.compile(r"const CFG = \{.*?\n\};", re.S)
def esc(s): return s.replace('"', '\\"')

made = []
for slug,portfoy,gm,tesis,oda,adr,ups in CARPAN:
    wa = WA + quote(f"{portfoy} için gerçek rakamı 15 dakikada konuşmak istiyorum")
    cfg = ('const CFG = {\n'
        f'  hotel:  "{esc(portfoy)}",\n'
        f'  gm:     "{esc(gm)}",\n'
        f'  city:   "",\n'
        f'  cur:    "₺",\n'
        f'  tesis:  {tesis},\n'
        f'  oda:    {oda},\n'
        f'  dol:    72,\n'
        f'  adr:    {adr},\n'
        f'  ota:    30,\n'
        f'  kom:    17,\n'
        f'  upsellPerOda: {ups},\n'
        f'  recovery: 0.35,\n'
        f'  meeting: "{wa}",\n'
        f'  talk:    "",\n'
        f'  cockpit: "#kokpit"\n'
        '};')
    out, n = CFG_RE.subn(cfg, TPL, count=1)
    assert n == 1, f"CFG bulunamadı: {slug}"
    d = BASE / slug
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(out, encoding="utf-8")
    made.append((slug, portfoy, tesis))

print(f"Portföy paneli üretilen: {len(made)}")
for slug, portfoy, tesis in made:
    print(f"  {slug:22} {portfoy:34} {tesis} tesis")
