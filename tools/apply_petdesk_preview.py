#!/usr/bin/env python3
"""Apply Pet Desk trial clauses + For pros banner. Preview only."""
from __future__ import annotations
import pathlib, re, shutil

ROOT = pathlib.Path('/workspace/petdesk-preview-20261110')
SITE = ROOT / 'site'
STATIC = ROOT / 'static'

PREVIEW_BAR = (
    '<div class="ppc-preview-bar" role="status" style="position:sticky;top:0;z-index:9999;'
    'background:#7a1f1f;color:#fff;font:600 13px/1.35 Inter,system-ui,sans-serif;'
    'padding:8px 12px;text-align:center">'
    'LOCAL PREVIEW ONLY — Pet Desk trial + For pros banner · await Marc « publie »</div>\n'
)

BANNER_SNIPPET = (SITE / 'assets/includes/ppc-pro-banner.html').read_text()
CSS_LINK_REL = '<link rel="stylesheet" href="../assets/css/ppc-pro-banner.css?v=20261110petdesk">'
CSS_LINK_ROOT = '<link rel="stylesheet" href="assets/css/ppc-pro-banner.css?v=20261110petdesk">'

touched: list[str] = []
gaps: list[str] = []


def mark(path: pathlib.Path):
    rel = str(path.relative_to(SITE))
    if rel not in touched:
        touched.append(rel)


def ensure_preview_bar(html: str) -> str:
    if 'ppc-preview-bar' in html:
        return html
    # after <body ...>
    m = re.search(r'(<body[^>]*>)', html, re.I)
    if not m:
        return html
    return html[: m.end()] + '\n' + PREVIEW_BAR + html[m.end() :]


def ensure_css_link(html: str, link: str) -> str:
    if 'ppc-pro-banner.css' in html:
        return html
    # before </head>
    return html.replace('</head>', link + '\n</head>', 1)


def banner_html(pro_href: str) -> str:
    return BANNER_SNIPPET.replace('__PRO_HREF__', pro_href)


# --- Terms ---
TERMS_INSERT = r'''
<h2 id="trial">14-day free trial</h2>
<p>The Pet Desk trial is free for 14 days. No card is required and there is no commitment to subscribe. Starting a trial does not create a paid subscription or authorize any payment.</p>
<p>The trial does not automatically convert to a paid subscription. There is no charge when the trial ends, and you do not need to cancel the trial to avoid a charge. If you want to subscribe, you must explicitly choose a paid plan and confirm your purchase through Paddle, our Merchant of Record. No payment will be taken without that choice and confirmation.</p>

<h2 id="paid-sub">Optional paid subscription</h2>
<p>Published prices:</p>
<div class="tablewrap"><table>
<thead><tr><th>Plan</th><th>Monthly billing (USD)</th><th>Annual billing (USD)</th></tr></thead>
<tbody>
<tr><td>Starter · Advisor</td><td>$49 per month</td><td>$468 per year, paid annually</td></tr>
<tr><td>Pro · Pet Desk Agency</td><td>$149 per month</td><td>$1,428 per year, paid annually</td></tr>
<tr><td>Enterprise · Corporate HR &amp; Global Mobility</td><td>$399 per month</td><td>$3,828 per year, paid annually</td></tr>
</tbody>
</table></div>
<p>Annual subscriptions are billed as the full annual total, not as monthly installments. Applicable taxes and the total payable are shown at Paddle checkout before you confirm a paid purchase.</p>
<p>Only a paid subscription that you choose and confirm renews automatically each selected monthly or annual billing period until cancelled. You may cancel before the next renewal; access continues through the end of the paid period.</p>
<p>The free trial and the 14-day refund guarantee are separate. The guarantee applies to an initial paid subscription purchase, monthly or annual. Its 14-calendar-day period starts on the paid purchase date, not the trial start date. See the <a href="refund-policy.html">Refund &amp; Cancellation Policy</a>. Nothing in these Terms limits rights that cannot be waived under applicable mandatory law.</p>

'''

def patch_terms():
    p = SITE / 'terms.html'
    t = p.read_text()
    if 'id="trial"' in t:
        print('terms: already patched')
        return
    # update dates
    t = t.replace(
        'Effective date: November 6, 2026 &middot; Last updated: November 6, 2026',
        'Effective date: November 6, 2026 &middot; Last updated: November 10, 2026',
    )
    # insert after Paddle section (before seats)
    anchor = '<h2 id="seats">4. Account Seats &amp; Acceptable Use</h2>'
    if anchor not in t:
        raise SystemExit('terms: seats anchor missing')
    t = t.replace(anchor, TERMS_INSERT + anchor)
    # renumber 4..9 -> 6..11
    renumbers = [
        ('id="seats">4. Account Seats', 'id="seats">6. Account Seats'),
        ('id="cancel">5. Cancellation', 'id="cancel">7. Cancellation'),
        ('id="disclaimer">6. Regulatory', 'id="disclaimer">8. Regulatory'),
        ('id="ip">7. Intellectual', 'id="ip">9. Intellectual'),
        ('id="liability">8. Limitation', 'id="liability">10. Limitation'),
        ('id="law">9. Governing', 'id="law">11. Governing'),
    ]
    for a, b in renumbers:
        t = t.replace(a, b)
    # clarify §3 auto-renew applies to paid only — note mild tension; keep live §3, pack clarifies in new sections
    t = ensure_preview_bar(t)
    p.write_text(t)
    mark(p)
    print('terms: ok')


REFUND_TRIAL = r'''
<h2 id="trial">Free trial: no payment to refund</h2>
<p>The Pet Desk trial is free for 14 days. No card is required and there is no commitment to subscribe. Starting a trial does not create a paid subscription or authorize any payment.</p>
<p>The trial does not automatically convert to a paid subscription. There is no charge when the trial ends, and you do not need to cancel the trial to avoid a charge. If you want to subscribe, you must explicitly choose a paid plan and confirm your purchase through Paddle, our Merchant of Record. No payment will be taken without that choice and confirmation.</p>
<p>Because the trial involves no payment, there is no trial payment to refund.</p>

'''

REFUND_SEP = (
    '<p>This refund period is separate from the free trial: taking a trial does not use up or shorten the initial paid purchase refund window.</p>\n'
)

REFUND_PRICES = r'''
<p>Published prices:</p>
<div class="tablewrap"><table>
<thead><tr><th>Plan</th><th>Monthly billing (USD)</th><th>Annual billing (USD)</th></tr></thead>
<tbody>
<tr><td>Starter · Advisor</td><td>$49 per month</td><td>$468 per year, paid annually</td></tr>
<tr><td>Pro · Pet Desk Agency</td><td>$149 per month</td><td>$1,428 per year, paid annually</td></tr>
<tr><td>Enterprise · Corporate HR &amp; Global Mobility</td><td>$399 per month</td><td>$3,828 per year, paid annually</td></tr>
</tbody>
</table></div>
<p>Annual subscriptions are billed as the full annual total, not as monthly installments. Applicable taxes and the total payable are shown at Paddle checkout before you confirm a paid purchase.</p>
'''


def patch_refund():
    p = SITE / 'refund-policy.html'
    t = p.read_text()
    if 'id="trial"' in t:
        print('refund: already patched')
        return
    t = t.replace(
        'Effective date: November 6, 2026 &middot; Last updated: November 6, 2026',
        'Effective date: November 6, 2026 &middot; Last updated: November 10, 2026',
    )
    # broaden intro: policy also covers free trial
    old_intro = 'This Refund &amp; Cancellation Policy applies to paid <strong>B2B Pet Desk</strong> subscriptions on PetPolicyCheck / Paw Passport. Free public guides are free and do not involve payment.'
    new_intro = 'This Refund &amp; Cancellation Policy applies to the free Pet Desk trial and to paid <strong>B2B Pet Desk</strong> subscriptions on PetPolicyCheck / Paw Passport. Free public guides are free and do not involve payment.'
    if old_intro in t:
        t = t.replace(old_intro, new_intro)
    anchor = '<h2 id="guarantee">14-Day Refund Guarantee</h2>'
    if anchor not in t:
        raise SystemExit('refund: guarantee anchor missing')
    t = t.replace(anchor, REFUND_TRIAL + anchor)
    # after first paragraph of guarantee, insert separation sentence
    g_first = (
        '<p>We offer a clear, friction-free <strong>14-day refund policy</strong>. '
        'If you are not satisfied with your initial B2B Pet Desk subscription purchase '
        '(monthly or annual), you may request a <strong>full refund within 14 calendar days</strong> '
        'of the purchase date.</p>'
    )
    if g_first in t and 'separate from the free trial' not in t:
        t = t.replace(g_first, g_first + '\n' + REFUND_SEP)
    # add prices before cancel section if not present
    if 'Published prices:' not in t:
        cancel = '<h2 id="cancel">One-Click Subscription Cancellation</h2>'
        t = t.replace(cancel, REFUND_PRICES + cancel)
    t = ensure_preview_bar(t)
    p.write_text(t)
    mark(p)
    gaps.append(
        'Refund: pack section "Separate 14-day refund guarantee" overlaps the live '
        '"14-Day Refund Guarantee" (live keeps how-to bullets + Paddle portal). '
        'Inserted free-trial section WORD FOR WORD; added pack separation sentence + '
        'published prices; did not delete live how-to list.'
    )
    print('refund: ok')


def patch_privacy_gap():
    gaps.append(
        'Privacy: NO draft Pet Desk trial/account clause in '
        '/workspace/petdesk-trial-copy-20261107/ (README + trial-check.md mark it as an '
        'open decision). Live privacy.html still says "PetPolicyCheck is a simple static '
        'website" and only covers Paddle billing, not trial/account processing or J10/J14 '
        'emails. Did NOT invent legal text. Page untouched except listed here.'
    )
    print('privacy: gap only (no text)')


def patch_pro():
    p = SITE / 'pro/index.html'
    t = p.read_text()
    if 'Start your free 14-day trial' in t and 'Will I be charged when my trial ends?' in t:
        print('pro: already patched')
        return

    # Button labels in HTML defaults
    t = t.replace('>Start 14-day trial</a>', '>Start your free 14-day trial</a>')
    t = t.replace(
        '>Start 14-day IPATA &amp; Relocation Agency trial</a>',
        '>Start your free 14-day trial</a>',
    )
    # Also update mailto subjects to free trial
    t = t.replace(
        'subject=B2B%20Pet%20Desk%20Pro%20-%2014-day%20IPATA%20trial',
        'subject=B2B%20Pet%20Desk%20Pro%20-%20free%2014-day%20trial',
    )
    t = t.replace(
        'subject=B2B%20Pet%20Desk%20Starter%20-%2014-day%20trial',
        'subject=B2B%20Pet%20Desk%20Starter%20-%20free%2014-day%20trial',
    )
    t = t.replace(
        'subject=B2B%20Pet%20Desk%20Enterprise%20-%2014-day%20trial',
        'subject=B2B%20Pet%20Desk%20Enterprise%20-%20free%2014-day%20trial',
    )

    micro = (
        '<p class="fine trial-micro" data-i="cta_micro">'
        '14 days free. No card. No commitment. No automatic subscription or charge when your trial ends. '
        'Subscribe only if you choose a paid plan and confirm your purchase through Paddle.'
        '</p>'
    )
    # Insert microcopy after each primary CTA (btn-pro pri), before ghost
    # Pattern: </a>\n      <a class="btn-pro ghost"
    if 'trial-micro' not in t:
        t = re.sub(
            r'(<a class="btn-pro pri"[^>]*>.*?</a>)\n(\s*)(<a class="btn-pro ghost")',
            r'\1\n\2' + micro + r'\n\2\3',
            t,
            count=3,
        )

    # Replace notice
    old_notice = (
        '<div class="notice" data-i="notice">\n'
        '  <strong>Self-serve checkout powered by Paddle.com</strong> (Merchant of Record — Card, PayPal, Wire/PO; VAT/Sales Tax handled automatically; 14-day refund guarantee). '
        'Request instant onboarding or trial access at <a href="mailto:contact@petpolicycheck.com">contact@petpolicycheck.com</a> while online checkout activates.\n'
        '</div>'
    )
    new_notice = (
        '<div class="notice" data-i="notice">\n'
        '  Your free trial does not create a paid subscription. If you later choose to subscribe, paid checkout is handled by Paddle, our Merchant of Record. '
        'Paid subscriptions renew monthly or annually until cancelled. Initial paid purchases have a separate 14-day refund guarantee starting on the purchase date. '
        'See our <a href="../terms.html">Terms</a> and <a href="../refund-policy.html">Refund &amp; Cancellation Policy</a>.\n'
        '</div>'
    )
    if old_notice in t:
        t = t.replace(old_notice, new_notice)
    elif 'while online checkout activates' in t:
        # fallback: replace inner HTML of notice
        t = re.sub(
            r'(<div class="notice" data-i="notice">)(.*?)(</div>)',
            new_notice,
            t,
            count=1,
            flags=re.S,
        )

    # FAQ additions before closing </section> of pro-faq
    faq_add = '''
  <details><summary data-i="f4t">Will I be charged when my trial ends?</summary><p data-i="f4b">No. The trial ends without a charge or an automatic paid subscription. To subscribe, you must choose a paid plan and confirm your purchase through Paddle. You do not need to cancel the trial to avoid a charge.</p></details>
  <details><summary data-i="f5t">Is the trial the same as the refund guarantee?</summary><p data-i="f5b">No. The trial is free for 14 days. The separate 14-day refund guarantee begins on the date of your initial paid purchase, if you choose to make one.</p></details>
'''
    if 'Will I be charged when my trial ends?' not in t:
        t = t.replace(
            '</section>\n<p class="fine" data-i="op">',
            faq_add + '</section>\n<p class="fine" data-i="op">',
            1,
        )

    # Update I.en strings inside the script
    # cta_trial
    t = t.replace(
        'cta_trial:"Start 14-day trial"',
        'cta_trial:"Start your free 14-day trial"',
    )
    t = t.replace(
        'cta_trial_ipata:"Start 14-day IPATA & Relocation Agency trial"',
        'cta_trial_ipata:"Start your free 14-day trial"',
    )
    # notice EN — escape carefully inside JS string
    old_en_notice = (
        'notice:"<strong>Self-serve checkout powered by Paddle.com</strong> (Merchant of Record — Card, PayPal, Wire/PO; VAT/Sales Tax handled automatically; 14-day refund guarantee). '
        'Request instant onboarding or trial access at <a href=\\"mailto:contact@petpolicycheck.com\\">contact@petpolicycheck.com</a> while online checkout activates."'
    )
    new_en_notice = (
        'notice:"Your free trial does not create a paid subscription. If you later choose to subscribe, paid checkout is handled by Paddle, our Merchant of Record. '
        'Paid subscriptions renew monthly or annually until cancelled. Initial paid purchases have a separate 14-day refund guarantee starting on the purchase date. '
        'See our <a href=\\"../terms.html\\">Terms</a> and <a href=\\"../refund-policy.html\\">Refund & Cancellation Policy</a>."'
    )
    if old_en_notice in t:
        t = t.replace(old_en_notice, new_en_notice)
    else:
        gaps.append('Pro: EN notice string in I.en not found for exact replace — check notice HTML.')

    # Add FAQ + micro keys to EN object — inject before faq_h or after f3b
    if 'f4t:' not in t:
        t = t.replace(
            'f3t:"Can I cancel anytime?",f3b:"Yes. Cancel before renewal from your Paddle customer portal. New paid subscriptions include a clear 14-day refund window.",op:',
            'f3t:"Can I cancel anytime?",f3b:"Yes. Cancel before renewal from your Paddle customer portal. New paid subscriptions include a clear 14-day refund window.",'
            'f4t:"Will I be charged when my trial ends?",'
            'f4b:"No. The trial ends without a charge or an automatic paid subscription. To subscribe, you must choose a paid plan and confirm your purchase through Paddle. You do not need to cancel the trial to avoid a charge.",'
            'f5t:"Is the trial the same as the refund guarantee?",'
            'f5b:"No. The trial is free for 14 days. The separate 14-day refund guarantee begins on the date of your initial paid purchase, if you choose to make one.",'
            'cta_micro:"14 days free. No card. No commitment. No automatic subscription or charge when your trial ends. Subscribe only if you choose a paid plan and confirm your purchase through Paddle.",'
            'op:',
        )

    # Other langs: align CTA label to free trial (pack is EN-only; keep existing translated notice but update CTA)
    for old, new in [
        ('cta_trial:"Essai 14 jours"', 'cta_trial:"Start your free 14-day trial"'),
        ('cta_trial_ipata:"Essai IPATA & agences 14 jours"', 'cta_trial_ipata:"Start your free 14-day trial"'),
        ('cta_trial:"Prueba de 14 días"', 'cta_trial:"Start your free 14-day trial"'),
        ('cta_trial_ipata:"Prueba IPATA y agencias 14 días"', 'cta_trial_ipata:"Start your free 14-day trial"'),
        ('cta_trial:"14-Tage-Test starten"', 'cta_trial:"Start your free 14-day trial"'),
        ('cta_trial_ipata:"14-Tage-IPATA- & Agency-Test"', 'cta_trial_ipata:"Start your free 14-day trial"'),
        ('cta_trial:"14일 체험 시작"', 'cta_trial:"Start your free 14-day trial"'),
        ('cta_trial_ipata:"IPATA & 이주 에이전시 14일 체험"', 'cta_trial_ipata:"Start your free 14-day trial"'),
        ('cta_trial:"14日間トライアル開始"', 'cta_trial:"Start your free 14-day trial"'),
        ('cta_trial_ipata:"IPATA＆代理店14日間トライアル"', 'cta_trial_ipata:"Start your free 14-day trial"'),
    ]:
        t = t.replace(old, new)

    gaps.append(
        'Pro: pack common CTA "Start your free 14-day trial" replaces live IPATA-specific '
        'CTA on the Pro card ("Start 14-day IPATA & Relocation Agency trial") — applied as pack '
        'instructs. Non-EN i18n CTA labels set to the EN pack string (pack is EN-only); '
        'non-EN notice/FAQ translations not rewritten. Trial buttons still mailto:contact@ '
        '(pack: destination not defined; must not hit paid checkout).'
    )

    t = ensure_preview_bar(t)
    p.write_text(t)
    mark(p)
    print('pro: ok')


def inject_banner_country(path: pathlib.Path, after_patterns: list[str]):
    t = path.read_text()
    if 'ppc-pro-banner' in t:
        print(f'banner skip (exists): {path.name}')
        return
    b = banner_html('../pro/')
    inserted = False
    for pat in after_patterns:
        if pat in t:
            t = t.replace(pat, pat + '\n' + b + '\n', 1)
            inserted = True
            break
    if not inserted:
        gaps.append(f'Banner: could not find insert anchor on countries/{path.name}')
        print(f'banner FAIL: {path.name}')
        return
    t = ensure_css_link(t, CSS_LINK_REL)
    t = ensure_preview_bar(t)
    path.write_text(t)
    mark(path)
    print(f'banner country: {path.name}')


def inject_banner_hotel(path: pathlib.Path):
    t = path.read_text()
    if 'ppc-pro-banner' in t:
        print(f'banner skip: {path.name}')
        return
    b = banner_html('../pro/')
    # after Expedia book aside, before chains — avoid putting inside Expedia card
    anchors = [
        '</aside>\n<h2 id="chains">',
        '</aside><h2 id="chains">',
        '<h2 id="chains">Hotel chain pet rules',
        '<h2 id="chains">',
    ]
    inserted = False
    for a in anchors:
        if a in t:
            if a.startswith('<h2'):
                t = t.replace(a, b + '\n' + a, 1)
            else:
                # keep aside close, insert banner, then chains
                t = t.replace(a, '</aside>\n' + b + '\n<h2 id="chains">' + a.split('<h2 id="chains">', 1)[-1] if False else a.replace('</aside>\n<h2 id="chains">', '</aside>\n' + b + '\n<h2 id="chains">').replace('</aside><h2 id="chains">', '</aside>\n' + b + '\n<h2 id="chains">'), 1)
            inserted = True
            break
    if not inserted:
        # fallback: after warn block / before first h2 chains-like
        m = re.search(r'(<h2 id="chains"[^>]*>)', t)
        if m:
            t = t[: m.start()] + b + '\n' + t[m.start() :]
            inserted = True
    if not inserted:
        gaps.append(f'Banner: could not find insert on hotels/{path.name}')
        print(f'banner FAIL hotel: {path.name}')
        return
    t = ensure_css_link(t, CSS_LINK_REL)
    t = ensure_preview_bar(t)
    path.write_text(t)
    mark(path)
    print(f'banner hotel: {path.name}')


def inject_banner_hotel_pets():
    path = SITE / 'hotel-pets/index.html'
    t = path.read_text()
    if 'ppc-pro-banner' in t:
        return
    b = banner_html('../pro/')
    # after lead, before first section
    m = re.search(r'(</p><section>)', t)
    if not m:
        m = re.search(r'(<section>)', t)
        if not m:
            gaps.append('Banner: hotel-pets hub insert failed')
            return
        t = t[: m.start()] + b + t[m.start() :]
    else:
        t = t.replace('</p><section>', '</p>' + b + '<section>', 1)
    t = ensure_css_link(t, CSS_LINK_REL)
    t = ensure_preview_bar(t)
    path.write_text(t)
    mark(path)
    print('banner hotel-pets: ok')


def mirror_to_static():
    """Keep static/ in sync for touched paths + new assets."""
    assets = [
        'assets/css/ppc-pro-banner.css',
        'assets/includes/ppc-pro-banner.html',
    ]
    for rel in assets + touched:
        src = SITE / rel
        dst = STATIC / rel
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    print(f'mirror: {len(touched)} pages + assets -> static/')


def main():
    patch_terms()
    patch_refund()
    patch_privacy_gap()
    patch_pro()

    # Countries
    inject_banner_country(
        SITE / 'countries/canada.html',
        ['</section>\n<section id="rail">', '</section>\n\n<section id="rail">'],
    )
    inject_banner_country(
        SITE / 'countries/mexico.html',
        ['</section>\n<section id="hubs">', '</section>\n\n<section id="hubs">'],
    )
    for name in ('uk.html', 'france.html', 'germany.html'):
        inject_banner_country(
            SITE / 'countries' / name,
            [
                '</section>\n\n<section id="hubs">',
                '</section>\n\n<section id="taxi">',
                '</section>\n<section id="hubs">',
                '</section>\n<section id="taxi">',
            ],
        )
    # USA: after federal table, before train
    inject_banner_country(
        SITE / 'countries/usa.html',
        ['</div>\n<h2 id="train">', '</tbody></table></div>\n<h2 id="train">'],
    )

    # Hotels city guides
    for p in sorted((SITE / 'hotels').glob('pet-friendly-hotels-*.html')):
        inject_banner_hotel(p)

    inject_banner_hotel_pets()

    mirror_to_static()

    report = ROOT / 'qa/petdesk/APPLY-REPORT.md'
    report.write_text(
        '# Apply report\n\n## Touched\n'
        + '\n'.join(f'- {x}' for x in touched)
        + '\n\n## Gaps / contradictions\n'
        + '\n'.join(f'- {g}' for g in gaps)
        + '\n'
    )
    print('DONE', len(touched), 'pages')
    for g in gaps:
        print('GAP:', g[:120])


if __name__ == '__main__':
    main()
