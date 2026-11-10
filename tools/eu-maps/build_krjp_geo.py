#!/usr/bin/env python3
"""Build South Korea (17) + Japan (47) map geo packs from Natural Earth 10m admin-1.
Public domain. Mirrors tools/eu-maps/build_eu_geo.py projection helpers.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import shapefile
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform, unary_union

ROOT = Path(__file__).resolve().parents[2]
SHP = ROOT / "data/eu-geo/ne10/ne_10m_admin_1_states_provinces"
OUT = ROOT / "site/assets/js"
W, H, PAD = 975, 610, 28

# Hubs already present on the world map (home-c.js)
KR_HUBS = [{"code": "ICN", "city": "Incheon", "lat": 37.46, "lon": 126.45, "region_iso": "28"}]
JP_HUBS = [{"code": "NRT", "city": "Narita", "lat": 35.77, "lon": 140.39, "region_iso": "13"}]


def round_f(x: float, n: int = 1) -> float:
    return round(float(x), n)


def ring_to_d(coords) -> str:
    if not coords:
        return ""
    parts = []
    for i, (x, y) in enumerate(coords):
        cmd = "M" if i == 0 else "L"
        parts.append(f"{cmd}{round_f(x)},{round_f(y)}")
    parts.append("Z")
    return "".join(parts)


def geom_to_d(g) -> str:
    if g.is_empty:
        return ""
    if g.geom_type == "Polygon":
        d = ring_to_d(list(g.exterior.coords))
        for hole in g.interiors:
            if len(hole.coords) >= 4:
                d += ring_to_d(list(hole.coords))
        return d
    if g.geom_type == "MultiPolygon":
        polys = sorted(g.geoms, key=lambda p: p.area, reverse=True)
        keep = []
        if not polys:
            return ""
        main = polys[0].area
        for p in polys:
            if p.area >= main * 0.002 or p.area > 80:
                keep.append(p)
        return "".join(geom_to_d(p) for p in keep)
    return ""


def fit_project(geoms: dict, view=(W, H, PAD)):
    fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    def project_ll(g):
        return transform(lambda x, y: fwd.transform(x, y), g)

    projected = {k: project_ll(g) for k, g in geoms.items()}
    minx = min(g.bounds[0] for g in projected.values())
    miny = min(g.bounds[1] for g in projected.values())
    maxx = max(g.bounds[2] for g in projected.values())
    maxy = max(g.bounds[3] for g in projected.values())
    bw, bh = maxx - minx, maxy - miny
    w, h, pad = view
    scale = min((w - 2 * pad) / bw, (h - 2 * pad) / bh)
    ox = (w - bw * scale) / 2
    oy = (h - bh * scale) / 2

    def to_svg(g):
        def _t(x, y):
            sx = ox + (x - minx) * scale
            sy = h - (oy + (y - miny) * scale)
            return (sx, sy)

        return transform(_t, g)

    meta = {"minx": minx, "miny": miny, "scale": scale, "ox": ox, "oy": oy, "h": h}
    return {k: to_svg(g) for k, g in projected.items()}, meta


def ll_to_svg(lon, lat, meta):
    fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = fwd.transform(lon, lat)
    sx = meta["ox"] + (x - meta["minx"]) * meta["scale"]
    sy = meta["h"] - (meta["oy"] + (y - meta["miny"]) * meta["scale"])
    return round_f(sx), round_f(sy)


def load_features(adm0: str):
    sf = shapefile.Reader(str(SHP))
    fields = [f[0] for f in sf.fields[1:]]
    out = []
    for sr, rec in zip(sf.shapes(), sf.records()):
        d = dict(zip(fields, rec))
        if d.get("adm0_a3") != adm0:
            continue
        geom = shape(sr.__geo_interface__)
        if geom.is_empty:
            continue
        out.append((d, geom))
    return out


def dissolve(groups: dict[str, list]):
    out = {}
    for key, geoms in groups.items():
        u = unary_union(geoms)
        if u.is_empty:
            continue
        u = u.simplify(0.02, preserve_topology=True)
        out[key] = u
    return out


# Main-islands lon/lat box: Hokkaidō–Kyūshū. Excludes Okinawa (~26°N) and remote
# Pacific outliers (Ogasawara, Minamitorishima / Ōtorishima, etc.) that otherwise
# shrink the fit to a third of the viewBox (same problem as un-inset Alaska).
JP_MAIN_W, JP_MAIN_S, JP_MAIN_E, JP_MAIN_N = 128.0, 30.05, 146.2, 45.75
# Okinawa main chain for the inset (drop Daitō / further outliers)
JP_OKI_W, JP_OKI_S, JP_OKI_E, JP_OKI_N = 122.5, 23.8, 131.5, 28.6


def keep_parts_in_box(g, west, south, east, north):
    """Keep polygon parts whose centroid lies inside the lon/lat box."""
    from shapely.geometry import MultiPolygon, Polygon

    def ok(poly):
        c = poly.centroid
        return west <= c.x <= east and south <= c.y <= north

    if g is None or g.is_empty:
        return None
    if g.geom_type == "Polygon":
        return g if ok(g) else None
    if g.geom_type == "MultiPolygon":
        keep = [p for p in g.geoms if ok(p)]
        if not keep:
            return None
        return keep[0] if len(keep) == 1 else MultiPolygon(keep)
    return g



def pack(svg_geoms: dict, names: dict[str, str], extra: dict | None = None):
    extra = extra or {}
    geo = {}
    for code, g in svg_geoms.items():
        g2 = g.simplify(0.8, preserve_topology=True)
        c = g2.representative_point()
        item = {
            "name": names[code],
            "d": geom_to_d(g2),
            "c": [round_f(c.x), round_f(c.y)],
            "cities": [],
        }
        if extra.get(code):
            item.update(extra[code])
        geo[code] = item
    return geo


def color_tones(geoms_ll: dict, n_tones=5) -> dict[str, str]:
    """Greedy graph coloring so neighbours get different st-tN classes."""
    codes = list(geoms_ll.keys())
    adj = {c: set() for c in codes}
    items = list(geoms_ll.items())
    for i, (a, ga) in enumerate(items):
        for b, gb in items[i + 1 :]:
            try:
                if ga.touches(gb) or ga.intersects(gb.buffer(0.01)):
                    adj[a].add(b)
                    adj[b].add(a)
            except Exception:
                pass
    # order by degree desc
    order = sorted(codes, key=lambda c: (-len(adj[c]), c))
    assign = {}
    for c in order:
        used = {assign[n] for n in adj[c] if n in assign}
        for t in range(1, n_tones + 1):
            if t not in used:
                assign[c] = t
                break
        else:
            assign[c] = (hash(c) % n_tones) + 1
    return {c: f"st-t{assign[c]}" for c in codes}


def clean_jp_name(name: str) -> str:
    name = name or ""
    for suf in (" Prefecture", " Metropolis", " Circuit"):
        if name.endswith(suf):
            name = name[: -len(suf)]
    # normalize common forms
    return name.replace("Ō", "O").replace("ō", "o").replace("ū", "u")


def build_korea():
    feats = load_features("KOR")
    by = {}
    names = {}
    for d, g in feats:
        iso = d.get("iso_3166_2") or ""
        code = iso.split("-")[-1] if iso else None
        if not code:
            continue
        name = d.get("name_en") or d.get("name")
        by.setdefault(code, []).append(g)
        names[code] = name
    assert len(by) == 17, f"expected 17 KR divisions, got {len(by)}"
    g = dissolve(by)
    svg, meta = fit_project(g)
    geo = pack(svg, names)
    tones = color_tones(g, n_tones=4)  # white/red/blue/charcoal
    airports = []
    for h in KR_HUBS:
        x, y = ll_to_svg(h["lon"], h["lat"], meta)
        airports.append(
            {
                "code": h["code"],
                "city": h["city"],
                "province": h["region_iso"],
                "state": h["region_iso"],
                "x": x,
                "y": y,
                "lat": h["lat"],
                "lon": h["lon"],
            }
        )
    return geo, airports, tones, names


def build_japan():
    feats = load_features("JPN")
    by = {}
    names = {}
    for d, g in feats:
        iso = d.get("iso_3166_2") or ""
        code = iso.split("-")[-1] if iso else None
        if not code:
            continue
        name = clean_jp_name(d.get("name_en") or d.get("name") or code)
        by.setdefault(code, []).append(g)
        names[code] = name
    assert len(by) == 47, f"expected 47 JP prefectures, got {len(by)}"

    # Clip each prefecture to main-island parts before dissolve/fit (drops Ogasawara etc.)
    main_raw = {k: v for k, v in by.items() if k != "47"}
    main_clipped = {}
    for code, geoms in main_raw.items():
        u = unary_union(geoms)
        clipped = keep_parts_in_box(u, JP_MAIN_W, JP_MAIN_S, JP_MAIN_E, JP_MAIN_N)
        if clipped is None or clipped.is_empty:
            raise SystemExit(f"JP {code} {names[code]} empty after mainland clip")
        main_clipped[code] = clipped.simplify(0.02, preserve_topology=True)

    svg, meta = fit_project(main_clipped, view=(W, H, 18))  # tighter pad → fill frame
    geo = pack(svg, {k: names[k] for k in main_clipped})
    tones = color_tones(main_clipped, n_tones=5)

    oki = by.get("47")
    if oki:
        og = unary_union(oki)
        og = keep_parts_in_box(og, JP_OKI_W, JP_OKI_S, JP_OKI_E, JP_OKI_N) or og
        og = og.simplify(0.02, preserve_topology=True)
        # Bottom-left inset like USA Hawaii
        slot = (36, 455, 230, 140)
        fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        pg = transform(lambda x, y: fwd.transform(x, y), og.simplify(0.04, preserve_topology=True))
        minx, miny, maxx, maxy = pg.bounds
        bw, bh = max(maxx - minx, 1e-6), max(maxy - miny, 1e-6)
        x0, y0, sw, sh = slot
        sc = min((sw - 12) / bw, (sh - 12) / bh)
        ox = x0 + (sw - bw * sc) / 2
        oy = y0 + (sh - bh * sc) / 2

        def _t(x, y):
            sx = ox + (x - minx) * sc
            sy = y0 + sh - ((oy - y0) + (y - miny) * sc)
            return (sx, sy)

        sg = transform(_t, pg).simplify(0.35, preserve_topology=True)
        c = sg.representative_point()
        geo["47"] = {
            "name": names["47"],
            "d": geom_to_d(sg),
            "c": [round_f(c.x), round_f(c.y)],
            "cities": [],
            "inset": True,
        }
        tones["47"] = "st-t3"

    airports = []
    for h in JP_HUBS:
        x, y = ll_to_svg(h["lon"], h["lat"], meta)
        airports.append(
            {
                "code": h["code"],
                "city": h["city"],
                "province": h["region_iso"],
                "state": h["region_iso"],
                "x": x,
                "y": y,
                "lat": h["lat"],
                "lon": h["lon"],
            }
        )
    return geo, airports, tones, names


def write_js(var_geo: str, var_air: str, geo: dict, airports: list, path: Path):
    path.write_text(
        "/* Natural Earth 10m admin-1 (public domain) → simplified SVG paths. */\n"
        f"window.{var_geo}={json.dumps(geo, ensure_ascii=False, separators=(',', ':'))};\n"
        f"window.{var_air}={json.dumps(airports, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )
    print(path.name, len(geo), "regions", len(airports), "airports", path.stat().st_size, "bytes")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    kr_geo, kr_air, kr_tones, kr_names = build_korea()
    jp_geo, jp_air, jp_tones, jp_names = build_japan()
    write_js("KR_GEO", "KR_GEO_AIRPORTS", kr_geo, kr_air, OUT / "south-korea-map-geo.js")
    write_js("JP_GEO", "JP_GEO_AIRPORTS", jp_geo, jp_air, OUT / "japan-map-geo.js")
    meta = {
        "kr": sorted(kr_geo.keys()),
        "jp": sorted(jp_geo.keys()),
        "kr_count": len(kr_geo),
        "jp_count": len(jp_geo),
        "kr_tones": kr_tones,
        "jp_tones": jp_tones,
        "kr_names": kr_names,
        "jp_names": jp_names,
        "source": "Natural Earth 10m Cultural admin-1 states and provinces",
        "license": "Public domain (Natural Earth)",
        "url": "https://www.naturalearthdata.com/",
        "okinawa": "inset (USA-style AK/HI offset)",
        "mainland_fit": "lon/lat box excludes Ogasawara/Minamitorishima; Okinawa inset separately",
    }
    qa = ROOT / "qa/krjp"
    qa.mkdir(parents=True, exist_ok=True)
    (qa / "geo-meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"kr": len(kr_geo), "jp": len(jp_geo), "kr_air": kr_air, "jp_air": jp_air}, indent=2))
    return meta


if __name__ == "__main__":
    main()
