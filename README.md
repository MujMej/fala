# fala

Sajt **fala.ba** i kartice koje idu uz svaki paket. @myjmej with love.

## Šta je gdje

| Folder / fajl | Šta je |
| --- | --- |
| `index.html` | Sajt koji se objavljuje na fala.ba (ne mijenjati ručno, pravi ga `build.py`) |
| `src/body.html` | Izgled i tekstovi sajta |
| `src/proizvodi.json` | Proizvodi, cijene, gramaže i varijante |
| `images/`, `fonts/` | Slike proizvoda i rukopis za „fala” |
| `kartice/` | Kartice za štampu, po jedna za svaki proizvod (4 po A4, obostrano) |
| `alati/kartice.py` | Pravi kartice; sastav i upotreba su upisani na vrhu fajla |
| `test_sajt.py` | Automatski test korpe, forme, cijena i sigurnosti |

## Izmjena sajta

1. Promijeni tekst u `src/body.html` ili cijenu u `src/proizvodi.json`.
2. `python3 build.py`
3. `python3 test_sajt.py` (treba: `pip install playwright && playwright install chromium`)
4. Commit i push; GitHub Pages objavi za minut-dva.

## Nove kartice

`python3 alati/kartice.py kartice/` (treba: `pip install reportlab qrcode pillow`)

Fontovi u `alati/fonts/` su pod SIL Open Font License.
