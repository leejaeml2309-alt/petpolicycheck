#!/usr/bin/env python3
"""Rebuild UK (12), France (13 metro) and Germany (16) map geo packs.

Source: Natural Earth 10m Cultural admin-1 states and provinces
        https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/
License: public domain (Natural Earth).

Topology-aware simplification via mapshaper (Visvalingam, shared edges preserved).

Airports (official lists; invent nothing; ambiguities flagged in the header
and in the preview report):

  UK — CAA Table 10.1 “EU and Other Intl Pax Traffic”, August 2026
        https://www.caa.co.uk/data-and-analysis/uk-aviation-market/airports/uk-airport-data/uk-airport-data-2026/august-2026/
        (CSV: Documents/Download/26836/…/17874). Every GB+NI reporting
        airport with international terminal passengers > 0 that month.
        Crown Dependencies (Guernsey, Jersey, Isle of Man) are in the
        same table under “Non UK Reporting Airports” and are omitted —
        they are not on this map. Table 01 (CSV 17856) gives rolling
        12-month size (Sep 2025–Aug 2026) used only for context.
        Major at full view: the 8 airports with ≥ 1,000,000 international
        terminal passengers in August 2026 (next is Newcastle at 597,778):
        LHR, LGW, MAN, STN, LTN, BHX, EDI, BRS.
        Flag: Blackpool / Sumburgh / part of Aberdeen “other intl” includes
        oil-rig charters; Farnborough, Biggin Hill and Oxford are mainly
        business aviation with small counts; Dundee, Kirkwall and Wick
        have only tens of international passengers.

  France — The legal list of aerodromes “ouverts au trafic international”
        is Annexe II of the arrêté of 18 July 2023
        https://www.legifrance.gouv.fr/loda/id/LEGITEXT000019430064
        (annexe also at juriblio). It includes 150+ fields, many GA /
        heliports / overseas — too broad to plot, and this map has no
        overseas inset. Plotted instead: UAF « Résultats d’activité des
        aéroports français 2025 » metropolitan commercial ranking with
        > 100,000 passengers
        https://www.aeroport.fr/system/files/2026-04/Resultats_d_activite_des_aeroports_francais_2025.DEFpdf.pdf
        (37 airports). The PDF has no per-airport international split;
        some of these (e.g. Ajaccio, Brest, Pau, Clermont-Ferrand) are
        largely domestic. Fields below 100k pax and all DROM/COM airports
        are omitted. Major at full view: the 10 metro airports with
        ≥ 5 million commercial passengers in 2025 (UAF “grands régionaux”
        threshold + the two Paris airports; next is Lille at 1.71M):
        CDG, ORY, NCE, MRS, LYS, BSL, TLS, NTE, BVA, BOD.
        Flag: EuroAirport Basel-Mulhouse is binational; IATA BSL/MLH,
        plotted as BSL, physically in Grand Est (Haut-Rhin). Beauvais
        (BVA) is in Hauts-de-France, not Île-de-France.

  Germany — ADV describes 22 “Internationale Verkehrsflughäfen”.
        BMV / LuftVG § 27d recognises 15 (DFS operates those towers).
        The extra 7 that ADV treats as international in its statistics
        are Dortmund, Frankfurt-Hahn, Friedrichshafen, Karlsruhe/Baden-
        Baden, Lübeck, Paderborn/Lippstadt and Weeze. This pack plots
        all 22. ADV monthly stats from 2026 omit Hahn
        (“ohne HHN ab 01.01.2026”) but Hahn is still on the official
        international list and is included. Memmingen (2.93M pax
        Jan–Sep 2026, almost all international) is ADV-regional and is
        NOT included — flag for Marc.
        Source: https://www.adv.aero/aktuelle-verkehrszahlen/
        https://dashboard.adv.aero/fileadmin/documents/Statistiken/2026/09.2026_ADV-Monatsstatistik.pdf
        https://bmdv.bund.de/SharedDocs/DE/Artikel/LF/flughaefen.html
        Major at full view: the 7 airports with ≥ 7 million passengers
        in ADV Jan–Sep 2026 YTD (next is Hannover at 4.11M):
        FRA, MUC, BER, DUS, HAM, CGN, STR.
        Flag: BER sits in Brandenburg (Schönefeld), not Berlin Land —
        the marker is attached to BB, same pattern as NRT in Chiba.

Coordinates: OurAirports airports.csv, public domain
        https://davidmegginson.github.io/ourairports-data/airports.csv
Cities: region / Land capitals and a few major cities, coordinates from
        Natural Earth 10m populated places (public domain). Missing
        places are flagged, not invented.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import shapefile
from shapely.geometry import mapping, shape, Point

# Reuse topology helpers from the KR/JP builder.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_krjp_geo as K  # noqa: E402

ROOT = K.ROOT
SHP = K.SHP
PLACES = K.PLACES
AIRPORTS_CSV = Path("/tmp/eu3-src/airports.csv")
if not AIRPORTS_CSV.exists():
    AIRPORTS_CSV = Path("/tmp/krjp-src/airports.csv")
OUT_SITE = K.OUT_SITE
OUT_STATIC = K.OUT_STATIC
W, H = K.W, K.H

UK_REGION = {
    ("England", "East"): ("EE", "East of England"),
    ("England", "East Midlands"): ("EM", "East Midlands"),
    ("England", "Greater London"): ("GL", "Greater London"),
    ("England", "North East"): ("NE", "North East"),
    ("England", "North West"): ("NW", "North West"),
    ("England", "South East"): ("SE", "South East"),
    ("England", "South West"): ("SW", "South West"),
    ("England", "West Midlands"): ("WM", "West Midlands"),
    ("England", "Yorkshire and the Humber"): ("YH", "Yorkshire and the Humber"),
    ("Northern Ireland", "Northern Ireland"): ("NIR", "Northern Ireland"),
}
UK_NATION = {
    "Scotland": ("SCT", "Scotland"),
    "Wales": ("WLS", "Wales"),
    "Northern Ireland": ("NIR", "Northern Ireland"),
}

FR_REGION = {
    "Hauts-de-France": ("HDF", "Hauts-de-France"),
    "Grand Est": ("GES", "Grand Est"),
    "Provence-Alpes-Côte-d'Azur": ("PAC", "Provence-Alpes-Côte d'Azur"),
    "Auvergne-Rhône-Alpes": ("ARA", "Auvergne-Rhône-Alpes"),
    "Nouvelle-Aquitaine": ("NAQ", "Nouvelle-Aquitaine"),
    "Occitanie": ("OCC", "Occitanie"),
    "Bourgogne-Franche-Comté": ("BFC", "Bourgogne-Franche-Comté"),
    "Pays de la Loire": ("PDL", "Pays de la Loire"),
    "Bretagne": ("BRE", "Bretagne"),
    "Normandie": ("NOR", "Normandie"),
    "Corse": ("COR", "Corse"),
    "Centre-Val de Loire": ("CVL", "Centre-Val de Loire"),
    "Île-de-France": ("IDF", "Île-de-France"),
}

DE_NAMES = {
    "SN": "Saxony",
    "BY": "Bavaria",
    "RP": "Rhineland-Palatinate",
    "SL": "Saarland",
    "SH": "Schleswig-Holstein",
    "NI": "Lower Saxony",
    "NW": "North Rhine-Westphalia",
    "BW": "Baden-Württemberg",
    "BB": "Brandenburg",
    "MV": "Mecklenburg-Western Pomerania",
    "HB": "Bremen",
    "HH": "Hamburg",
    "HE": "Hesse",
    "TH": "Thuringia",
    "ST": "Saxony-Anhalt",
    "BE": "Berlin",
}

# name, region, is_capital (of the mapped unit)
UK_CITIES = [
    ("London", "GL", True),
    ("Birmingham", "WM", True),
    ("Manchester", "NW", True),
    ("Liverpool", "NW", False),
    ("Leeds", "YH", True),
    ("Sheffield", "YH", False),
    ("Newcastle upon Tyne", "NE", True),
    ("Nottingham", "EM", True),
    ("Bristol", "SW", True),
    ("Southampton", "SE", True),
    ("Norwich", "EE", True),
    ("Edinburgh", "SCT", True),
    ("Glasgow", "SCT", False),
    ("Cardiff", "WLS", True),
    ("Belfast", "NIR", True),
]
FR_CITIES = [
    ("Paris", "IDF", True),
    ("Lille", "HDF", True),
    ("Strasbourg", "GES", True),
    ("Marseille", "PAC", True),
    ("Nice", "PAC", False),
    ("Lyon", "ARA", True),
    ("Bordeaux", "NAQ", True),
    ("Toulouse", "OCC", True),
    ("Dijon", "BFC", True),
    ("Nantes", "PDL", True),
    ("Rennes", "BRE", True),
    ("Rouen", "NOR", True),
    ("Ajaccio", "COR", True),
    ("Orleans", "CVL", True),  # NE NAMEASCII
    ("Montpellier", "OCC", False),
]
DE_CITIES = [
    ("Berlin", "BE", True),
    ("Hamburg", "HH", True),
    ("Bremen", "HB", True),
    ("Munich", "BY", True),
    ("Stuttgart", "BW", True),
    ("Dusseldorf", "NW", True),
    ("Cologne", "NW", False),
    ("Dortmund", "NW", False),
    ("Dresden", "SN", True),
    ("Leipzig", "SN", False),
    ("Wiesbaden", "HE", True),
    ("Frankfurt", "HE", False),
    ("Hanover", "NI", True),
    ("Kiel", "SH", True),
    ("Mainz", "RP", True),
    ("Saarbrucken", "SL", True),
    ("Potsdam", "BB", True),
    ("Schwerin", "MV", True),
    ("Erfurt", "TH", True),
    ("Magdeburg", "ST", True),
    ("Nuremberg", "BY", False),
]

UK_MAJORS = {"LHR", "LGW", "MAN", "STN", "LTN", "BHX", "EDI", "BRS"}
FR_MAJORS = {"CDG", "ORY", "NCE", "MRS", "LYS", "BSL", "TLS", "NTE", "BVA", "BOD"}
DE_MAJORS = {"FRA", "MUC", "BER", "DUS", "HAM", "CGN", "STR"}

# English names; IATA is the official designator. Region is a hint; PIP wins.
UK_AIRPORTS = [
    {"code": "LHR", "name": "London Heathrow Airport", "city": "London", "region": "GL"},
    {"code": "LGW", "name": "London Gatwick Airport", "city": "London", "region": "SE"},
    {"code": "STN", "name": "London Stansted Airport", "city": "London", "region": "EE"},
    {"code": "LTN", "name": "London Luton Airport", "city": "Luton", "region": "EE"},
    {"code": "LCY", "name": "London City Airport", "city": "London", "region": "GL"},
    {"code": "SEN", "name": "London Southend Airport", "city": "Southend", "region": "EE"},
    {"code": "MAN", "name": "Manchester Airport", "city": "Manchester", "region": "NW"},
    {"code": "BHX", "name": "Birmingham Airport", "city": "Birmingham", "region": "WM"},
    {"code": "EDI", "name": "Edinburgh Airport", "city": "Edinburgh", "region": "SCT"},
    {"code": "BRS", "name": "Bristol Airport", "city": "Bristol", "region": "SW"},
    {"code": "GLA", "name": "Glasgow Airport", "city": "Glasgow", "region": "SCT"},
    {"code": "NCL", "name": "Newcastle International Airport", "city": "Newcastle upon Tyne", "region": "NE"},
    {"code": "LPL", "name": "Liverpool John Lennon Airport", "city": "Liverpool", "region": "NW"},
    {"code": "LBA", "name": "Leeds Bradford Airport", "city": "Leeds", "region": "YH"},
    {"code": "EMA", "name": "East Midlands Airport", "city": "Derby", "region": "EM"},
    {"code": "BFS", "name": "Belfast International Airport", "city": "Belfast", "region": "NIR"},
    {"code": "BHD", "name": "George Best Belfast City Airport", "city": "Belfast", "region": "NIR"},
    {"code": "ABZ", "name": "Aberdeen International Airport", "city": "Aberdeen", "region": "SCT"},
    {"code": "BOH", "name": "Bournemouth Airport", "city": "Bournemouth", "region": "SW"},
    {"code": "CWL", "name": "Cardiff Airport", "city": "Cardiff", "region": "WLS"},
    {"code": "SOU", "name": "Southampton Airport", "city": "Southampton", "region": "SE"},
    {"code": "INV", "name": "Inverness Airport", "city": "Inverness", "region": "SCT"},
    {"code": "PIK", "name": "Glasgow Prestwick Airport", "city": "Prestwick", "region": "SCT"},
    {"code": "EXT", "name": "Exeter Airport", "city": "Exeter", "region": "SW"},
    {"code": "NWI", "name": "Norwich Airport", "city": "Norwich", "region": "EE"},
    {"code": "NQY", "name": "Cornwall Airport Newquay", "city": "Newquay", "region": "SW"},
    {"code": "LSI", "name": "Sumburgh Airport", "city": "Sumburgh", "region": "SCT"},
    {"code": "MME", "name": "Teesside International Airport", "city": "Darlington", "region": "NE"},
    {"code": "LDY", "name": "City of Derry Airport", "city": "Derry", "region": "NIR"},
    {"code": "HUY", "name": "Humberside Airport", "city": "Kirmington", "region": "YH"},
    {"code": "KOI", "name": "Kirkwall Airport", "city": "Kirkwall", "region": "SCT"},
    {"code": "FAB", "name": "Farnborough Airport", "city": "Farnborough", "region": "SE"},
    {"code": "DND", "name": "Dundee Airport", "city": "Dundee", "region": "SCT"},
    {"code": "BLK", "name": "Blackpool Airport", "city": "Blackpool", "region": "NW"},
    {"code": "BQH", "name": "London Biggin Hill Airport", "city": "London", "region": "GL"},
    {"code": "OXF", "name": "Oxford Airport", "city": "Oxford", "region": "SE"},
    {"code": "WIC", "name": "Wick John O'Groats Airport", "city": "Wick", "region": "SCT"},
]
FR_AIRPORTS = [
    {"code": "CDG", "name": "Paris Charles de Gaulle Airport", "city": "Paris", "region": "IDF"},
    {"code": "ORY", "name": "Paris Orly Airport", "city": "Paris", "region": "IDF"},
    {"code": "NCE", "name": "Nice Côte d'Azur Airport", "city": "Nice", "region": "PAC"},
    {"code": "MRS", "name": "Marseille Provence Airport", "city": "Marseille", "region": "PAC"},
    {"code": "LYS", "name": "Lyon-Saint-Exupéry Airport", "city": "Lyon", "region": "ARA"},
    {"code": "BSL", "name": "EuroAirport Basel-Mulhouse-Freiburg", "city": "Mulhouse", "region": "GES"},
    {"code": "TLS", "name": "Toulouse-Blagnac Airport", "city": "Toulouse", "region": "OCC"},
    {"code": "NTE", "name": "Nantes Atlantique Airport", "city": "Nantes", "region": "PDL"},
    {"code": "BVA", "name": "Paris Beauvais-Tillé Airport", "city": "Beauvais", "region": "HDF"},
    {"code": "BOD", "name": "Bordeaux-Mérignac Airport", "city": "Bordeaux", "region": "NAQ"},
    {"code": "LIL", "name": "Lille-Lesquin Airport", "city": "Lille", "region": "HDF"},
    {"code": "MPL", "name": "Montpellier Méditerranée Airport", "city": "Montpellier", "region": "OCC"},
    {"code": "AJA", "name": "Ajaccio Napoléon Bonaparte Airport", "city": "Ajaccio", "region": "COR"},
    {"code": "BIA", "name": "Bastia-Poretta Airport", "city": "Bastia", "region": "COR"},
    {"code": "SXB", "name": "Strasbourg Airport", "city": "Strasbourg", "region": "GES"},
    {"code": "BIQ", "name": "Biarritz Pays Basque Airport", "city": "Biarritz", "region": "NAQ"},
    {"code": "FSC", "name": "Figari-Sud Corse Airport", "city": "Figari", "region": "COR"},
    {"code": "BES", "name": "Brest Bretagne Airport", "city": "Brest", "region": "BRE"},
    {"code": "LDE", "name": "Tarbes-Lourdes-Pyrénées Airport", "city": "Tarbes", "region": "OCC"},
    {"code": "RNS", "name": "Rennes-Saint-Jacques Airport", "city": "Rennes", "region": "BRE"},
    {"code": "PGF", "name": "Perpignan-Rivesaltes Airport", "city": "Perpignan", "region": "OCC"},
    {"code": "CLY", "name": "Calvi-Sainte-Catherine Airport", "city": "Calvi", "region": "COR"},
    {"code": "CFR", "name": "Caen-Carpiquet Airport", "city": "Caen", "region": "NOR"},
    {"code": "CCF", "name": "Carcassonne Airport", "city": "Carcassonne", "region": "OCC"},
    {"code": "LRH", "name": "La Rochelle-Île de Ré Airport", "city": "La Rochelle", "region": "NAQ"},
    {"code": "BZR", "name": "Béziers Cap d'Agde Airport", "city": "Béziers", "region": "OCC"},
    {"code": "LIG", "name": "Limoges-Bellegarde Airport", "city": "Limoges", "region": "NAQ"},
    {"code": "GNB", "name": "Grenoble-Alpes-Isère Airport", "city": "Grenoble", "region": "ARA"},
    {"code": "CFE", "name": "Clermont-Ferrand Auvergne Airport", "city": "Clermont-Ferrand", "region": "ARA"},
    {"code": "FNI", "name": "Nîmes-Alès-Camargue-Cévennes Airport", "city": "Nîmes", "region": "OCC"},
    {"code": "EGC", "name": "Bergerac Dordogne Périgord Airport", "city": "Bergerac", "region": "NAQ"},
    {"code": "PUF", "name": "Pau Pyrénées Airport", "city": "Pau", "region": "NAQ"},
    {"code": "TLN", "name": "Toulon-Hyères Airport", "city": "Toulon", "region": "PAC"},
    {"code": "CMF", "name": "Chambéry-Savoie Airport", "city": "Chambéry", "region": "ARA"},
    {"code": "TUF", "name": "Tours Val de Loire Airport", "city": "Tours", "region": "CVL"},
    {"code": "RDZ", "name": "Rodez-Aveyron Airport", "city": "Rodez", "region": "OCC"},
    {"code": "ETZ", "name": "Metz-Nancy-Lorraine Airport", "city": "Metz", "region": "GES"},
]
DE_AIRPORTS = [
    {"code": "BER", "name": "Berlin Brandenburg Airport", "city": "Berlin", "region": "BB"},
    {"code": "BRE", "name": "Bremen Airport", "city": "Bremen", "region": "HB"},
    {"code": "DRS", "name": "Dresden Airport", "city": "Dresden", "region": "SN"},
    {"code": "DUS", "name": "Düsseldorf Airport", "city": "Dusseldorf", "region": "NW"},
    {"code": "ERF", "name": "Erfurt-Weimar Airport", "city": "Erfurt", "region": "TH"},
    {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "region": "HE"},
    {"code": "HAM", "name": "Hamburg Airport", "city": "Hamburg", "region": "HH"},
    {"code": "HAJ", "name": "Hannover Airport", "city": "Hanover", "region": "NI"},
    {"code": "CGN", "name": "Cologne Bonn Airport", "city": "Cologne", "region": "NW"},
    {"code": "LEJ", "name": "Leipzig/Halle Airport", "city": "Leipzig", "region": "SN"},
    {"code": "MUC", "name": "Munich Airport", "city": "Munich", "region": "BY"},
    {"code": "FMO", "name": "Münster Osnabrück Airport", "city": "Munster", "region": "NW"},
    {"code": "NUE", "name": "Nuremberg Airport", "city": "Nuremberg", "region": "BY"},
    {"code": "SCN", "name": "Saarbrücken Airport", "city": "Saarbrucken", "region": "SL"},
    {"code": "STR", "name": "Stuttgart Airport", "city": "Stuttgart", "region": "BW"},
    {"code": "DTM", "name": "Dortmund Airport", "city": "Dortmund", "region": "NW"},
    {"code": "HHN", "name": "Frankfurt-Hahn Airport", "city": "Hahn", "region": "RP"},
    {"code": "FDH", "name": "Friedrichshafen Airport", "city": "Friedrichshafen", "region": "BW"},
    {"code": "FKB", "name": "Karlsruhe/Baden-Baden Airport", "city": "Baden-Baden", "region": "BW"},
    {"code": "LBC", "name": "Lübeck Airport", "city": "Lubeck", "region": "SH"},
    {"code": "PAD", "name": "Paderborn Lippstadt Airport", "city": "Paderborn", "region": "NW"},
    {"code": "NRN", "name": "Weeze Airport", "city": "Weeze", "region": "NW"},
]


def load_ne_features(adm0: str):
    sf = shapefile.Reader(str(SHP))
    fields = [f[0] for f in sf.fields[1:]]
    out = []
    for sr, rec in zip(sf.shapes(), sf.records()):
        d = dict(zip(fields, rec))
        if d.get("adm0_a3") != adm0:
            continue
        g = shape(sr.__geo_interface__)
        if g.is_empty:
            continue
        out.append((d, g))
    return out


def features_to_geojson(rows: list, dest: Path):
    fc = {"type": "FeatureCollection", "features": []}
    for ppc_id, ppc_name, g in rows:
        fc["features"].append({
            "type": "Feature",
            "properties": {"ppc_id": ppc_id, "ppc_name": ppc_name},
            "geometry": mapping(g),
        })
    dest.write_text(json.dumps(fc), encoding="utf-8")


def mapshaper_dissolve(src: Path, percent: str, dest: Path):
    cmd = [
        "npx", "--yes", "mapshaper", str(src),
        "-dissolve", "ppc_id", "copy-fields=ppc_name",
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
        code = str(props.get("ppc_id") or "")
        names[code] = props.get("ppc_name") or code
        geoms[code] = shape(feat["geometry"])
    return geoms, names


def pip_region(lon, lat, ll_geoms: dict):
    pt = Point(lon, lat)
    for code, g in ll_geoms.items():
        if g.contains(pt) or g.touches(pt):
            return code
    # nearest by centroid distance (coastal airports sometimes sit just outside)
    best, bd = None, 1e9
    for code, g in ll_geoms.items():
        d = g.distance(pt)
        if d < bd:
            best, bd = code, d
    # only accept if reasonably close (~0.35 deg ~ 30 km)
    if bd <= 0.35:
        return best
    return None


def attach_airports(specs, oa, meta, ll_geoms, majors):
    out = []
    for s in specs:
        info = oa.get(s["code"])
        if not info:
            # BSL may be stored only as MLH
            if s["code"] == "BSL":
                info = oa.get("MLH")
            if not info:
                raise SystemExit(f"missing OurAirports coords for {s['code']}")
        pip = pip_region(info["lon"], info["lat"], ll_geoms)
        region = pip or s["region"]
        if s["code"] == "BRE":
            region = "HB"  # OA iso_region DE-HB; NE 10m puts the point ~200m into NI
        if pip and pip != s["region"]:
            print(f"NOTE airport {s['code']} PIP={pip} (hint was {s['region']})")
        if not pip:
            print(f"WARN airport {s['code']} not inside any region; using hint {s['region']}")
        x, y = K.ll_to_svg(info["lon"], info["lat"], meta)
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
        if s["code"] in majors:
            item["mapLabel"] = s["code"]
            item["mapName"] = (
                s["name"]
                .replace(" International Airport", "")
                .replace(" Airport", "")
            )
            item["major"] = True
        else:
            item["zoomOnly"] = True
        out.append(item)
    return out


HEADER = (
    "/* Natural Earth 10m admin-1 (public domain, https://www.naturalearthdata.com/) "
    "→ topology-aware mapshaper simplify (shared borders preserved) → SVG paths.\n"
    "   UK international airports: CAA Table 10.1 August 2026 "
    "https://www.caa.co.uk/data-and-analysis/uk-aviation-market/airports/uk-airport-data/uk-airport-data-2026/august-2026/\n"
    "   France: UAF 2025 metro commercial airports >100k pax "
    "https://www.aeroport.fr/system/files/2026-04/Resultats_d_activite_des_aeroports_francais_2025.DEFpdf.pdf"
    " (legal 'open to international traffic' list is broader: arrêté 18 Jul 2023 Annexe II).\n"
    "   Germany: 22 ADV international Verkehrsflughäfen (15 BMV §27d + 7 ADV); "
    "https://dashboard.adv.aero/fileadmin/documents/Statistiken/2026/09.2026_ADV-Monatsstatistik.pdf\n"
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
        write_js(var_geo, var_air, geo, airports, folder / filename)


def add_cities(geo, cities, meta, places, aliases):
    """aliases: {requested_name: [NE candidate names]}"""
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
        x, y = K.ll_to_svg(place["lon"], place["lat"], meta)
        # Prefer a readable English display name (our list), not NE ascii.
        display = name
        if name == "Dusseldorf":
            display = "Düsseldorf"
        elif name == "Saarbrucken":
            display = "Saarbrücken"
        elif name == "Orleans":
            display = "Orléans"
        geo[region].setdefault("cities", []).append({
            "n": display, "x": x, "y": y, "cap": bool(is_cap),
        })
        used.append(display)
    return used


ALIASES = {
    "Newcastle upon Tyne": ["Newcastle upon Tyne", "Newcastle"],
    "Dusseldorf": ["Dusseldorf", "Düsseldorf", "Duesseldorf"],
    "Saarbrucken": ["Saarbrucken", "Saarbrücken"],
    "Orleans": ["Orleans", "Orléans"],
    "Hanover": ["Hanover", "Hannover"],
    "Cologne": ["Cologne", "Koln", "Köln"],
    "Munich": ["Munich", "Munchen", "München"],
    "Nuremberg": ["Nuremberg", "Nurnberg", "Nürnberg"],
    "Frankfurt": ["Frankfurt", "Frankfurt am Main"],
}


def build_uk(oa, places):
    feats = load_ne_features("GBR")
    rows, skipped = [], []
    for d, g in feats:
        unit = d.get("geonunit") or ""
        reg = d.get("region") or ""
        if unit in ("Scotland", "Wales"):
            code, name = UK_NATION[unit]
        elif (unit, reg) in UK_REGION:
            code, name = UK_REGION[(unit, reg)]
        else:
            skipped.append((unit, reg, d.get("name")))
            continue
        rows.append((code, name, g))
    if skipped:
        print("WARN UK unmatched", skipped[:8], "n", len(skipped))
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "uk-in.geojson"
        dest = Path(td) / "uk-out.geojson"
        features_to_geojson(rows, src)
        ll, names = mapshaper_dissolve(src, "24%", dest)
    expected = {"NIR", "WLS", "SCT", "NE", "NW", "YH", "EM", "WM", "EE", "SE", "SW", "GL"}
    missing = expected - set(ll)
    extra = set(ll) - expected
    if missing or extra:
        raise SystemExit(f"UK key mismatch missing={missing} extra={extra}")
    # right gutter for London callout
    svg, meta = K.fit_project(ll, pads=(36, 28, 145, 32))
    geo = K.pack(svg, names)
    K.assign_callouts_fixed(geo, ["GL"], x_col=852, side="east")
    add_cities(geo, UK_CITIES, meta, places, ALIASES)
    airports = attach_airports(UK_AIRPORTS, oa, meta, ll, UK_MAJORS)
    return geo, airports, meta


def build_france(oa, places):
    feats = load_ne_features("FRA")
    rows, skipped = [], []
    for d, g in feats:
        if (d.get("geonunit") or "") != "France":
            continue  # drop overseas
        reg = d.get("region") or ""
        if reg not in FR_REGION:
            skipped.append((reg, d.get("name")))
            continue
        code, name = FR_REGION[reg]
        rows.append((code, name, g))
    if skipped:
        print("WARN FR unmatched", skipped)
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "fr-in.geojson"
        dest = Path(td) / "fr-out.geojson"
        features_to_geojson(rows, src)
        ll, names = mapshaper_dissolve(src, "26%", dest)
    expected = set(v[0] for v in FR_REGION.values())
    missing = expected - set(ll)
    extra = set(ll) - expected
    if missing or extra:
        raise SystemExit(f"FR key mismatch missing={missing} extra={extra}")
    # top gutter for Île-de-France callout
    svg, meta = K.fit_project(ll, pads=(28, 72, 28, 28))
    geo = K.pack(svg, names)
    # place IDF label in the top gutter, centred on its x
    if "IDF" in geo:
        geo["IDF"]["callout"] = True
        geo["IDF"]["lx"] = K.round_f(geo["IDF"]["c"][0])
        geo["IDF"]["ly"] = 28
    add_cities(geo, FR_CITIES, meta, places, ALIASES)
    airports = attach_airports(FR_AIRPORTS, oa, meta, ll, FR_MAJORS)
    return geo, airports, meta


def build_germany(oa, places):
    feats = load_ne_features("DEU")
    rows = []
    for d, g in feats:
        iso = (d.get("iso_3166_2") or "").replace("DE-", "")
        if iso not in DE_NAMES:
            print("WARN DE unexpected", d.get("iso_3166_2"), d.get("name_en"))
            continue
        rows.append((iso, DE_NAMES[iso], g))
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "de-in.geojson"
        dest = Path(td) / "de-out.geojson"
        features_to_geojson(rows, src)
        ll, names = mapshaper_dissolve(src, "30%", dest)
    expected = set(DE_NAMES)
    missing = expected - set(ll)
    extra = set(ll) - expected
    if missing or extra:
        raise SystemExit(f"DE key mismatch missing={missing} extra={extra}")
    # east gutter for Berlin; a little top pad for Hamburg / Bremen
    svg, meta = K.fit_project(ll, pads=(48, 44, 140, 28))
    geo = K.pack(svg, names)
    K.assign_callouts_fixed(geo, ["BE"], x_col=852, side="east")
    K.assign_callouts_fixed(geo, ["HH", "HB"], x_col=42, side="west")
    add_cities(geo, DE_CITIES, meta, places, ALIASES)
    airports = attach_airports(DE_AIRPORTS, oa, meta, ll, DE_MAJORS)
    return geo, airports, meta


def main():
    if not SHP.exists():
        raise SystemExit(f"missing shapefile {SHP}")
    K.AIRPORTS_CSV = AIRPORTS_CSV
    oa = K.load_ourairports()
    print("building UK")
    uk_geo, uk_ap, _ = build_uk(oa, K.load_places("GBR"))
    emit("UK_GEO", "UK_GEO_AIRPORTS", uk_geo, uk_ap, "uk-map-geo.js")
    print("building France")
    fr_geo, fr_ap, _ = build_france(oa, K.load_places("FRA"))
    emit("FR_GEO", "FR_GEO_AIRPORTS", fr_geo, fr_ap, "france-map-geo.js")
    print("building Germany")
    de_geo, de_ap, _ = build_germany(oa, K.load_places("DEU"))
    emit("DE_GEO", "DE_GEO_AIRPORTS", de_geo, de_ap, "germany-map-geo.js")
    for geo, ap, tag in ((uk_geo, uk_ap, "UK"), (fr_geo, fr_ap, "FR"), (de_geo, de_ap, "DE")):
        print(tag, "regions", len(geo), "cities", sum(len(g.get("cities") or []) for g in geo.values()),
              "airports", len(ap), "majors", sum(1 for a in ap if a.get("major")),
              "zoomOnly", sum(1 for a in ap if a.get("zoomOnly")))


if __name__ == "__main__":
    main()
