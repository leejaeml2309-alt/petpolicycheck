/* Airport QR pages: scoped preview-safe nav and UTM-only propagation. */
(function () {
  'use strict';
  function boot() {
    var root = new URL(document.documentElement.dataset.siteRoot, document.baseURI);
    // Shared pastilles builds root-relative navigation from pathname depth.
    // Rebase it to this site's root when previewed below a directory prefix.
    document.querySelectorAll('#site-menu a').forEach(function (a) {
      var href = a.getAttribute('href');
      if (href && !/^(?:[a-z]+:|\/\/)/i.test(href)) {
        a.href = new URL(href.replace(/^(?:\.\.\/)+/, ''), root).href;
      }
    });
    var incoming = new URLSearchParams(location.search);
    function propagate(a) {
      var href = a.getAttribute('href');
      if (!href || href[0] === '#') return;
      var url = new URL(href, document.baseURI);
      if (url.origin !== location.origin || !url.pathname.startsWith(root.pathname)) return;
      incoming.forEach(function (value, key) {
        if (/^utm_[a-z0-9_]+$/i.test(key)) url.searchParams.set(key, value);
      });
      a.href = url.href;
    }
    document.querySelectorAll('a[href]').forEach(propagate);
    document.addEventListener('click', function (event) {
      var a = event.target.closest && event.target.closest('a[href]');
      if (a) propagate(a);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
}());

/* Pet map full-screen overlay */
(function(){function init(){var b=document.querySelector('.pm-open');if(!b)return;var o=document.createElement('div');o.className='pm-overlay';o.hidden=true;o.setAttribute('role','dialog');o.setAttribute('aria-modal','true');o.setAttribute('aria-label','Pet map, full screen');o.innerHTML='<div class="pm-ohead"><strong>Pet map</strong><div class="pm-zoom"><button type="button" data-z="-1" aria-label="Zoom out">−</button><button type="button" data-z="1" aria-label="Zoom in">+</button><button type="button" class="pm-close" aria-label="Close full-screen map">×</button></div></div><div class="pm-obody"></div>';document.body.appendChild(o);var body=o.querySelector('.pm-obody'),close=o.querySelector('.pm-close'),z=1;
var svg=b.querySelector('svg').cloneNode(true);svg.querySelectorAll('[id]').forEach(function(n){n.id='fs-'+n.id});svg.setAttribute('aria-labelledby',svg.getAttribute('aria-labelledby').split(' ').map(function(x){return 'fs-'+x}).join(' '));svg.querySelectorAll('[marker-end]').forEach(function(n){n.setAttribute('marker-end',n.getAttribute('marker-end').replace('#','#fs-'))});body.appendChild(svg);
function setz(){svg.style.width=(100*z)+'%'}o.querySelectorAll('[data-z]').forEach(function(x){x.addEventListener('click',function(){z=Math.min(3,Math.max(1,z+0.5*x.getAttribute('data-z')));setz()})});
function open(){o.hidden=false;document.documentElement.style.overflow='hidden';close.focus()}function shut(){o.hidden=true;document.documentElement.style.overflow='';z=1;setz();b.focus()}
b.addEventListener('click',open);close.addEventListener('click',shut);o.addEventListener('keydown',function(ev){if(ev.key==='Escape'){shut()}if(ev.key==='Tab'){var f=o.querySelectorAll('button'),first=f[0],last=f[f.length-1];if(ev.shiftKey&&document.activeElement===first){ev.preventDefault();last.focus()}else if(!ev.shiftKey&&document.activeElement===last){ev.preventDefault();first.focus()}}})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init()}());
