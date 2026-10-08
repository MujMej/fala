"""fala kartice: jedna prednja strana po liniji, poleđina po proizvodu, 4 kartice po A4 s reznim oznakama.
Upotreba: python3 alati/kartice.py kartice/
Potrebno: pip install reportlab qrcode pillow"""
import sys, math, random, qrcode, subprocess, glob, os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor as H
from PIL import Image

OUT = sys.argv[1].rstrip("/") + "/"
F = G = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"
FALA_FONT = sys.argv[2] if len(sys.argv) > 2 else F + "Satisfy-Regular.ttf"
pdfmetrics.registerFont(TTFont("FALA", FALA_FONT))
pdfmetrics.registerFont(TTFont("HAND", F + "CaveatBrush-Regular.ttf"))
pdfmetrics.registerFont(TTFont("HAND2", F + "Caveat-Bold.ttf"))
pdfmetrics.registerFont(TTFont("PL", G + "Poppins-Light.ttf"))
pdfmetrics.registerFont(TTFont("PR", G + "Poppins-Regular.ttf"))
pdfmetrics.registerFont(TTFont("PM", G + "Poppins-Medium.ttf"))

INK, SAGE, LAVD, CAM, HONEY = H("#2f3b29"), H("#6c8160"), H("#6d5ea0"), H("#e6b93f"), H("#c9963c")
NOTE, RULE, TODO = H("#fbf7ee"), H("#e4dccb"), H("#c0392b")
CW, CH, B = 74 * mm, 105 * mm, 3 * mm

random.seed(7)
def lilac_png(path, base=(222, 214, 238)):
    im = Image.new("RGB", (660, 920), base); px = im.load()
    for y in range(920):
        for x in range(660):
            n = random.randint(-7, 7); px[x, y] = (base[0] + n, base[1] + n, base[2] + n)
    im.save(path); return ImageReader(path)
LILAC = lilac_png(OUT + "_lilac.png")

q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=20, border=1)
q.add_data("http://fala.ba"); q.make(fit=True)
q.make_image(fill_color="#2f3b29", back_color="#fbf7ee").convert("RGB").save(OUT + "_qr.png")
QR = ImageReader(OUT + "_qr.png")

# ---------------- proizvodi ----------------
HERBS = ["Neven", "Kamilica", "Menta", "Veren", "Kantarion", "Jorgovan",
         "Ružmarin", "Žalfija", "Lavanda", "Čuber", "Narandža", "Limun"]
MACERAT_NOTE = "Macerat: osušena biljka 40 dana odležava u hladno cijeđenom ekstra djevičanskom maslinovom ulju, zaštićena od svjetla, pa se procijedi."
PILING_SASTAV = ("Krupna morska so, Epsom so, šećer, mljevena riža, ulje kokosa, badema i ricinusa, "
                 "macerat ljekovitog bilja, sušeno bilje i eterična ulja varijante.")
BOMB_SASTAV = ("Soda bikarbona i limunska kiselina (2 : 1), morska so, Epsom so, mlijeko u prahu, "
               "čaj od bilja, kokosovo ulje, macerat kamilice i eterično ulje varijante.")
KUGLICE_SASTAV = ("Krupna morska so, soda bikarbona i limunska kiselina (2 : 0,5), Epsom so, mlijeko u prahu, "
                  "čaj od bilja (do 10 g na 100 g) i eterično ulje varijante.")
STOPALA_UPOTREBA = ("Preliti vrelom vodom i ostaviti 3 do 5 minuta da se bilje otvori. Kad voda dođe do temperature "
                    "koja tebi prija, potopi stopala i odmori se.")
PRODUCTS = [
    dict(key="piling", line="izvana", title="Piling za tijelo", sizes=["100 g", "300 g"],
         variants=["Citrus", "Narandža + ružmarin", "Pačuli + žalfija", "Hibiskus + ruža + jasmin",
                   "Pepermint", "Lavanda", "Vanila + kokos", "Limun + đumbir + z. čaj"],
         sastav=PILING_SASTAV,
         upotreba="Najbolje washclothom: na vlažnu kožu, kružnim pokretima, pa isprati toplom vodom. Samo za vanjsku upotrebu."),
    dict(key="balzam", line="izvana", title="Balzam", sizes=["5 g", "55 g"], variants=[],
         sastav="Pčelinji vosak, kokosovo ulje, shea butter, bademovo ulje, ricinusovo ulje, ulje koštica grožđa i macerat ljekovitog bilja.",
         herbs="MACERAT OD", herb_note=MACERAT_NOTE,
         upotreba="Malo balzama utrljati u suhu kožu: usne, ruke, laktove, pete. Samo za vanjsku upotrebu."),
    dict(key="bathbomb", line="izvana", title="Bathbomb", sizes=["Kuglica do 50 g", "Krofna do 100 g"],
         variants=["Lavanda", "Pepermint", "Citrus", "Kantarion", "Lipa + jasmin", "Ruža + hibiskus + šipak", "Limun + zeleni čaj"],
         sastav=BOMB_SASTAV,
         upotreba="Ubaci u kadu s toplom vodom i pusti da se rastopi. Ulja ostaju na koži i na kadi: oprez, klizavo je."),
    dict(key="patkica", line="djeca", title="Duckbomb patkica", sizes=["1 patkica", "Paket 4"], variants=[],
         sastav="Soda bikarbona i limunska kiselina (2 : 1), morska so, mlijeko u prahu, kokosovo ulje i macerat kamilice. Bez boja.",
         upotreba="Ubaci u toplu vodu za kupanje. Djeca se kupaju uz nadzor odrasle osobe. Kada može biti klizava."),
    dict(key="kuglice-stopala", line="bossonoga", title="Kuglice za stopala", sizes=["1 kom", "9 kom", "16 kom"], variants=[],
         sastav=KUGLICE_SASTAV, lead="Jedna kuglica, jedna nožica.",
         upotreba="U lavor stavi po jednu kuglicu za svaku nogu. " + STOPALA_UPOTREBA),
    dict(key="soli-stopala", line="bossonoga", title="Soli za stopala", sizes=["100 g", "200 g", "300 g"],
         variants=["Lavanda", "Pepermint", "Citrus", "Hibiskus + ruža + jasmin", "Kamilica + neven + kantarion", "Vanila + kokos"],
         sastav=KUGLICE_SASTAV,
         upotreba="Drvenom kašičicom dozirati u lavor. " + STOPALA_UPOTREBA),
    dict(key="macerat", line="izvana", title="Macerat", sizes=["______ ml"], variants=[],
         sastav="Osušena biljka i hladno cijeđeno ekstra djevičansko maslinovo ulje. Biljka 40 dana odležava u zatvorenoj staklenoj tegli, zaštićena od svjetla, uz povremeno protresanje. Zatim se procijedi i čuva u tamnoj boci.",
         herbs="BILJKA",
         upotreba="Nekoliko kapi utrljati u kožu ili dodati u kupku. Samo za vanjsku upotrebu."),
    dict(key="cvrsti-parfem", line="izvana", title="Čvrsti parfem", sizes=["______ g"],
         variants=["Ružmarin", "Citrus", "Sandalovina", "Pačuli", "Jasmin", "Vanila", "Pepermint"],
         sastav="Pčelinji vosak, kokosovo ulje, shea butter, macerat ljekovitog bilja i eterična ulja varijante.",
         upotreba="Prstom nanesi na zapešća, vrat ili bradu; toplina kože polako budi miris. Pepermint je lijep za laganu masažu sljepoočnica i tjemena, samo ga drži dalje od očiju."),
]
LINES = {
    "izvana": dict(label="FALA IZVANA", greet="Drago moje tijelo,", close="što si uz mene.", ring="IZNUTRA · IZVANA · FALA.BA · "),
    "djeca": dict(label="FALA IZVANA · ZA DJECU", greet="Drago moje tijelo,", close="što si uz mene.", ring="IZNUTRA · IZVANA · FALA.BA · ", ducks=True),
    "bossonoga": dict(label="BOSSONOGA · ZA STOPALA", greet="Drage moje noge,", close="što me nosite.", ring="BOSSONOGA · FALA.BA · "),
}

# ---------------- crtanje ----------------
def T(c, t, x, y, font, size, col, center=True, sp=0, right=False):
    c.setFont(font, size); c.setFillColor(col)
    if sp:
        w = sum(pdfmetrics.stringWidth(ch, font, size) for ch in t) + sp * (len(t) - 1)
        cx = x - w / 2 if center else x
        for ch in t: c.drawString(cx, y, ch); cx += pdfmetrics.stringWidth(ch, font, size) + sp
    elif right: c.drawRightString(x, y, t)
    elif center: c.drawCentredString(x, y, t)
    else: c.drawString(x, y, t)

def para(c, text, x, y, w, font="PL", size=5.9, lead=7.7, col=INK):
    c.setFont(font, size); c.setFillColor(col); line = ""
    for word in text.split():
        t = (line + " " + word).strip()
        if pdfmetrics.stringWidth(t, font, size) > w: c.drawString(x, y, line); y -= lead; line = word
        else: line = t
    if line: c.drawString(x, y, line); y -= lead
    return y

def box(c, x, y, s=2.1 * mm):
    c.setStrokeColor(LAVD); c.setLineWidth(0.6); c.roundRect(x, y - 0.5 * mm, s, s, 0.5 * mm, stroke=1, fill=0)

def chamomile(c, x, y, r):
    c.saveState(); c.translate(x, y)
    c.setFillColor(H("#fffdf7")); c.setStrokeColor(H("#d9d2c2")); c.setLineWidth(0.3)
    for i in range(14):
        c.saveState(); c.rotate(i * 360 / 14); c.ellipse(r * 0.25, -r * 0.16, r, r * 0.16, stroke=1, fill=1); c.restoreState()
    c.setFillColor(CAM); c.circle(0, 0, r * 0.3, stroke=0, fill=1)
    c.setFillColor(HONEY); c.circle(r * 0.06, -r * 0.06, r * 0.16, stroke=0, fill=1); c.restoreState()


DUCKY = H("#e6b93f")
def duck(c, x, y, s=1.0, flip=False, fill=None):
    """Obris patkice: tijelo, glava, kljun, krilo, oko."""
    c.saveState(); c.translate(x, y)
    if flip: c.scale(-1, 1)
    c.scale(s, s)
    c.setStrokeColor(INK); c.setLineWidth(0.9 / s); c.setLineJoin(1); c.setLineCap(1)
    if fill: c.setFillColor(fill)
    p = c.beginPath()
    p.moveTo(-9, 0)
    p.curveTo(-11, 6, -7, 9, -3, 7)          # rep gore
    p.curveTo(-1, 6.2, 1, 6.6, 2.5, 7.2)
    p.curveTo(0.5, 9, 0.5, 14.5, 5, 15.2)     # vrat i glava
    p.curveTo(9.5, 15.8, 11, 12, 9.4, 9.6)
    p.lineTo(12.6, 9.2)                        # kljun
    p.curveTo(13, 8.2, 11.5, 7.8, 9.0, 8.2)
    p.curveTo(11.5, 6, 11, 0.5, 6, -1)        # prsa
    p.curveTo(1, -2.6, -6, -2.4, -9, 0)
    p.close()
    c.drawPath(p, stroke=1, fill=1 if fill else 0)
    w = c.beginPath(); w.moveTo(-4, 3.2); w.curveTo(-1, 5, 3, 4.5, 4, 2); w.curveTo(1, 2.6, -2, 2, -4, 3.2)
    c.drawPath(w, stroke=1, fill=0)
    c.setFillColor(INK); c.circle(6.3, 12.4, 0.75, stroke=0, fill=1)
    c.setFillColor(HONEY); kb = c.beginPath(); kb.moveTo(9.4, 9.6); kb.lineTo(12.6, 9.2); kb.curveTo(13, 8.2, 11.5, 7.8, 9.0, 8.2); kb.close()
    c.drawPath(kb, stroke=0, fill=1)
    c.restoreState()

def foot(c, x, y, s=1.0, ang=0, col=LAVD, alpha=0.28):
    """Otisak pačje noge: zaobljena peta, opna sa zaobljenim rubom i tri prsta."""
    c.saveState(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    c.setFillColor(col); c.setFillAlpha(alpha)
    w = c.beginPath()
    w.moveTo(-0.9, -0.6)
    w.curveTo(-2.4, 1.2, -4.0, 3.2, -4.4, 5.4)      # lijevi rub do vrha lijevog prsta
    w.curveTo(-3.2, 4.4, -2.0, 4.3, -1.2, 5.0)       # zaobljena opna
    w.curveTo(-0.8, 5.8, -0.4, 6.8, 0, 7.4)          # srednji prst
    w.curveTo(0.4, 6.8, 0.8, 5.8, 1.2, 5.0)
    w.curveTo(2.0, 4.3, 3.2, 4.4, 4.4, 5.4)          # opna i desni prst
    w.curveTo(4.0, 3.2, 2.4, 1.2, 0.9, -0.6)
    w.curveTo(0.6, -1.6, -0.6, -1.6, -0.9, -0.6)     # peta
    w.close(); c.drawPath(w, stroke=0, fill=1)
    c.setStrokeColor(col); c.setStrokeAlpha(min(alpha * 1.8, 1)); c.setLineCap(1); c.setLineWidth(0.55)
    for tx, ty in [(-3.7, 4.9), (0, 6.6), (3.7, 4.9)]:
        c.line(0, 0.2, tx, ty)
    c.restoreState()

def trail(c, x0, y0, x1, y1, n, s=1.0, alpha=0.28):
    import math as _m
    ang = _m.degrees(_m.atan2(y1 - y0, x1 - x0)) - 90
    for i in range(n):
        t = i / max(n - 1, 1)
        side = 1.6 * mm * (1 if i % 2 else -1)
        nx, ny = -_m.sin(_m.radians(ang + 90)), _m.cos(_m.radians(ang + 90))
        x = x0 + (x1 - x0) * t + side * _m.cos(_m.radians(ang))
        y = y0 + (y1 - y0) * t + side * _m.sin(_m.radians(ang))
        foot(c, x, y, s, ang, alpha=alpha)

def base(c):
    c.drawImage(LILAC, -B, -B, CW + 2 * B, CH + 2 * B)
    c.setFillColor(NOTE); c.roundRect(6 * mm, 6 * mm, CW - 12 * mm, CH - 12 * mm, 1.5 * mm, stroke=0, fill=1)

def front(c, L):
    base(c)
    c.setStrokeColor(RULE); c.setLineWidth(0.35)
    for yy in range(33, 88, 7): c.line(11 * mm, yy * mm, CW - 11 * mm, yy * mm)
    T(c, L["greet"], 12 * mm, 84.5 * mm, "HAND2", 15, LAVD, center=False)
    if L.get("ducks"):
        trail(c, 37 * mm, 27 * mm, CW - 21 * mm, 33 * mm, 4, 1.3, 0.3)
        duck(c, CW - 14 * mm, 33.2 * mm, 1.0, fill=H("#fff3c4"))
        duck(c, CW - 15 * mm, 81 * mm, 0.62, fill=H("#fff3c4"))
    else:
        chamomile(c, CW - 12 * mm, 84 * mm, 3 * mm)
    c.saveState(); c.translate(CW / 2 + 1.5 * mm, 58.5 * mm); c.rotate(-4)
    size = 92
    while pdfmetrics.stringWidth("fala", "FALA", size) > CW - 25 * mm: size -= 2
    c.setFont("FALA", size); c.setFillColor(INK); c.drawCentredString(0, 0, "fala"); c.restoreState()
    T(c, L["close"], CW - 12 * mm, 42 * mm, "HAND2", 15, LAVD, right=True)
    cx, cy, r = 22.5 * mm, 19.5 * mm, 11.5 * mm
    c.setStrokeColor(LAVD); c.setLineWidth(0.8); c.circle(cx, cy, r, stroke=1, fill=0); c.circle(cx, cy, r - 1.2 * mm, stroke=1, fill=0)
    txt = L["ring"]; c.setFont("PM", 4.3); c.setFillColor(LAVD)
    for i, ch in enumerate(txt):
        a = 90 - i * 360 / len(txt); rr = r - 3.1 * mm
        c.saveState(); c.translate(cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a)))
        c.rotate(a - 90); c.drawCentredString(0, 0, ch); c.restoreState()
    qs = 9.6 * mm; c.drawImage(QR, cx - qs / 2, cy - qs / 2, qs, qs)
    T(c, "@myjmej", CW - 22 * mm, 21 * mm, "HAND2", 13, INK)
    T(c, "with love", CW - 22 * mm, 16 * mm, "HAND2", 13, INK)

def back(c, P, k=1.0):
    base(c)
    x, w = 10.5 * mm, CW - 21 * mm
    T(c, P["title"], CW / 2, CH - 16 * mm, "HAND", 21 if len(P["title"]) < 17 else 18, INK)
    T(c, LINES[P["line"]]["label"], CW / 2, CH - 20.8 * mm, "PM", 5.0, LAVD, sp=1.1)
    y = CH - 27.5 * mm
    fs, lead = 5.9 * k, 7.7 * k
    def lab(t):
        T(c, t, x, y, "PM", 5.0, LAVD, center=False, sp=0.8)
    if P.get("lead"):
        T(c, P["lead"], CW / 2, y + 0.4 * mm, "HAND2", 11, INK); y -= 6 * mm
    lab("U PAKETU"); y -= 4.6 * k * mm
    col = (w + 1 * mm) / max(len(P["sizes"]), 2)
    for i, sz in enumerate(P["sizes"]):
        box(c, x + i * col, y); T(c, sz, x + i * col + 3.3 * mm, y, "PR", 6.3, INK, center=False)
    y -= 5.6 * k * mm
    def grid(items, ncol=2):
        nonlocal y
        rows = math.ceil(len(items) / ncol)
        cols = [items[i * rows:(i + 1) * rows] for i in range(ncol)]
        f = 5.8 * k
        while True:
            widths = [max((pdfmetrics.stringWidth(v, "PL", f) for v in cl), default=0) for cl in cols]
            if sum(widths) + ncol * 3 * mm + (ncol - 1) * 3 * mm <= w or f <= 4.6: break
            f -= 0.1
        gap = (w - sum(widths) - ncol * 3 * mm) / max(ncol - 1, 1) if ncol > 1 else 0
        cx = x
        for ci, cl in enumerate(cols):
            for ri, v in enumerate(cl):
                yy = y - ri * 3.8 * k * mm
                box(c, cx, yy, 1.9 * mm); T(c, v, cx + 3 * mm, yy, "PL", f, INK, center=False)
            cx += 3 * mm + widths[ci] + gap
        y -= rows * 3.8 * k * mm + 1.6 * mm
    if P["variants"]:
        lab("VARIJANTA"); y -= 4.4 * k * mm; grid(P["variants"])
    lab("SASTAV"); y -= 3.5 * k * mm
    y = para(c, P["sastav"], x, y, w, size=fs, lead=lead)
    if P.get("herbs"):
        y -= 1.2 * mm; lab(P["herbs"]); y -= 4.2 * k * mm
        grid(HERBS + ["______"], ncol=3)
        if P.get("herb_note"):
            y += 0.6 * mm; y = para(c, P["herb_note"], x, y, w, font="PL", size=5.2 * k, lead=6.6 * k, col=LAVD)
    y -= 1.2 * mm; lab("KAKO KORISTITI"); y -= 3.5 * k * mm
    y = para(c, P["upotreba"], x, y, w, size=fs, lead=lead)
    if LINES[P["line"]].get("ducks"):
        duck(c, 15 * mm, CH - 22.6 * mm, 0.42, fill=H("#fff3c4"))
        duck(c, CW - 15 * mm, CH - 22.6 * mm, 0.42, flip=True, fill=H("#fff3c4"))
        trail(c, 13 * mm, 22 * mm, CW - 24 * mm, 29 * mm, 6, 1.3, 0.3)
        duck(c, CW - 15 * mm, 29.5 * mm, 1.15, fill=H("#fff3c4"))
    T(c, "Svaka serija je jedinstvena.", CW / 2, 14 * mm, "HAND2", 10.5, LAVD)
    T(c, "Serija ______", x, 9 * mm, "PL", 5.5, INK, center=False)
    T(c, "Datum ______", CW - x, 9 * mm, "PL", 5.5, INK, right=True)
    return y

import io
def fit_k(P):
    """Najveća gustina pri kojoj tekst ne udari u 'Svaka serija'."""
    for k in [1.0, 0.95, 0.9, 0.85, 0.8, 0.76]:
        tmp = canvas.Canvas(io.BytesIO(), pagesize=(CW, CH))
        if back(tmp, P, k) > 17.5 * mm: return k
    print("PREPUNO:", P["key"]); return 0.76

def back_fit(c, P):
    back(c, P, fit_k(P))

def crop(c, ox, oy):
    c.setStrokeColor(H("#888888")); c.setLineWidth(0.3); L = 4 * mm
    for X in (ox, ox + CW):
        for Y in (oy, oy + CH):
            c.line(X, Y - B - L if Y == oy else Y + B, X, Y - B if Y == oy else Y + B + L)
            c.line(X - B - L if X == ox else X + B, Y, X - B if X == ox else X + B + L, Y)

def sheet(c, draw, *a):
    PW, PH = A4; gx = gy = 10 * mm
    x0, y0 = (PW - (2 * CW + gx)) / 2, (PH - (2 * CH + gy)) / 2
    for col in range(2):
        for row in range(2):
            ox, oy = x0 + col * (CW + gx), y0 + row * (CH + gy)
            c.saveState(); c.translate(ox, oy)
            p = c.beginPath(); p.rect(-B, -B, CW + 2 * B, CH + 2 * B); c.clipPath(p, stroke=0, fill=0)
            draw(c, *a); c.restoreState(); crop(c, ox, oy)
    c.showPage()

# štampa: jedan PDF po proizvodu (strana 1 prednja, strana 2 poleđina), 4 kartice po A4
for P in PRODUCTS:
    c = canvas.Canvas(OUT + f"kartica-{P['key']}.pdf", pagesize=A4)
    c.setTitle(f"fala kartica – {P['title']}")
    sheet(c, front, LINES[P["line"]]); sheet(c, back_fit, P); c.save()

# pregled: sve kartice jedna do druge
c = canvas.Canvas(OUT + "_pregled.pdf", pagesize=(CW, CH))
for L in ("izvana", "djeca", "bossonoga"): front(c, LINES[L]); c.showPage()
for P in PRODUCTS: back_fit(c, P); c.showPage()
c.save()
for f in glob.glob(OUT + "_p-*.png"): os.remove(f)
subprocess.run(["pdftoppm", "-r", "170", "-png", OUT + "_pregled.pdf", OUT + "_p"], check=True)
ims = [Image.open(p) for p in sorted(glob.glob(OUT + "_p-*.png"))]
w, h = ims[0].size; g = 30; cols = 4; rows = math.ceil(len(ims) / cols)
sheet_img = Image.new("RGB", (cols * w + (cols + 1) * g, rows * h + (rows + 1) * g), (236, 236, 232))
for i, im in enumerate(ims): sheet_img.paste(im, (g + (i % cols) * (w + g), g + (i // cols) * (h + g)))
sheet_img.save(OUT + "pregled-kartica.png"); print("ok", len(ims))
