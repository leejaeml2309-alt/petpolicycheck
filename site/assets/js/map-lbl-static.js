/* Compact-map label applier (UK/FR/DE/IT/ES/JP/KR).
   Reads precomputed PPC_LABEL_PLAN and applies positions, visibility and
   type colours only. No fill sampling, no slot search, no layout thrash.
   Never loads a plan on USA / Canada / Mexico pages. */
(function(){
  const CFG = window.PPC_MAP;
  if(!CFG) return;
  const root = document.getElementById(CFG.idRoot || 'country-map');
  if(!root || !root.classList.contains('map-lbl-sm')) return;
  const plan = window.PPC_LABEL_PLAN;
  if(!plan || !plan.tiers || !plan.tiers.length) return;

  const HIDE_CLS = ['lbl-crowd','ct-label-crowd','ap-code-crowd','ap-name-crowd','ct-crowd','ap-crowd','ppc-lbl-hide'];

  function mapEl(){ return document.getElementById('map'); }

  function pickTier(){
    const m=mapEl();
    if(!m) return plan.tiers[0];
    const w=m.getBoundingClientRect().width||0;
    const mobile=w<500;
    const vb=(m.viewBox && m.viewBox.baseVal && m.viewBox.baseVal.width) || plan.mapW || 975;
    const k=vb/(plan.mapW||975);
    let best=null, bestD=1e9;
    for(const t of plan.tiers){
      if(!!t.mobile !== mobile) continue;
      const d=Math.abs((t.k||1)-k);
      if(d<bestD){ bestD=d; best=t; }
    }
    if(best) return best;
    for(const t of plan.tiers){
      const d=Math.abs((t.k||1)-k);
      if(d<bestD){ bestD=d; best=t; }
    }
    return best || plan.tiers[0];
  }

  function allTexts(){
    const m=mapEl();
    if(!m) return [];
    return [...m.querySelectorAll('#g-lb text, #g-ct .ct text, #g-ap .ap text')];
  }

  function norm(s){ return String(s||'').replace(/\s+/g,' ').trim(); }

  function typOf(el){
    if(el.classList.contains('lbl-group') || (el.dataset && el.dataset.group)) return 'group';
    if(el.classList.contains('is-cap') || (el.dataset && el.dataset.kind==='capital') || (el.closest && el.closest('.ct.cap'))) return 'capital';
    if(el.classList.contains('ap-label') || (el.dataset && el.dataset.kind==='airport') || el.closest('.ap')) return 'airport';
    if(el.classList.contains('ct-label') || (el.dataset && el.dataset.kind==='city') || el.closest('.ct')) return el.classList.contains('is-cap')?'capital':'city';
    if(el.classList.contains('lbl')) return 'region';
    return 'region';
  }

  function findEl(rec){
    if(rec.id){
      const el=document.getElementById(rec.id);
      if(el) return el;
    }
    if(rec.sel){
      try{
        const el=document.querySelector(rec.sel);
        if(el) return el;
      }catch(e){}
    }
    if(rec.typ==='group' && rec.name){
      const g=document.querySelector('#g-lb text.lbl-group[data-group="'+rec.name+'"]');
      if(g) return g;
    }
    const name=norm(rec.name);
    if(!name) return null;
    const cands=allTexts().filter(el => norm(el.textContent)===name);
    if(cands.length===1) return cands[0];
    if(rec.typ){
      const typHit=cands.filter(el => typOf(el)===rec.typ || (rec.typ==='capital' && typOf(el)==='city'));
      if(typHit.length) return typHit[0];
    }
    return cands[0]||null;
  }

  function clearHide(el){
    el.classList.remove.apply(el.classList, HIDE_CLS);
    el.style.removeProperty('display');
    const g=el.closest && el.closest('.ct, .ap');
    if(g) g.classList.remove('ct-crowd','ap-crowd','ap-code-crowd');
    if(el.dataset && el.dataset.owner){
      const og=document.querySelector('#g-ct .ct[data-k="'+el.dataset.owner+'"], #g-ap .ap[data-code="'+el.dataset.owner+'"]');
      if(og) og.classList.remove('ct-crowd','ap-crowd','ap-code-crowd');
    }
  }

  function applyWrap(el, wrap){
    if(!wrap || !wrap.length) return;
    const ns=el.namespaceURI;
    while(el.firstChild) el.removeChild(el.firstChild);
    wrap.forEach(function(line, i){
      const ts=document.createElementNS(ns,'tspan');
      ts.setAttribute('x', el.getAttribute('x')||0);
      if(i===0) ts.setAttribute('dy','0');
      else ts.setAttribute('dy', line.dy || '1.05em');
      ts.textContent=line.text;
      el.appendChild(ts);
    });
  }

  function applyRec(rec){
    const el=findEl(rec);
    if(!el) return;
    clearHide(el);
    if(rec.hide){
      const cls=rec.hideClass || (rec.typ==='airport' ? 'ap-code-crowd' : rec.typ==='region' ? 'lbl-crowd' : 'ct-label-crowd');
      el.classList.add(cls, 'ppc-lbl-hide');
      return;
    }
    el.classList.remove('ppc-lbl-hide');
    if(rec.x!=null) el.setAttribute('x', rec.x);
    if(rec.y!=null) el.setAttribute('y', rec.y);
    if(rec.anchor) el.setAttribute('text-anchor', rec.anchor);
    el.classList.toggle('lbl-on-dark', !!rec.onDark);
    if(rec.isCap) el.classList.add('is-cap');
    else el.classList.remove('is-cap');
    if(rec.tight) el.classList.add('lbl-tight');
    if(rec.kt!=null && rec.kt!=='') el.style.setProperty('--kt', String(rec.kt));
    else el.style.removeProperty('--kt');
    if(rec.wrap) applyWrap(el, rec.wrap);
    if(rec.leadSel){
      const lead=document.querySelector(rec.leadSel);
      if(lead){
        if(rec.leadHidden) lead.classList.add('lbl-crowd','ppc-lbl-hide');
        else lead.classList.remove('lbl-crowd','ppc-lbl-hide');
      }
    }
  }

  function applyIcons(icons){
    if(!icons) return;
    icons.forEach(function(ic){
      const g=document.querySelector('#g-ap .ap[data-code="'+ic.code+'"]');
      if(!g) return;
      if(ic.tx!=null && ic.ty!=null){
        g.setAttribute('transform','translate('+ic.tx+' '+ic.ty+')');
      }
    });
  }

  function applyPlan(){
    const t=pickTier();
    if(!t || !t.labels) return;
    allTexts().forEach(function(el){ el.classList.add('ppc-lbl-hide'); });
    t.labels.forEach(applyRec);
    applyIcons(t.icons);
  }

  CFG.afterLabels = applyPlan;
  window.PPC_applyLabelContrast = applyPlan;
  if(document.getElementById('map')){
    applyPlan();
  }
})();
