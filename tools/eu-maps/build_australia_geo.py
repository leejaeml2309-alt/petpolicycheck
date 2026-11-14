#!/usr/bin/env python3
"""Build Australia (8 states/territories) map geo pack.

Source: Natural Earth 10m Cultural admin-1 states and provinces
        https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/
License: public domain (Natural Earth).

Topology-aware simplification via mapshaper (Visvalingam, shared edges preserved).
Tasmania sits at its true position (no inset). Jervis Bay Territory is merged
into the ACT so the NSW south coast has no hole. Macquarie Island and Lord Howe
Island are omitted so they do not stretch the viewBox.

Airports: major international-traffic fields only, from BITRE Airport Traffic
Data, financial year 2024–25 (international revenue passengers):
https://www.bitre.gov.au/resource/aviation/airport-traffic-data
Kept: SYD, MEL, BNE, PER, ADL, CNS, OOL.
Dropped: DRW and every smaller international / designated field (CBR, HBA, MCY, …).

Airport coordinates: OurAirports, public domain
https://davidmegginson.github.io/ourairports-data/airports.csv
City coordinates: Geoscience Australia Gazetteer-style WGS84 (CBD / place centre)
so airport–city link lines remain visible; Natural Earth 10m populated places
used as a cross-check.
"""
from __future__ import annotations

import csv
import json
import subprocess
import tempfile
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.ops import transform, unary_union

ROOT = Path(__file__).resolve().parents[2]
SHP = ROOT / "data/eu-geo/ne10/ne_10m_admin_1_states_provinces.shp"
AIRPORTS_CSV = Path("/tmp/krjp-src/airports.csv")
if not AIRPORTS_CSV.exists():
    AIRPORTS_CSV = Path("/tmp/jpkr/airports.csv")
OUT_SITE = ROOT / "site/assets/js"
OUT_STATIC = ROOT / "static/assets/js"
W, H, PAD = 975, 610, 28

# BITRE FY 2024–25 international revenue passengers (Airport Traffic Data).
# CNS (664,953) ranks above OOL (624,270), so both are kept. DRW (234,831)
# is a clear step down and is dropped.
AU_AIRPORTS = [
    {"code": "SYD", "name": "Sydney Kingsford Smith International Airport", "city": "Sydney", "region": "NSW", "page": None, "linkCity": "Sydney"},
    {"code": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "region": "VIC", "page": None, "linkCity": "Melbourne"},
    {"code": "BNE", "name": "Brisbane International Airport", "city": "Brisbane", "region": "QLD", "page": None, "linkCity": "Brisbane"},
    {"code": "PER", "name": "Perth International Airport", "city": "Perth", "region": "WA", "page": None, "linkCity": "Perth"},
    {"code": "ADL", "name": "Adelaide International Airport", "city": "Adelaide", "region": "SA", "page": None, "linkCity": "Adelaide"},
    {"code": "CNS", "name": "Cairns International Airport", "city": "Cairns", "region": "QLD", "page": None, "linkCity": "Cairns"},
    {"code": "OOL", "name": "Gold Coast Airport", "city": "Gold Coast", "region": "QLD", "page": None, "linkCity": "Gold Coast"},
]

# Official English names for the eight states and territories.
AU_NAMES = {
    "NSW": "New South Wales",
    "VIC": "Victoria",
    "QLD": "Queensland",
    "SA": "South Australia",
    "WA": "Western Australia",
    "TAS": "Tasmania",
    "NT": "Northern Territory",
    "ACT": "Australian Capital Territory",
}

# CBD / place-centre WGS84 (Gazetteer-style). Canberra is the only capital.
# State capitals are plain cities (major=True so they can show at rest).
# (name, region, is_national_capital, major)
AU_CITIES = [
    ("Canberra", "ACT", True, True),
    ("Sydney", "NSW", False, True),
    ("Melbourne", "VIC", False, True),
    ("Brisbane", "QLD", False, True),
    ("Perth", "WA", False, True),
    ("Adelaide", "SA", False, True),
    ("Gold Coast", "QLD", False, True),
    ("Hobart", "TAS", False, True),
    ("Darwin", "NT", False, True),
    ("Cairns", "QLD", False, True),
    ("Newcastle", "NSW", False, False),
    ("Wollongong", "NSW", False, False),
    ("Geelong", "VIC", False, False),
    ("Townsville", "QLD", False, False),
    ("Toowoomba", "QLD", False, False),
    ("Ballarat", "VIC", False, False),
    ("Bendigo", "VIC", False, False),
    ("Launceston", "TAS", False, False),
    ("Alice Springs", "NT", False, False),
    ("Sunshine Coast", "QLD", False, False),
]

# Gazetteer-style WGS84 (lon, lat). CBD points so airport–city lines stay visible.
# Cross-checked against Natural Earth 10m populated places.
GAZETTEER = {
    "Canberra": (149.1287, -35.2820),
    "Sydney": (151.2093, -33.8688),
    "Melbourne": (144.9631, -37.8136),
    "Brisbane": (153.0251, -27.4698),
    "Perth": (115.8605, -31.9505),
    "Adelaide": (138.5990, -34.9285),
    "Gold Coast": (153.4000, -28.0167),
    "Hobart": (147.3272, -42.8821),
    "Darwin": (130.8418, -12.4634),
    "Cairns": (145.7709, -16.9256),
    "Newcastle": (151.7817, -32.9283),
    "Wollongong": (150.8931, -34.4278),
    "Geelong": (144.3617, -38.1499),
    "Townsville": (146.8169, -19.2590),
    "Toowoomba": (151.9539, -27.5598),
    "Ballarat": (143.8503, -37.5622),
    "Bendigo": (144.2794, -36.7570),
    "Launceston": (147.1441, -41.4332),
    "Alice Springs": (133.8807, -23.6980),
    "Sunshine Coast": (153.0920, -26.6500),
}


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
    fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = fwd.transform(lon, lat)
    sx = meta["ox"] + (x - meta["minx"]) * meta["scale"]
    sy = meta["h"] - (meta["oy"] + (y - meta["miny"]) * meta["scale"])
    return round_f(sx), round_f(sy)


def load_admin1():
    import shapefile
    if not SHP.exists():
        raise SystemExit(f"missing shapefile {SHP}")
    sf = shapefile.Reader(str(SHP))
    fields = [f[0] for f in sf.fields[1:]]
    by_iso = {}
    jervis = None
    for rec, shp in zip(sf.records(), sf.shapes()):
        d = dict(zip(fields, rec))
        if d.get("adm0_a3") != "AUS":
            continue
        name = (d.get("name") or "").strip()
        iso = str(d.get("iso_3166_2") or "")
        if name in {"Macquarie Island", "Lord Howe Island"}:
            print("omit offshore", name, iso)
            continue
        geom = shape(shp.__geo_interface__)
        if name == "Jervis Bay Territory" or "X02" in iso:
            jervis = geom
            print("queue Jervis Bay merge into ACT")
            continue
        code = iso.replace("AU-", "")
        if code not in AU_NAMES:
            print("skip unexpected", iso, name)
            continue
        if code in by_iso:
            by_iso[code] = unary_union([by_iso[code], geom])
        else:
            by_iso[code] = geom
    if jervis is not None:
        if "ACT" not in by_iso:
            raise SystemExit("ACT missing; cannot merge Jervis Bay")
        by_iso["ACT"] = unary_union([by_iso["ACT"], jervis])
        print("merged Jervis Bay Territory into ACT")
    missing = [k for k in AU_NAMES if k not in by_iso]
    if missing:
        raise SystemExit(f"missing states: {missing}")
    return by_iso


def mapshaper_simplify(geoms: dict, percent: str, dest: Path):
    gj = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"iso": k, "name_en": AU_NAMES[k]}, "geometry": mapping(g)}
            for k, g in geoms.items()
        ],
    }
    src = dest.with_name("au-src.geojson")
    src.write_text(json.dumps(gj), encoding="utf-8")
    cmd = [
        "npx", "--yes", "mapshaper", str(src),
        "-clean",
        "-simplify", "visvalingam", "weighted", "keep-shapes", percent,
        "-clean",
        "-o", "format=geojson", "gj2008", str(dest),
    ]
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)
    data = json.loads(dest.read_text(encoding="utf-8"))
    out = {}
    for feat in data["features"]:
        iso = str(feat["properties"]["iso"])
        out[iso] = shape(feat["geometry"])
    return out


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


def pack(svg_geoms: dict, names: dict[str, str]):
    geo = {}
    for code, g in svg_geoms.items():
        c = g.representative_point()
        geo[code] = {
            "name": names[code],
            "d": geom_to_d(g),
            "c": [round_f(c.x), round_f(c.y)],
            "cities": [],
            "area": round(g.area, 1),
        }
    return geo


def attach_airports(specs, oa, meta):
    out = []
    for s in specs:
        info = oa.get(s["code"])
        if not info:
            raise SystemExit(f"missing OurAirports coords for {s['code']}")
        x, y = ll_to_svg(info["lon"], info["lat"], meta)
        item = {
            "code": s["code"],
            "name": s["name"],
            "city": s["city"],
            "province": s["region"],
            "state": s["region"],
            "x": x,
            "y": y,
            "lat": round(info["lat"], 6),
            "lon": round(info["lon"], 6),
            "mapLabel": s["code"],
            "mapName": s["name"].replace(" International Airport", "").replace(" Airport", ""),
            "major": True,
            "linkCity": s["linkCity"],
        }
        if s.get("page"):
            item["page"] = s["page"]
        out.append(item)
        print(f"  airport {s['code']} {info['lat']:.5f},{info['lon']:.5f} -> {x},{y}")
    return out


def add_cities(geo, meta):
    for name, region, is_cap, major in AU_CITIES:
        if region not in geo:
            raise SystemExit(f"city region missing {name} {region}")
        if name not in GAZETTEER:
            raise SystemExit(f"missing gazetteer coords for {name}")
        lon, lat = GAZETTEER[name]
        x, y = ll_to_svg(lon, lat, meta)
        rec = {"n": name, "x": x, "y": y, "lat": lat, "lon": lon}
        if is_cap:
            rec["cap"] = True
        if major:
            rec["major"] = True
        geo[region].setdefault("cities", []).append(rec)
        print(f"  city {name} {lat:.4f},{lon:.4f} -> {x},{y} cap={is_cap} major={major}")


HEADER = (
    "/* Natural Earth 10m admin-1 (public domain, https://www.naturalearthdata.com/) "
    "→ topology-aware mapshaper simplify (shared borders preserved) → SVG paths. "
    "Tasmania at true position. Jervis Bay Territory merged into ACT. "
    "Macquarie Island and Lord Howe Island omitted (viewBox).\n"
    "   Airports: major international-traffic fields only, BITRE Airport Traffic Data "
    "FY 2024–25 international revenue passengers "
    "https://www.bitre.gov.au/resource/aviation/airport-traffic-data "
    "(SYD, MEL, BNE, PER, ADL, CNS, OOL). CNS ranks above OOL; DRW is a clear step down and is omitted.\n"
    "   Airport coordinates: OurAirports, public domain "
    "https://davidmegginson.github.io/ourairports-data/airports.csv\n"
    "   City coordinates: Gazetteer-style WGS84 CBD / place centres, cross-checked "
    "against Natural Earth 10m populated places (public domain). Canberra is the only capital. */\n"
)


def write_js(geo: dict, airports: list, path: Path):
    clean = {}
    for k, v in geo.items():
        item = {kk: vv for kk, vv in v.items() if kk != "area"}
        clean[k] = item
    path.write_text(
        HEADER
        + f"window.AU_GEO={json.dumps(clean, ensure_ascii=False, separators=(',', ':'))};\n"
        + f"window.AU_GEO_AIRPORTS={json.dumps(airports, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )
    print(path, len(clean), "regions", len(airports), "airports", path.stat().st_size, "bytes")


def main():
    oa = load_ourairports()
    raw = load_admin1()
    with tempfile.TemporaryDirectory() as td:
        geoms = mapshaper_simplify(raw, "18%", Path(td) / "au.geojson")
    # Slightly more padding on the east/south for Sydney/Gold Coast/Hobart labels.
    svg, meta = fit_project(geoms, view=(W, H, 24), pads=(22, 26, 36, 34))
    geo = pack(svg, AU_NAMES)
    airs = attach_airports(AU_AIRPORTS, oa, meta)
    add_cities(geo, meta)
    for out in (OUT_SITE, OUT_STATIC):
        out.mkdir(parents=True, exist_ok=True)
        write_js(geo, airs, out / "australia-map-geo.js")


if __name__ == "__main__":
    main()
