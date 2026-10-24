#!/usr/bin/env python3
"""Free 'Pet Travel Checklist USA' PDF (US Letter, 2 pages) -> static/downloads/.

Every fact below is copied from the site's own data (data/countries/usa.json, data/airlines/*.json,
data/cabin_limits.json, data/hotels/us-chains.json, data/routes/*.json, products.json guides).
No affiliate links; links carry only a plain utm_source/utm_medium/utm_campaign.
Needs headless Google Chrome.  Usage:  python3 checklist/make_checklist_pdf.py [--light]
Also writes static/assets/img/checklist-thumb.webp (page-1 thumbnail for /pet-travel-checklist/) if pdftoppm + Pillow exist.
"""
import subprocess, sys, tempfile, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIGHT = "--light" in sys.argv
OUT = ROOT / "static" / "downloads" / ("pet-travel-checklist-usa-print.pdf" if LIGHT else "pet-travel-checklist-usa.pdf")
BASE = "https://petpolicycheck.com"
UTM = "utm_source=checklist_pdf&utm_medium=pdf&utm_campaign=pet_travel_checklist_usa"


def u(path, frag=""):
    return f"{BASE}/{path}?{UTM}" + (f"#{frag}" if frag else "")


def link(path, text, frag=""):
    return f'<a href="{u(path, frag)}">{text}</a>'


def more(path, label, frag=""):
    shown = f"petpolicycheck.com/{path}" + (f"#{frag}" if frag else "")
    return f'<p class="more">{label}: <a href="{u(path, frag)}">{shown}</a></p>'


def ul(items):
    return "<ul class='cb'>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


F = (ROOT / "static" / "assets" / "fonts").as_uri()
LOGO = (ROOT / "static" / "assets" / "img" / "logo-mark.png").as_uri()

docs = ul([
    "<b>Vet health certificate.</b> Airlines may require a health and acclimation certificate signed by a licensed vet <b>within 10 days of travel</b> (USDA APHIS).",
    "<b>Leaving the US?</b> The destination country sets the rules. A USDA-accredited vet prepares the health certificate and submits it to <b>USDA APHIS for endorsement</b> (VEHCS). Follow the destination&rsquo;s timing.",
    "<b>Rabies vaccination certificate.</b> Some states and countries require one; each state&rsquo;s rule is in our " + link("countries/usa.html", "state table", "states") + ".",
    "<b>Microchip.</b> Dogs entering the US need one readable by a universal scanner; Japan and South Korea require an <b>ISO</b> microchip.",
    "<b>CDC Dog Import Form receipt</b> (free) for every dog entering the US, including US dogs coming home. The dog must look healthy, be at least 6 months old and be microchipped. Dogs from CDC high-risk rabies countries need extra forms.",
    "<b>Cats entering the US:</b> no federal proof of rabies vaccination (recommended); state and airline rules still apply.",
    "<b>Destination extras</b> (pointers only, read the guide): "
    + link("countries/usa.html", "Hawaii", "st-hi") + " (two rabies shots + passing OIE-FAVN test to avoid quarantine of up to 120 days) &middot; "
    + link("routes/usa-to-japan.html", "Japan") + " (rabies titer, 180-day wait, notice 40+ days ahead) &middot; "
    + link("routes/usa-to-south-korea.html", "South Korea") + " (FAVN titer, blood drawn within 24 months) &middot; "
    + link("countries/usa.html", "Guam", "territories") + ".",
])

fly = ul([
    "<b>Cabin or hold depends on the airline.</b> Cabin only: JetBlue, Southwest. Baggage compartment/hold option: Alaska, Hawaiian, Air Canada; Air France and Lufthansa over 8 kg. "
    "American, Delta, United: no checked pets for the general public (cargo only for active-duty US military / State Department on orders). British Airways: no pets in the cabin.",
    "<b>Carrier must fit under the seat in front of you.</b> A common limit is about <b>18 x 11 x 11 in</b> (American soft-sided, Delta recommended); Alaska and Hawaiian 17 x 11 x 9.5 in; JetBlue 17 x 12.5 x 8.5 in; United soft-sided 11 x 18 x 11 in (max 10 in tall on the 737 MAX). Not stated? <b>Check your airline.</b>",
    "<b>Weight limit:</b> many airlines state none for the cabin; Air France and Lufthansa allow 8 kg pet + carrier. Otherwise, <b>check your airline</b>.",
    "<b>Reserve your pet&rsquo;s spot with the airline</b> before you buy the ticket: pet space is limited per flight. Check fees and breed or route restrictions on our airline page.",
    "<b>Security:</b> you may be asked to take your pet out of the carrier at screening; a carrier tether helps.",
])
fly_more = (f'<p class="more">Airline pages: {link("airlines/american.html","American")} &middot; {link("airlines/delta.html","Delta")} &middot; '
            f'{link("airlines/united.html","United")} &middot; {link("airlines/alaska.html","Alaska")} &middot; {link("airlines/southwest.html","Southwest")} &middot; '
            f'{link("airlines/jetblue.html","JetBlue")} &middot; {link("airlines/hawaiian.html","Hawaiian")}</p>'
            + more("products/under-seat-carrier-size-by-airline.html", "Carrier size by airline"))

train = ul([
    "<b>Dogs and cats only</b>, at least 8 weeks old, vaccinations current; one pet per passenger.",
    "<b>20 lb max</b>, pet + carrier combined. Leak-proof, ventilated carrier, max 19 x 14 x 10.5 in, under your seat (counts as a carry-on).",
    "<b>Trips up to 7 hours</b> including connections. Coach and Acela Business only.",
    "<b>Reserve</b> your pet&rsquo;s spot (fee varies by route), sign the Pet Release online and <b>check in 45 minutes</b> before departure at staffed stations.",
    "No pets on Auto Train or to Canada on the Adirondack, Maple Leaf and Amtrak Cascades.",
])

hotels = ul([
    "<b>Confirm the pet policy directly with the hotel</b> (call or message) before you book: fees, weight limits and number of pets are set by each brand and often by each hotel.",
    "<b>Check the weight limit</b> (per pet or combined) and how many pets are allowed per room.",
    "<b>Check the pet fee</b> (per night or per stay) and any deposit.",
    "<b>Declare your pet at check-in</b>; some chains do not allow pets left alone in the room.",
])

dep = ul([
    "Ask your vet when to <b>feed</b> before the trip; pack the pet&rsquo;s usual food for the whole trip, plus a little extra.",
    "Water and a travel bowl.",
    "Collar or harness with <b>ID tags</b>; microchip details up to date.",
    "<b>Leash</b> and harness.",
    "<b>Absorbent pad</b> (puppy pad) or towel to line the carrier.",
    "Poop bags, or travel litter for cats.",
    "Medications and your vet&rsquo;s phone number.",
    "<b>Copies of documents</b> (paper + phone): health certificate, rabies certificate, CDC receipt, bookings.",
    "Something that smells like home in the carrier.",
    "<b>Arrive early</b>: Amtrak check-in is 45 minutes before departure; for flights, <b>check your airline</b>.",
])

CSS = f"""
@font-face{{font-family:Marcellus;src:url({F}/marcellus-latin.woff2) format('woff2')}}
@font-face{{font-family:Inter;src:url({F}/inter-var-latin.woff2) format('woff2');font-weight:100 900}}
@page{{size:Letter;margin:0}}
*{{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
html,body{{margin:0}}
body{{--bg:#0b1719;--card:#11252a;--head:#f5ecd6;--ink:#ece4d0;--mut:#c9c2ae;--gold:#d9b765;--line:#2b4146;--link:#e3c27a;
 font:9.4pt/1.42 Inter,sans-serif;color:var(--ink);background:var(--bg)}}
body.light{{--bg:#ffffff;--card:#fbf7ee;--head:#0b1719;--ink:#1d2a2c;--mut:#4a5557;--gold:#8a6a1f;--line:#d9cfb8;--link:#7a5a12}}
.pg{{width:8.5in;height:11in;padding:.5in .55in .45in;position:relative;overflow:hidden;page-break-after:always;background:var(--bg)}}
.pg:last-child{{page-break-after:auto}}
.hd{{display:flex;align-items:center;gap:12px;border-bottom:1.5px solid var(--gold);padding-bottom:10px;margin-bottom:12px}}
.badge{{width:58px;height:44px;border-radius:11px;background:#fdf8ef;box-shadow:0 0 0 1.5px #d9b765;display:flex;align-items:center;justify-content:center;flex:none}}
.badge img{{width:50px}}
.wm{{font-family:Marcellus,serif;font-size:17pt;color:var(--head)}}.wm span{{color:var(--gold)}}
.hd .r{{margin-left:auto;text-align:right;font-size:8.2pt;color:var(--mut)}}
h1{{font-family:Marcellus,serif;font-weight:400;color:var(--head);font-size:25pt;line-height:1.1;margin:0 0 4px}}
.lead{{margin:0 0 12px;color:var(--ink);font-size:10pt}}
h2{{font-family:Marcellus,serif;font-weight:400;color:var(--head);font-size:13.5pt;margin:0 0 5px;display:flex;align-items:baseline;gap:8px}}
h2 .n{{color:var(--gold);font-size:11pt}}
h2 a{{color:inherit;text-decoration:none}}
.sec{{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:8px;padding:9px 13px 8px;margin:0 0 10px;break-inside:avoid}}
ul.cb{{list-style:none;margin:0;padding:0}}
ul.cb li{{position:relative;padding-left:20px;margin:0 0 4px}}
ul.cb li:before{{content:"";position:absolute;left:0;top:2px;width:10px;height:10px;border:1.4px solid var(--gold);border-radius:2px}}
b{{color:var(--head);font-weight:650}}
a{{color:var(--link);text-decoration:underline;text-decoration-thickness:.6px;text-underline-offset:1.5px}}
.more{{margin:3px 0 0;font-size:8.4pt;color:var(--mut)}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.ft{{position:absolute;left:.55in;right:.55in;bottom:.35in;border-top:1px solid var(--line);padding-top:7px;font-size:7.9pt;color:var(--mut);display:flex;justify-content:space-between;gap:12px}}
.ft b{{color:var(--gold)}}
.note{{font-size:8.6pt;color:var(--mut);margin:6px 0 0}}
"""

head = (f'<div class="hd"><div class="badge"><img src="{LOGO}" alt=""></div><div class="wm">PetPolicy<span>Check</span></div>'
        f'<div class="r">Free to print and share<br><a href="{u("pet-travel-checklist/")}">petpolicycheck.com</a></div></div>')
foot = lambda n: (f'<div class="ft"><span><b>Last checked: Oct 2026.</b> Rules change; always confirm with the airline and official sources. '
                  f'Not legal or veterinary advice.</span><span>{n} / 2</span></div>')

HTML = f"""<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>Pet Travel Checklist USA | PetPolicyCheck</title><style>{CSS}</style></head>
<body class="{'light' if LIGHT else ''}">
<section class="pg">{head}
<h1>Pet Travel Checklist: USA</h1>
<p class="lead">Flying, taking the train or staying in a hotel with your dog or cat. Tick each box; every rule links to the page where we cite the official source.</p>
<div class="sec"><h2><span class="n">1</span><a href="{u('countries/usa.html','federal')}">Documents</a></h2>{docs}{more("countries/usa.html", "US federal and state rules", "federal")}</div>
<div class="sec"><h2><span class="n">2</span><a href="{u('products/under-seat-carrier-size-by-airline.html')}">Flying: cabin or hold, and carrier size</a></h2>{fly}{fly_more}</div>
{foot(1)}</section>
<section class="pg">{head}
<div class="sec"><h2><span class="n">3</span><a href="{u('countries/usa.html','train')}">Train: Amtrak</a></h2>{train}{more("countries/usa.html", "Amtrak pet rules and source", "train")}</div>
<div class="sec"><h2><span class="n">4</span><a href="{u('hotels/')}">Hotels</a></h2>{hotels}{more("hotels/", "Pet policies of US hotel chains", "chains")}</div>
<div class="sec"><h2><span class="n">5</span><a href="{u('products/cat-travel-checklist.html')}">Departure day</a></h2>{dep}
<p class="more">Packing lists: {link("products/cat-travel-checklist.html","Cat travel checklist")} &middot; {link("products/dog-road-trip-packing-list.html","Dog road-trip packing list")} &middot; {link("book/","Plan the whole trip")}</p></div>
<p class="note">Service animals follow separate rules; see each airline page and Amtrak&rsquo;s rules. Destination rules (Hawaii, Japan, South Korea and others) can take months to meet; start early.</p>
{foot(2)}</section>
</body></html>"""

tmp = Path(tempfile.mkdtemp())
src = tmp / "checklist.html"
src.write_text(HTML)
OUT.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files",
                "--no-pdf-header-footer", f"--print-to-pdf={OUT}", src.as_uri()], check=True, capture_output=True)
print(OUT, OUT.stat().st_size, "bytes")
if not LIGHT and shutil.which("pdftoppm"):
    from PIL import Image
    subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-r", "60", "-png", str(OUT), str(tmp / "t")], check=True)
    im = Image.open(next(tmp.glob("t*.png"))).convert("RGB")
    im.thumbnail((480, 640))
    im.save(ROOT / "static" / "assets" / "img" / "checklist-thumb.webp", "WEBP", quality=82)
    print("thumb", im.size)
