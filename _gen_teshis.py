#!/usr/bin/env python3
# Teşhis demosu üretici — amiral template'i baz alıp her otele CFG enjekte eder.
# Kaynak veriler: Codex tur 1 (otel_demo_arastirma.md). Oda=gerçek/Codex, ADR/OTA/upsell=sektör varsayımı (demoda slider'la düzeltilebilir).
import re, pathlib
BASE = pathlib.Path(__file__).parent
TPL = (BASE / "grand-hyatt-izmir" / "index.html").read_text(encoding="utf-8")

WA = "https://wa.me/905344318734?text="
def wa(name):  # WhatsApp ön-dolu mesaj
    from urllib.parse import quote
    return WA + quote(f"{name} için gerçek rakamı 15 dakikada konuşmak istiyorum")

RAIL = "https://alya-konsiyerj.up.railway.app/?hotel="

# slug, ad, şehir, para, oda, adr, ota%, kom%, upsell/oda, railway_slug(varsa)
HOTELS = [
 ("grand-hyatt-istanbul","Grand Hyatt İstanbul","İstanbul","₺",360,7000,30,17,130,"grand-hyatt-istanbul"),
 ("westin-nisantasi","The Westin İstanbul Nişantaşı","İstanbul","₺",150,6000,30,17,110,None),
 ("mgallery-bodrum","MGallery The Bodrum Yalıkavak","Bodrum","₺",97,9000,35,17,180,None),
 ("allium-bodrum","Allium Bodrum Resort & Spa","Bodrum","₺",38,13000,35,17,280,None),
 ("radisson-president-oldtown","Radisson President Old Town İstanbul","İstanbul","₺",201,4500,35,17,90,None),
 ("elite-world-grand","Elite World Grand İstanbul","İstanbul","₺",250,3500,30,17,75,None),
 ("swissotel-tbilisi","Swissôtel Tbilisi","Tiflis","€",130,170,30,17,12,None),
 ("doubletree-canakkale","DoubleTree by Hilton Çanakkale","Çanakkale","₺",155,3000,30,17,65,None),
 ("hampton-arnavutkoy","Hampton by Hilton İstanbul Arnavutköy","İstanbul","₺",150,2800,30,15,45,None),
 ("selectum-city-atasehir","Selectum City Ataşehir","İstanbul","₺",316,3500,30,17,80,None),
 ("arkin-iskele","The Arkın İskele Hotel","KKTC İskele","€",400,140,30,17,22,None),
 ("andriake-beach","Andriake Beach Club","Demre, Antalya","₺",420,3200,25,17,70,None),
 ("merlot-eskisehir","The Merlot Hotel Eskişehir","Eskişehir","₺",80,2500,30,15,50,None),
 ("midas-ankara","Midas Hotel Ankara","Ankara","₺",100,2500,30,15,55,None),
 ("kalamis-marina","39 Kalamış Marina Hotel","İstanbul","₺",39,5000,30,17,100,None),
 ("pinea-resort","Pinea Hotel Resort & Spa","Golem, Arnavutluk","€",34,120,30,17,18,None),
 ("golf-jesolo","Golf Club Jesolo","Jesolo, İtalya","€",7,150,20,15,25,None),
 ("alicante-golf","Hotel Alicante Golf","Alicante, İspanya","€",156,160,25,15,20,None),
]

CFG_RE = re.compile(r"const CFG = \{.*?\n\};", re.S)

def esc(s): return s.replace('"', '\\"')

made = []
for slug,name,city,cur,oda,adr,ota,kom,ups,rail in HOTELS:
    talk = (RAIL + rail) if rail else ""  # railway içeriği yoksa "Alya ile konuş" gizlenir (yanlış otel gösterme)
    cfg = ('const CFG = {\n'
        f'  hotel:  "{esc(name)}",\n'
        f'  gm:     "",\n'
        f'  city:   "{esc(city)}",\n'
        f'  cur:    "{cur}",\n'
        f'  oda:    {oda},\n'
        f'  dol:    72,\n'
        f'  adr:    {adr},\n'
        f'  ota:    {ota},\n'
        f'  kom:    {kom},\n'
        f'  upsellPerOda: {ups},\n'
        f'  recovery: 0.35,\n'
        f'  meeting: "{wa(name)}",\n'
        f'  talk:    "{talk}",\n'
        f'  cockpit: "#kokpit"\n'
        '};')
    out, n = CFG_RE.subn(cfg, TPL, count=1)
    assert n == 1, f"CFG bulunamadı: {slug}"
    d = BASE / slug
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(out, encoding="utf-8")
    made.append((slug,name,oda,cur))

print(f"Üretilen: {len(made)} demo")
for slug,name,oda,cur in made:
    print(f"  {slug:32} {name:40} {oda} oda {cur}")
