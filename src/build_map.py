"""Turn the geoBoundaries ADM1 outline of Mozambique into small inline SVG paths.

The source is 259 KB of coordinates. The page budget is tens of kilobytes, so the
rings are thinned with Douglas-Peucker and the coordinates rounded to one decimal
in SVG space - at this size nothing finer is visible anyway.

Run indirectly via build_site.py; run directly to print the size.
"""

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SRC = ("https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/"
       "gbOpen/MOZ/{lvl}/geoBoundaries-MOZ-{lvl}_simplified.geojson")
W, H = 300, 620          # viewBox; Mozambique is far taller than it is wide
MIN_RING_AREA = 0.05     # drop offshore islets that render as single pixels


def fetch(lvl="ADM1"):
    dst = RAW / f"moz_{lvl.lower()}.geojson"
    if not dst.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(SRC.format(lvl=lvl), headers={"User-Agent": "quinhao-etl/1.0"})
        with urllib.request.urlopen(req) as r:
            dst.write_bytes(r.read())
    return json.loads(dst.read_text())


def perp(p, a, b):
    """Perpendicular distance from p to segment ab, in degrees - good enough here."""
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return ((x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2) ** 0.5


def simplify(pts, tol):
    if len(pts) < 3:
        return pts
    i = max(range(1, len(pts) - 1), key=lambda k: perp(pts[k], pts[0], pts[-1]))
    if perp(pts[i], pts[0], pts[-1]) <= tol:
        return [pts[0], pts[-1]]
    return simplify(pts[:i + 1], tol)[:-1] + simplify(pts[i:], tol)


def ring_area(r):
    return abs(sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1]
                   for i in range(len(r) - 1))) / 2


def build(tol=0.02, lvl="ADM1", bounds=None):
    """bounds pins ADM2 to the ADM1 projection so the two layers line up exactly."""
    gj = fetch(lvl)
    rings = []
    for f in gj["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        keep = [p[0] for p in polys if ring_area(p[0]) >= MIN_RING_AREA]
        rings.append((f["properties"]["shapeName"], keep))

    if bounds:
        x0, x1, y0, y1 = bounds
    else:
        xs = [x for _, ps in rings for p in ps for x, _ in p]
        ys = [y for _, ps in rings for p in ps for _, y in p]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    sx, sy = W / (x1 - x0), H / (y1 - y0)
    scale = min(sx, sy)
    ox = (W - (x1 - x0) * scale) / 2
    oy = (H - (y1 - y0) * scale) / 2

    out = {}
    _ = (x0, x1, y0, y1)
    for name, polys in rings:
        d = []
        for ring in polys:
            pts = [(round(ox + (x - x0) * scale, 1), round(oy + (y1 - y) * scale, 1))
                   for x, y in simplify(ring, tol)]
            d.append("M" + "L".join(f"{x} {y}" for x, y in pts) + "Z")
        out[name] = "".join(d)
    return out, W, H, (x0, x1, y0, y1)


if __name__ == "__main__":
    paths, w, h, _b = build()
    blob = json.dumps(paths, separators=(",", ":"))
    print(f"{len(paths)} provinces, {len(blob)/1024:.1f} KB of path data, viewBox {w}x{h}")
    for k, v in paths.items():
        print(f"  {k:<14} {len(v):>6} chars")
