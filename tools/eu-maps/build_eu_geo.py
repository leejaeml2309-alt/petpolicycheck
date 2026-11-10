#!/usr/bin/env python3
"""Build simplified SVG path geo packs for UK / France / Germany maps.
Source: Natural Earth 10m admin-1 states/provinces (public domain).
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import shapefile
from pyproj import Transformer
from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from shapely.ops import transform, unary_union

ROOT = Path(__file__).resolve().parents[2]
SHP = ROOT / "data/eu-geo/ne10/ne_10m_admin_1_states_provinces"
OUT = ROOT / "site/assets/js"
W, H, PAD = 975, 610, 28


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
        # keep largest polygons first; drop tiny crumbs
        polys = sorted(g.geoms, key=lambda p: p.area, reverse=True)
        keep = []
        if not polys:
            return ""
        main = polys[0].area
        for p in polys:
            if p.area >= main * 0.002 or p.area > 80:  # svg units after project
                keep.append(p)
        return "".join(geom_to_d(p) for p in keep)
    return ""


def fit_project(geoms: dict[str, object], view=(W, H, PAD)):
    """Project lon/lat geoms to SVG with a fitted equirectangular-ish mercator."""
    # Use Web Mercator then affine-fit into viewBox
    fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    def project_ll(g):
        return transform(lambda x, y: fwd.transform(x, y), g)

    projected = {k: project_ll(g) for k, g in geoms.items()}
    # bounds
    minx = min(g.bounds[0] for g in projected.values())
    miny = min(g.bounds[1] for g in projected.values())
    maxx = max(g.bounds[2] for g in projected.values())
    maxy = max(g.bounds[3] for g in projected.values())
    bw, bh = maxx - minx, maxy - miny
    w, h, pad = view
    scale = min((w - 2 * pad) / bw, (h - 2 * pad) / bh)
    # center
    ox = (w - bw * scale) / 2
    oy = (h - bh * scale) / 2

    def to_svg(g):
        def _t(x, y):
            sx = ox + (x - minx) * scale
            # flip Y for SVG
            sy = h - (oy + (y - miny) * scale)
            return (sx, sy)

        return transform(_t, g)

    return {k: to_svg(g) for k, g in projected.items()}, scale


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
        # light simplify in degrees before project (~2km)
        u = u.simplify(0.02, preserve_topology=True)
        out[key] = u
    return out


def pack(svg_geoms: dict, names: dict[str, str], abbrevs: dict[str, str] | None = None):
    abbrevs = abbrevs or {}
    geo = {}
    for code, g in svg_geoms.items():
        # further simplify in svg space
        g2 = g.simplify(0.8, preserve_topology=True)
        c = g2.representative_point()
        geo[code] = {
            "name": names[code],
            "d": geom_to_d(g2),
            "c": [round_f(c.x), round_f(c.y)],
            "cities": [],
        }
        if abbrevs.get(code):
            # keep code as key; name separate
            pass
    return geo


def build_uk():
    feats = load_features("GBR")
    # 4 nations via geonunit
    by_nation = defaultdict(list)
    by_eng_region = defaultdict(list)
    for d, g in feats:
        unit = d.get("geonunit") or ""
        if unit in ("England", "Scotland", "Wales", "Northern Ireland"):
            by_nation[unit].append(g)
        if unit == "England":
            reg = d.get("region") or ""
            # Map NE English regions to the 9 ITL1 / former GORs
            # Greater London is its own; others are already the 8 + London
            if reg:
                by_eng_region[reg].append(g)

    NATION_CODE = {
        "England": "ENG",
        "Scotland": "SCT",
        "Wales": "WLS",
        "Northern Ireland": "NIR",
    }
    nations = dissolve({NATION_CODE[k]: v for k, v in by_nation.items() if k in NATION_CODE})
    names = {
        "ENG": "England",
        "SCT": "Scotland",
        "WLS": "Wales",
        "NIR": "Northern Ireland",
    }
    svg, _ = fit_project(nations)
    geo = pack(svg, names)

    # English regions optional pack (same projection frame as UK nations — re-fit alone for clarity)
    # Normalize region names
    REGION_CODE = {
        "North East": "NE",
        "North West": "NW",
        "Yorkshire and the Humber": "YH",
        "East Midlands": "EM",
        "West Midlands": "WM",
        "East": "EE",
        "East of England": "EE",
        "Greater London": "GL",
        "London": "GL",
        "South East": "SE",
        "South West": "SW",
    }
    reg_groups = defaultdict(list)
    reg_names = {}
    for reg, geoms in by_eng_region.items():
        code = REGION_CODE.get(reg)
        if not code:
            # skip non-standard
            continue
        reg_groups[code].extend(geoms)
        reg_names[code] = "East of England" if code == "EE" and reg.startswith("East") else (
            "Greater London" if code == "GL" else reg
        )
    regions = dissolve(reg_groups)
    # Include SCT/WLS/NIR as context? Optional map is England-only regions — fit England regions alone
    if regions:
        rsvg, _ = fit_project(regions)
        rgeo = pack(rsvg, reg_names)
    else:
        rgeo = {}
    return geo, rgeo


def build_france():
    feats = load_features("FRA")
    metro = defaultdict(list)
    overseas = defaultdict(list)
    OVERSEAS_UNITS = {
        "French Guiana": ("GF", "French Guiana"),
        "Guyane française": ("GF", "French Guiana"),
        "Martinique": ("MQ", "Martinique"),
        "Guadeloupe": ("GP", "Guadeloupe"),
        "Réunion": ("RE", "Réunion"),
        "Reunion": ("RE", "Réunion"),
        "Mayotte": ("YT", "Mayotte"),
    }
    # 13 metropolitan regions (post-2016) — use region field when geonunit is France
    REGION_ABBR = {
        "Auvergne-Rhône-Alpes": "ARA",
        "Bourgogne-Franche-Comté": "BFC",
        "Bretagne": "BRE",
        "Centre-Val de Loire": "CVL",
        "Corse": "COR",
        "Grand Est": "GES",
        "Hauts-de-France": "HDF",
        "Île-de-France": "IDF",
        "Ile-de-France": "IDF",
        "Normandie": "NOR",
        "Nouvelle-Aquitaine": "NAQ",
        "Occitanie": "OCC",
        "Pays de la Loire": "PDL",
        "Provence-Alpes-Côte-d'Azur": "PAC",
        "Provence-Alpes-Côte d'Azur": "PAC",
    }
    for d, g in feats:
        unit = d.get("geonunit") or ""
        reg = d.get("region") or ""
        if unit in OVERSEAS_UNITS or reg in OVERSEAS_UNITS:
            key = OVERSEAS_UNITS.get(unit) or OVERSEAS_UNITS.get(reg)
            if key:
                overseas[key[0]].append(g)
            continue
        if unit != "France" and unit not in ("", None):
            # Corsica is France geonunit usually
            if "Corse" in (reg or "") or "Corse" in (unit or ""):
                metro["COR"].append(g)
            continue
        abbr = REGION_ABBR.get(reg)
        if abbr:
            metro[abbr].append(g)

    names = {
        "ARA": "Auvergne-Rhône-Alpes",
        "BFC": "Bourgogne-Franche-Comté",
        "BRE": "Bretagne",
        "CVL": "Centre-Val de Loire",
        "COR": "Corse",
        "GES": "Grand Est",
        "HDF": "Hauts-de-France",
        "IDF": "Île-de-France",
        "NOR": "Normandie",
        "NAQ": "Nouvelle-Aquitaine",
        "OCC": "Occitanie",
        "PDL": "Pays de la Loire",
        "PAC": "Provence-Alpes-Côte d'Azur",
    }
    metro_g = dissolve(metro)
    svg, scale = fit_project(metro_g)
    geo = pack(svg, names)

    # Overseas inset: project each separately into small slots bottom-right
    o_names = {"GF": "French Guiana", "MQ": "Martinique", "GP": "Guadeloupe", "RE": "Réunion", "YT": "Mayotte"}
    o_diss = dissolve(overseas)
    slots = [
        (720, 430, 110, 80),
        (840, 430, 110, 80),
        (720, 520, 110, 70),
        (840, 520, 70, 70),
        (920, 520, 40, 70),
    ]
    for (code, g), slot in zip(o_diss.items(), slots):
        # fit into slot
        fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        pg = transform(lambda x, y: fwd.transform(x, y), g.simplify(0.05, preserve_topology=True))
        minx, miny, maxx, maxy = pg.bounds
        bw, bh = max(maxx - minx, 1e-6), max(maxy - miny, 1e-6)
        x0, y0, sw, sh = slot
        sc = min((sw - 8) / bw, (sh - 8) / bh)
        ox = x0 + (sw - bw * sc) / 2
        oy = y0 + (sh - bh * sc) / 2

        def _t(x, y, _ox=ox, _oy=oy, _sc=sc, _miny=miny, _minx=minx, _y0=y0, _sh=sh):
            sx = _ox + (x - _minx) * _sc
            sy = _y0 + _sh - ((_oy - _y0) + (y - _miny) * _sc)
            return (sx, sy)

        sg = transform(_t, pg).simplify(0.4, preserve_topology=True)
        c = sg.representative_point()
        geo[code] = {
            "name": o_names.get(code, code),
            "d": geom_to_d(sg),
            "c": [round_f(c.x), round_f(c.y)],
            "cities": [],
            "inset": True,
        }
    return geo


def build_germany():
    feats = load_features("DEU")
    by = {}
    names = {}
    # Prefer postal code; fix Brandenburg postal which NE marks BE wrongly for Brandenburg
    POSTAL_FIX = {"Brandenburg": "BB"}
    for d, g in feats:
        name = d.get("name_en") or d.get("name")
        postal = POSTAL_FIX.get(name) or d.get("postal") or d.get("abbrev")
        if not postal:
            continue
        # Berlin and Brandenburg both BE in dump — fix
        if name == "Berlin":
            postal = "BE"
        if name == "Brandenburg":
            postal = "BB"
        by.setdefault(postal, []).append(g)
        names[postal] = name
    g = dissolve(by)
    svg, _ = fit_project(g)
    return pack(svg, names)


def write_js(var_geo: str, var_air: str, geo: dict, path: Path):
    payload = json.dumps(geo, ensure_ascii=False, separators=(",", ":"))
    path.write_text(
        f"/* Natural Earth 10m admin-1 (public domain) → simplified SVG paths. */\n"
        f"window.{var_geo}={payload};\n"
        f"window.{var_air}=[];\n",
        encoding="utf-8",
    )
    print(path.name, len(geo), "regions", path.stat().st_size, "bytes")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    uk, uk_reg = build_uk()
    write_js("UK_GEO", "UK_GEO_AIRPORTS", uk, OUT / "uk-map-geo.js")
    if uk_reg:
        write_js("UK_ENG_REGIONS_GEO", "UK_ENG_REGIONS_AIRPORTS", uk_reg, OUT / "uk-eng-regions-geo.js")
    fr = build_france()
    write_js("FR_GEO", "FR_GEO_AIRPORTS", fr, OUT / "france-map-geo.js")
    de = build_germany()
    write_js("DE_GEO", "DE_GEO_AIRPORTS", de, OUT / "germany-map-geo.js")
    # also dump region keys for data files
    meta = {
        "uk": list(uk.keys()),
        "uk_eng_regions": list(uk_reg.keys()),
        "fr": list(fr.keys()),
        "de": list(de.keys()),
        "source": "Natural Earth 10m Cultural admin-1 states and provinces",
        "license": "Public domain (Natural Earth)",
        "url": "https://www.naturalearthdata.com/",
    }
    (ROOT / "qa/eu-maps/geo-meta.json").parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "qa/eu-maps/geo-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
