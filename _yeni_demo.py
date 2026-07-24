#!/usr/bin/env python3
"""Lead → kısa demo linki (saniyeler).

Kullanım:
    python3 _yeni_demo.py 905372707414            # numaradan isim+sektör bulur
    python3 _yeni_demo.py "Cafe Eli Vegan" restoran
    python3 _yeni_demo.py 905372707414 klinik     # sektörü zorla

Yapar: slug klasörü + redirect index.html + git commit&push → kısa link basar.
Kısa link kullanılır çünkü uzun ?ad=&tur= linkinde '&tur=' kırpılırsa demo
sessizce klinik varsayılana düşüyor.
"""
import os, re, sys, subprocess, urllib.parse

REPO = "/home/bba1/alya-panel"
LISTS = "/home/bba1/hyatt/dokümanlar/custom-outreach"
SECTORS = {"klinik", "kuafor", "restoran", "su", "otel"}

FILE_SECTOR = {  # dosya adı → kesin sektör
    "WA_LINKLER_SU.md": "su",
    "WA_LINKLER_restoran.md": "restoran",
    "WA_LINKLER_otel.md": "otel",
}

GUESS = [  # isimden tahmin (sıra önemli)
    ("klinik", ["dental", "diş", "dis ", "dent", "klinik", "poliklinik", "ağız", "ortodont", "implant", "medikal", "tıp", "doktor", "hastane"]),
    ("kuafor", ["kuaför", "kuafor", "coiffure", "coiffeur", "güzellik", "beauty", "saç", "hair", "nail", "tırnak", "estetik"]),
    ("otel", ["hotel", "otel", "resort", "suit", "pansiyon", "apart", "konak"]),
    ("su", ["damacana", "su bayi", "sırma", "erikli", "aqua", "pınar su", "hayat su"]),
    ("restoran", ["cafe", "kafe", "restoran", "restaurant", "lokanta", "kebap", "pizza", "burger", "fırın", "pastane",
                  "bistro", "meyhane", "ocakbaşı", "mutfak", "food", "chicken", "dürüm", "çiğköfte", "vegan", "coffee", "bar"]),
]

TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")


def slugify(name: str) -> str:
    s = name.translate(TR).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "demo"


def find_by_phone(num: str):
    """Numarayı WA listelerinde ara → (isim, sektör|None)."""
    num = re.sub(r"\D", "", num)
    for fn in sorted(os.listdir(LISTS)):
        if not fn.startswith("WA_LINKLER_"):
            continue
        path = os.path.join(LISTS, fn)
        lines = open(path, encoding="utf-8").read().splitlines()
        for i, line in enumerate(lines):
            if num in line:
                # isim: yukarıdaki en yakın "### " ya da "- **...**" satırı
                for j in range(i - 1, max(-1, i - 6), -1):
                    m = re.match(r"^#{1,6}\s*(.+?)\s*$", lines[j]) or re.match(r"^-\s*\*\*(.+?)\*\*", lines[j])
                    if m:
                        return m.group(1).strip(), FILE_SECTOR.get(fn)
                return None, FILE_SECTOR.get(fn)
    return None, None


def guess_sector(name: str) -> str:
    low = name.translate(TR).lower()
    raw = name.lower()
    for sec, keys in GUESS:
        for k in keys:
            if k in raw or k.translate(TR).lower() in low:
                return sec
    return "klinik"


REDIRECT = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url=../demo/?ad={q_name}&tur={tur}">
<title>{name} — WhatsApp Asistanı</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#0b141a;color:#cfeee7;display:grid;place-items:center;height:100vh;margin:0}}</style>
</head>
<body>
<p>Yönlendiriliyor…</p>
<script>location.replace('../demo/?ad='+encodeURIComponent({js_name})+'&tur={tur}');</script>
</body>
</html>
"""


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    arg1 = sys.argv[1].strip()
    forced = sys.argv[2].strip().lower() if len(sys.argv) > 2 else None

    if re.fullmatch(r"[\d\s+()-]{10,}", arg1):          # numara verildi
        name, sec = find_by_phone(arg1)
        if not name:
            print(f"❌ {arg1} listede bulunamadı — isim ve sektörü elle ver:\n"
                  f"   python3 _yeni_demo.py \"İşletme Adı\" restoran"); sys.exit(2)
        print(f"🔎 Listede bulundu: {name}" + (f" (dosya sektörü: {sec})" if sec else ""))
    else:                                                # isim verildi
        name, sec = arg1, None

    tur = forced if forced in SECTORS else (sec or guess_sector(name))
    name = re.sub(r"\s*\([^)]*\)", "", name).strip()   # "(Bornova)" gibi konum ekini at
    name = re.sub(r"\s*/\s*.*$", "", name).strip() or name  # "X / Y Bayii" → X
    slug = slugify(name)
    folder = os.path.join(REPO, slug)
    os.makedirs(folder, exist_ok=True)
    html = REDIRECT.format(
        q_name=urllib.parse.quote(name), tur=tur, name=name,
        js_name=repr(name).replace('"', '\\"'),
    )
    open(os.path.join(folder, "index.html"), "w", encoding="utf-8").write(html)

    subprocess.run(["git", "add", f"{slug}/index.html"], cwd=REPO, check=True)
    subprocess.run(["git", "commit", "-q", "-m", f"demo: {name} ({tur})"], cwd=REPO)
    subprocess.run(["git", "push", "-q", "origin", "master"], cwd=REPO, check=True)

    print(f"✅ {name}  ·  sektör: {tur}")
    print(f"🔗 https://serdarbba.github.io/alya-panel/{slug}/")
    print("   (GitHub Pages ~1 dk içinde aktif)")


if __name__ == "__main__":
    main()
