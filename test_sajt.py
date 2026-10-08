"""Automatski test sajta fala: pokreće sajt lokalno i prolazi kroz njega kao kupac.
Pokretanje: python3 test_sajt.py"""
import http.server, threading, functools, urllib.parse, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(
    type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_port}/index.html"

results = []
def check(name, ok, info=""):
    results.append((name, bool(ok), info))

def msg_of(pg):
    href = pg.get_attribute("#send", "href")
    return urllib.parse.unquote(href.split("text=", 1)[1]) if "text=" in href else ""

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    pg = ctx.new_page()
    errors, bad = [], []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" and "fonts.g" not in m.text and "ERR_TUNNEL" not in m.text and "ERR_" not in m.text else None)
    pg.on("response", lambda r: bad.append(f"{r.status} {r.url}") if r.status >= 400 and "127.0.0.1" in r.url else None)
    pg.goto(URL); pg.wait_for_load_state("networkidle")

    # 1. učitavanje
    check("Stranica se učitava bez JavaScript grešaka", not errors, "; ".join(errors[:3]))
    check("Korpa je zatvorena pri učitavanju", not pg.is_visible("#drawer"))

    # 2. sve slike postoje
    for t in ["all", "njega", "bossonoga", "kreativno"]:
        pg.click(f'[data-tab="{t}"]'); pg.wait_for_timeout(150)
    pg.click('[data-tab="all"]')
    pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading='eager')")
    pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(500)
    broken = pg.evaluate("[...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'))")
    check("Sve slike proizvoda se učitavaju", not broken and not bad, ", ".join((broken + bad)[:5]))

    # 3. linije i kartice
    pg.click('[data-line="bossonoga"]'); pg.wait_for_timeout(200)
    groups = pg.eval_on_selector_all(".gh h4", "e => e.map(x => x.textContent)")
    check("Klik na Bossonoga liniju pokazuje samo stopala", groups == ["Kuglice za stopala", "Soli za stopala"], str(groups))
    pg.click('[data-tab="njega"]'); pg.wait_for_timeout(200)
    groups = pg.eval_on_selector_all(".gh h4", "e => e.map(x => x.textContent)")
    check("fala izvana ima pilinge, balzame, bathbombs, macerate i parfeme",
          all(g in groups for g in ["Pilinzi", "Balzami", "Bathbombs", "Macerati", "Čvrsti parfemi"]), str(groups))
    sast = pg.locator(".sastav").count()
    check("Proizvodi imaju sastav na klik", sast >= 10, f"{sast} proizvoda sa sastavom")

    # 4. dodavanje u korpu
    card = pg.locator('.card[data-id="scrub-paculi-zalfija"]')
    card.locator("[data-size]").select_option("1")          # 300g
    card.locator("[data-add]").click(); card.locator("[data-add]").click()
    pg.click("#openCart")
    check("Korpa broji 2 komada", pg.inner_text("#count") == "2")
    check("Cijena 2 × piling 300 g = 42 KM", pg.inner_text("#s-items") == "42 KM", pg.inner_text("#s-items"))

    # 5. poštarina i pakovanje
    pg.select_option("#f-ship", "post"); pg.select_option("#f-pay", "cod")
    check("Pošta pouzećem dodaje 10 KM", pg.inner_text("#s-total") == "52 KM", pg.inner_text("#s-total"))
    pg.select_option("#f-pay", "bank")
    check("Pošta uz uplatu dodaje 8 KM", pg.inner_text("#s-total") == "50 KM", pg.inner_text("#s-total"))
    pg.select_option("#f-gift", "5")
    check("Poklon pakovanje s karticom dodaje 5 KM", pg.inner_text("#s-total") == "55 KM", pg.inner_text("#s-total"))

    # 6. provjera forme
    pg.click("#send", modifiers=[]) if False else None
    pg.evaluate("document.getElementById('send').target=''")   # da test ne otvara novi tab
    pg.locator("#send").click(no_wait_after=True); pg.wait_for_timeout(150)
    check("Bez imena javlja grešku", "ime" in pg.inner_text("#err").lower(), pg.inner_text("#err"))
    pg.fill("#f-name", "Test Kupac"); pg.fill("#f-phone", "061 000 000")
    pg.locator("#send").click(no_wait_after=True); pg.wait_for_timeout(150)
    check("Za poštu bez adrese javlja grešku", "adresu" in pg.inner_text("#err"), pg.inner_text("#err"))
    pg.fill("#f-addr", "Ulica 1"); pg.fill("#f-city", "Banja Luka"); pg.fill("#f-note", "Za mamu")
    m = msg_of(pg)
    check("WhatsApp poruka ima proizvod, količinu i ukupno",
          "2 × Piling Pačuli + Žalfija, 300g = 42 KM" in m and "Ukupno: 55 KM" in m and "Za mamu" in m, m.replace("\n", " | ")[:160])
    check("Poruka ide na WhatsApp broj iz podešavanja", pg.get_attribute("#send", "href").startswith("https://wa.me/387"))

    # 7. količina na nulu briše stavku
    pg.click('[data-q="0"][data-d="-1"]'); pg.click('[data-q="0"][data-d="-1"]')
    check("Smanjenje na 0 briše proizvod iz korpe", pg.inner_text("#count") == "0")
    pg.click("#closeCart")

    # 8. pokušaj podmetanja lažne cijene i koda kroz preglednik
    pg.evaluate("""localStorage.setItem('fala-korpa', JSON.stringify([
      {id:'scrub-citrus', variant:'Citrus', size:'300g', qty:3, price:0, name:'<img src=x onerror=alert(1)>'},
      {id:'nepostoji', qty:1, price:-100},
      {id:'acc-washcloth', qty:1000}
    ]))""")
    dialogs = []; pg.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
    pg.reload(); pg.wait_for_load_state("networkidle"); pg.click("#openCart"); pg.wait_for_timeout(200)
    check("Izmijenjena cijena se ignoriše (3 × 21 + 99 × 5 = 558 KM)", pg.inner_text("#s-items") == "558 KM", pg.inner_text("#s-items"))
    check("Nepostojeći proizvod se izbacuje iz korpe", pg.locator(".item").count() == 2)
    check("Podmetnuti kod se ne izvršava", not dialogs and pg.locator(".item img[src='x']").count() == 0)
    pg.evaluate("localStorage.clear()")

    # 9. dugmad "Pitaj" nose izabranu varijantu
    pg.reload(); pg.click('[data-tab="njega"]')
    mc = pg.locator('.card[data-id="x-macerat"]')
    mc.locator("[data-variant]").select_option("Jorgovan")
    href = urllib.parse.unquote(mc.locator("a.add").get_attribute("href"))
    check("„Pitaj” za macerat šalje izabranu biljku", "Macerat po izboru (Jorgovan)" in href, href[-60:])

    # 10. vanjski linkovi
    unsafe = pg.eval_on_selector_all('a[target=_blank]', "e => e.filter(a => !(a.rel||'').includes('noopener')).map(a => a.href)")
    check("Svi vanjski linkovi imaju zaštitu (noopener)", not unsafe, ", ".join(unsafe))

    # 11. telefon
    m = b.new_page(viewport={"width": 360, "height": 780})
    m.goto(URL); m.wait_for_load_state("networkidle")
    for t in ["all", "njega", "bossonoga", "kreativno"]:
        m.click(f'[data-tab="{t}"]')
        w = m.evaluate("document.documentElement.scrollWidth")
        if w > 360: break
    check("Na uskom telefonu (360 px) nema širenja u stranu", w <= 360, f"širina {w}px")
    m.click("#openCart")
    check("Korpa na telefonu staje u ekran", m.evaluate("document.getElementById('drawer').getBoundingClientRect().width") <= 360)

    # 12. sigurnosna zaglavlja
    html = (ROOT / "index.html").read_text()
    check("Stranica ima Content-Security-Policy", "Content-Security-Policy" in html)
    check("Nema skrivenih ključeva ni lozinki u kodu",
          not any(k in html.lower() for k in ["api_key", "apikey", "secret", "password", "token"]))
    b.close()

w = max(len(n) for n, _, _ in results)
for n, ok, info in results:
    print(("PROŠLO  " if ok else "PALO    ") + n.ljust(w) + ("   " + info if (info and not ok) else ""))
print(f"\n{sum(ok for _, ok, _ in results)}/{len(results)} testova prošlo")
