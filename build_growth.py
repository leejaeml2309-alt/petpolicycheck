"""Step B+C growth pages: route×airline SEO, tools hubs, veterans. Invoked from build.py."""
from __future__ import annotations
import json, html, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "site"
DATA = ROOT / "data"
LANGS = ["en", "fr", "es", "de", "ko", "ja"]
TODAY = "2026-11-07"

# Minimal UI chrome translations for route pages (shell uses ppc-i18n.js)
ROUTE_I18N = {
  "en": {"hub":"Pet travel routes by airline","cta_pass":"Open Pet Travel Passport","cta_fit":"Check carrier fit","cta_cmp":"Compare airline fees","cta_titer":"Titer countdown","faq_h":"FAQ","src":"Sources","fee":"Published cabin fee","dims":"Under-seat / cabin carrier","wt":"Weight notes","cargo":"Hold / cargo","svc":"Service animal note","entry":"Destination entry summary","disc":"Fees and dimensions are copied from each airline's official materials we verified. Rules change — re-check the airline and government page before you book. Not legal or veterinary advice."},
  "fr": {"hub":"Itinéraires animaliers par compagnie","cta_pass":"Ouvrir le Passeport voyage","cta_fit":"Vérifier le bag","cta_cmp":"Comparer les frais","cta_titer":"Compte à rebours titrage","faq_h":"FAQ","src":"Sources","fee":"Frais cabine publiés","dims":"Cage cabine / sous le siège","wt":"Poids","cargo":"Soute / cargo","svc":"Note animal d'assistance","entry":"Résumé d'entrée","disc":"Les frais et dimensions proviennent des pages officielles vérifiées. Les règles changent — revérifiez avant de réserver. Pas un conseil juridique ou vétérinaire."},
  "es": {"hub":"Rutas con mascota por aerolínea","cta_pass":"Abrir Pasaporte de viaje","cta_fit":"Comprobar transportín","cta_cmp":"Comparar tarifas","cta_titer":"Cuenta regresiva de título","faq_h":"FAQ","src":"Fuentes","fee":"Tarifa de cabina","dims":"Transportín bajo asiento","wt":"Peso","cargo":"Bodega / cargo","svc":"Nota animal de servicio","entry":"Resumen de entrada","disc":"Tarifas y medidas copiadas de fuentes oficiales verificadas. Las normas cambian — confirme antes de reservar. No es asesoramiento legal ni veterinario."},
  "de": {"hub":"Reiserouten mit Haustier nach Airline","cta_pass":"Pet Travel Passport öffnen","cta_fit":"Transporttasche prüfen","cta_cmp":"Gebühren vergleichen","cta_titer":"Titer-Countdown","faq_h":"FAQ","src":"Quellen","fee":"Kabinengebühr","dims":"Untersitz-Transportbox","wt":"Gewicht","cargo":"Frachtraum","svc":"Hinweis Assistenzhund","entry":"Einreise-Überblick","disc":"Gebühren und Maße stammen aus verifizierten offiziellen Quellen. Regeln ändern sich — vor Buchung erneut prüfen. Keine Rechts- oder Tierarztberatung."},
  "ko": {"hub":"항공사별 반려동물 노선 가이드","cta_pass":"여행 패스포트 열기","cta_fit":"이동장 맞는지 확인","cta_cmp":"항공 요금 비교","cta_titer":"항체가 카운트다운","faq_h":"자주 묻는 질문","src":"출처","fee":"기내 요금","dims":"좌석 밑 이동장","wt":"체중","cargo":"위탁/화물","svc":"보조견 안내","entry":"입국 요약","disc":"요금·치수는 검증한 공식 자료에서 가져왔어요. 규정은 바뀔 수 있으니 예약 전에 다시 확인하세요. 법률·수의 조언이 아니에요."},
  "ja": {"hub":"航空会社別ペット旅行ルート","cta_pass":"旅行パスポートを開く","cta_fit":"キャリア適合を確認","cta_cmp":"航空料金を比較","cta_titer":"抗体価カウントダウン","faq_h":"FAQ","src":"出典","fee":"機内料金","dims":"座席下キャリア","wt":"体重","cargo":"預け入れ/貨物","svc":"補助犬メモ","entry":"入国概要","disc":"料金・寸法は検証した公式資料から転記しています。規則は変わるため、予約前に再確認してください。法律・獣医の助言ではありません。"},
}

def e(s):
  return html.escape(str(s if s is not None else ""), quote=True)

def load_airlines():
  out = {}
  for p in (DATA / "airlines").glob("*.json"):
    out[p.stem] = json.loads(p.read_text())
  return out

def dims_summary(a):
  dims = a.get("max_carrier_dimensions")
  if not dims:
    return "See official airline pet page (dimensions not in our verified snapshot)."
  if isinstance(dims, (dict, list)):
    return json.dumps(dims, ensure_ascii=False)[:280]
  return str(dims)

def fee_summary(a):
  fees = a.get("fees")
  if not fees:
    return "Check airline (no structured fee in our verified snapshot)."
  if isinstance(fees, list):
    bits = []
    for f in fees[:4]:
      if isinstance(f, dict):
        lab=f.get("label") or f.get("route") or f.get("name") or ""
        amt=f.get("amount") or f.get("fee") or ""
        bits.append((lab+(": "+str(amt) if amt else "")).strip(": ") or str(f))
      else:
        bits.append(str(f))
    return " · ".join(bits) if bits else str(fees)
  return str(fees)

def page_shell(cfg, title, desc, body, path, root, jsonld=None, hreflang=None, ads=True):
  """Thin wrapper importing build.page to avoid circular import issues at module load."""
  import build as B
  return B.page(cfg, title, desc, body, path, root, jsonld=jsonld, ads=ads)

def hreflang_links(base, slug, lang, localized=True):
  # EN canonical at /routes/{slug}.html; localized at /routes/{lang}/{slug}.html
  # localized=False: only x-default + en (no /routes/{lang}/ page is generated for this slug,
  # so emitting those alternates would point to 404s — content-fixes 2026-11-07).
  links = []
  links.append(f'<link rel="alternate" hreflang="x-default" href="{base}/routes/{slug}.html">')
  links.append(f'<link rel="alternate" hreflang="en" href="{base}/routes/{slug}.html">')
  for L in (LANGS if localized else ()):
    if L == "en":
      continue
    links.append(f'<link rel="alternate" hreflang="{L}" href="{base}/routes/{L}/{slug}.html">')
  return "\n".join(links)

def faq_ld(slug, from_n, to_n, airline_name, entry, dims, fee):
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {"@type": "Question", "name": f"Can I fly {from_n} to {to_n} with a pet on {airline_name}?",
       "acceptedAnswer": {"@type": "Answer", "text": f"Cabin/cargo rules and fees for {airline_name} are summarized from the airline's official materials we verified. Under-seat note: {dims}. Fee snapshot: {fee}. Always re-check before booking."}},
      {"@type": "Question", "name": f"What entry rules apply for pets arriving in {to_n} from {from_n}?",
       "acceptedAnswer": {"@type": "Answer", "text": entry}},
      {"@type": "Question", "name": "Where can I build a dated checklist for this corridor?",
       "acceptedAnswer": {"@type": "Answer", "text": "Use the PetPolicyCheck Pet Travel Passport and titer countdown tools, then confirm on the official government and airline pages."}},
    ],
  }

def render_route_body(pair, airline, ui, root, lang="en"):
  name = airline.get("name") or pair["airline"]
  dims = dims_summary(airline)
  wt = airline.get("max_combined_weight") or "See official airline page (weight not in verified snapshot)"
  cargo = airline.get("checked_or_cargo") or "See airline page"
  if isinstance(cargo, (dict, list)):
    cargo = json.dumps(cargo, ensure_ascii=False)[:280]
  svc = airline.get("service_animal_note") or "See airline accessibility page"
  fee = fee_summary(airline)
  official = airline.get("official_url") or "#"
  verified = airline.get("last_verified") or airline.get("last_checked") or TODAY
  from_n, to_n = pair["from"], pair["to"]
  return f"""
<section class="wrap" style="padding:18px 0 40px;max-width:920px;margin:0 auto">
<p class="eyebrow" style="color:var(--gold,#d9b765);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase">{e(from_n)} → {e(to_n)} · {e(name)}</p>
<h1 style="font-family:var(--disp,Marcellus,serif);font-weight:400;color:var(--head,#f5efe0);margin:0 0 10px">Flying a pet {e(from_n)} to {e(to_n)} on {e(name)}</h1>
<p class="sub" style="color:var(--mut,#a9b3a4);max-width:65ch">Verified snapshot for corridor planning. Cabin/cargo numbers from our airline dataset (checked {e(verified)}). Destination summary cites {e(pair.get('auth'))}.</p>
<div class="grid" style="display:grid;gap:12px;margin:18px 0">
  <div class="card" style="border:1px solid rgba(217,183,101,.25);border-radius:14px;padding:14px 16px;background:rgba(11,23,25,.45)">
    <h2 style="margin:0 0 8px;font-size:1.05rem;color:var(--gold,#d9b765)">{e(ui['entry'])}</h2>
    <p style="margin:0;color:#e8e0d0;line-height:1.5">{e(pair['entry'])}</p>
  </div>
  <div class="card" style="border:1px solid rgba(217,183,101,.25);border-radius:14px;padding:14px 16px;background:rgba(11,23,25,.45)">
    <h2 style="margin:0 0 8px;font-size:1.05rem;color:var(--gold,#d9b765)">{e(name)}</h2>
    <ul style="margin:0;padding-left:1.1rem;color:#e8e0d0;line-height:1.55">
      <li><b>{e(ui['fee'])}:</b> {e(fee)}</li>
      <li><b>{e(ui['dims'])}:</b> {e(dims)}</li>
      <li><b>{e(ui['wt'])}:</b> {e(wt)}</li>
      <li><b>{e(ui['cargo'])}:</b> {e(str(cargo)[:320])}</li>
      <li><b>{e(ui['svc'])}:</b> {e(str(svc)[:320])}</li>
      <li><b>{e(ui['src'])}:</b> <a href="{e(official)}" rel="noopener" target="_blank">Official airline page ↗</a> · verified {e(verified)}</li>
    </ul>
  </div>
</div>
<p style="display:flex;flex-wrap:wrap;gap:10px;margin:18px 0">
  <a class="btn" href="{root}passport/?from={e(pair['from_code'])}&to={e(pair['to_code'])}&lang={lang}">{e(ui['cta_pass'])}</a>
  <a class="btn ghost" href="{root}fit/?airline={e(pair['airline'])}&lang={lang}">{e(ui['cta_fit'])}</a>
  <a class="btn ghost" href="{root}airlines/compare/?lang={lang}">{e(ui['cta_cmp'])}</a>
  <a class="btn ghost" href="{root}titer-calculator/?dest={e(pair['to_code'])}&lang={lang}">{e(ui['cta_titer'])}</a>
</p>
<section>
  <h2 style="font-family:var(--disp,Marcellus,serif);font-weight:400">{e(ui['faq_h'])}</h2>
  <details style="margin:8px 0;padding:10px 12px;border:1px solid rgba(217,183,101,.2);border-radius:10px"><summary>Cabin vs cargo on {e(name)}?</summary><p>Use the dimensions and weight notes above, then confirm on the airline page. Soft-sided carriers often get more under-seat flex when the airline documents it.</p></details>
  <details style="margin:8px 0;padding:10px 12px;border:1px solid rgba(217,183,101,.2);border-radius:10px"><summary>Government paperwork for {e(to_n)}?</summary><p>{e(pair['entry'])}</p></details>
  <details style="margin:8px 0;padding:10px 12px;border:1px solid rgba(217,183,101,.2);border-radius:10px"><summary>Military PCS or service dog?</summary><p>See <a href="{root}military-pcs/">Military PCS</a> and <a href="{root}veterans/">Veterans hub</a> for DOT / CTA / JTR notes.</p></details>
</section>
<p class="disc" style="margin-top:22px;color:var(--mut,#a9b3a4);font-size:.9rem">{e(ui['disc'])}</p>
<p><a href="{root}routes/">{e(ui['hub'])} →</a></p>
</section>
"""

def build_routes(cfg):
  import build as B
  base = B.site_base(cfg)
  airlines = load_airlines()
  pairs = json.loads((DATA / "routes" / "meta" / "corridor_airline_pairs.json").read_text())["pairs"]
  urls = []
  (OUT / "routes").mkdir(parents=True, exist_ok=True)
  for L in LANGS:
    if L != "en":
      (OUT / "routes" / L).mkdir(parents=True, exist_ok=True)

  # Hub
  cards = []
  for pair in pairs:
    a = airlines.get(pair["airline"])
    if not a:
      continue
    slug = f"{pair['id']}-{pair['airline']}"
    cards.append(f'<li><a href="{slug}.html"><b>{e(pair["from"])} → {e(pair["to"])}</b> · {e(a.get("name"))}</a></li>')
  hub_body = f"""
<section class="wrap" style="padding:18px 0 40px;max-width:920px;margin:0 auto">
<p class="eyebrow" style="color:var(--gold,#d9b765);letter-spacing:.08em;text-transform:uppercase">Routes · Airlines</p>
<h1 style="font-family:var(--disp,Marcellus,serif);font-weight:400">Pet travel routes by airline</h1>
<p class="sub" style="color:var(--mut,#a9b3a4);max-width:65ch">Static corridor × airline guides built from our verified airline JSON and government entry summaries. Open Passport, Fit Check, or the fee comparator for the interactive tools.</p>
<ul style="line-height:1.7">{''.join(cards)}</ul>
<p style="display:flex;flex-wrap:wrap;gap:10px;margin-top:18px">
  <a class="btn" href="../passport/">Pet Travel Passport</a>
  <a class="btn ghost" href="../fit/">Under-seat fit</a>
  <a class="btn ghost" href="../titer-calculator/">Titer countdown</a>
  <a class="btn ghost" href="../airlines/compare/">Fee comparator</a>
</p>
</section>"""
  (OUT / "routes" / "index.html").write_text(
    B.page(cfg, f"Pet travel routes by airline | {cfg['site_name']}",
           "Corridor × airline pet travel guides with verified cabin dimensions, fees, and entry summaries.",
           hub_body, "routes/index.html", "../",
           jsonld=[B.bc_ld(cfg, [("Home", ""), ("Routes", "routes/")])]))
  urls.append((f"{base}/routes/", TODAY))

  # Flagship localized: first pair per corridor (up to 12) get 6-lang variants; all pairs get EN
  flagship_ids = []
  seen = set()
  for pair in pairs:
    if pair["id"] not in seen:
      seen.add(pair["id"])
      flagship_ids.append(f"{pair['id']}-{pair['airline']}")

  for pair in pairs:
    a = airlines.get(pair["airline"])
    if not a:
      continue
    slug = f"{pair['id']}-{pair['airline']}"
    # EN
    ui = ROUTE_I18N["en"]
    body = render_route_body(pair, a, ui, "../")
    title = f"Pet on {a.get('name')}: {pair['from']} to {pair['to']} | {cfg['site_name']}"
    desc = f"Verified cabin/cargo notes for {a.get('name')} on {pair['from']}→{pair['to']}, plus {pair.get('auth')} entry summary."
    html_page = B.page(cfg, title, desc, body, f"routes/{slug}.html", "../",
                       jsonld=[faq_ld(slug, pair["from"], pair["to"], a.get("name"), pair["entry"], dims_summary(a), fee_summary(a)),
                               B.bc_ld(cfg, [("Home", ""), ("Routes", "routes/"), (f"{pair['from']}→{pair['to']}", f"routes/{slug}.html")])])
    # inject hreflang before </head>
    hl = hreflang_links(base, slug, "en", localized=slug in flagship_ids)
    html_page = html_page.replace("</head>", hl + "\n</head>", 1)
    (OUT / "routes" / f"{slug}.html").write_text(html_page)
    urls.append((f"{base}/routes/{slug}.html", TODAY))

    if slug in flagship_ids:
      for L in LANGS:
        if L == "en":
          continue
        uiL = ROUTE_I18N[L]
        bodyL = render_route_body(pair, a, uiL, "../../", L)
        pageL = B.page(cfg, title, desc, bodyL, f"routes/{L}/{slug}.html", "../../",
                       jsonld=[faq_ld(slug, pair["from"], pair["to"], a.get("name"), pair["entry"], dims_summary(a), fee_summary(a))])
        pageL = pageL.replace("</head>", hreflang_links(base, slug, L) + "\n</head>", 1)
        pageL = pageL.replace('<html lang="en-US">', f'<html lang="{L}">', 1)
        (OUT / "routes" / L / f"{slug}.html").write_text(pageL)
        urls.append((f"{base}/routes/{L}/{slug}.html", TODAY))

  return urls

def copy_static_dir(name: str):
  src = ROOT / "static" / name
  dst = OUT / name
  if not src.exists():
    return
  import shutil
  if dst.exists():
    shutil.rmtree(dst)
  shutil.copytree(src, dst)

def growth_tool_urls(base):
  paths = [
    "titer-calculator/", "fit/", "widgets/", "military-pcs/", "flight-volunteer/", "veterans/",
  ]
  return [(f"{base}/{p}", TODAY) for p in paths]


def inject_discovery():
  """Add discovery cards into generated hub pages after the main build writes them."""
  block_tpl = """
<section class="blk wrap no-print" id="ppc-growth-discover" style="padding:18px 0 8px">
<h2 style="font-family:var(--disp,Marcellus,serif);font-weight:400;margin:0 0 8px">More planning tools</h2>
<p class="sub" style="margin:0 0 10px;color:var(--mut,#a9b3a4)">Routes, under-seat fit, titer countdown, military PCS, flight-volunteer kit, and veterans hub.</p>
<p style="display:flex;flex-wrap:wrap;gap:8px;margin:0">
<a class="btn ghost" href="{root}routes/">Routes</a>
<a class="btn ghost" href="{root}fit/">Fit check</a>
<a class="btn ghost" href="{root}titer-calculator/">Titer</a>
<a class="btn ghost" href="{root}military-pcs/">Military PCS</a>
<a class="btn ghost" href="{root}flight-volunteer/">Flight volunteer</a>
<a class="btn ghost" href="{root}veterans/">Veterans</a>
<a class="btn ghost" href="{root}widgets/">Widgets</a>
</p>
</section>
"""
  targets = [
    (OUT / "passport" / "index.html", "../"),
    (OUT / "book" / "index.html", "../"),
    (OUT / "airlines" / "compare" / "index.html", "../../"),
  ]
  for path, root in targets:
    if not path.exists():
      continue
    txt = path.read_text()
    if "ppc-growth-discover" in txt:
      continue
    block = block_tpl.format(root=root)
    if "</main>" in txt:
      txt = txt.replace("</main>", block + "\n</main>", 1)
    elif "<footer" in txt:
      txt = txt.replace("<footer", block + "\n<footer", 1)
    else:
      continue
    path.write_text(txt)

def build_all(cfg):
  """Generate routes + copy static growth hubs. Returns sitemap url tuples."""
  urls = []
  urls += build_routes(cfg)
  for name in ["titer-calculator", "fit", "widgets", "military-pcs", "flight-volunteer", "veterans"]:
    copy_static_dir(name)
  import build as B
  base = B.site_base(cfg)
  urls += growth_tool_urls(base)
  # embed script path
  emb = ROOT / "static" / "assets" / "js" / "embed-policy.js"
  if emb.exists():
    (OUT / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (OUT / "assets" / "js" / "embed-policy.js").write_text(emb.read_text())
  inject_discovery()
  return urls

if __name__ == "__main__":
  import build as B
  cfg = B.load_config()
  B.OUT.mkdir(exist_ok=True)
  print(build_all(cfg)[:5], "...")
