#!/usr/bin/env python3
"""Integrate Manager UK/FR/DE pack into eu-maps preview worktree. Local only."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ROOT = Path("/workspace/eu-maps-preview-20261110")
PACK = Path("/workspace/country-pages-uk-fr-de-20261110")
APPROVED_ROUTES = (
    "https://www.gov.uk/government/publications/pet-travel-approved-air-sea-and-rail-carriers-and-routes/"
    "approved-air-routes-for-pet-travel"
)
PREVIEW_BAR = (
    '<div class="ppc-preview-bar" role="status" style="position:sticky;top:0;z-index:9999;'
    "background:#7a1f1f;color:#fff;font:600 13px/1.35 Inter,system-ui,sans-serif;padding:8px 12px;"
    'text-align:center">LOCAL PREVIEW ONLY — EU country pages + maps (UK · France · Germany) · '
    "await Marc « publie »</div>"
)
KOREA_WARN = (
    '<div class="warn"><b>Travelling from South Korea?</b> South Korea is not on the UK or EU '
    "listed-country lists: your pet needs a rabies antibody titre test, then a 3-month wait after "
    "the blood sample, before entry.</div>"
)
FR_FAQ_NOTE = (
    "<p>Note: the French Ministry of Agriculture FAQ (last updated 11 June 2025) still cites the "
    "repealed Regulations (EU) 576/2013 and 577/2013 and a 4-month certificate validity. This page "
    "follows the EU rules in force since 22 April 2026 (Regulations (EU) 2026/131, 2026/705 and "
    "2026/636).</p>"
)

META = {
    "uk": {
        "file": "uk.html",
        "map": "uk-map.html",
        "js": "uk-map-data.js",
        "geo": "uk-map-geo.js",
        "geo_var": "UK_GEO",
        "ap_var": "UK_GEO_AIRPORTS",
        "data_var": "UK_MAP_DATA",
        "code": "UK",
        "name": "United Kingdom",
        "title": "Pet travel rules for the United Kingdom: entering Great Britain with a dog or cat | PetPolicyCheck",
        "desc": "GOV.UK / Defra pet entry rules for Great Britain, Dangerous Dogs Act, hubs including Glasgow and Newcastle, TfL, National Rail and return to the US. Checked 10 November 2026.",
        "unit": "nation",
        "unitPlural": "nations",
        "accent": "unionjack",
        "pack": "uk",
        "guideUrl": "uk.html",
        "crumb": "United Kingdom",
    },
    "fr": {
        "file": "france.html",
        "map": "france-map.html",
        "js": "france-map-data.js",
        "geo": "france-map-geo.js",
        "geo_var": "FR_GEO",
        "ap_var": "FR_GEO_AIRPORTS",
        "data_var": "FR_MAP_DATA",
        "code": "FR",
        "name": "France",
        "title": "Pet travel rules for France: EU entry, catégories 1–2, hubs | PetPolicyCheck",
        "desc": "France pet entry under EU 2026 rules, catégorie 1/2 dogs, hubs, RATP, SNCF and return to the US. Checked 10 November 2026.",
        "unit": "region",
        "unitPlural": "regions",
        "accent": "tricolore",
        "pack": "fr",
        "guideUrl": "france.html",
        "crumb": "France",
    },
    "de": {
        "file": "germany.html",
        "map": "germany-map.html",
        "js": "germany-map-data.js",
        "geo": "germany-map-geo.js",
        "geo_var": "DE_GEO",
        "ap_var": "DE_GEO_AIRPORTS",
        "data_var": "DE_MAP_DATA",
        "code": "DE",
        "name": "Germany",
        "title": "Pet travel rules for Germany: EU entry, HundVerbrEinfG, hubs | PetPolicyCheck",
        "desc": "Germany pet entry under EU 2026 rules, federal breed import ban, hubs, BVG, Deutsche Bahn and return to the US. Checked 10 November 2026.",
        "unit": "Land",
        "unitPlural": "Länder",
        "accent": "schwarzrotgold",
        "pack": "de",
        "guideUrl": "germany.html",
        "crumb": "Germany",
    },
}

REGION_MAP = {
    "uk": [
        (re.compile(r"^Scotland", re.I), "SCT"),
        (re.compile(r"^Wales", re.I), "WLS"),
        (re.compile(r"^Northern Ireland", re.I), "NIR"),
        (re.compile(r"^England", re.I), "ENG"),
    ],
    "fr": [
        (re.compile(r"Île-de-France|Ile-de-France", re.I), "IDF"),
        (re.compile(r"Provence-Alpes-Côte d'Azur|Provence-Alpes-Cote d'Azur", re.I), "PAC"),
        (re.compile(r"Auvergne-Rhône-Alpes|Auvergne-Rhone-Alpes", re.I), "ARA"),
        (re.compile(r"Hauts-de-France", re.I), "HDF"),
        (re.compile(r"Grand Est", re.I), "GES"),
        (re.compile(r"Nouvelle-Aquitaine", re.I), "NAQ"),
        (re.compile(r"Occitanie", re.I), "OCC"),
        (re.compile(r"Bourgogne-Franche-Comté|Bourgogne-Franche-Comte", re.I), "BFC"),
        (re.compile(r"Pays de la Loire", re.I), "PDL"),
        (re.compile(r"Bretagne", re.I), "BRE"),
        (re.compile(r"Normandie", re.I), "NOR"),
        (re.compile(r"Corse", re.I), "COR"),
        (re.compile(r"Centre-Val de Loire", re.I), "CVL"),
    ],
    "de": [
        (re.compile(r"^Bayern|Bavaria", re.I), "BY"),
        (re.compile(r"^Hessen|Hesse", re.I), "HE"),
        (re.compile(r"^Hamburg", re.I), "HH"),
        (re.compile(r"^Nordrhein-Westfalen|North Rhine", re.I), "NW"),
        (re.compile(r"^Brandenburg", re.I), "BB"),
        (re.compile(r"^Berlin", re.I), "BE"),
        (re.compile(r"^Baden-Württemberg|Baden-Wurttemberg", re.I), "BW"),
        (re.compile(r"^Niedersachsen|Lower Saxony", re.I), "NI"),
        (re.compile(r"^Sachsen-Anhalt", re.I), "ST"),
        (re.compile(r"^Sachsen|Saxony", re.I), "SN"),
        (re.compile(r"^Schleswig-Holstein", re.I), "SH"),
        (re.compile(r"^Mecklenburg", re.I), "MV"),
        (re.compile(r"^Rheinland-Pfalz|Rhineland", re.I), "RP"),
        (re.compile(r"^Saarland", re.I), "SL"),
        (re.compile(r"^Thüringen|Thuringen|Thuringia", re.I), "TH"),
        (re.compile(r"^Bremen", re.I), "HB"),
    ],
}

TONES = {
    "uk": {"ENG": "st-t1", "SCT": "st-t2", "WLS": "st-t3", "NIR": "st-t4"},
    "fr": {
        "HDF": "st-t1", "GES": "st-t2", "PAC": "st-t3", "ARA": "st-t4", "NAQ": "st-t5",
        "OCC": "st-t1", "BFC": "st-t2", "PDL": "st-t3", "BRE": "st-t4", "NOR": "st-t5",
        "COR": "st-t1", "CVL": "st-t2", "IDF": "st-t3", "GF": "st-t4", "MQ": "st-t5",
        "GP": "st-t1", "RE": "st-t2", "YT": "st-t3",
    },
    "de": {
        "SN": "st-t1", "BY": "st-t2", "RP": "st-t3", "SL": "st-t4", "SH": "st-t5",
        "NI": "st-t1", "NW": "st-t2", "BW": "st-t3", "BB": "st-t4", "MV": "st-t5",
        "HB": "st-t1", "HH": "st-t2", "HE": "st-t3", "TH": "st-t4", "ST": "st-t5", "BE": "st-t1",
    },
}


def todo_to_soon(text: str | None) -> str | None:
    if text is None or not isinstance(text, str):
        return text
    t = text
    if re.match(r"^\s*TODO\b", t, re.I):
        return "Policy details coming soon."
    t = re.sub(r"\([^)]*TODO[^)]*\)", "(Policy details coming soon.)", t, flags=re.I)
    t = re.sub(r"TODO:?[^.]*\.", "Policy details coming soon. ", t, flags=re.I)
    t = re.sub(r"TODO:?.*$", "Policy details coming soon.", t, flags=re.I)
    # Uber: never publish a fixed amount
    t = re.sub(
        r"(extra may apply[^.]*?(?:check(?: the)? app)[^.]*\.)",
        "price shown in the app.",
        t,
        flags=re.I,
    )
    t = re.sub(
        r"no fixed (?:£|euro|EUR|pound|amount)[^.]*\.",
        "price shown in the app.",
        t,
        flags=re.I,
    )
    t = re.sub(
        r"check the upfront price in the app[^.]*\.",
        "price shown in the app.",
        t,
        flags=re.I,
    )
    for bad in ("PPC Manager", "preview stub", "Checked Pending", "STUB"):
        t = t.replace(bad, "")
    return re.sub(r" {2,}", " ", t).strip()


def sanitize(o):
    if isinstance(o, dict):
        return {k: sanitize(v) for k, v in o.items()}
    if isinstance(o, list):
        return [sanitize(v) for v in o]
    if isinstance(o, str):
        return todo_to_soon(o)
    return o


def map_region(pack: str, region: str) -> str | None:
    for rx, code in REGION_MAP[pack]:
        if rx.search(region or ""):
            return code
    return None


def add_gla_ncl(hubs: list) -> list:
    have = {h["iata"] for h in hubs}
    extras = [
        {
            "iata": "GLA",
            "name": "Glasgow Airport",
            "city": "Glasgow",
            "region_or_province": "Scotland",
            "lat": 55.871899,
            "lon": -4.43306,
            "coords_source": "OurAirports airports.csv (davidmegginson.github.io/ourairports-data), fetched 2026-11-10",
            "official_site_url": "https://www.glasgowairport.com/",
            "pet_relief_url_or_note": {
                "url": None,
                "note": (
                    "Named on the GOV.UK approved commercial air-routes list (updated 9 November 2026) "
                    f"with ARC. Confirm the live list: {APPROVED_ROUTES}"
                ),
            },
            "local_transit_or_taxi_pet_note": (
                "National Express: ordinary pets not carried (assistance dogs only). "
                "National Rail: up to two small domestic animals free (Conditions of Travel from 30 July 2026). "
                "Uber Pet: price shown in the app."
            ),
            "sample_vet_clinic": {
                "name": "Vets Now Glasgow (24h hospital)",
                "city": "Glasgow",
                "url": "https://www.vets-now.com/find-an-emergency-vet/glasgow/",
                "note": "24-hour pet emergency hospital.",
            },
            "hotel_search_query": "dog friendly hotels Glasgow",
            "grooming": [],
            "grooming_search_query": "dog grooming Glasgow",
        },
        {
            "iata": "NCL",
            "name": "Newcastle International Airport",
            "city": "Newcastle upon Tyne",
            "region_or_province": "England (Tyne and Wear)",
            "lat": 55.037958,
            "lon": -1.689577,
            "coords_source": "OurAirports airports.csv (davidmegginson.github.io/ourairports-data), fetched 2026-11-10",
            "official_site_url": "https://www.newcastleairport.com/",
            "pet_relief_url_or_note": {
                "url": None,
                "note": (
                    "Named on the GOV.UK approved commercial air-routes list (updated 9 November 2026) "
                    f"with ARC. Confirm the live list: {APPROVED_ROUTES}"
                ),
            },
            "local_transit_or_taxi_pet_note": (
                "National Express: ordinary pets not carried (assistance dogs only). "
                "National Rail: up to two small domestic animals free (Conditions of Travel from 30 July 2026). "
                "Uber Pet: price shown in the app."
            ),
            "sample_vet_clinic": {
                "name": "Vets Now Newcastle (24h hospital)",
                "city": "Newcastle upon Tyne",
                "url": "https://www.vets-now.com/find-an-emergency-vet/newcastle/",
                "note": "24-hour pet emergency hospital.",
            },
            "hotel_search_query": "dog friendly hotels Newcastle",
            "grooming": [],
            "grooming_search_query": "dog grooming Newcastle",
        },
    ]
    out = list(hubs)
    for e in extras:
        if e["iata"] not in have:
            out.append(e)
    return out


def load_geo(path: Path, var: str):
    t = path.read_text(encoding="utf-8")
    m = re.search(rf"window\.{var}\s*=\s*(\{{.*?\}});\s*window\.", t, re.S)
    if not m:
        m = re.search(rf"window\.{var}\s*=\s*(\{{.*?\}});", t, re.S)
    if not m:
        raise SystemExit(f"GEO not found {var} in {path}")
    return json.loads(m.group(1)), t


def write_both(rel: str, text: str):
    for base in (ROOT / "site", ROOT / "static"):
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    print("wrote", rel)


def convert(pack: str, meta: dict):
    raw = sanitize(json.loads((PACK / pack / "map-data.json").read_text(encoding="utf-8")))
    if pack == "uk":
        raw["hubs"] = add_gla_ncl(raw["hubs"])
    geo_path = ROOT / "site/assets/js" / meta["geo"]
    geo, geo_src = load_geo(geo_path, meta["geo_var"])
    er = raw["entry_rules"]
    dogs = er.get("dogs") or {}
    cats = er.get("cats") or {}
    breeds_src = er.get("banned_or_restricted_breeds") or {}

    hubs_out = {}
    airports = []
    state_hub = {}
    special = {}
    offsets: dict[str, int] = {}

    for h in raw.get("hubs") or []:
        region = h.get("region_or_province") or ""
        code = map_region(pack, region)
        if not code:
            print("WARN unmapped", pack, region, h.get("iata"))
            continue
        iata = h["iata"]
        relief = h.get("pet_relief_url_or_note") or {}
        if isinstance(relief, str):
            relief = {"url": None, "note": relief}
        vet = h.get("sample_vet_clinic") or {}
        cx, cy = geo[code]["c"]
        n = offsets.get(code, 0)
        offsets[code] = n + 1
        ax = round(cx + (n * 18) - 6, 1)
        ay = round(cy - 12 - (n * 14), 1)
        city_name = (h.get("city") or "").split(",")[0].strip() or geo[code]["name"]
        cities = geo[code].setdefault("cities", [])
        if not any(c.get("n") == city_name for c in cities):
            cities.append({"n": city_name, "x": ax, "y": ay + 8})
        city = next(c for c in cities if c["n"] == city_name)

        hubs_out[iata] = {
            "iata": iata,
            "name": h.get("name"),
            "city": city_name,
            "region": region,
            "lat": h.get("lat"),
            "lon": h.get("lon"),
            "site": h.get("official_site_url") or "",
            "relief_url": relief.get("url") or None,
            "relief_note": relief.get("note") or "",
            "transit": h.get("local_transit_or_taxi_pet_note") or "",
            "vet": {
                "name": vet.get("name"),
                "city": vet.get("city"),
                "url": vet.get("url"),
                "note": vet.get("note"),
            }
            if vet.get("name")
            else None,
            "hotel_q": h.get("hotel_search_query") or f"pet friendly hotels {city_name}",
            "grooming": h.get("grooming") or [],
            "grooming_q": h.get("grooming_search_query") or f"dog grooming {city_name}",
        }
        if h.get("local_breed_alert"):
            special[code] = {
                "title": f'{geo[code]["name"]} breed note',
                "rule": h["local_breed_alert"],
                "src": er.get("official_url") or "",
            }
        airports.append(
            {
                "code": iata,
                "city": city_name,
                "province": code,
                "state": code,
                "x": city["x"],
                "y": city["y"] - 8,
                "lat": h.get("lat"),
                "lon": h.get("lon"),
            }
        )
        state_hub.setdefault(code, iata)

    tr = raw.get("transport") or {}
    rail: dict = {}
    if isinstance(tr.get("train"), dict):
        train = tr["train"]
        rail["train"] = {
            "rule": train.get("summary") or "Policy details coming soon.",
            "url": (train.get("official_urls") or [None])[0],
        }
    if isinstance(tr.get("taxi"), dict):
        taxi = tr["taxi"]
        uber_url = None
        for u in taxi.get("official_urls") or []:
            if u and "uber" in u.lower():
                uber_url = u
                break
        rail["uber_pet"] = {
            "rule": "Uber Pet: price shown in the app. Availability varies by city.",
            "url": uber_url or ((taxi.get("official_urls") or [None])[0]),
        }
    if isinstance(tr.get("bus"), dict):
        bus = tr["bus"]
        rail["bus"] = {
            "rule": bus.get("summary") or "Policy details coming soon.",
            "url": (bus.get("official_urls") or [None])[0],
        }

    hotels = {"chains": []}
    for ch in (raw.get("hotels") or {}).get("chains") or []:
        hotels["chains"].append(
            {
                "chain": ch.get("name") or ch.get("chain"),
                "policy": ch.get("rule") or ch.get("policy") or "Policy details coming soon.",
                "url": ch.get("url") or "",
            }
        )

    grooming = raw.get("grooming") or {}
    data = {
        "country": meta["code"],
        "name": meta["name"],
        "unit": meta["unit"],
        "unitPlural": meta["unitPlural"],
        "accent": meta["accent"],
        "tones": TONES[pack],
        "guideUrl": meta["guideUrl"],
        "authority": er.get("authority_name") or "Coming soon",
        "officialUrl": er.get("official_url") or "",
        "supportingUrls": er.get("supporting_urls") or [],
        "lastChecked": er.get("last_checked") or "",
        "dogs": {
            "microchip": dogs.get("microchip") or "Policy details coming soon",
            "rabies_vaccine": dogs.get("rabies_vaccine") or "Policy details coming soon",
            "titer_test_required": dogs.get("titer_test_required") or "Policy details coming soon",
            "health_certificate_cvi": dogs.get("health_certificate_cvi") or "Policy details coming soon",
            "import_permit_or_form": dogs.get("import_permit_or_form") or "Policy details coming soon",
            "age_minimum": dogs.get("age_minimum"),
            "special_notes": [todo_to_soon(x) for x in (dogs.get("special_notes") or [])],
        },
        "cats": {
            "microchip": cats.get("microchip") or "Policy details coming soon",
            "rabies_vaccine": cats.get("rabies_vaccine") or "Policy details coming soon",
            "health_certificate_cvi": cats.get("health_certificate_cvi") or "Policy details coming soon",
            "special_notes": [todo_to_soon(x) for x in (cats.get("special_notes") or [])],
        },
        "breeds": {
            "national": breeds_src.get("national") or "Policy details coming soon",
            "subnational": breeds_src.get("subnational") or [],
        },
        "returnToUs": er.get("return_to_us_note") or "Policy details coming soon.",
        "special": special,
        "alertStates": list(special.keys()),
        "provHub": dict(state_hub),
        "stateHub": dict(state_hub),
        "hubs": hubs_out,
        "rail": rail,
        "hotels": hotels,
        "groomingNote": {
            "culture_note": grooming.get("culture_note") or "",
            "vaccine_norms": grooming.get("vaccine_norms") or "",
            "international_docs_warning": grooming.get("international_docs_warning") or "",
        },
        "approved_air_routes_url": raw.get("approved_air_routes_url"),
        "approved_air_routes_note": raw.get("approved_air_routes_note"),
    }

    # Write map-data.js
    js = f"window.{meta['data_var']}={json.dumps(data, ensure_ascii=False, separators=(',', ':'))};"
    write_both(f"assets/js/{meta['js']}", js)

    # Patch geo airports + cities into geo js
    new_geo_json = json.dumps(geo, ensure_ascii=False, separators=(",", ":"))
    new_ap_json = json.dumps(airports, ensure_ascii=False, separators=(",", ":"))
    # Replace GEO object and AIRPORTS array
    t = geo_src
    t = re.sub(
        rf"window\.{meta['geo_var']}\s*=\s*\{{.*?\}};",
        f"window.{meta['geo_var']}={new_geo_json};",
        t,
        count=1,
        flags=re.S,
    )
    if re.search(rf"window\.{meta['ap_var']}\s*=", t):
        t = re.sub(
            rf"window\.{meta['ap_var']}\s*=\s*\[.*?\];",
            f"window.{meta['ap_var']}={new_ap_json};",
            t,
            count=1,
            flags=re.S,
        )
    else:
        t = t.rstrip() + f"\nwindow.{meta['ap_var']}={new_ap_json};\n"
    write_both(f"assets/js/{meta['geo']}", t)
    print(pack, "hubs", list(hubs_out), "airports", [a["code"] for a in airports])
    return data


def process_content(pack: str, meta: dict) -> str:
    raw = (PACK / pack / "content.html").read_text(encoding="utf-8")
    # Drop HTML comments (may contain Manager/internal notes)
    body = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    # Hide parks section entirely
    body = re.sub(
        r'<section id="parks">.*?</section>',
        "",
        body,
        count=1,
        flags=re.S,
    )
    # TODO → coming soon in visible copy
    body = todo_to_soon(body) if False else body  # apply per-text-node style below
    # Replace TODO paragraphs / inline TODOs carefully
    body = re.sub(
        r"<p>\s*TODO:?.*?</p>",
        "<p>Policy details coming soon.</p>",
        body,
        flags=re.S | re.I,
    )
    body = re.sub(
        r"<li>\s*TODO:?.*?</li>",
        "<li>Policy details coming soon.</li>",
        body,
        flags=re.S | re.I,
    )
    body = re.sub(r"\([^)]*TODO[^)]*\)", "(Policy details coming soon.)", body, flags=re.I)
    body = re.sub(r"TODO:?[^.<:]*\.", "Policy details coming soon. ", body, flags=re.I)
    body = re.sub(r"TODO:?[^<]*", "Policy details coming soon.", body, flags=re.I)
    # Uber fixed amount → price shown in the app
    body = re.sub(
        r"no fixed (?:£|euro|EUR|pound|amount)[^.<]*",
        "price shown in the app",
        body,
        flags=re.I,
    )
    body = re.sub(
        r"check the upfront price in the app[^.<]*",
        "price shown in the app",
        body,
        flags=re.I,
    )
    body = re.sub(
        r"extra may apply[^.<]*check(?: the)? app[^.<]*",
        "price shown in the app",
        body,
        flags=re.I,
    )
    # Insert Korea warn at top of entry section
    body = re.sub(
        r'(<section id="federal">\s*<h2>[^<]*</h2>)',
        r"\1\n" + KOREA_WARN,
        body,
        count=1,
    )
    if pack == "fr":
        # After Korea warn (or after first p following h2), add FAQ note once
        body = re.sub(
            r'(<section id="federal">\s*<h2>[^<]*</h2>\s*' + re.escape(KOREA_WARN) + r")",
            r"\1\n" + FR_FAQ_NOTE,
            body,
            count=1,
        )
    # Update UK hubs note about GLA/NCL now present
    body = body.replace(
        "The GOV.UK commercial list updated 9 November 2026 also names Glasgow and Newcastle — they are not yet separate map hubs (question for Marc).",
        "The GOV.UK commercial list updated 9 November 2026 also names Glasgow and Newcastle — both are on the UK map.",
    )
    # Scrub remaining internal words
    for bad in ("PPC Manager", "preview stub", "Checked Pending"):
        body = body.replace(bad, "")
    return body.strip()


def build_page(pack: str, meta: dict):
    canada = (ROOT / "site/countries/canada.html").read_text(encoding="utf-8")
    content = process_content(pack, meta)
    # Head: noindex + title/desc/canonical/og
    head = canada
    if "noindex" not in head:
        head = head.replace(
            '<meta name="viewport"',
            '<meta name="robots" content="noindex,nofollow">\n<meta name="viewport"',
            1,
        )
    # titles
    head = re.sub(r"<title>.*?</title>", f"<title>{meta['title']}</title>", head, count=1)
    head = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{meta["desc"]}">',
        head,
        count=1,
    )
    for prop in ("og:title", "twitter:title"):
        head = re.sub(
            rf'<meta (?:name|property)="{prop}" content="[^"]*">',
            f'<meta property="{prop}" content="{meta["title"]}">'
            if prop.startswith("og:")
            else f'<meta name="{prop}" content="{meta["title"]}">',
            head,
            count=1,
        )
    for prop in ("og:description", "twitter:description"):
        head = re.sub(
            rf'<meta (?:name|property)="{prop}" content="[^"]*">',
            f'<meta property="{prop}" content="{meta["desc"]}">'
            if prop.startswith("og:")
            else f'<meta name="{prop}" content="{meta["desc"]}">',
            head,
            count=1,
        )
    # canonical + urls
    slug = meta["file"]
    head = head.replace("countries/canada.html", f"countries/{slug}")
    head = head.replace("Canada pet travel rules", f"{meta['crumb']} pet travel rules")
    # Replace main
    main_new = f'<main class="wrap" id="main">\n{content}\n</main>'
    head = re.sub(r"<main class=\"wrap\" id=\"main\">.*?</main>", main_new, head, count=1, flags=re.S)
    # Preview bar after <body...>
    if "ppc-preview-bar" not in head:
        head = re.sub(r"(<body[^>]*>)", r"\1\n" + PREVIEW_BAR, head, count=1)
    write_both(f"countries/{slug}", head)


def patch_country_map_js():
    """breedBlock already patched; extend road/hotel for EU transport + non-CA hotel heading."""
    for rel in ("site/assets/js/country-map.js", "static/assets/js/country-map.js"):
        p = ROOT / rel
        t = p.read_text(encoding="utf-8")
        # roadSection: render train/bus for EU
        if "DATA.rail.train" not in t:
            needle = "  if(DATA.rail && DATA.rail.uber_pet){\n    s += `<h4>Rides</h4>"
            insert = (
                "  if(DATA.rail && DATA.rail.train){\n"
                "    s += `<h4>Train</h4><p>${esc(DATA.rail.train.rule)}</p>`;\n"
                "    if(DATA.rail.train.url) s += `<div class=\"links\">${lk('🚆','Official train pet rules','',DATA.rail.train.url,'off')}</div>`;\n"
                "  }\n"
                "  if(DATA.rail && DATA.rail.bus){\n"
                "    s += `<h4>Bus / coach</h4><p>${esc(DATA.rail.bus.rule)}</p>`;\n"
                "    if(DATA.rail.bus.url) s += `<div class=\"links\">${lk('🚌','Official bus pet rules','',DATA.rail.bus.url,'off')}</div>`;\n"
                "  }\n"
                "  if(DATA.rail && DATA.rail.uber_pet){\n"
                "    s += `<h4>Rides</h4>"
            )
            if needle not in t:
                raise SystemExit("road uber needle missing")
            t = t.replace(needle, insert, 1)
            # Fix Uber label to be country-neutral
            t = t.replace(
                "${lk('🚗','Uber Pet (Canada)','',DATA.rail.uber_pet.url,'off')}",
                "${lk('🚗','Uber Pet','',DATA.rail.uber_pet.url,'off')}",
            )
        # hotel heading
        t = t.replace(
            "<h4>Verified Canadian chains</h4>",
            "<h4>Hotel chains</h4>",
        )
        # breedBlock: already uses DATA.breed || DATA.breeds — ensure breeds path works (Manager uses breeds after convert)
        p.write_text(t, encoding="utf-8")
        print("patched", rel)


def patch_palettes():
    """Flag-gradient tones at USA-like brightness; DE black stays readable (charcoal, not #000)."""
    css_paths = [ROOT / "site/assets/css/country-map.css", ROOT / "static/assets/css/country-map.css"]
    # UK: #012169 / white / #C8102E
    uk = """html.accent-unionjack #country-map{--accent:#C8102E;--accent-ink:#f4f6fa}
html.accent-unionjack #country-map .st.st-t1{fill:#C8102E !important}
html.accent-unionjack #country-map .st.st-t2{fill:#e8e4dc !important}
html.accent-unionjack #country-map .st.st-t3{fill:#3a5f9a !important}
html.accent-unionjack #country-map .st.st-t4{fill:#a82a40 !important}
html.accent-unionjack #country-map .st.st-t5{fill:#012169 !important}
"""
    # FR: #0055A4 / white / #EF4135
    fr = """html.accent-tricolore #country-map{--accent:#0055A4;--accent-ink:#f4f6fa}
html.accent-tricolore #country-map .st.st-t1{fill:#0055A4 !important}
html.accent-tricolore #country-map .st.st-t2{fill:#e8e4dc !important}
html.accent-tricolore #country-map .st.st-t3{fill:#EF4135 !important}
html.accent-tricolore #country-map .st.st-t4{fill:#3a7ab8 !important}
html.accent-tricolore #country-map .st.st-t5{fill:#c45a5a !important}
"""
    # DE: charcoal (readable) / #DD0000 / #FFCE00 — never pure black fills
    de = """html.accent-schwarzrotgold #country-map{--accent:#DD0000;--accent-ink:#f4efe6}
html.accent-schwarzrotgold #country-map .st.st-t1{fill:#3a3a3a !important}
html.accent-schwarzrotgold #country-map .st.st-t2{fill:#DD0000 !important}
html.accent-schwarzrotgold #country-map .st.st-t3{fill:#FFCE00 !important}
html.accent-schwarzrotgold #country-map .st.st-t4{fill:#5a5a5a !important}
html.accent-schwarzrotgold #country-map .st.st-t5{fill:#c44a4a !important}
"""
    for p in css_paths:
        t = p.read_text(encoding="utf-8")
        t = re.sub(
            r"html\.accent-unionjack #country-map\{--accent:[^}]+\}.*?html\.accent-unionjack #country-map \.st\.st-t5\{[^}]+\}",
            uk.strip().replace("\n", "\n"),
            t,
            count=1,
            flags=re.S,
        )
        # More reliable line-by-line replace of st-t fills
        def repl_block(accent: str, fills: dict, accent_color: str, ink: str, text: str) -> str:
            text = re.sub(
                rf"html\.accent-{accent} #country-map\{{--accent:[^;]+;--accent-ink:[^}}]+\}}",
                f"html.accent-{accent} #country-map{{--accent:{accent_color};--accent-ink:{ink}}}",
                text,
                count=1,
            )
            for tone, color in fills.items():
                text = re.sub(
                    rf"(html\.accent-{accent} #country-map \.st\.{tone}\{{fill:)[^ !]+",
                    rf"\1{color}",
                    text,
                    count=1,
                )
            return text

        t = repl_block(
            "unionjack",
            {"st-t1": "#C8102E", "st-t2": "#e8e4dc", "st-t3": "#3a5f9a", "st-t4": "#a82a40", "st-t5": "#2450a0"},
            "#C8102E",
            "#f4f6fa",
            t,
        )
        # t5 was #012169 which is very dark — use #2450a0 for readability while keeping navy family
        t = repl_block(
            "tricolore",
            {"st-t1": "#0055A4", "st-t2": "#e8e4dc", "st-t3": "#EF4135", "st-t4": "#3a7ab8", "st-t5": "#c45a5a"},
            "#0055A4",
            "#f4f6fa",
            t,
        )
        t = repl_block(
            "schwarzrotgold",
            {"st-t1": "#3a3a3a", "st-t2": "#DD0000", "st-t3": "#FFCE00", "st-t4": "#5a5a5a", "st-t5": "#c44a4a"},
            "#DD0000",
            "#f4efe6",
            t,
        )
        # switcher dots
        t = t.replace(
            "#map-switch .msw-tab.accent-unionjack i{background:#c45a6a;",
            "#map-switch .msw-tab.accent-unionjack i{background:#C8102E;",
        )
        t = t.replace(
            "#map-switch .msw-tab.accent-tricolore i{background:#4a6fa5;",
            "#map-switch .msw-tab.accent-tricolore i{background:#0055A4;",
        )
        t = t.replace(
            "#map-switch .msw-tab.accent-schwarzrotgold i{background:#8a6e52;",
            "#map-switch .msw-tab.accent-schwarzrotgold i{background:#DD0000;",
        )
        p.write_text(t, encoding="utf-8")
        print("palette", p)


def patch_world_colors():
    """Same colour system as USA/CA/MX: signature fills + soft stroke. Flag-aligned."""
    for rel in ("site/assets/css/home-c.css", "static/assets/css/home-c.css"):
        p = ROOT / rel
        t = p.read_text(encoding="utf-8")
        # UK red (Union Jack), FR blue, DE gold-leaning red — match signature style of us/ca/mx
        repls = {
            ".legend .sw.cov-uk{background:#c45a6a;box-shadow:inset 0 0 0 1.5px #f4f6fa}":
                ".legend .sw.cov-uk{background:#C8102E;box-shadow:inset 0 0 0 1.5px #f4f6fa}",
            ".legend .sw.cov-fr{background:#4a6fa5}":
                ".legend .sw.cov-fr{background:#0055A4}",
            ".legend .sw.cov-de{background:#8a6e52;box-shadow:inset 0 0 0 1.5px #c4a574}":
                ".legend .sw.cov-de{background:#DD0000;box-shadow:inset 0 0 0 1.5px #FFCE00}",
            ".country.cov-uk{fill:#c45a6a;stroke:#f4f6fa;stroke-width:.55}.country.cov-uk:hover,.country.cov-uk:focus{fill:#d47280}":
                ".country.cov-uk{fill:#C8102E;stroke:#f4f6fa;stroke-width:.55}.country.cov-uk:hover,.country.cov-uk:focus{fill:#e02a48}",
            ".country.cov-fr{fill:#4a6fa5;stroke:#e8e4dc;stroke-width:.55}.country.cov-fr:hover,.country.cov-fr:focus{fill:#5d82b8}":
                ".country.cov-fr{fill:#0055A4;stroke:#e8e4dc;stroke-width:.55}.country.cov-fr:hover,.country.cov-fr:focus{fill:#1a6fbf}",
            ".country.cov-de{fill:#8a6e52;stroke:#c4a574;stroke-width:.6}.country.cov-de:hover,.country.cov-de:focus{fill:#9c7e60}":
                ".country.cov-de{fill:#DD0000;stroke:#FFCE00;stroke-width:.6}.country.cov-de:hover,.country.cov-de:focus{fill:#f01010}",
        }
        for a, b in repls.items():
            if a in t:
                t = t.replace(a, b)
            else:
                print("WARN world css miss", a[:60])
        p.write_text(t, encoding="utf-8")
        print("world css", rel)


def patch_map_pages_meta():
    """Point map intros at real country pages; refresh cache-bust; keep preview bar."""
    updates = {
        "uk-map.html": {
            "intro": "Pick a nation (England, Scotland, Wales, Northern Ireland). Open the <a href=\"uk.html\">UK pet-travel guide</a> for full entry rules. <a href=\"../?view=map\">World map</a> · <a href=\"../airlines/compare/\">Airline fees</a>.",
            "portal": "Open a nation for hub notes, airports (including Glasgow and Newcastle) and the journey steps.",
            "desc": "United Kingdom pet-travel map: England, Scotland, Wales and Northern Ireland with GOV.UK hubs.",
        },
        "france-map.html": {
            "intro": "Pick a metropolitan region (13). Overseas departments appear in the corner inset. Open the <a href=\"france.html\">France pet-travel guide</a> for full entry rules. <a href=\"../?view=map\">World map</a> · <a href=\"../airlines/compare/\">Airline fees</a>.",
            "portal": "Open a region for hub notes and the journey steps. Overseas: Guadeloupe, Martinique, French Guiana, Réunion, Mayotte.",
            "desc": "France pet-travel map: 13 metropolitan regions plus an overseas inset.",
        },
        "germany-map.html": {
            "intro": "Pick a Land (16 Länder). Open the <a href=\"germany.html\">Germany pet-travel guide</a> for full entry rules. <a href=\"../?view=map\">World map</a> · <a href=\"../airlines/compare/\">Airline fees</a>.",
            "portal": "Open a Land for hub notes and the journey steps.",
            "desc": "Germany pet-travel map: 16 Länder with EU entry hubs.",
        },
    }
    for fname, u in updates.items():
        for base in (ROOT / "site/countries", ROOT / "static/countries"):
            p = base / fname
            t = p.read_text(encoding="utf-8")
            t = re.sub(
                r'(<div class="intro">.*?<p>).*?(</p></div>)',
                r"\1" + u["intro"] + r"\2",
                t,
                count=1,
                flags=re.S,
            )
            t = re.sub(
                r'(<div class="portal"[^>]*>.*?<p>).*?(</p>)',
                r"\1" + u["portal"] + r"\2",
                t,
                count=1,
                flags=re.S,
            )
            t = re.sub(
                r'<meta name="description" content="[^"]*">',
                f'<meta name="description" content="{u["desc"]}">',
                t,
                count=1,
            )
            # cache bust
            t = t.replace("country-map.css?v=eu2", "country-map.css?v=eu3")
            t = t.replace("country-map.js?v=eu2", "country-map.js?v=eu3")
            t = re.sub(r"(\w+-map-data\.js)\?v=[^\"]+", r"\1?v=eu3", t)
            t = re.sub(r"(\w+-map-geo\.js)\?v=[^\"]+", r"\1?v=eu3", t)
            p.write_text(t, encoding="utf-8")
        print("map page", fname)


def patch_usa_france():
    for rel in ("site/routes/usa-france.html", "static/routes/usa-france.html"):
        p = ROOT / rel
        t = p.read_text(encoding="utf-8")
        n = t.count("F1839")
        t = t.replace(
            "https://www.service-public.gouv.fr/particuliers/vosdroits/F1839",
            "https://www.service-public.gouv.fr/particuliers/vosdroits/F35788",
        )
        p.write_text(t, encoding="utf-8")
        print("usa-france F1839→F35788", rel, "replacements", n)


def patch_index_guides():
    """GUIDES already have UK/FR/DE; refresh summaries to real content + keep label offsets."""
    for rel in ("site/index.html", "static/index.html"):
        p = ROOT / rel
        t = p.read_text(encoding="utf-8")
        m = re.search(r"var GUIDES=(\{.*?\})\s*;;var LIVE", t, re.S)
        if not m:
            m = re.search(r"var GUIDES=(\{.*?\});var LIVE", t, re.S)
        G = json.loads(m.group(1))
        G["826"].update(
            {
                "url": "https://petpolicycheck.com/countries/uk.html",
                "map_url": "countries/uk-map.html",
                "cta": "See UK pet travel rules",
                "map_cta": "Explore the UK nations map",
                "line": "GOV.UK / Defra entry rules, Dangerous Dogs Act, hubs including Glasgow & Newcastle",
                "summary": "Great Britain entry rules from GOV.UK (Defra / APHA): microchip before rabies, ≥21-day wait, tapeworm for dogs, GB health certificate from listed countries. Northern Ireland follows EU/DAERA rules. Checked 10 November 2026.",
                "option": "United Kingdom ★ guide",
                "label_left": True,
                "label_dx": -14,
                "label_dy": -12,
                "pin": [-3.2, 55.2],
            }
        )
        G["250"].update(
            {
                "url": "https://petpolicycheck.com/countries/france.html",
                "map_url": "countries/france-map.html",
                "cta": "See France pet travel rules",
                "map_cta": "Explore the France regions map",
                "line": "EU 2026 entry rules, catégorie 1–2 dogs, hubs and return to the US",
                "summary": "France follows EU pet-entry rules in force since 22 April 2026 (Regulations (EU) 2026/131, 2026/705, 2026/636). Catégorie 1 dogs: import and transit prohibited. Checked 10 November 2026.",
                "option": "France ★ guide",
                "label_left": True,
                "label_dx": -16,
                "label_dy": 18,
                "pin": [2.0, 46.2],
            }
        )
        G["276"].update(
            {
                "url": "https://petpolicycheck.com/countries/germany.html",
                "map_url": "countries/germany-map.html",
                "cta": "See Germany pet travel rules",
                "map_cta": "Explore the Germany Länder map",
                "line": "EU 2026 entry rules, HundVerbrEinfG breed import ban, hubs",
                "summary": "Germany follows EU pet-entry rules in force since 22 April 2026. Federal HundVerbrEinfG bans import of certain breeds (pit bull types and crosses). Checked 10 November 2026.",
                "option": "Germany ★ guide",
                "label_left": False,
                "label_dx": 16,
                "label_dy": -10,
                "pin": [11.2, 51.4],
            }
        )
        new = json.dumps(G, ensure_ascii=False)
        t = t[: m.start(1)] + new + t[m.end(1) :]
        p.write_text(t, encoding="utf-8")
        print("GUIDES", rel)


def collect_todos():
    todos = []
    for pack in ("uk", "fr", "de"):
        for name in ("content.html", "map-data.json"):
            text = (PACK / pack / name).read_text(encoding="utf-8")
            for i, line in enumerate(text.splitlines(), 1):
                if "TODO" in line:
                    todos.append(f"{pack}/{name}:{i}: {line.strip()[:140]}")
    return todos


def main():
    patch_country_map_js()
    for pack, meta in META.items():
        convert(pack, meta)
        build_page(pack, meta)
    patch_palettes()
    patch_world_colors()
    patch_map_pages_meta()
    patch_usa_france()
    patch_index_guides()
    todos = collect_todos()
    (ROOT / "qa/eu-maps/remaining-todos.txt").write_text("\n".join(todos) + "\n", encoding="utf-8")
    print("TODO count", len(todos))
    print("DONE")


if __name__ == "__main__":
    main()
