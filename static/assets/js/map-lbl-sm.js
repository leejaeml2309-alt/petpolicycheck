/* Compact plain-label contrast + placement (UK/FR/DE/IT/ES/JP/KR only).
   Samples real pixels under each label bbox (map rendered without labels).
   Land uses the shared dark type colours; light tints are for sea (and gold
   selection) only. Never loads on USA / Canada / Mexico pages. */
(function(){
  const CFG = window.PPC_MAP;
  if(!CFG) return;
  const root = document.getElementById(CFG.idRoot || 'country-map');
  if(!root || !root.classList.contains('map-lbl-sm')) return;
  const CC = (CFG.data && CFG.data.country) || (typeof DATA!=='undefined' && DATA.country) || '';
  const JPKR = /^(JP|KR)$/.test(CC);
  /* Preferred anchors (user units), keyed by label type so a region name
     never steals an airport or city of the same word (Kansai, Jeju, Naha). */
  const PREFERRED = JPKR ? {
    region: {
      'Gyeonggi': {x:545, y:162, anchor:'middle'},
      'South Jeolla': {x:488, y:408, anchor:'start'},
      'South Chungcheong': {x:484, y:268, anchor:'middle'},
      'Kansai': {x:339, y:385, anchor:'end'},
      'Chubu': {x:430, y:375, anchor:'middle'},
      'Kyushu-Okinawa': {x:122, y:542, anchor:'middle'}
    },
    city: {
      'Hongseong': {x:460, y:218, anchor:'middle'},
      'Ulsan': {x:695, y:350, anchor:'start'},
      'Jeju': {x:446, y:524, anchor:'middle'},
      'Naha': {x:140, y:518, anchor:'end'},
      'Sendai': {x:518, y:292, anchor:'middle'},
      'Yokohama': {x:475, y:426, anchor:'end'},
      'Kobe': {x:338, y:438, anchor:'end'},
      'Osaka': {x:350, y:418, anchor:'middle'},
      'Sejong': {x:548, y:250, anchor:'start'}
    },
    capital: {
      'Seoul': {x:504, y:134, anchor:'start'},
      'Tokyo': {x:469, y:404, anchor:'end'}
    },
    airport: {
      'HND': {x:512, y:430, anchor:'start'},
      'KIX': {x:400, y:515, anchor:'start'},
      'Kansai': {x:336, y:448, anchor:'end'},
      'NRT': {x:530, y:388, anchor:'start'},
      'OKA': {x:128, y:478, anchor:'end'},
      'Naha': {x:128, y:490, anchor:'end'},
      'CJU': {x:420, y:538, anchor:'end'},
      'CJJ': {x:575, y:225, anchor:'start'}
    }
  } : {};
  function prefLookup(bucket, n){
    if(!bucket || !n) return null;
    if(Object.prototype.hasOwnProperty.call(bucket, n)) return bucket[n];
    const slim=String(n).replace(/\s+/g,'').toLowerCase();
    for(const k of Object.keys(bucket)){
      if(k.replace(/\s+/g,'').toLowerCase()===slim) return bucket[k];
    }
    return null;
  }
  function prefOf(n, typ){
    if(!n || !PREFERRED || !PREFERRED.region) return null;
    const order = typ==='capital' ? ['capital','city']
      : typ ? [typ]
      : ['region','capital','city','airport'];
    for(const t of order){
      const hit=prefLookup(PREFERRED[t], n);
      if(hit) return hit;
    }
    return null;
  }
  function pinAllowed(it, mobile, full){
    if(!prefOf(it.name, it.typ)) return false;
    if(full && it.el && it.el.classList.contains('map-name')) return false;
    if(mobile && (it.typ==='city' || it.typ==='capital' || it.typ==='airport')) return false;
    if(mobile && full && it.typ==='region') return false;
    if(mobile && full && it.typ==='city' && !it.el.classList.contains('is-major') && !it.el.classList.contains('is-cap')) return false;
    return true;
  }
  const MUST_CITY = new Set(['Tokyo','Osaka','Nagoya']);
  const SECONDARY_CITY = new Set(['Yokohama','Kobe','Kyoto']);
  function labelName(el){
    return (el.textContent||'').replace(/\s+/g,' ').trim();
  }
  function isSouthChungcheong(n){
    return /^south\s*chung\s*cheong$/i.test(n);
  }
  function isSouthJeolla(n){
    return /^south\s*jeolla$/i.test(n);
  }
  function isGyeonggi(n){
    return /^gyeonggi$/i.test(n);
  }

  function srgb(c){ c=c/255; return c<=0.04045 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4); }
  function lumRgb(r,g,b){ return 0.2126*srgb(r)+0.7152*srgb(g)+0.0722*srgb(b); }
  function parseColor(str){
    if(!str || str==='none' || str==='transparent') return null;
    let m=String(str).trim().match(/^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)(?:\s*,\s*([\d.]+))?/i);
    if(m){
      if(m[4]!==undefined && +m[4]===0) return null;
      return [+m[1],+m[2],+m[3]];
    }
    m=String(str).trim().match(/^#([0-9a-f]{6})$/i);
    if(m){ const n=parseInt(m[1],16); return [(n>>16)&255,(n>>8)&255,n&255]; }
    m=String(str).trim().match(/^#([0-9a-f]{3})$/i);
    if(m){ const h=m[1]; return [parseInt(h[0]+h[0],16),parseInt(h[1]+h[1],16),parseInt(h[2]+h[2],16)]; }
    return null;
  }
  function contrast(a,b){
    const L1=lumRgb(a[0],a[1],a[2]), L2=lumRgb(b[0],b[1],b[2]);
    const hi=Math.max(L1,L2), lo=Math.min(L1,L2);
    return (hi+0.05)/(lo+0.05);
  }
  function cssColor(el, prop, fallbackVar){
    const cs=getComputedStyle(el);
    let v=parseColor(cs[prop] || cs.getPropertyValue(prop));
    if(v) return v;
    if(fallbackVar){
      v=parseColor(getComputedStyle(root).getPropertyValue(fallbackVar).trim());
      if(v) return v;
    }
    return null;
  }
  function isShown(el){
    if(!el) return false;
    const cs=getComputedStyle(el);
    if(cs.display==='none' || cs.visibility==='hidden' || +cs.opacity===0) return false;
    if(el.closest && el.closest('.ct-crowd,.lbl-crowd,.ap-crowd,.ap-code-crowd,.ap-name-crowd,.ct-label-crowd')) return false;
    const b=el.getBoundingClientRect();
    return b.width>2 && b.height>2;
  }
  function typeOf(el){
    if(el.dataset && el.dataset.kind) return el.dataset.kind;
    if(el.classList.contains('ct-label')) return el.classList.contains('is-cap') ? 'capital' : 'city';
    if(el.classList.contains('ap-label')) return 'airport';
    if(el.classList.contains('lbl')) return 'region';
    const g=el.closest('.ct');
    if(g) return g.classList.contains('cap') ? 'capital' : 'city';
    if(el.closest('.ap')) return 'airport';
    return 'region';
  }
  const DARK_VAR={region:'--lbl-region', city:'--lbl-city', capital:'--lbl-capital', airport:'--lbl-airport'};
  const LIGHT_VAR={region:'--lbl-region-on-dark', city:'--lbl-city-on-dark', capital:'--lbl-capital-on-dark', airport:'--lbl-airport-on-dark'};
  const GOLD=[0x6d,0x5a,0x2c];

  function seaRgb(){
    const svg=document.getElementById('map');
    let el=svg && (svg.closest('.mapcard') || svg.closest('.mapwrap') || svg.parentElement);
    while(el){
      const c=parseColor(getComputedStyle(el).backgroundColor);
      if(c) return c;
      el=el.parentElement;
    }
    const paper=parseColor(getComputedStyle(root).getPropertyValue('--paper').trim());
    return paper || [17,37,42];
  }
  function isClose(a,b,tol){
    return Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1])+Math.abs(a[2]-b[2])<=(tol||28);
  }

  let _sampleRestore=null;
  let _stPaths=null;
  function stPaths(){
    if(!_stPaths) _stPaths=[...document.querySelectorAll('#g-st path.st')];
    return _stPaths;
  }
  function hideLabelsForSample(m){
    if(_sampleRestore) _sampleRestore();
    const prev=[];
    m.querySelectorAll('#g-lb, #g-ct text, #g-ap text, .lbl-lead, .zoom, #g-ct circle, #g-ap .ap-mark, #g-ap .pad, #g-ap .glyph').forEach(n=>{
      prev.push([n, n.style.pointerEvents]);
      n.style.pointerEvents='none';
    });
    _sampleRestore=function(){
      prev.forEach(([n,pe])=>{ n.style.pointerEvents=pe; });
      _sampleRestore=null;
    };
  }
  /* Mathematical fill: computed style of the path.st (or sea) under a user-space
     point via isPointInFill. Never sample pixels; mixed land/sea is read correctly. */
  function fillAtUser(ux, uy, sea){
    const svg=document.getElementById('map');
    if(!svg) return sea;
    const pt=svg.createSVGPoint();
    pt.x=ux; pt.y=uy;
    for(const p of stPaths()){
      try{
        if(p.isPointInFill(pt)){
          const f=parseColor(getComputedStyle(p).fill);
          if(f) return f;
        }
      }catch(e){}
    }
    return sea;
  }
  function sampleBox(box, sea){
    if(!box) return null;
    const svg=document.getElementById('map');
    const ctm=svg && svg.getScreenCTM();
    if(!ctm) return null;
    const inv=ctm.inverse();
    const pad=0.5;
    const x0=box.left+pad, y0=box.top+pad, x1=box.right-pad, y1=box.bottom-pad;
    if(x1<=x0 || y1<=y0) return null;
    /* Centre + four corners, as required for worst-case contrast. */
    const colors=[];
    [[0.5,0.5],[0,0],[1,0],[0,1],[1,1]].forEach(([fx,fy])=>{
      const p=svg.createSVGPoint();
      p.x=x0+(x1-x0)*fx;
      p.y=y0+(y1-y0)*fy;
      const u=p.matrixTransform(inv);
      const c=fillAtUser(u.x, u.y, sea);
      colors.push({c, L:lumRgb(c[0],c[1],c[2])});
    });
    const n=colors.length||1;
    let minL=1, maxL=0, nSea=0, nGold=0;
    colors.forEach(o=>{
      if(o.L<minL) minL=o.L;
      if(o.L>maxL) maxL=o.L;
      if(isClose(o.c, sea, 30)) nSea++;
      if(isClose(o.c, GOLD, 36)) nGold++;
    });
    const landN=n-nSea;
    const landFrac=landN/n;
    const goldFrac=nGold/n;
    let pairC=1;
    for(let i=0;i<colors.length;i++){
      for(let j=i+1;j<colors.length;j++){
        const c=contrast(colors[i].c, colors[j].c);
        if(c>pairC) pairC=c;
      }
    }
    const seaLandMix=nSea>0 && landN>0;
    const strong=seaLandMix;
    return {colors, n, nSea, landFrac, goldFrac, minL, maxL, lumRange:maxL-minL, pairC, seaLandMix, strong};
  }

  function worst(colors, text){
    let w=99;
    for(const o of colors){ const r=contrast(text, o.c); if(r<w) w=r; }
    return w;
  }

  function userPerPx(){
    const svg=document.getElementById('map');
    const r=svg.getBoundingClientRect();
    const vb=svg.viewBox.baseVal;
    return vb.width/Math.max(1,r.width);
  }
  function slotRing(x,y,anchors,maxPx){
    const u=userPerPx();
    const out=[{x,y,anchor:anchors||null}];
    const rings = JPKR ? [8,12,16,20,26,32,40,48,58,70] : [10,16,24,32,42,54];
    rings.filter(px=>maxPx==null||px<=maxPx).forEach(px=>{
      const d=px*u;
      [[d,0,'start'],[-d,0,'end'],[0,d,anchors],[0,-d,anchors],
       [d,d,'start'],[-d,d,'end'],[d,-d,'start'],[-d,-d,'end']].forEach(p=>{
        out.push({x:x+p[0], y:y+p[1], anchor:p[2]||anchors||null});
      });
    });
    return out;
  }
  function applyPos(el,s){
    el.setAttribute('x', (+s.x).toFixed(1));
    el.setAttribute('y', (+s.y).toFixed(1));
    if(s.anchor) el.setAttribute('text-anchor', s.anchor);
    el.querySelectorAll('tspan').forEach(ts=>ts.setAttribute('x', (+s.x).toFixed(1)));
    /* Yokohama is a wide city name on a narrow coastal strip; squeeze so it
       stays fully on land next to its dot without covering NGO or Tokyo. */
    if(labelName(el)==='Yokohama'){
      el.setAttribute('textLength','48');
      el.setAttribute('lengthAdjust','spacingAndGlyphs');
    }
  }
  function inflate(b,p){
    return {left:b.left-p, right:b.right+p, top:b.top-p, bottom:b.bottom+p};
  }
  function overlaps(a,b,pad){
    const p=pad||0;
    return !(a.right+p<b.left || a.left-p>b.right || a.bottom+p<b.top || a.top-p>b.bottom);
  }
  function inMapFull(box, mapBox){
    return box.left>=mapBox.left+1 && box.right<=mapBox.right-1 && box.top>=mapBox.top+1 && box.bottom<=mapBox.bottom-1;
  }

  function collectMarks(m){
    const out=[];
    m.querySelectorAll('#g-ap .ap').forEach(g=>{
      if(getComputedStyle(g).display==='none') return;
      const mark=g.querySelector('.ap-mark')||g.querySelector('.pad');
      if(!mark) return;
      const b=mark.getBoundingClientRect();
      if(b.width<1) return;
      const code=(g.getAttribute('data-code')||'').trim();
      out.push({box:inflate(b, JPKR?4:2), kind:'ap-icon', code, owner:code, cx:(b.left+b.right)/2, cy:(b.top+b.bottom)/2});
    });
    m.querySelectorAll('#g-ct .ct').forEach(g=>{
      if(getComputedStyle(g).display==='none' || g.classList.contains('ct-crowd')) return;
      const mark=g.querySelector('circle.ring')||g.querySelector('circle');
      if(!mark) return;
      const b=mark.getBoundingClientRect();
      if(b.width<1) return;
      const key=(g.getAttribute('data-k')||g.getAttribute('data-name')||'').trim();
      out.push({box:inflate(b, JPKR?4:2), kind:'ct-mark', owner:key, cx:(b.left+b.right)/2, cy:(b.top+b.bottom)/2});
    });
    return out;
  }

  function markIsOwn(el, mk){
    const owner=(el.dataset && el.dataset.owner)||'';
    if(!mk) return false;
    if(owner && mk.owner && owner===mk.owner) return true;
    if(owner && mk.code && owner===mk.code) return true;
    if(owner){
      const tail=owner.split('|').pop();
      if(tail && (tail===mk.owner || tail===mk.code || (mk.owner&&mk.owner.split('|').pop()===tail))) return true;
    }
    const g=el.closest && el.closest('.ct, .ap');
    if(g){
      const key=(g.getAttribute('data-k')||g.getAttribute('data-code')||'').trim();
      if(key && (key===mk.owner || key===mk.code)) return true;
    }
    return false;
  }
  function nudgeOffMarks(el, marks, mapBox){
    if(!el || !marks || !marks.length) return;
    let x=+(el.getAttribute('x')), y=+(el.getAttribute('y'));
    const a=el.getAttribute('text-anchor')||'middle';
    const svg=el.ownerSVGElement;
    if(!svg) return;
    const ctm=svg.getScreenCTM();
    if(!ctm) return;
    const inv=ctm.inverse();
    for(let i=0;i<16;i++){
      const box=el.getBoundingClientRect();
      let hit=null;
      for(const mk of marks){
        if(markIsOwn(el, mk)) continue;
        if(overlaps(box, mk.box, 0)){ hit=mk; break; }
      }
      if(!hit) return;
      const cx=hit.cx!=null?hit.cx:(hit.box.left+hit.box.right)/2;
      const cy=hit.cy!=null?hit.cy:(hit.box.top+hit.box.bottom)/2;
      const vx=(box.left+box.right)/2-cx, vy=(box.top+box.bottom)/2-cy;
      const len=Math.hypot(vx,vy)||1;
      const p0=svg.createSVGPoint(); p0.x=cx; p0.y=cy;
      const u0=p0.matrixTransform(inv);
      const p1=svg.createSVGPoint(); p1.x=cx+vx/len*8; p1.y=cy+vy/len*8;
      const u1=p1.matrixTransform(inv);
      const dx=u1.x-u0.x, dy=u1.y-u0.y;
      x+=dx; y+=dy;
      applyPos(el,{x,y,anchor:a});
      const live=el.getBoundingClientRect();
      if(!inMapFull(live, mapBox)){
        x-=dx; y-=dy;
        applyPos(el,{x,y,anchor:a});
        return;
      }
    }
  }

  function hideItem(el){
    const typ=typeOf(el);
    if(typ==='region') el.classList.add('lbl-crowd');
    else if(typ==='capital' || typ==='city'){
      if(JPKR){
        el.classList.add('ct-label-crowd');
      } else {
        const g=el.closest('.ct');
        if(g) g.classList.add('ct-crowd');
        else el.classList.add('ct-label-crowd');
      }
    } else {
      el.classList.add('ap-code-crowd');
    }
    const id=(el.id||'').replace(/^l-/,'');
    if(id){
      const lead=document.querySelector('#g-lb line.lbl-lead[data-a="'+id+'"]');
      if(lead) lead.classList.add('lbl-crowd');
    }
  }

  function unwrap(t){
    const ts=t.querySelectorAll('tspan');
    if(!ts.length) return;
    const parts=[...ts].map(s=>(s.textContent||'').trim()).filter(Boolean);
    t.textContent=parts.join(' ');
  }
  function tryWrap(el){
    if(el.querySelector('tspan')) return false;
    const raw=(el.textContent||'').trim();
    const ns='http://www.w3.org/2000/svg';
    const x=el.getAttribute('x')||'0';
    if(isSouthChungcheong(raw.replace(/\s+/g,' '))){
      const svg=document.getElementById('map');
      const deep=svg && (svg.classList.contains('is-zoomed') && svg.getBoundingClientRect().width<500);
      const lines= deep ? ['SOUTH','CHUNGCHEONG'] : ['SOUTH','CHUNG','CHEONG'];
      el.textContent='';
      lines.forEach((line,i)=>{
        const ts=document.createElementNS(ns,'tspan');
        ts.setAttribute('x',x);
        ts.setAttribute('dy', i===0?'0':'1.15em');
        ts.textContent=line;
        el.appendChild(ts);
      });
      return true;
    }
    const sp=raw.lastIndexOf(' ');
    if(sp<3 || raw.length<12) return false;
    const a=raw.slice(0,sp), b=raw.slice(sp+1);
    if(!b) return false;
    el.textContent='';
    const t1=document.createElementNS(ns,'tspan');
    t1.setAttribute('x',x); t1.setAttribute('dy','0'); t1.textContent=a;
    const t2=document.createElementNS(ns,'tspan');
    t2.setAttribute('x',x); t2.setAttribute('dy','1.15em'); t2.textContent=b;
    el.appendChild(t1); el.appendChild(t2);
    return true;
  }

  function priOf(el){
    if(el.classList.contains('lbl-group')){
      const mobile=document.getElementById('map') && document.getElementById('map').getBoundingClientRect().width<500;
      const zoomed=document.querySelector('svg#map.is-zoomed');
      return (!zoomed && !mobile) ? 9 : 36;
    }
    if((el.dataset && el.dataset.kind==='capital') || el.classList.contains('is-cap')) return 20;
    const g=el.closest('.ct');
    if(g && g.classList.contains('cap')) return 20;
    if((el.dataset && el.dataset.kind==='city' && el.classList.contains('is-major')) || (g && g.classList.contains('major'))) return 24;
    if((el.dataset && el.dataset.kind==='airport') || el.classList.contains('ap-label') || el.closest('.ap')) return 12;
    if(el.classList.contains('lbl')){
      const n=labelName(el);
      if(JPKR && (isGyeonggi(n)||isSouthJeolla(n)||isSouthChungcheong(n))) return 22;
      return 40;
    }
    return 54;
  }

  function evalSlot(el, typ, dark, light, sea, box, marks, others, mapBox){
    if(!box || !inMapFull(box, mapBox)) return null;
    for(const mk of marks){
      const own=mk.kind==='ap-icon' && mk.code && (
        (el.dataset && el.dataset.owner===mk.code) ||
        (el.closest && el.closest('.ap') && el.closest('.ap').getAttribute('data-code')===mk.code)
      );
      /* JP/KR: IATA also keeps a 4px gap from its own plane icon. */
      if(own && !JPKR) continue;
      if(overlaps(box, mk.box, JPKR?0:0.5)) return null;
    }
    for(const ot of others){
      if(ot===el) continue;
      if(!isShown(ot)) continue;
      const ob=ot.getBoundingClientRect();
      if(overlaps(box, ob, JPKR?4:3)) return null;
    }
    const sm=sampleBox(box, sea);
    if(!sm) return null;
    const cDark=worst(sm.colors, dark);
    const cLight=worst(sm.colors, light);
    const onSea=sm.landFrac<0.12;
    const onSel=sm.goldFrac>0.55 && sm.landFrac>0.7;
    const mixed=sm.seaLandMix;
    const strong=sm.strong;
    let used, ratio, surface;
    if(onSea){
      used='light'; ratio=cLight; surface='sea';
    } else if(onSel){
      used=(cDark>=4.5 && cDark>=cLight)?'dark':'light';
      ratio=used==='dark'?cDark:cLight;
      surface='sel';
    } else {
      used='dark'; ratio=cDark; surface='land';
    }
    const pass=ratio>=4.5 && !mixed && !strong;
    return {sm, cDark, cLight, used, ratio, surface, mixed, strong, pass, onSea};
  }

  function applyContrast(){
    const m=document.getElementById('map');
    if(!m) return [];
    _stPaths=null;
    m.querySelectorAll('#g-lb text.lbl').forEach(unwrap);
    const sea=seaRgb();
    hideLabelsForSample(m);
    const mapBox=m.getBoundingClientRect();
    const marks=collectMarks(m);
    const texts=[...m.querySelectorAll('#g-lb text.lbl, #g-lb text.ct-label, #g-lb text.ap-label, #g-ct .ct text, #g-ap .ap text')];
    const mobile=mapBox.width<500;
    const full=!m.classList.contains('is-zoomed');
    const report=[];

    const items=texts.map(el=>{
      const typ=typeOf(el);
      let ox=+(el.dataset.ox!=null?el.dataset.ox:el.getAttribute('x'));
      let oy=+(el.dataset.oy!=null?el.dataset.oy:el.getAttribute('y'));
      let ota=el.dataset.ota||el.getAttribute('text-anchor')||'middle';
      const n=labelName(el);
      const pref=prefOf(n, typ);
      if(pref){ ox=pref.x; oy=pref.y; ota=pref.anchor||ota; }
      return {el, typ, pri:priOf(el), ox, oy, ota, group:el.classList.contains('lbl-group'), name:n};
    }).sort((a,b)=>a.pri-b.pri);

    const placed=[];
    items.forEach(it=>{
      it.el.classList.remove('lbl-on-dark');
      if(prefOf(it.name, it.typ)) applyPos(it.el, {x:it.ox, y:it.oy, anchor:it.ota});
      if(JPKR && mobile && full && it.typ==='region'){
        hideItem(it.el);
        return;
      }
      if(!isShown(it.el)){
        const mustCity=JPKR && MUST_CITY.has(it.name);
        const mustReg=JPKR && !(mobile && full) && (isSouthJeolla(it.name)||isGyeonggi(it.name)||isSouthChungcheong(it.name));
        const pinned=pinAllowed(it, mobile, full);
        const rescue=(it.group && full && !mobile) || mustCity || mustReg || pinned || (!JPKR && it.pri<=24) || (JPKR && it.typ==='capital');
        if(!rescue) return;
        it.el.classList.remove('lbl-crowd','ct-label-crowd','ap-code-crowd','ct-crowd','ap-name-crowd');
        const g=it.el.closest('.ct, .ap') || (it.el.dataset.owner && (
          document.querySelector('#g-ct .ct[data-k="'+it.el.dataset.owner+'"]') ||
          document.querySelector('#g-ap .ap[data-code="'+it.el.dataset.owner+'"]')
        ));
        if(g) g.classList.remove('ct-crowd','ap-crowd','ap-code-crowd');
        applyPos(it.el, {x:it.ox, y:it.oy, anchor:it.ota});
      }
      /* Long KR region names: wrap first so the slot search uses the 2-line box.
         Tight tracking keeps GYEONGGI / SOUTH CHUNGCHEONG on their own land. */
      if(JPKR && it.typ==='region' && !it.group && (isSouthChungcheong(it.name)||isSouthJeolla(it.name))){
        it.el.classList.add('lbl-tight');
        tryWrap(it.el);
      }
      const dark=cssColor(it.el,'fill', DARK_VAR[it.typ]) || [18,35,58];
      const light=parseColor(getComputedStyle(root).getPropertyValue(LIGHT_VAR[it.typ]).trim()) || [232,238,246];
      const others=placed.map(p=>p.el);
      const keepGroup=it.group && full && !mobile;

      function consider(wrapped){
        const box=it.el.getBoundingClientRect();
        return evalSlot(it.el, it.typ, dark, light, sea, box, marks, others, mapBox);
      }

      let ev=consider(false);
      let chosen=null;
      const needLand=JPKR && (isSouthJeolla(it.name)||isSouthChungcheong(it.name)||isGyeonggi(it.name));
      const prefer=(ev, slot)=>{
        if(!ev) return -100;
        let s=0;
        if(ev.pass) s+=50;
        if(ev.surface==='land') s+=20;
        if(ev.surface==='sel') s+=8;
        if(ev.ratio>=4.5) s+=10+Math.min(ev.ratio,8);
        if(!ev.mixed) s+=8;
        if(!ev.strong) s+=8;
        if(ev.onSea && ev.ratio>=4.5 && !ev.mixed) s+= needLand ? -40 : 6;
        if(needLand && ev.surface!=='land') s-=50;
        if(needLand && ev.sm && ev.sm.landFrac>=0.9) s+=15;
        if(JPKR && slot && (it.typ==='city' || it.typ==='capital' || it.typ==='airport')){
          const dist=Math.hypot((slot.x||0)-it.ox, (slot.y||0)-it.oy);
          s -= dist * 0.6; /* stay close to the city's own marker */
        }
        return s;
      };

      const prefHit=prefOf(it.name, it.typ);
      const pinnedEarly=pinAllowed(it, mobile, full);
      const prefOk=ev && ev.ratio>=4.5 && !ev.mixed && (ev.surface==='land' || ev.onSea || ev.surface==='sea');
      const prefSlotOk=ev && ev.ratio>=4.5 && !ev.mixed && (ev.surface==='land' || ev.onSea || ev.surface==='sea');
      if(pinnedEarly && !mobile && full){
        applyPos(it.el, {x:it.ox, y:it.oy, anchor:it.ota});
        ev=consider(false);
        chosen={ev, wrapped:!!it.el.querySelector('tspan')};
      } else if(ev && ev.pass && (ev.surface==='land' || ev.onSea)){
        chosen={ev, wrapped:false};
      } else if(prefHit && prefSlotOk){
        chosen={ev, wrapped:false};
      } else {
        const maxPx=pinnedEarly ? (full ? (mobile ? 14 : 16) : (mobile ? 20 : 24)) : (prefHit ? (full ? (mobile ? 18 : 28) : (mobile ? 40 : 56)) : (JPKR
          ? (it.group?72:(MUST_CITY.has(it.name)||it.typ==='capital')?(full?44:56):(it.typ==='city'?40:(it.typ==='region'?64:24)))
          : (it.group?72:((it.typ==='capital'||it.typ==='city')?56:(it.typ==='region'?48:36)))));
        const slots=slotRing(it.ox, it.oy, it.ota, maxPx);
        let best=null, bestS=-999;
        for(const s of slots){
          applyPos(it.el, {x:s.x, y:s.y, anchor:s.anchor||it.ota});
          const e=consider(false);
          const sc=prefer(e,s);
          if(e && sc>bestS){ bestS=sc; best={ev:e, s, wrapped:false}; if(e.pass && e.surface==='land' && (!JPKR || Math.hypot(s.x-it.ox,s.y-it.oy)<16)) break; }
        }
        // long region names: try a two-line wrap if still failing
        if((!best || !best.ev || !best.ev.pass) && it.typ==='region' && !it.group){
          if(tryWrap(it.el)){
            for(const s of slots){
              applyPos(it.el, {x:s.x, y:s.y, anchor:s.anchor||it.ota});
              const e=consider(true);
              const sc=prefer(e,s)+1;
              if(e && sc>bestS){ bestS=sc; best={ev:e, s, wrapped:true}; if(e.pass && e.surface==='land' && (!JPKR || Math.hypot(s.x-it.ox,s.y-it.oy)<16)) break; }
            }
            if(!best || !best.wrapped) unwrap(it.el);
          }
        }
        if(best && best.s){
          const drift=Math.hypot(best.s.x-it.ox, best.s.y-it.oy);
          if(pinnedEarly && drift>24){
            applyPos(it.el, {x:it.ox, y:it.oy, anchor:it.ota});
            const evPref=consider(false);
            if(evPref){ ev=evPref; chosen={ev, wrapped:false}; }
            else {
              applyPos(it.el, {x:best.s.x, y:best.s.y, anchor:best.s.anchor||it.ota});
              ev=best.ev; chosen=best;
            }
          } else {
            applyPos(it.el, {x:best.s.x, y:best.s.y, anchor:best.s.anchor||it.ota});
            ev=best.ev;
            chosen=best;
          }
        } else {
          ev=best?best.ev:ev;
          chosen=best;
          if(pinnedEarly){
            applyPos(it.el, {x:it.ox, y:it.oy, anchor:it.ota});
            ev=consider(false);
            chosen={ev, wrapped:false};
          }
        }
      }

      ev=chosen?chosen.ev:ev;
      const mustCity=JPKR && MUST_CITY.has(it.name);
      const mustRegLand=JPKR && !(mobile && full) && (isSouthJeolla(it.name)||isGyeonggi(it.name));
      const mustRegZoom=JPKR && isSouthChungcheong(it.name) && !full;
      const pinned=pinAllowed(it, mobile, full);
      const mustShow=keepGroup || mustCity || mustRegLand || mustRegZoom || pinned || it.typ==='capital' || (!JPKR && it.pri<=20);
      const ok=ev && ev.ratio>=4.5 && !ev.mixed && (ev.surface!=='land' || ev.used==='dark' || ev.surface==='sel');
      const okSea=ev && ev.onSea && ev.ratio>=4.5 && !ev.mixed;
      const landOk=ev && ev.surface==='land' && ev.used==='dark' && ev.ratio>=4.5 && !ev.mixed && !ev.strong;
      /* JP/KR IATA at full view, or secondary cluster cities, hide unless a clean 4px slot exists. */
      const hideIfCrowded=JPKR && full && (it.typ==='airport' || SECONDARY_CITY.has(it.name));
      if(needLand && !landOk && !pinned){
        if(mustShow){
          if(!landOk){ hideItem(it.el); return; }
        } else {
          hideItem(it.el); return;
        }
      }
      if(hideIfCrowded && !(ok || okSea) && !pinned){
        hideItem(it.el); return;
      }
      if(!ok && !okSea && !pinned){
        if(mustCity && ev && ev.ratio>=4.5 && !ev.mixed){
          /* keep Tokyo / Osaka / Nagoya in-frame at the closest clean slot */
        } else if(mustShow && ev && ev.ratio>=4.5 && !ev.mixed){
          /* keep */
        } else if(!mustShow){
          hideItem(it.el);
          return;
        } else if(!ev || ev.mixed || ev.ratio<4.5){
          if(!keepGroup){ hideItem(it.el); return; }
        }
      }
      if(JPKR && !full && !ev){
        hideItem(it.el);
        return;
      }
      if(JPKR && !full){
        const live=it.el.getBoundingClientRect();
        if(!inMapFull(live, mapBox)){
          hideItem(it.el);
          return;
        }
      }
      if(JPKR && (it.typ==='airport' || it.typ==='city' || it.typ==='capital')){
        nudgeOffMarks(it.el, marks, mapBox);
        const evAfter=consider(false);
        if(evAfter) ev=evAfter;
      }
      let onLandPinned=false;
      if(pinned){
        if(!(chosen && chosen.s)){
          applyPos(it.el, {x:it.ox, y:it.oy, anchor:it.ota});
        }
        if(!ev) ev=consider(false);
        let onLand=false;
        const ax=+(it.el.getAttribute('x'));
        const ay=+(it.el.getAttribute('y'));
        try{
          document.querySelectorAll('#g-st path.st').forEach(p=>{
            if(onLand) return;
            const pt=p.ownerSVGElement.createSVGPoint();
            pt.x=ax; pt.y=ay;
            if(p.isPointInFill(pt)) onLand=true;
          });
        }catch(e){}
        onLandPinned=onLand;
        if(onLand) it.el.classList.remove('lbl-on-dark');
        else if(ev && ev.onSea) it.el.classList.add('lbl-on-dark');
      }
      if(!(pinned && onLandPinned)){
        if(ev && ev.used==='light') it.el.classList.add('lbl-on-dark');
        else it.el.classList.remove('lbl-on-dark');
      }
      const box=it.el.getBoundingClientRect();
      if(it.group){
        const id=it.el.getAttribute('data-group');
      }
      const leadId=(it.el.id||'').replace(/^l-/,'');
      if(leadId){
        const lead=m.querySelector('#g-lb line.lbl-lead[data-a="'+leadId+'"]');
        if(lead && !lead.classList.contains('lbl-crowd')){
          lead.setAttribute('x2', it.el.getAttribute('x'));
          lead.setAttribute('y2', it.el.getAttribute('y'));
        }
      }
      if(!isShown(it.el)) return;
      (function nudgeUnity(){
        if(!JPKR) return;
        let box=it.el.getBoundingClientRect();
        let sm0=sampleBox(box, sea);
        if(!sm0 || !sm0.seaLandMix) return;
        const x0=+(it.el.getAttribute('x')), y0=+(it.el.getAttribute('y'));
        const a=it.el.getAttribute('text-anchor')||it.ota;
        const othersNow=placed.map(p=>p.el);
        const wantLand=sm0.landFrac>=0.5;
        const dirs=[[0,-1],[0,1],[-1,0],[1,0],[-1,-1],[1,-1],[-1,1],[1,1]];
        for(const step of [4,8,12,16,22,28,36,48,60]){
          for(const [dx,dy] of dirs){
            applyPos(it.el,{x:x0+dx*step, y:y0+dy*step, anchor:a});
            const b=it.el.getBoundingClientRect();
            if(!inMapFull(b, mapBox)) continue;
            let hit=false;
            for(const mk of marks){
              if(markIsOwn(it.el, mk)) continue;
              if(overlaps(b, mk.box, 0)){ hit=true; break; }
            }
            if(hit) continue;
            for(const ot of othersNow){
              if(!isShown(ot)) continue;
              if(overlaps(b, ot.getBoundingClientRect(), JPKR?4:3)){ hit=true; break; }
            }
            if(hit) continue;
            const sm1=sampleBox(b, sea);
            if(sm1 && !sm1.seaLandMix && (wantLand?sm1.landFrac>0.9:sm1.landFrac<0.12)){
              return;
            }
          }
        }
        applyPos(it.el,{x:x0,y:y0,anchor:a});
      })();
      const liveBox=it.el.getBoundingClientRect();
      const sm=sampleBox(liveBox, sea) || (ev && ev.sm) || null;
      if(JPKR && sm && sm.seaLandMix && !(pinnedEarly && !mobile && full)){
        hideItem(it.el);
        return;
      }
      let used, ratio, surface, mixed, onSea, cDark, cLight;
      if(sm){
        cDark=worst(sm.colors, dark);
        cLight=worst(sm.colors, light);
        onSea=sm.landFrac<0.12;
        mixed=!!sm.seaLandMix;
        if(onSea){ used='light'; ratio=cLight; surface='sea'; }
        else if(sm.goldFrac>0.55 && sm.landFrac>0.7){
          used=(cDark>=4.5 && cDark>=cLight)?'dark':'light';
          ratio=used==='dark'?cDark:cLight;
          surface='sel';
        } else { used='dark'; ratio=cDark; surface='land'; }
      } else if(ev){
        used=ev.used; ratio=ev.ratio; surface=ev.surface; mixed=ev.mixed;
        cDark=ev.cDark; cLight=ev.cLight; onSea=ev.onSea; 
      } else {
        used='dark'; ratio=0; surface='?'; mixed=true; cDark=0; cLight=0; onSea=false;
      }
      if(used==='light') it.el.classList.add('lbl-on-dark');
      else it.el.classList.remove('lbl-on-dark');
      ev=Object.assign({}, ev||{}, {sm, used, ratio, surface, mixed, onSea, cDark, cLight});
      placed.push({el:it.el, box:liveBox, ev});
      const inkRgb=(used==='light')?light:dark;
      let worstBg=null, worstR=99;
      if(sm && sm.colors){
        sm.colors.forEach(o=>{
          const r=contrast(inkRgb, o.c);
          if(r<worstR){ worstR=r; worstBg=o.c; }
        });
      }
      function hexOf(rgb){
        if(!rgb) return '';
        return '#'+rgb.map(n=>('0'+Math.round(n).toString(16)).slice(-2)).join('');
      }
      if(worstR<99) ratio=worstR;
      const item={
        text:(it.el.textContent||'').replace(/\s+/g,' ').trim(),
        type:it.typ,
        group:!!it.group,
        surface:surface||'?',
        fill: worstBg ? 'rgb('+worstBg.join(',')+')' : '',
        fillHex: hexOf(worstBg),
        ink: hexOf(inkRgb),
        landFrac: sm?Math.round(sm.landFrac*100)/100:null,
        lumRange: sm?Math.round(sm.lumRange*100)/100:null,
        pairC: sm?Math.round(sm.pairC*100)/100:null,
        varianceFail: !!(mixed),
        dark: cDark!=null?Math.round(cDark*100)/100:null,
        light: cLight!=null?Math.round(cLight*100)/100:null,
        used: used||'dark',
        ratio: Math.round((ratio||0)*100)/100,
        pass: !!(ratio>=4.5 && !mixed),
        passLand: !!(surface==='land' && ratio>=4.5 && used==='dark' && !mixed)
      };
      report.push(item);
    });

    if(_sampleRestore) _sampleRestore();
    window.PPC_labelContrast=report;
    return report;
  }

  CFG.afterLabels = function(){ applyContrast(); };
  window.PPC_applyLabelContrast=applyContrast;
  if(document.readyState==='complete') setTimeout(applyContrast, 60);
  else window.addEventListener('load', function(){ setTimeout(applyContrast, 60); });
})();
