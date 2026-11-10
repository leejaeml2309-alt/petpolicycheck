#!/usr/bin/env python3
"""Rebuild South Korea (17) + Japan (47) map geo packs.

Source: Natural Earth 10m Cultural admin-1 states and provinces
        https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/
License: public domain (Natural Earth).

Topology-aware simplification via mapshaper (Visvalingam, shared edges preserved)
so neighbouring regions touch with no gaps when zooming. Previous build
simplified each polygon independently (shapely.simplify), which opened gaps.

Airports (international scheduled / officially named international):
  Korea — KAC English site (https://www.airport.co.kr/wwweng/index.do)
          names 7 as “International”: Gimpo, Gimhae, Jeju, Daegu, Cheongju,
          Muan, Yangyang; plus Incheon International Airport, operated by
          IIAC (not KAC), https://www.airport.kr/
          Other KAC airports (Gwangju, Ulsan, Yeosu, Pohang Gyeongju,
          Sacheon, Gunsan, Wonju) are listed without “International” and
          are NOT included — flag for Marc.
  Japan — MLIT “各空港における国際線就航状況調べ”, 2026 winter schedule
          authorised data (direct scheduled passenger flights):
          https://www.mlit.go.jp/koku/content/002028812.pdf
          (index: https://www.mlit.go.jp/koku/koku_tk1_000013.html)
          Via-only list (002028813.pdf) adds no extra airports.
Coordinates: OurAirports airports.csv, public domain
          https://davidmegginson.github.io/ourairports-data/airports.csv
Cities: capital + official metropolitan/provincial capitals (KR) and
        major cities with Natural Earth pop_max >= 1,000,000 (JP);
        coordinates from Natural Earth 10m populated places (public domain).
"""
from __future__ import annotations

import csv
import json
import math
import subprocess
import tempfile
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import MultiPolygon, mapping, shape
from shapely.ops import transform, unary_union

ROOT = Path(__file__).resolve().parents[2]
SHP = ROOT / "data/eu-geo/ne10/ne_10m_admin_1_states_provinces.shp"
PLACES = Path("/tmp/ne10/places/ne_10m_populated_places.shp")
AIRPORTS_CSV = Path("/tmp/krjp-src/airports.csv")
OUT_SITE = ROOT / "site/assets/js"
OUT_STATIC = ROOT / "static/assets/js"
W, H, PAD = 975, 610, 28

# Official English names (KAC / IIAC). IATA from the same operators' usage.
KR_AIRPORTS = [
    # IIAC
    {"code": "ICN", "name": "Incheon International Airport", "city": "Incheon", "region": "28", "page": "../airport/ICN/"},
    # KAC, named International on https://www.airport.co.kr/wwweng/index.do
    {"code": "GMP", "name": "Gimpo International Airport", "city": "Seoul", "region": "11", "page": None},
    {"code": "PUS", "name": "Gimhae International Airport", "city": "Busan", "region": "26", "page": None},
    {"code": "CJU", "name": "Jeju International Airport", "city": "Jeju City", "region": "49", "page": None},
    {"code": "CJJ", "name": "Cheongju International Airport", "city": "Cheongju", "region": "43", "page": None},
    {"code": "TAE", "name": "Daegu International Airport", "city": "Daegu", "region": "27", "page": None},
    {"code": "MWX", "name": "Muan International Airport", "city": "Muan", "region": "46", "page": None},
    {"code": "YNY", "name": "Yangyang International Airport", "city": "Yangyang", "region": "42", "page": None},
]

# Official list = airports with a “空港 集計” row in MLIT 002028812.pdf (2026 winter, direct).
# English names cleaned from OurAirports (public domain); IATA standard.
JP_AIRPORTS = [
    {"code": "AKJ", "name": "Asahikawa Airport", "city": "Asahikawa", "region": "01", "page": None},
    {"code": "CTS", "name": "New Chitose Airport", "city": "Sapporo", "region": "01", "page": None},
    {"code": "HKD", "name": "Hakodate Airport", "city": "Hakodate", "region": "01", "page": None},
    {"code": "AOJ", "name": "Aomori Airport", "city": "Aomori", "region": "02", "page": None},
    {"code": "HNA", "name": "Iwate Hanamaki Airport", "city": "Hanamaki", "region": "03", "page": None},
    {"code": "SDJ", "name": "Sendai Airport", "city": "Sendai", "region": "04", "page": None},
    {"code": "IBR", "name": "Ibaraki Airport", "city": "Omitama", "region": "08", "page": None},
    {"code": "NRT", "name": "Narita International Airport", "city": "Narita", "region": "12", "page": "../airport/NRT/"},
    {"code": "HND", "name": "Tokyo International Airport (Haneda)", "city": "Tokyo", "region": "13", "page": "../airport/HND/"},
    {"code": "KIJ", "name": "Niigata Airport", "city": "Niigata", "region": "15", "page": None},
    {"code": "TOY", "name": "Toyama Airport", "city": "Toyama", "region": "16", "page": None},
    {"code": "KMQ", "name": "Komatsu Airport", "city": "Komatsu", "region": "17", "page": None},
    {"code": "FSZ", "name": "Shizuoka Airport", "city": "Makinohara", "region": "22", "page": None},
    {"code": "NGO", "name": "Chubu Centrair International Airport", "city": "Tokoname", "region": "23", "page": None},
    {"code": "KIX", "name": "Kansai International Airport", "city": "Osaka", "region": "27", "page": "../airport/KIX/"},
    {"code": "OKJ", "name": "Okayama Airport", "city": "Okayama", "region": "33", "page": None},
    {"code": "HIJ", "name": "Hiroshima Airport", "city": "Hiroshima", "region": "34", "page": None},
    {"code": "YGJ", "name": "Yonago Kitaro Airport", "city": "Yonago", "region": "31", "page": None},
    {"code": "TAK", "name": "Takamatsu Airport", "city": "Takamatsu", "region": "37", "page": None},
    {"code": "TKS", "name": "Tokushima Awaodori Airport", "city": "Tokushima", "region": "36", "page": None},
    {"code": "MYJ", "name": "Matsuyama Airport", "city": "Matsuyama", "region": "38", "page": None},
    {"code": "KKJ", "name": "Kitakyushu Airport", "city": "Kitakyushu", "region": "40", "page": None},
    {"code": "FUK", "name": "Fukuoka Airport", "city": "Fukuoka", "region": "40", "page": None},
    {"code": "HSG", "name": "Saga Airport", "city": "Saga", "region": "41", "page": None},
    {"code": "NGS", "name": "Nagasaki Airport", "city": "Nagasaki", "region": "42", "page": None},
    {"code": "OIT", "name": "Oita Airport", "city": "Oita", "region": "44", "page": None},
    {"code": "KMJ", "name": "Kumamoto Airport", "city": "Kumamoto", "region": "43", "page": None},
    {"code": "KMI", "name": "Miyazaki Airport", "city": "Miyazaki", "region": "45", "page": None},
    {"code": "KOJ", "name": "Kagoshima Airport", "city": "Kagoshima", "region": "46", "page": None},
    {"code": "OKA", "name": "Naha Airport", "city": "Naha", "region": "47", "page": None},
    {"code": "SHI", "name": "Shimojishima Airport", "city": "Miyakojima", "region": "47", "page": None},
    {"code": "ISG", "name": "New Ishigaki Airport", "city": "Ishigaki", "region": "47", "page": None},
]

# KR: official metro/special cities + provincial capitals (not invented).
# Metro cities that ARE the region are still listed so airport/city panels resolve,
# but we omit a duplicate city marker when the city name equals the region name.
KR_CITIES = [
    # (name, region, capital_of_region, also_show_marker_if_same_name)
    ("Seoul", "11", True),
    ("Busan", "26", True),
    ("Daegu", "27", True),
    ("Incheon", "28", True),
    ("Gwangju", "29", True),
    ("Daejeon", "30", True),
    ("Ulsan", "31", True),
    ("Sejong", "50", True),
    ("Suwon", "41", True),       # Gyeonggi capital
    ("Chuncheon", "42", True),   # Gangwon capital
    ("Cheongju", "43", True),    # North Chungcheong capital
    ("Hongseong", "44", True),   # South Chungcheong capital
    ("Jeonju", "45", True),      # North Jeolla / Jeonbuk capital
    ("Muan", "46", True),        # South Jeolla capital
    ("Andong", "47", True),      # North Gyeongsang capital
    ("Changwon", "48", True),    # South Gyeongsang capital
    ("Jeju City", "49", True),   # Jeju capital
]

# JP: major cities, pop_max >= 1e6 in Natural Earth 10m populated places (public domain).
# Tokyo is the prefecture name too — marker omitted when names match.
JP_CITY_CANDIDATES = [
    "Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo", "Fukuoka", "Kobe",
    "Kawasaki", "Kyoto", "Saitama", "Hiroshima", "Sendai", "Chiba",
    "Kitakyushu", "Sakai",
]

# Manual region for JP cities (prefecture iso)
JP_CITY_REGION = {
    "Tokyo": "13", "Yokohama": "14", "Osaka": "27", "Nagoya": "23",
    "Sapporo": "01", "Fukuoka": "40", "Kobe": "28", "Kawasaki": "14",
    "Kyoto": "26", "Saitama": "11", "Hiroshima": "34", "Sendai": "04",
    "Chiba": "12", "Kitakyushu": "40", "Sakai": "27",
}

JP_MAIN_W, JP_MAIN_S, JP_MAIN_E, JP_MAIN_N = 128.0, 30.05, 146.2, 45.75
# Wider Ryukyu box so Ishigaki / Shimojishima stay in the Okinawa inset
JP_OKI_W, JP_OKI_S, JP_OKI_E, JP_OKI_N = 122.8, 23.9, 131.4, 27.6

ASCII_MAP = str.maketrans({"Ō": "O", "ō": "o", "ū": "u", "Ū": "U", "ā": "a", "ī": "i", "ē": "e", "ō": "o", "Ō": "O"})


def ascii_name(s: str) -> str:
    s = (s or "").translate(ASCII_MAP)
    for suf in (" Prefecture", " Metropolis", " Circuit", " Urban Prefecture"):
        if s.endswith(suf):
            s = s[: -len(suf)]
    if s in ("Hokkaidō",):
        s = "Hokkaido"
    return s


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
    if g is None or g.is_empty:
        return ""
    if g.geom_type == "Polygon":
        d = ring_to_d(list(g.exterior.coords))
        for hole in g.interiors:
            if len(hole.coords) >= 4:
                d += ring_to_d(list(hole.coords))
        return d
    if g.geom_type == "MultiPolygon":
        polys = sorted(g.geoms, key=lambda p: p.area, reverse=True)
        return "".join(geom_to_d(p) for p in polys)
    return ""


def fit_project(geoms: dict, view=(W, H, PAD), pads=None):
    """pads = (left, top, right, bottom). If omitted, `view[2]` is applied on all sides."""
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
    if pads:
        pl, pt, pr, pb = pads
    else:
        pl = pt = pr = pb = pad
    scale = min((w - pl - pr) / bw, (h - pt - pb) / bh)
    ox = pl + ((w - pl - pr) - bw * scale) / 2
    oy = pb + ((h - pt - pb) - bh * scale) / 2

    def to_svg(g):
        def _t(x, y):
            sx = ox + (x - minx) * scale
            sy = h - (oy + (y - miny) * scale)
            return (sx, sy)
        return transform(_t, g)

    meta = {"minx": minx, "miny": miny, "scale": scale, "ox": ox, "oy": oy, "h": h, "kind": "main"}
    return {k: to_svg(g) for k, g in projected.items()}, meta


def ll_to_svg(lon, lat, meta):
    if meta.get("kind") == "inset":
        fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        x, y = fwd.transform(lon, lat)
        sx = meta["ox"] + (x - meta["minx"]) * meta["scale"]
        sy = meta["y0"] + meta["sh"] - ((meta["oy"] - meta["y0"]) + (y - meta["miny"]) * meta["scale"])
        return round_f(sx), round_f(sy)
    fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = fwd.transform(lon, lat)
    sx = meta["ox"] + (x - meta["minx"]) * meta["scale"]
    sy = meta["h"] - (meta["oy"] + (y - meta["miny"]) * meta["scale"])
    return round_f(sx), round_f(sy)


def keep_parts_in_box(g, west, south, east, north, near_deg=None):
    def in_box(poly):
        c = poly.centroid
        return west <= c.x <= east and south <= c.y <= north

    if g is None or g.is_empty:
        return None
    parts = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    keep = [p for p in parts if in_box(p)]
    if not keep:
        return None
    if near_deg is None:
        return keep[0] if len(keep) == 1 else MultiPolygon(keep)
    largest = max(keep, key=lambda p: p.area)
    lc = largest.centroid
    near = []
    for p in keep:
        c = p.centroid
        if p.area >= largest.area * 0.25:
            near.append(p)
        elif abs(c.x - lc.x) <= near_deg and abs(c.y - lc.y) <= near_deg:
            near.append(p)
    if not near:
        near = [largest]
    return near[0] if len(near) == 1 else MultiPolygon(near)


def mapshaper_dissolve_and_simplify(adm0: str, percent: str, dest: Path):
    if not SHP.exists():
        raise SystemExit(f"missing shapefile {SHP}")
    cmd = [
        "npx", "--yes", "mapshaper", str(SHP),
        "-filter", f'adm0_a3 == "{adm0}"',
        "-each", "iso=String(iso_3166_2).replace(/.*-/, '')",
        "-dissolve", "iso", "copy-fields=name,name_en",
        "-clean",
        "-simplify", "visvalingam", "weighted", "keep-shapes", percent,
        "-clean",
        "-o", "format=geojson", "gj2008", str(dest),
    ]
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)
    data = json.loads(dest.read_text(encoding="utf-8"))
    geoms, names = {}, {}
    for feat in data["features"]:
        props = feat.get("properties") or {}
        iso = str(props.get("iso") or "").zfill(2) if adm0 == "JPN" else str(props.get("iso") or "")
        if adm0 == "KOR" and len(iso) == 1:
            iso = iso.zfill(2)
        names[iso] = ascii_name(props.get("name_en") or props.get("name") or iso)
        geoms[iso] = shape(feat["geometry"])
    return geoms, names


def load_ourairports():
    out = {}
    with AIRPORTS_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            iata = (row.get("iata_code") or "").strip()
            if not iata or row.get("type") == "closed":
                continue
            rank = {"large_airport": 0, "medium_airport": 1, "small_airport": 2}.get(row["type"], 9)
            if iata not in out or rank < out[iata][0]:
                out[iata] = (rank, {
                    "lat": float(row["latitude_deg"]),
                    "lon": float(row["longitude_deg"]),
                    "oa_name": row["name"],
                    "iso_region": row.get("iso_region") or "",
                })
    return {k: v[1] for k, v in out.items()}


def load_places(adm0: str):
    import shapefile
    sf = shapefile.Reader(str(PLACES))
    fields = [f[0] for f in sf.fields[1:]]
    rows = []
    for rec in sf.records():
        d = dict(zip(fields, rec))
        if d.get("ADM0_A3") != adm0:
            continue
        rows.append({
            "name": d.get("NAMEASCII") or d.get("NAME") or d.get("NAME_EN") or "",
            "name_en": d.get("NAME_EN") or "",
            "alt": d.get("NAMEALT") or "",
            "lat": float(d["LATITUDE"]),
            "lon": float(d["LONGITUDE"]),
            "pop": int(d["POP_MAX"] or 0),
            "adm1": d.get("ADM1NAME") or "",
            "feature": d.get("FEATURECLA") or "",
        })
    return rows


def find_place(places, *candidates):
    cands = [c.lower() for c in candidates]
    # exact then startswith
    for key in ("name", "name_en"):
        for p in places:
            if (p[key] or "").lower() in cands:
                return p
    for p in places:
        alts = [a.strip().lower() for a in (p["alt"] or "").split("|") if a.strip()]
        if any(a in cands for a in alts):
            return p
    return None


def attach_airports(specs, oa, meta_for_region):
    out = []
    for s in specs:
        info = oa.get(s["code"])
        if not info:
            raise SystemExit(f"missing OurAirports coords for {s['code']}")
        meta = meta_for_region(s["region"])
        x, y = ll_to_svg(info["lon"], info["lat"], meta)
        item = {
            "code": s["code"],
            "name": s["name"],
            "city": s["city"],
            "province": s["region"],
            "state": s["region"],
            "x": x,
            "y": y,
            "lat": round(info["lat"], 4),
            "lon": round(info["lon"], 4),
        }
        if s.get("page"):
            item["page"] = s["page"]
        # Named labels on the biggest hubs (USA mapLabel/mapName pattern)
        if s["code"] in {"ICN", "GMP", "PUS", "CJU", "NRT", "HND", "KIX", "NGO", "FUK", "CTS", "OKA"}:
            item["mapLabel"] = s["code"]
            item["mapName"] = s["name"].replace(" International Airport", "").replace(" Airport", "")
        # JP: only these 7 at full view (see module docstring / geo header).
        if s["code"] in {"NRT", "HND", "KIX", "NGO", "FUK", "CTS", "OKA"}:
            item["major"] = True
        elif s["code"] not in {"ICN", "GMP", "PUS", "CJU", "CJJ", "TAE", "MWX", "YNY"}:
            item["zoomOnly"] = True
        out.append(item)
    return out


def pack(svg_geoms: dict, names: dict[str, str], extra: dict | None = None):
    extra = extra or {}
    geo = {}
    for code, g in svg_geoms.items():
        c = g.representative_point()
        item = {
            "name": names[code],
            "d": geom_to_d(g),
            "c": [round_f(c.x), round_f(c.y)],
            "cities": [],
            "area": round(g.area, 1),
        }
        if extra.get(code):
            item.update(extra[code])
        geo[code] = item
    return geo


def assign_callouts(geo: dict, side="east", x_col=None, min_area=900, long_name=9):
    """Leader lines for small / crowded regions, USA-style stacked column."""
    tiny = []
    for a, g in geo.items():
        if g.get("inset"):
            continue
        name = g["name"]
        area = g.get("area") or 0
        # long names need more room
        need = min_area if len(name) < long_name else min_area * 1.4
        if area < need:
            tiny.append(a)
    if not tiny:
        return
    # sort by current y
    tiny.sort(key=lambda a: geo[a]["c"][1])
    if x_col is None:
        x_col = 948 if side == "east" else 36
    # stack with 16px minimum
    ys = [geo[a]["c"][1] for a in tiny]
    placed = []
    last = -1e9
    for y in ys:
        ly = max(y, last + 16)
        placed.append(ly)
        last = ly
    # recenter the stack around the original mean
    if placed:
        shift = (ys[0] + ys[-1]) / 2 - (placed[0] + placed[-1]) / 2
        placed = [y + shift for y in placed]
        # clamp into view
        overflow_hi = max(0, placed[-1] - (H - 14))
        overflow_lo = max(0, 14 - placed[0])
        placed = [y - overflow_hi + overflow_lo for y in placed]
    for a, ly in zip(tiny, placed):
        geo[a]["callout"] = True
        geo[a]["lx"] = round_f(x_col)
        geo[a]["ly"] = round_f(ly)



def assign_callouts_fixed(geo: dict, codes: list, x_col: float, side="east"):
    """USA-style stacked leader labels for an explicit tiny-region list only."""
    tiny = [a for a in codes if a in geo and not geo[a].get("inset")]
    if not tiny:
        return
    tiny.sort(key=lambda a: geo[a]["c"][1])
    ys = [geo[a]["c"][1] for a in tiny]
    placed, last = [], -1e9
    for y in ys:
        ly = max(y, last + 18)
        placed.append(ly)
        last = ly
    if placed:
        shift = (ys[0] + ys[-1]) / 2 - (placed[0] + placed[-1]) / 2
        placed = [y + shift for y in placed]
        overflow_hi = max(0, placed[-1] - (H - 16))
        overflow_lo = max(0, 16 - placed[0])
        placed = [y - overflow_hi + overflow_lo for y in placed]
    for a, ly in zip(tiny, placed):
        geo[a]["callout"] = True
        geo[a]["lx"] = round_f(x_col)
        geo[a]["ly"] = round_f(ly)

def add_cities(geo, cities, meta_for_region, places, same_name_markers=False):
    used = []
    for name, region, is_cap in cities:
        if region not in geo:
            print("WARN city region missing", name, region)
            continue
        place = find_place(places, name, name.replace(" City", ""))
        if not place:
            # Official provincial capitals not in NE 10m places.
            # Coordinates from Wikidata via the English Wikipedia page summary
            # (Hongseong County; Muan County). Sejong is already the region label.
            WD = {
                "Hongseong": {"lat": 36.5994, "lon": 126.6628, "pop": 0},
                "Muan": {"lat": 34.9897, "lon": 126.4714, "pop": 0},
            }
            if name not in WD:
                print("WARN no NE place for", name)
                continue
            place = WD[name]
            print("city coords from Wikidata/Wikipedia summary:", name, place)
        meta = meta_for_region(region)
        x, y = ll_to_svg(place["lon"], place["lat"], meta)
        # skip on-map marker when the region label is already this name
        if (not same_name_markers) and geo[region]["name"].split()[0] == name.split()[0] and geo[region]["name"] in (name, name.replace(" City", "")):
            # still record for panel, but no separate map marker? User asked cities on the map.
            # Duplicate "Seoul" on Seoul is noisy — skip marker, keep in a hidden list? Skip.
            print("skip duplicate marker", name, "in", geo[region]["name"])
            continue
        cap = is_cap
        geo[region].setdefault("cities", []).append({
            "n": name,
            "x": x,
            "y": y,
            "cap": bool(cap),
        })
        used.append(name)
    return used


HEADER = (
    "/* Natural Earth 10m admin-1 (public domain, https://www.naturalearthdata.com/) "
    "→ topology-aware mapshaper simplify (shared borders preserved) → SVG paths.\n"
    "   Korea international airports: KAC https://www.airport.co.kr/wwweng/index.do "
    "(Gimpo, Gimhae, Jeju, Daegu, Cheongju, Muan, Yangyang International) + "
    "IIAC Incheon https://www.airport.kr/\n"
    "   Japan international scheduled airports: MLIT 2026 winter authorised data, "
    "direct passenger flights https://www.mlit.go.jp/koku/content/002028812.pdf "
    "(index https://www.mlit.go.jp/koku/koku_tk1_000013.html).\n"
    "   Airport coordinates: OurAirports, public domain "
    "https://davidmegginson.github.io/ourairports-data/airports.csv\n"
    "   City coordinates: Natural Earth 10m populated places (public domain). */\n"
)


def write_js(var_geo: str, var_air: str, geo: dict, airports: list, path: Path):
    # drop helper area from public payload
    clean = {}
    for k, v in geo.items():
        item = {kk: vv for kk, vv in v.items() if kk != "area"}
        clean[k] = item
    path.write_text(
        HEADER
        + f"window.{var_geo}={json.dumps(clean, ensure_ascii=False, separators=(',', ':'))};\n"
        + f"window.{var_air}={json.dumps(airports, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )
    print(path.relative_to(ROOT), len(clean), "regions", len(airports), "airports", path.stat().st_size, "bytes")


def build_korea(oa, places):
    with tempfile.TemporaryDirectory() as td:
        geoms, names = mapshaper_dissolve_and_simplify("KOR", "28%", Path(td) / "kr.geojson")
    assert len(geoms) == 17, f"expected 17 KR divisions, got {len(geoms)} {sorted(geoms)}"
    # Prefer the established English names already used on the site
    names.update({
        "11": "Seoul", "26": "Busan", "27": "Daegu", "28": "Incheon",
        "29": "Gwangju", "30": "Daejeon", "31": "Ulsan", "41": "Gyeonggi",
        "42": "Gangwon", "43": "North Chungcheong", "44": "South Chungcheong",
        "45": "North Jeolla", "46": "South Jeolla", "47": "North Gyeongsang",
        "48": "South Gyeongsang", "49": "Jeju", "50": "Sejong",
    })
    svg, meta = fit_project(geoms, view=(W, H, 28), pads=(150, 24, 24, 24))
    geo = pack(svg, names)
    # Only the tiniest metros (USA approach): Seoul, Incheon, Sejong
    assign_callouts_fixed(geo, ["11", "28", "50"], x_col=138, side="west")
    def meta_for(_r):
        return meta
    airs = attach_airports(KR_AIRPORTS, oa, meta_for)
    used = add_cities(geo, [(n, r, c) for n, r, c in KR_CITIES], meta_for, places)
    print("KR cities on map:", used)
    return geo, airs, names


def inset_okinawa(og, slot=(28, 430, 250, 168)):
    fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    pg = transform(lambda x, y: fwd.transform(x, y), og)
    minx, miny, maxx, maxy = pg.bounds
    bw, bh = max(maxx - minx, 1e-6), max(maxy - miny, 1e-6)
    x0, y0, sw, sh = slot
    sc = min((sw - 10) / bw, (sh - 10) / bh)
    ox = x0 + (sw - bw * sc) / 2
    oy = y0 + (sh - bh * sc) / 2

    def _t(x, y):
        sx = ox + (x - minx) * sc
        sy = y0 + sh - ((oy - y0) + (y - miny) * sc)
        return (sx, sy)

    sg = transform(_t, pg)
    meta = {
        "kind": "inset", "minx": minx, "miny": miny, "scale": sc,
        "ox": ox, "oy": oy, "y0": y0, "sh": sh,
    }
    return sg, meta


def build_japan(oa, places):
    with tempfile.TemporaryDirectory() as td:
        raw, names = mapshaper_dissolve_and_simplify("JPN", "22%", Path(td) / "jp.geojson")
    assert len(raw) == 47, f"expected 47 JP prefectures, got {len(raw)} {sorted(raw)}"
    names = {k: ascii_name(v) for k, v in names.items()}
    names.update({
        "01": "Hokkaido", "13": "Tokyo", "26": "Kyoto", "27": "Osaka",
        "28": "Hyogo", "39": "Kochi", "44": "Oita", "47": "Okinawa",
    })

    main = {}
    for code, g in raw.items():
        if code == "47":
            continue
        clipped = keep_parts_in_box(g, JP_MAIN_W, JP_MAIN_S, JP_MAIN_E, JP_MAIN_N, near_deg=1.55)
        if clipped is None or clipped.is_empty:
            raise SystemExit(f"JP {code} {names[code]} empty after mainland clip")
        main[code] = clipped

    # Re-simplify mainland together after clip so shared edges stay shared
    with tempfile.TemporaryDirectory() as td:
        gj = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "properties": {"iso": k, "name_en": names[k]}, "geometry": mapping(g)}
                for k, g in main.items()
            ],
        }
        src = Path(td) / "main.geojson"
        dst = Path(td) / "main-s.geojson"
        src.write_text(json.dumps(gj), encoding="utf-8")
        subprocess.check_call([
            "npx", "--yes", "mapshaper", str(src),
            "-clean",
            "-simplify", "visvalingam", "weighted", "keep-shapes", "45%",
            "-clean",
            "-o", "format=geojson", "gj2008", str(dst),
        ])
        data = json.loads(dst.read_text(encoding="utf-8"))
        main = {}
        for feat in data["features"]:
            iso = str(feat["properties"]["iso"]).zfill(2)
            main[iso] = shape(feat["geometry"])

    svg, meta = fit_project(main, view=(W, H, 20), pads=(18, 18, 155, 18))
    geo = pack(svg, {k: names[k] for k in main})
    # Only crowded/tiny prefectures (USA approach): Tokyo, Kanagawa, Saitama, Osaka, Nara
    assign_callouts_fixed(geo, ["13", "14", "11", "27", "29"], x_col=828, side="east")

    oki_meta = None
    og = raw.get("47")
    if og is not None:
        # Keep the whole Ryukyu chain in-box (no near_deg) so Ishigaki / Shimoji stay
        og = keep_parts_in_box(og, JP_OKI_W, JP_OKI_S, JP_OKI_E, JP_OKI_N, near_deg=None) or og
        sg, oki_meta = inset_okinawa(og)
        c = sg.representative_point()
        geo["47"] = {
            "name": names["47"],
            "d": geom_to_d(sg),
            "c": [round_f(c.x), round_f(c.y)],
            "cities": [],
            "inset": True,
        }

    def meta_for(r):
        return oki_meta if r == "47" and oki_meta else meta

    airs = attach_airports(JP_AIRPORTS, oa, meta_for)

    # JP cities: only those with NE pop_max >= 1,000,000
    jp_cities = []
    for nm in JP_CITY_CANDIDATES:
        p = find_place(places, nm)
        if not p:
            print("WARN JP city not in NE places", nm)
            continue
        if p["pop"] < 1_000_000:
            print("JP skip <1e6", nm, p["pop"])
            continue
        print("JP city", nm, "pop_max", p["pop"], "->", JP_CITY_REGION[nm])
        jp_cities.append((nm, JP_CITY_REGION[nm], nm == "Tokyo"))
    used = add_cities(geo, jp_cities, meta_for, places)
    print("JP cities on map:", used)
    return geo, airs, names


def main():
    if not AIRPORTS_CSV.exists():
        raise SystemExit(f"missing {AIRPORTS_CSV}")
    oa = load_ourairports()
    kr_places = load_places("KOR")
    jp_places = load_places("JPN")
    print("NE places KR", len(kr_places), "JP", len(jp_places))

    kr_geo, kr_air, _ = build_korea(oa, kr_places)
    jp_geo, jp_air, _ = build_japan(oa, jp_places)

    # verify every data-file key will have a path
    for label, geo, path in (
        ("KR", kr_geo, ROOT / "site/assets/js/south-korea-map-data.js"),
        ("JP", jp_geo, ROOT / "site/assets/js/japan-map-data.js"),
    ):
        t = path.read_text(encoding="utf-8")
        # keys in tones
        import re
        m = re.search(r'"tones":\{([^}]+)\}', t)
        keys = re.findall(r'"(\d+)":', m.group(1)) if m else []
        missing = [k for k in keys if k not in geo or not geo[k].get("d")]
        extra = [k for k in geo if k not in keys]
        print(label, "data keys", len(keys), "geo", len(geo), "missing", missing, "extra", extra)
        if missing:
            raise SystemExit(f"{label} data keys without path: {missing}")

    for out in (OUT_SITE, OUT_STATIC):
        out.mkdir(parents=True, exist_ok=True)
        write_js("KR_GEO", "KR_GEO_AIRPORTS", kr_geo, kr_air, out / "south-korea-map-geo.js")
        write_js("JP_GEO", "JP_GEO_AIRPORTS", jp_geo, jp_air, out / "japan-map-geo.js")


if __name__ == "__main__":
    main()
