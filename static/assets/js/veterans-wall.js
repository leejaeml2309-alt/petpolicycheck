(function () {
  'use strict';

  var ROOT = document.getElementById('wall-of-heroes');
  if (!ROOT) return;

  var grid = document.getElementById('woh-grid');
  var consent = document.getElementById('woh-consent');
  var mailBtn = document.getElementById('woh-mailto');
  var MAILTO = {
    to: 'contact@petpolicycheck.com',
    subject: 'Wall of Heroes — K9 photo submission',
    body: [
      'Hello PetPolicyCheck team,',
      '',
      'I would like to submit a photo for the Wall of Heroes on petpolicycheck.com/veterans/.',
      '',
      'Dog first name: ',
      'Role / general unit (no insignia, badge, or rank): ',
      'Years of service (optional): ',
      'City / country (optional): ',
      '',
      'I confirm:',
      '- I own the rights to the photo(s).',
      '- 1 to 3 photos attached; the dog alone or from behind; no human face or name; no military insignia, badge, rank, or license plate.',
      '- I consent to publication of the approved photo(s) on petpolicycheck.com only (Wall of Heroes).',
      '- I understand each photo is reviewed by your team before it goes live, and I can ask for removal at any time.',
      '',
      'Thank you.'
    ].join('\n')
  };

  var EMPTY_SLOTS = [
    { title: 'Your K9 could be here', sub: 'Be the first hero' },
    { title: 'Your K9 could be here', sub: 'Share a photo' },
    { title: 'Be the first hero', sub: 'Service dogs welcome' },
    { title: 'Your K9 could be here', sub: 'Reviewed before publish' },
    { title: 'Honor a partner', sub: 'Name the dog only' }
  ];

  var PAW_SVG =
    '<svg class="woh-placeholder__ico" viewBox="0 0 64 64" aria-hidden="true" fill="none">' +
    '<circle cx="20" cy="18" r="7" stroke="#8a96a8" stroke-width="2"/>' +
    '<circle cx="44" cy="18" r="7" stroke="#8a96a8" stroke-width="2"/>' +
    '<circle cx="12" cy="34" r="6" stroke="#8a96a8" stroke-width="2"/>' +
    '<circle cx="52" cy="34" r="6" stroke="#8a96a8" stroke-width="2"/>' +
    '<ellipse cx="32" cy="44" rx="14" ry="12" stroke="#8a96a8" stroke-width="2"/>' +
    '</svg>';

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function emptyCard(slot) {
    return (
      '<article class="woh-card woh-card--empty" aria-label="Empty gallery slot">' +
      '<div class="woh-card__media"><div class="woh-placeholder">' +
      PAW_SVG +
      '<strong style="display:block;color:#c9d3e0">' +
      esc(slot.title) +
      '</strong>' +
      esc(slot.sub) +
      '</div></div>' +
      '<div class="woh-card__body"><p class="woh-card__meta">Awaiting a verified submission</p></div>' +
      '</article>'
    );
  }

  function heroCard(h) {
    var meta = [h.role, h.years].filter(Boolean).join(' · ');
    return (
      '<article class="woh-card">' +
      '<div class="woh-card__media">' +
      '<img src="' +
      esc(h.photo) +
      '" alt="' +
      esc(h.alt || h.name || 'Service dog') +
      '" loading="lazy" width="640" height="480">' +
      '</div>' +
      '<div class="woh-card__body">' +
      '<p class="woh-card__name">' +
      esc(h.name || 'K9') +
      '</p>' +
      (meta ? '<p class="woh-card__meta">' + esc(meta) + '</p>' : '') +
      '</div></article>'
    );
  }

  function renderEmpty() {
    grid.innerHTML = EMPTY_SLOTS.map(emptyCard).join('');
  }

  function renderHeroes(heroes) {
    if (!heroes || !heroes.length) {
      renderEmpty();
      return;
    }
    grid.innerHTML = heroes.map(function (h) {
      return heroCard(h);
    }).join('');
  }

  function dataUrl() {
    return '../data/veterans-wall.json';
  }

  function syncMailto() {
    var ok = !!(consent && consent.checked);
    if (!mailBtn) return;
    mailBtn.setAttribute('aria-disabled', ok ? 'false' : 'true');
    if (ok) {
      mailBtn.removeAttribute('tabindex');
      mailBtn.href =
        'mailto:' +
        MAILTO.to +
        '?subject=' +
        encodeURIComponent(MAILTO.subject) +
        '&body=' +
        encodeURIComponent(MAILTO.body);
    } else {
      mailBtn.href = '#woh-consent';
      mailBtn.setAttribute('tabindex', '-1');
    }
  }

  if (consent) {
    consent.addEventListener('change', syncMailto);
  }
  if (mailBtn) {
    mailBtn.addEventListener('click', function (e) {
      if (!consent || !consent.checked) {
        e.preventDefault();
        if (consent) consent.focus();
      }
    });
  }
  syncMailto();

  fetch(dataUrl(), { credentials: 'same-origin' })
    .then(function (r) {
      if (!r.ok) throw new Error('wall data ' + r.status);
      return r.json();
    })
    .then(function (data) {
      var heroes = (data && data.heroes) || [];
      renderHeroes(heroes);
    })
    .catch(function () {
      renderEmpty();
    });
})();
