#!/usr/bin/env python3
"""Rebuild Italy (20 regions) and Spain (17 CCAA + Ceuta + Melilla) map geo packs.

Source: Natural Earth 10m Cultural admin-1 states and provinces
        https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/
License: public domain (Natural Earth).

Topology-aware simplification via mapshaper (Visvalingam, shared edges preserved).

Airports (official lists; invent nothing):

  Italy — ENAC « Aeroporti di interesse nazionale » (d.P.R. n. 201/2015),
        updated 23 June 2026:
        https://www.enac.gov.it/aeroporti/infrastrutture-aeroportuali/aeroporti-in-italia/
        39 airports of national interest. Three are marked strategic
        international hubs (*): Milano Malpensa, Roma Fiumicino, Venezia.
        Ten further airports are marked strategic (**): Bari, Bologna,
        Cagliari, Catania, Firenze, Lamezia Terme, Napoli, Palermo, Pisa,
        Torino. This pack plots all 39.
        ENAC « Dati di traffico 2025 » also lists 44 airports open to
        commercial civil traffic (same URL family:
        https://www.enac.gov.it/app/uploads/2026/05/Dati-di-traffico-2025-v.0.7.pdf).
        The extra 5 — Albenga (ALL), Aosta (AOT), Bolzano (BZO), Forlì (FRL)
        and Marina di Campo / Elba (EBA) — are omitted here because they
        are not on the national-interest list (most are aerotaxi / very
        small). Flag for Marc.
        Major at full view: the 10 busiest passenger airports in recent
        ENAC/Assaeroporti rankings (Fiumicino, Malpensa, Bergamo, Venice,
        Naples, Catania, Bologna, Linate, Ciampino, Palermo):
        FCO, MXP, BGY, VCE, NAP, CTA, BLQ, LIN, CIA, PMO.

  Spain — Aena official « Our airports » network page (46 airports + 2
        heliports in Spain):
        https://www.aena.es/en/passengers/our-airports.html
        Plotted: the Aena commercial passenger airports. Excluded from
        the same page, and flagged: Madrid-Cuatro Vientos, Sabadell and
        Son Bonet (general aviation); Ceuta (JCU) and Algeciras (AEI)
        (heliports, not airports). Ceuta therefore has no airport marker;
        Melilla (MLN) does. Non-Aena fields (Lleida-Alguaire, Castellón)
        are not on the official Aena list and are not plotted.
        Canary Islands use a USA-Hawaii / Japan-Okinawa style inset.
        Major at full view: Aena's largest passenger airports
        (Madrid-Barajas, Barcelona-El Prat, Palma, Málaga, Alicante,
        Gran Canaria, Tenerife Sur, Valencia, Seville, Bilbao):
        MAD, BCN, PMI, AGP, ALC, LPA, TFS, VLC, SVQ, BIO.

Coordinates: OurAirports airports.csv, public domain
        https://davidmegginson.github.io/ourairports-data/airports.csv
Cities: regional capitals plus a few major cities; coordinates from
        Natural Earth 10m populated places (public domain). Missing
        places are flagged, not invented.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from shapely.geometry import Point, box, mapping, shape
from shapely.ops import polylabel, unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_eu3_geo as E  # noqa: E402
import build_krjp_geo as K  # noqa: E402

ROOT = K.ROOT
SHP = K.SHP
AIRPORTS_CSV = Path("/tmp/eu3-src/airports.csv")
if not AIRPORTS_CSV.exists():
    AIRPORTS_CSV = Path("/tmp/krjp-src/airports.csv")
OUT_SITE = K.OUT_SITE
OUT_STATIC = K.OUT_STATIC

# Natural Earth `region` field → (id, English display name)
IT_REGION = {
    "Abruzzo": ("ABR", "Abruzzo"),
    "Apulia": ("PUG", "Apulia"),
    "Basilicata": ("BAS", "Basilicata"),
    "Calabria": ("CAL", "Calabria"),
    "Campania": ("CAM", "Campania"),
    "Emilia-Romagna": ("EMR", "Emilia-Romagna"),
    "Friuli-Venezia Giulia": ("FVG", "Friuli-Venezia Giulia"),
    "Lazio": ("LAZ", "Lazio"),
    "Liguria": ("LIG", "Liguria"),
    "Lombardia": ("LOM", "Lombardy"),
    "Marche": ("MAR", "Marche"),
    "Molise": ("MOL", "Molise"),
    "Piemonte": ("PIE", "Piedmont"),
    "Sardegna": ("SAR", "Sardinia"),
    "Sicily": ("SIC", "Sicily"),
    "Toscana": ("TOS", "Tuscany"),
    "Trentino-Alto Adige": ("TAA", "Trentino-South Tyrol"),
    "Umbria": ("UMB", "Umbria"),
    "Valle d'Aosta": ("VDA", "Aosta Valley"),
    "Veneto": ("VEN", "Veneto"),
}

ES_REGION = {
    "Andalucía": ("AN", "Andalusia"),
    "Aragón": ("AR", "Aragon"),
    "Asturias": ("AS", "Asturias"),
    "Canary Is.": ("CN", "Canary Islands"),
    "Cantabria": ("CB", "Cantabria"),
    "Castilla y León": ("CL", "Castile and León"),
    "Castilla-La Mancha": ("CM", "Castilla-La Mancha"),
    "Cataluña": ("CT", "Catalonia"),
    "Ceuta": ("CE", "Ceuta"),
    "Extremadura": ("EX", "Extremadura"),
    "Foral de Navarra": ("NC", "Navarre"),
    "Galicia": ("GA", "Galicia"),
    "Islas Baleares": ("IB", "Balearic Islands"),
    "La Rioja": ("RI", "La Rioja"),
    "Madrid": ("MD", "Community of Madrid"),
    "Melilla": ("ML", "Melilla"),
    "Murcia": ("MC", "Region of Murcia"),
    "País Vasco": ("PV", "Basque Country"),
    "Valenciana": ("VC", "Valencian Community"),
}

# Capitals + a few major extra cities. Display name, region, is_capital.
IT_CITIES = [
    ("Rome", "LAZ", True),
    ("Milan", "LOM", True),
    ("Naples", "CAM", True),
    ("Turin", "PIE", True),
    ("Palermo", "SIC", True),
    ("Genoa", "LIG", True),
    ("Bologna", "EMR", True),
    ("Florence", "TOS", True),
    ("Bari", "PUG", True),
    ("Venice", "VEN", True),
    ("Verona", "VEN", False),
    ("Catania", "SIC", False),
    ("Trieste", "FVG", True),
    ("Cagliari", "SAR", True),
    ("Perugia", "UMB", True),
    ("Ancona", "MAR", True),
    ("L'Aquila", "ABR", True),
    ("Campobasso", "MOL", True),
    ("Potenza", "BAS", True),
    ("Catanzaro", "CAL", True),
    ("Aosta", "VDA", True),
    ("Trento", "TAA", True),
]

ES_CITIES = [
    ("Madrid", "MD", True),
    ("Barcelona", "CT", True),
    ("Valencia", "VC", True),
    ("Seville", "AN", True),
    ("Malaga", "AN", False),
    ("Zaragoza", "AR", True),
    ("Murcia", "MC", True),
    ("Palma", "IB", True),
    ("Las Palmas", "CN", True),
    ("Santa Cruz de Tenerife", "CN", True),
    ("Bilbao", "PV", False),
    ("Vitoria", "PV", True),
    ("Oviedo", "AS", True),
    ("Santander", "CB", True),
    ("Valladolid", "CL", True),
    ("Toledo", "CM", True),
    ("Merida", "EX", True),
    ("Santiago", "GA", True),
    ("Logrono", "RI", True),
    ("Pamplona", "NC", True),
    ("Alicante", "VC", False),
    ("Ceuta", "CE", True),
    ("Melilla", "ML", True),
]

IT_MAJORS = {"FCO", "MXP", "BGY", "VCE", "NAP", "CTA", "BLQ", "LIN", "CIA", "PMO"}
ES_MAJORS = {"MAD", "BCN", "PMI", "AGP", "ALC", "LPA", "TFS", "VLC", "SVQ", "BIO"}

# ENAC national-interest list (English names; IATA official designators).
IT_AIRPORTS = [
    {"code": "AHO", "name": "Alghero-Fertilia Airport", "city": "Alghero", "region": "SAR"},
    {"code": "AOI", "name": "Ancona Falconara Airport", "city": "Ancona", "region": "MAR"},
    {"code": "BRI", "name": "Bari Karol Wojtyła Airport", "city": "Bari", "region": "PUG"},
    {"code": "BGY", "name": "Milan Bergamo Airport", "city": "Bergamo", "region": "LOM"},
    {"code": "BLQ", "name": "Bologna Guglielmo Marconi Airport", "city": "Bologna", "region": "EMR"},
    {"code": "VBS", "name": "Brescia Airport", "city": "Brescia", "region": "LOM"},
    {"code": "BDS", "name": "Brindisi Airport", "city": "Brindisi", "region": "PUG"},
    {"code": "CAG", "name": "Cagliari Elmas Airport", "city": "Cagliari", "region": "SAR"},
    {"code": "CTA", "name": "Catania Fontanarossa Airport", "city": "Catania", "region": "SIC"},
    {"code": "CIY", "name": "Comiso Airport", "city": "Comiso", "region": "SIC"},
    {"code": "CRV", "name": "Crotone Airport", "city": "Crotone", "region": "CAL"},
    {"code": "CUF", "name": "Cuneo International Airport", "city": "Cuneo", "region": "PIE"},
    {"code": "FLR", "name": "Florence Airport", "city": "Florence", "region": "TOS"},
    {"code": "FOG", "name": "Foggia Airport", "city": "Foggia", "region": "PUG"},
    {"code": "GOA", "name": "Genoa Cristoforo Colombo Airport", "city": "Genoa", "region": "LIG"},
    {"code": "SUF", "name": "Lamezia Terme International Airport", "city": "Lamezia Terme", "region": "CAL"},
    {"code": "LMP", "name": "Lampedusa Airport", "city": "Lampedusa", "region": "SIC"},
    {"code": "LIN", "name": "Milan Linate Airport", "city": "Milan", "region": "LOM"},
    {"code": "MXP", "name": "Milan Malpensa Airport", "city": "Milan", "region": "LOM"},
    {"code": "NAP", "name": "Naples International Airport", "city": "Naples", "region": "CAM"},
    {"code": "OLB", "name": "Olbia Costa Smeralda Airport", "city": "Olbia", "region": "SAR"},
    {"code": "PMO", "name": "Palermo Airport", "city": "Palermo", "region": "SIC"},
    {"code": "PNL", "name": "Pantelleria Airport", "city": "Pantelleria", "region": "SIC"},
    {"code": "PMF", "name": "Parma Airport", "city": "Parma", "region": "EMR"},
    {"code": "PEG", "name": "Perugia San Francesco d'Assisi Airport", "city": "Perugia", "region": "UMB"},
    {"code": "PSR", "name": "Abruzzo Airport", "city": "Pescara", "region": "ABR"},
    {"code": "PSA", "name": "Pisa International Airport", "city": "Pisa", "region": "TOS"},
    {"code": "REG", "name": "Reggio Calabria Airport", "city": "Reggio Calabria", "region": "CAL"},
    {"code": "RMI", "name": "Federico Fellini International Airport", "city": "Rimini", "region": "EMR"},
    {"code": "CIA", "name": "Rome Ciampino Airport", "city": "Rome", "region": "LAZ"},
    {"code": "FCO", "name": "Rome Fiumicino Airport", "city": "Rome", "region": "LAZ"},
    {"code": "QSR", "name": "Salerno Costa d'Amalfi Airport", "city": "Salerno", "region": "CAM"},
    {"code": "TAR", "name": "Taranto-Grottaglie Airport", "city": "Taranto", "region": "PUG"},
    {"code": "TRN", "name": "Turin Airport", "city": "Turin", "region": "PIE"},
    {"code": "TPS", "name": "Vincenzo Florio Airport Trapani-Birgi", "city": "Trapani", "region": "SIC"},
    {"code": "TSF", "name": "Treviso Airport", "city": "Treviso", "region": "VEN"},
    {"code": "TRS", "name": "Trieste – Friuli Venezia Giulia Airport", "city": "Trieste", "region": "FVG"},
    {"code": "VCE", "name": "Venice Marco Polo Airport", "city": "Venice", "region": "VEN"},
    {"code": "VRN", "name": "Verona Villafranca Airport", "city": "Verona", "region": "VEN"},
]

# Aena official English names from https://www.aena.es/en/passengers/our-airports.html
# Excludes GA (Cuatro Vientos, Sabadell, Son Bonet) and heliports (Ceuta, Algeciras).
ES_AIRPORTS = [
    {"code": "LCG", "name": "A Coruña Airport", "city": "A Coruña", "region": "GA"},
    {"code": "MAD", "name": "Adolfo Suárez Madrid-Barajas Airport", "city": "Madrid", "region": "MD"},
    {"code": "ALC", "name": "Alicante-Elche Miguel Hernández Airport", "city": "Alicante", "region": "VC"},
    {"code": "LEI", "name": "Almería Airport", "city": "Almería", "region": "AN"},
    {"code": "OVD", "name": "Asturias Airport", "city": "Oviedo", "region": "AS"},
    {"code": "BJZ", "name": "Badajoz Airport", "city": "Badajoz", "region": "EX"},
    {"code": "BIO", "name": "Bilbao Airport", "city": "Bilbao", "region": "PV"},
    {"code": "RGS", "name": "Burgos Airport", "city": "Burgos", "region": "CL"},
    {"code": "ACE", "name": "César Manrique-Lanzarote Airport", "city": "Arrecife", "region": "CN"},
    {"code": "ODB", "name": "Córdoba Airport", "city": "Córdoba", "region": "AN"},
    {"code": "VDE", "name": "El Hierro Airport", "city": "El Hierro", "region": "CN"},
    {"code": "GRX", "name": "Federico García Lorca Granada-Jaén Airport", "city": "Granada", "region": "AN"},
    {"code": "FUE", "name": "Fuerteventura Airport", "city": "Puerto del Rosario", "region": "CN"},
    {"code": "GRO", "name": "Girona-Costa Brava Airport", "city": "Girona", "region": "CT"},
    {"code": "LPA", "name": "Gran Canaria Airport", "city": "Las Palmas", "region": "CN"},
    {"code": "HSK", "name": "Huesca-Pirineos Airport", "city": "Huesca", "region": "AR"},
    {"code": "IBZ", "name": "Ibiza Airport", "city": "Ibiza", "region": "IB"},
    {"code": "RMU", "name": "Región de Murcia International Airport", "city": "Murcia", "region": "MC"},
    {"code": "XRY", "name": "Jerez Airport", "city": "Jerez", "region": "AN"},
    {"code": "BCN", "name": "Josep Tarradellas Barcelona-El Prat Airport", "city": "Barcelona", "region": "CT"},
    {"code": "GMZ", "name": "La Gomera Airport", "city": "La Gomera", "region": "CN"},
    {"code": "SPC", "name": "La Palma Airport", "city": "Santa Cruz de La Palma", "region": "CN"},
    {"code": "LEN", "name": "León Airport", "city": "León", "region": "CL"},
    {"code": "RJL", "name": "Logroño-Agoncillo Airport", "city": "Logroño", "region": "RI"},
    {"code": "MLN", "name": "Melilla Airport", "city": "Melilla", "region": "ML"},
    {"code": "MAH", "name": "Menorca Airport", "city": "Mahón", "region": "IB"},
    {"code": "AGP", "name": "Málaga-Costa del Sol Airport", "city": "Málaga", "region": "AN"},
    {"code": "PMI", "name": "Palma de Mallorca Airport", "city": "Palma", "region": "IB"},
    {"code": "PNA", "name": "Pamplona Airport", "city": "Pamplona", "region": "NC"},
    {"code": "REU", "name": "Reus Airport", "city": "Reus", "region": "CT"},
    {"code": "SLM", "name": "Salamanca Airport", "city": "Salamanca", "region": "CL"},
    {"code": "EAS", "name": "San Sebastián Airport", "city": "San Sebastián", "region": "PV"},
    {"code": "SCQ", "name": "Santiago-Rosalía de Castro Airport", "city": "Santiago de Compostela", "region": "GA"},
    {"code": "SDR", "name": "Seve Ballesteros-Santander Airport", "city": "Santander", "region": "CB"},
    {"code": "SVQ", "name": "Sevilla Airport", "city": "Seville", "region": "AN"},
    {"code": "TFN", "name": "Tenerife Norte-Ciudad de La Laguna Airport", "city": "Santa Cruz de Tenerife", "region": "CN"},
    {"code": "TFS", "name": "Tenerife Sur Airport", "city": "Tenerife", "region": "CN"},
    {"code": "VLC", "name": "Valencia Airport", "city": "Valencia", "region": "VC"},
    {"code": "VLL", "name": "Valladolid Airport", "city": "Valladolid", "region": "CL"},
    {"code": "VGO", "name": "Vigo Airport", "city": "Vigo", "region": "GA"},
    {"code": "VIT", "name": "Vitoria Airport", "city": "Vitoria-Gasteiz", "region": "PV"},
    {"code": "ZAZ", "name": "Zaragoza Airport", "city": "Zaragoza", "region": "AR"},
    {"code": "ABC", "name": "Albacete Airport", "city": "Albacete", "region": "CM"},
]

# Canary Islands geographic box (lon/lat) for the inset, like JP Okinawa.
ES_CN_W, ES_CN_S, ES_CN_E, ES_CN_N = -18.35, 27.55, -13.20, 29.55

ALIASES = {
    **E.ALIASES,
    "Rome": ["Rome", "Roma"],
    "Milan": ["Milan", "Milano"],
    "Naples": ["Naples", "Napoli"],
    "Turin": ["Turin", "Torino"],
    "Genoa": ["Genoa", "Genova"],
    "Florence": ["Florence", "Firenze"],
    "Venice": ["Venice", "Venezia"],
    "L'Aquila": ["L'Aquila", "LAquila", "Aquila"],
    "Aosta": ["Aosta", "Aoste"],
    "Seville": ["Seville", "Sevilla"],
    "Malaga": ["Malaga", "Málaga"],
    "Las Palmas": ["Las Palmas", "Las Palmas de Gran Canaria"],
    "Santa Cruz de Tenerife": ["Santa Cruz de Tenerife"],

    "Vitoria": ["Vitoria", "Vitoria-Gasteiz", "Gasteiz"],
    "Santiago": ["Santiago", "Santiago de Compostela"],
    "Merida": ["Merida", "Mérida"],
    "Logrono": ["Logrono", "Logroño"],
    "Palma": ["Palma", "Palma de Mallorca"],
    "Pamplona": ["Pamplona", "Iruña", "Pamplona/Iruña"],
}

DISPLAY = {
    "Malaga": "Málaga",
    "Merida": "Mérida",
    "Logrono": "Logroño",
    "Vitoria": "Vitoria-Gasteiz",
    "Santiago": "Santiago de Compostela",
    "Las Palmas": "Las Palmas",
    "Santa Cruz de Tenerife": "Santa Cruz de Tenerife",
    "L'Aquila": "L'Aquila",
}


HEADER = (
    "/* Natural Earth 10m admin-1 (public domain, https://www.naturalearthdata.com/) "
    "→ topology-aware mapshaper simplify (shared borders preserved) → SVG paths.\n"
    "   Italy airports: ENAC aeroporti di interesse nazionale (d.P.R. 201/2015), "
    "updated 23 June 2026 "
    "https://www.enac.gov.it/aeroporti/infrastrutture-aeroportuali/aeroporti-in-italia/\n"
    "   Spain airports: Aena official network "
    "https://www.aena.es/en/passengers/our-airports.html "
    "(excludes GA fields Cuatro Vientos / Sabadell / Son Bonet and heliports Ceuta / Algeciras).\n"
    "   Airport coordinates: OurAirports, public domain "
    "https://davidmegginson.github.io/ourairports-data/airports.csv\n"
    "   City coordinates: Natural Earth 10m populated places (public domain). */\n"
)


def write_js(var_geo, var_air, geo, airports, path: Path):
    clean = {}
    for k, v in geo.items():
        clean[k] = {kk: vv for kk, vv in v.items() if kk != "area"}
    path.write_text(
        HEADER
        + f"window.{var_geo}={json.dumps(clean, ensure_ascii=False, separators=(',', ':'))};\n"
        + f"window.{var_air}={json.dumps(airports, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )
    print(path.relative_to(ROOT), len(clean), "regions", len(airports), "airports", path.stat().st_size, "bytes")


def emit(var_geo, var_air, geo, airports, filename):
    for folder in (OUT_SITE, OUT_STATIC):
        folder.mkdir(parents=True, exist_ok=True)
        write_js(var_geo, var_air, geo, airports, folder / filename)


def add_cities(geo, cities, meta_for, places, aliases):
    used = []
    for name, region, is_cap in cities:
        if region not in geo:
            print("WARN city region missing", name, region)
            continue
        cands = aliases.get(name, [name])
        place = K.find_place(places, *cands)
        if not place:
            print("WARN no NE place for", name, "tried", cands)
            continue
        x, y = K.ll_to_svg(place["lon"], place["lat"], meta_for(region))
        display = DISPLAY.get(name, name)
        geo[region].setdefault("cities", []).append({
            "n": display, "x": x, "y": y, "cap": bool(is_cap),
        })
        used.append(display)
    return used


def gather_rows(adm0: str, mapping_tbl: dict):
    feats = E.load_ne_features(adm0)
    buckets = {}
    skipped = []
    for d, g in feats:
        reg = d.get("region") or ""
        if reg not in mapping_tbl:
            skipped.append((reg, d.get("name"), d.get("name_en")))
            continue
        code, name = mapping_tbl[reg]
        buckets.setdefault(code, {"name": name, "parts": []})
        buckets[code]["parts"].append(g)
    if skipped:
        print("WARN unmatched", adm0, skipped[:12], "n", len(skipped))
    rows = []
    for code, info in buckets.items():
        g = unary_union(info["parts"])
        rows.append((code, info["name"], g))
    return rows



def restore_dropped_islands(ll: dict, orig: dict, specs: list[tuple]):
    """Re-attach small islands that mapshaper -clean dropped as slivers."""
    extras = {}
    for code, lon, lat, name in specs:
        src = orig.get(code)
        if src is None or src.is_empty:
            print("WARN no original geom to restore", name, code)
            continue
        parts = list(src.geoms) if src.geom_type == "MultiPolygon" else [src]
        pt = Point(lon, lat)
        dest = ll.get(code)
        if dest is not None and not dest.is_empty and dest.buffer(0.03).contains(pt):
            print("island already present", name)
            continue
        hit = None
        for part in parts:
            if part.contains(pt) or part.buffer(0.06).contains(pt):
                hit = part
                break
        if hit is None:
            nearest = min(parts, key=lambda part: part.distance(pt))
            if nearest.distance(pt) <= 0.25 and nearest.area < 0.15:
                hit = nearest
        if hit is None or hit.area > 0.15:
            hit = pt.buffer(0.045)
            print(f"restore island {name} as {hit.area:.4f} deg² disc")
        else:
            print(f"restore island {name} from original polygon area={hit.area:.5f}")
        extras.setdefault(code, []).append(hit)
    for code, extra in extras.items():
        ll[code] = unary_union([ll[code], *extra])


def largest_poly(g):
    parts = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    return max(parts, key=lambda part: part.area)


def svg_label_point(g):
    largest = largest_poly(g)
    try:
        pt = polylabel(largest, tolerance=0.5)
    except Exception:
        pt = largest.representative_point()
    if not largest.contains(pt):
        pt = largest.representative_point()
    return pt


def apply_interior_labels(geo: dict, svg: dict):
    """Pole-of-inaccessibility on the largest polygon. Long names that do
    not fit inside the region are hidden at full view (labelZoom)."""
    for code, g in svg.items():
        if code not in geo:
            continue
        pt = svg_label_point(g)
        geo[code]["c"] = [K.round_f(pt.x), K.round_f(pt.y)]
        geo[code].pop("callout", None)
        geo[code].pop("lx", None)
        geo[code].pop("ly", None)
        name = geo[code]["name"]
        # Uppercase + tracking at ~10.5px ≈ 6.2px per character.
        tw = max(20.0, len(name) * 6.2)
        th = 12.0
        rect = box(pt.x - tw / 2, pt.y - th / 2, pt.x + tw / 2, pt.y + th / 2)
        try:
            gg = g.buffer(0)
            contains = gg.contains(rect)
            inside = gg.contains(pt)
        except Exception:
            contains, inside = False, True
        minx, miny, maxx, maxy = g.bounds
        bw, bh = maxx - minx, maxy - miny
        # Large, roomy regions can host the label visually even if a concave
        # edge clips one corner of the text box. Thin or tiny ones wait for zoom.
        roomy = inside and tw <= bw * 0.88 and th <= bh * 0.42
        if contains or roomy:
            geo[code].pop("labelZoom", None)
            print(f"labelOK   {code} {name}")
        else:
            geo[code]["labelZoom"] = True
            print(f"labelZoom {code} {name} (text {tw:.0f}x{th:.0f} vs bbox {bw:.0f}x{bh:.0f})")



def tune_canaries_label(geo):
    """Write «Santa Cruz de Tenerife» in full, stacked above the city so the
    long name stays inside the inset / adjacent water at 1280 and 390."""
    for c in (geo.get("CN") or {}).get("cities") or []:
        if c.get("n") != "Santa Cruz de Tenerife":
            continue
        c["lines"] = ["Santa Cruz", "de Tenerife"]
        c["anchor"] = "start"
        # Pinned two-line block above the western Canaries, fully on-map at
        # 1280 and 390 (middle/city-x placements clipped the left edge at 390).
        c["lx"] = 24.0
        c["ly"] = 478.0
        c["pinLabel"] = True
        return
    print("WARN Santa Cruz de Tenerife city missing from Canaries")


def build_italy(oa, places):
    rows = gather_rows("ITA", IT_REGION)
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "it-in.geojson"
        dest = Path(td) / "it-out.geojson"
        E.features_to_geojson(rows, src)
        ll, names = E.mapshaper_dissolve(src, "26%", dest)
    expected = set(v[0] for v in IT_REGION.values())
    missing = expected - set(ll)
    extra = set(ll) - expected
    if missing or extra:
        raise SystemExit(f"IT key mismatch missing={missing} extra={extra}")
    # Keep Sicily and Sardinia in geographic place (like Corsica on the France map).
    orig = {code: geom for code, _name, geom in rows}
    restore_dropped_islands(ll, orig, [
        ("SIC", 12.591, 35.509, "Lampedusa"),
        ("SIC", 12.031, 36.787, "Pantelleria"),
    ])
    svg, meta = K.fit_project(ll, pads=(16, 8, 16, 10))
    geo = K.pack(svg, names)
    apply_interior_labels(geo, svg)
    add_cities(geo, IT_CITIES, lambda _r: meta, places, ALIASES)
    airports = E.attach_airports(IT_AIRPORTS, oa, meta, ll, IT_MAJORS)
    for item in airports:
        item.pop("mapName", None)
    return geo, airports, meta


def build_spain(oa, places):
    rows = gather_rows("ESP", ES_REGION)
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "es-in.geojson"
        dest = Path(td) / "es-out.geojson"
        E.features_to_geojson(rows, src)
        ll, names = E.mapshaper_dissolve(src, "26%", dest)
    expected = set(v[0] for v in ES_REGION.values())
    missing = expected - set(ll)
    extra = set(ll) - expected
    if missing or extra:
        raise SystemExit(f"ES key mismatch missing={missing} extra={extra}")

    main = {k: g for k, g in ll.items() if k != "CN"}
    svg, meta = K.fit_project(main, pads=(28, 36, 56, 28))
    geo = K.pack(svg, {k: names[k] for k in main})
    apply_interior_labels(geo, svg)

    cn_meta = None
    og = ll.get("CN")
    if og is not None:
        og = K.keep_parts_in_box(og, ES_CN_W, ES_CN_S, ES_CN_E, ES_CN_N, near_deg=None) or og
        sg, cn_meta = K.inset_okinawa(og, slot=(24, 462, 208, 132))
        c = sg.representative_point()
        geo["CN"] = {
            "name": names["CN"],
            "d": K.geom_to_d(sg),
            "c": [K.round_f(c.x), K.round_f(c.y)],
            "cities": [],
            "inset": True,
            "area": round(sg.area, 1),
        }
        apply_interior_labels({"CN": geo["CN"]}, {"CN": sg})

    def meta_for(region):
        return cn_meta if region == "CN" and cn_meta else meta

    add_cities(geo, ES_CITIES, meta_for, places, ALIASES)
    tune_canaries_label(geo)

    # Project airports with the matching meta (Canaries → inset).
    out = []
    for s in ES_AIRPORTS:
        info = oa.get(s["code"])
        if not info:
            raise SystemExit(f"missing OurAirports coords for {s['code']}")
        pip = E.pip_region(info["lon"], info["lat"], ll)
        region = pip or s["region"]
        if pip and pip != s["region"]:
            print(f"NOTE airport {s['code']} PIP={pip} (hint was {s['region']})")
        if not pip:
            print(f"WARN airport {s['code']} not inside any region; using hint {s['region']}")
        x, y = K.ll_to_svg(info["lon"], info["lat"], meta_for(region))
        item = {
            "code": s["code"],
            "name": s["name"],
            "city": s["city"],
            "province": region,
            "state": region,
            "x": x,
            "y": y,
            "lat": round(info["lat"], 4),
            "lon": round(info["lon"], 4),
        }
        if s["code"] in ES_MAJORS:
            item["mapLabel"] = s["code"]
            item["major"] = True
        else:
            item["zoomOnly"] = True
        out.append(item)
    return geo, out, meta


def main():
    if not SHP.exists():
        raise SystemExit(f"missing shapefile {SHP}")
    K.AIRPORTS_CSV = AIRPORTS_CSV
    E.AIRPORTS_CSV = AIRPORTS_CSV
    oa = K.load_ourairports()
    print("building Italy")
    it_geo, it_ap, _ = build_italy(oa, K.load_places("ITA"))
    emit("IT_GEO", "IT_GEO_AIRPORTS", it_geo, it_ap, "italy-map-geo.js")
    print("building Spain")
    es_geo, es_ap, _ = build_spain(oa, K.load_places("ESP"))
    emit("ES_GEO", "ES_GEO_AIRPORTS", es_geo, es_ap, "spain-map-geo.js")
    for geo, ap, tag in ((it_geo, it_ap, "IT"), (es_geo, es_ap, "ES")):
        print(tag, "regions", len(geo),
              "cities", sum(len(g.get("cities") or []) for g in geo.values()),
              "named", [g["name"] for g in geo.values()],
              "airports", len(ap),
              "majors", sum(1 for a in ap if a.get("major")),
              "zoomOnly", sum(1 for a in ap if a.get("zoomOnly")))


if __name__ == "__main__":
    main()
