"""Sastavlja index.html (za GitHub Pages) i preview.html (za pregled) iz src/body.html i kataloga proizvoda."""
import json, pathlib

ROOT = pathlib.Path(__file__).parent
src = (ROOT / "src/body.html").read_text()
data = json.loads((ROOT / "src/proizvodi.json").read_text())

FIELDS = ("id", "name", "price", "size", "sizeOptions", "variants", "desc", "image", "variantImages", "sizeImages")
keep = {k: [{f: x[f] for f in FIELDS if x.get(f) is not None} for x in v] for k, v in data.items()}

body = src.replace("__DATA__", json.dumps(keep, ensure_ascii=False))
(ROOT / "preview.html").write_text(body)

CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'none'; object-src 'none'; "
       "base-uri 'self'; form-action 'none'")
head, rest = body.split("</style>", 1)
(ROOT / "index.html").write_text(
    '<!doctype html>\n<html lang="bs">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n'
    '<meta name="referrer" content="strict-origin-when-cross-origin">\n'
    + head + "</style>\n</head>\n<body>\n" + rest + "\n</body>\n</html>\n")
print("index.html i preview.html su sastavljeni")
