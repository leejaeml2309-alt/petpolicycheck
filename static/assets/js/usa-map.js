function clampVB(v){const w=Math.min(975,Math.max(MINW,v[2])),h=w*610/975;
 const cx=v[0]+v[2]/2,cy=v[1]+v[3]/2;let x=cx-w/2,y=cy-h/2;
 x=Math.max(0,Math.min(975-w,x));y=Math.max(0,Math.min(610-h,y));return [x,y,w,h]}
const MAP_W=975;
function currentLbl(){
  return 'A';
}
function applyLblAttr(){
  const opt=currentLbl();
  window.__usaLbl=opt;
  document.documentElement.setAttribute('data-lbl',opt);
  const root=$('#usa-map')||document.getElementById('usa-map');
  if(root) root.setAttribute('data-lbl',opt);
  return opt;
}
function mountLabelLegend(){
  const root = $('#usa-map') || document.getElementById('usa-map');
  const host = root && root.querySelector('.mapcard');
  if(!host) return;
  const opt=applyLblAttr();
  const lang = ((document.documentElement.lang||'') + ' ' + (document.documentElement.getAttribute('data-lang')||'')).toLowerCase();
  let loc='en';
  try{ loc = (localStorage.getItem('ppc_lang')||loc); }catch(_){}
  if(/^\/de(\/|$)/.test(location.pathname) || /\bde\b/.test(lang)) loc='de';
  else if(/\bit\b/.test(lang) || loc==='it') loc='it';
  else if(/\bes\b/.test(lang) || loc==='es') loc='es';
  const L = loc==='es'
    ? {r:'Estados', c:'Ciudades', k:'Capital', a:'Aeropuertos', aria:'Leyenda de etiquetas'}
    : loc==='it'
    ? {r:'Stati', c:'Città', k:'Capitale', a:'Aeroporti', aria:'Legenda etichette'}
    : loc==='de'
    ? {r:'Bundesstaaten', c:'Städte', k:'Hauptstadt', a:'Flughäfen', aria:'Legende der Beschriftungen'}
    : {r:'States', c:'Cities', k:'Capital', a:'Airports', aria:'Label colour legend'};
  const sm={r:'TX',c:'Chicago',k:'Denver',a:'LAX'};
  let box=host.querySelector('.lbl-legend');
  if(!box){
    box=document.createElement('div');
    box.className='lbl-legend';
    box.setAttribute('role','note');
    host.appendChild(box);
  }
  box.setAttribute('aria-label', L.aria);
  box.innerHTML =
    '<span class="ll-r"><i aria-hidden="true">'+sm.r+'</i>'+L.r+'</span>'+
    '<span class="ll-c"><i aria-hidden="true">'+sm.c+'</i>'+L.c+'</span>'+
    '<span class="ll-k"><i aria-hidden="true">'+sm.k+'</i>'+L.k+'</span>'+
    '<span class="ll-a"><b aria-hidden="true">'+sm.a+'</b>'+L.a+'</span>';
}


function syncLabelScale(){
  const m=$('#map'); if(!m) return;
  const w=m.getBoundingClientRect().width||MAP_W;
  m.style.setProperty('--map-w-px', Math.max(1,w).toFixed(1));
}
function _box(el){
  const b=el.getBoundingClientRect();
  if(b.width<2||b.height<2||b.bottom<=0||b.right<=0) return null;
  return b;
}
function _overlap(a,b,pad){
  return !(a.right+pad<b.left || a.left-pad>b.right || a.bottom+pad<b.top || a.top-pad>b.bottom);
}
/* Hide secondary labels that collide. Priority (kept first): major airports,
   capitals, large region names, then minor cities, then small region names.
   Secondaries are allowed back when zoom gives them room. */
function _userPerPx(){
  const m=$('#map'); if(!m) return 1;
  const w=m.getBoundingClientRect().width||MAP_W;
  const vb=(m.viewBox&&m.viewBox.baseVal&&m.viewBox.baseVal.width)||MAP_W;
  return vb/w;
}
function _rememberPos(el){
  if(el.dataset.ox==null){
    el.dataset.ox=el.getAttribute('x')||'0';
    el.dataset.oy=el.getAttribute('y')||'0';
    el.dataset.ota=el.getAttribute('text-anchor')||'';
  }
}
function _restorePos(el){
  _rememberPos(el);
  el.setAttribute('x', el.dataset.ox);
  el.setAttribute('y', el.dataset.oy);
  if(el.dataset.ota) el.setAttribute('text-anchor', el.dataset.ota);
  else el.removeAttribute('text-anchor');
}
function _applyPos(el, s){
  el.setAttribute('x', (+s.x).toFixed(1));
  el.setAttribute('y', (+s.y).toFixed(1));
  if(s.anchor) el.setAttribute('text-anchor', s.anchor);
}
function _slotRing(x, y, anchors, maxPx){
  const u=_userPerPx();
  const out=[{x,y,anchor:anchors||null}];
  [16,28,42,58,76].filter(px=>maxPx==null||px<=maxPx).forEach(px=>{
    const d=px*u;
    [[d,0,'start'],[-d,0,'end'],[0,d,anchors],[0,-d,anchors],
     [d,d,'start'],[-d,d,'end'],[d,-d,'start'],[-d,-d,'end']].forEach(p=>{
      out.push({x:x+p[0], y:y+p[1], anchor:p[2]||anchors||null});
    });
  });
  return out;
}
function _overlapArea(a,b,pad){
  const x=Math.max(0, Math.min(a.right,b.right)-Math.max(a.left,b.left)+2*pad);
  const y=Math.max(0, Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)+2*pad);
  return (x>0 && y>0) ? x*y : 0;
}
function _scoreSlot(box, placed, pad){
  let n=0, area=0;
  for(const p of placed){
    const a=_overlapArea(box,p.box,pad);
    if(a){ n++; area+=a; }
  }
  return {n, area};
}
function _airportRank(code){
  const R={ATL:0,LAX:1,ORD:2,DFW:3,DEN:4,JFK:5,SFO:6,LAS:7,SEA:8,MIA:9,CLT:10,PHX:11,EWR:12,MCO:13,IAH:14,BOS:15,MSP:16,DTW:17,FLL:18,PHL:19,LGA:20,BWI:21,DCA:22,IAD:23,SLC:24,SAN:25,TPA:26,PDX:27,HNL:28,STL:30,MSY:31,IND:32,CLE:33,CVG:34,BDL:35,CHS:36,MKE:37,ABQ:38,OMA:39,BOI:40,OKC:41,PVD:42,BHM:43,DSM:44,BZN:45,PWM:46,LIT:47,ICT:48,FSD:49,BTV:50,MHT:51,JAN:52,FAR:53,JAC:54,CRW:55,ILG:56,
    LHR:0,LGW:1,MAN:2,STN:3,LTN:4,BHX:5,EDI:6,BRS:7,
    CDG:0,ORY:1,NCE:2,MRS:3,LYS:4,BSL:5,TLS:6,NTE:7,BVA:8,BOD:9,
    FRA:0,MUC:1,BER:2,DUS:3,HAM:4,CGN:5,STR:6,
    ICN:0,GMP:1,PUS:2,CJU:3,
    HND:0,NRT:1,KIX:2,ITM:3,FUK:4,CTS:5,NGO:6,OKA:7};
  const n=R[(code||'').toUpperCase()];
  return (n==null)?25:n;
}
const EXISTING_AP={LGA:1,EWR:1,JFK:1,LAX:1,SFO:1,ORD:1,MDW:1,MIA:1,IAH:1,HOU:1,DFW:1,SEA:1,DEN:1,ATL:1,ANC:1,HNL:1,LAS:1,PHX:1,SAN:1,SLC:1,AUS:1,MSP:1,DTW:1,BNA:1,CLT:1,MCO:1,TPA:1,FLL:1,BOS:1,PHL:1,BWI:1,IAD:1,DCA:1};
const _NEW_AP_SLOTS=[
  [8,3,'start'],[-8,3,'end'],[10,3,'start'],[-10,3,'end'],[12,3,'start'],[-12,3,'end'],
  [8,-8,'start'],[-8,-8,'end'],[12,-8,'start'],[-12,-8,'end'],
  [0,-14,'middle'],[0,16,'middle'],[0,-20,'middle'],[0,22,'middle'],
  [14,12,'start'],[-14,12,'end'],[16,-16,'start'],[-16,-16,'end'],
  [18,3,'start'],[-18,3,'end'],[8,16,'start'],[-8,16,'end'],
  [20,8,'start'],[-20,8,'end'],[24,3,'start'],[-24,3,'end']
];
let _packSuspended=false;
let _packAppliedKey='';
function _usaInk(userBox, ax, ay){
  return {dl:userBox.l-ax, dr:userBox.r-ax, dt:userBox.t-ay, db:userBox.btm-ay, w:userBox.w, h:userBox.h};
}
function _usaBoxAt(ax, ay, anchor, ink, sameAnchor){
  if(sameAnchor) return {l:ax+ink.dl, r:ax+ink.dr, t:ay+ink.dt, btm:ay+ink.db, w:ink.w, h:ink.h};
  const w=ink.w, h=ink.h, dt=ink.dt;
  let l;
  if(anchor==='end') l=ax-w;
  else if(anchor==='middle') l=ax-w/2;
  else l=ax;
  return {l:l, r:l+w, t:ay+dt, btm:ay+dt+h, w:w, h:h};
}
function _hitU(a,b,pad){
  pad=pad||0;
  return (Math.min(a.r,b.r)-Math.max(a.l,b.l)>pad && Math.min(a.btm,b.btm)-Math.max(a.t,b.t)>pad);
}

const _TA={s:'start',m:'middle',e:'end',start:'start',middle:'middle',end:'end'};
function _lblBucket(){
  const w=window.innerWidth||1280;
  return w<500?'390':(w<1360?'1280':'1440');
}
function _nearNE(){
  if(typeof isFull==='function' && isFull()) return false;
  const v=vb||[0,0,975,610];
  return Math.abs(v[0]-760)<8 && Math.abs(v[1]-70)<8 && Math.abs(v[2]-230)<8;
}
const LBL_REGIONS={
  ne:[760,70,230,176],
  chicago:[560,160,200,200*610/975],
  texas:[440,440,200,200*610/975],
  florida:[740,500,200,200*610/975],
  dc:[760,200,200,200*610/975]
};
function _nearRegion(){
  if(typeof isFull==='function' && isFull()) return null;
  const v=vb||[0,0,975,610];
  for(const name of Object.keys(LBL_REGIONS)){
    const b=LBL_REGIONS[name];
    if(Math.abs(v[0]-b[0])<10 && Math.abs(v[1]-b[1])<10 && Math.abs(v[2]-b[2])<10) return name;
  }
  return null;
}
function _planKey(){
  const opt=currentLbl();
  const b=_lblBucket();
  if(typeof isFull==='function' && isFull()) return [opt,b,'full'];
  const r=_nearRegion();
  return [opt,b,r||'zoom'];
}
function _setTxt(el, x, y, ta){
  if(x!=null) el.setAttribute('x', (+x).toFixed(1));
  if(y!=null) el.setAttribute('y', (+y).toFixed(1));
  if(ta){ const a=_TA[ta]||ta; if(a) el.setAttribute('text-anchor', a); }
}
function applyUsaLabelPlan(){
  const m=$('#map'); if(!m) return;
  const pack=window.USA_LBL_PLANS; if(!pack) return false;
  const [opt,bucket,mode]=_planKey();
  const plan=(pack[opt]&&(pack[opt][bucket+'|'+mode]||(mode==='zoom'&&pack[opt][bucket+'|full'])))||null;
  if(!plan) return false;
  m.querySelectorAll('#g-lb line.lbl-lead[data-temp="1"]').forEach(n=>n.remove());
  m.querySelectorAll('.lbl-crowd,.ct-crowd,.ap-crowd,.ap-name-crowd,.ap-code-crowd').forEach(n=>n.classList.remove('lbl-crowd','ct-crowd','ap-crowd','ap-name-crowd','ap-code-crowd'));
  const st=plan.st||{};
  m.querySelectorAll('#g-lb text.lbl').forEach(t=>{
    const id=(t.id||'').replace(/^l-/,'');
    const p=st[id];
    const call=t.closest('.st-callout');
    if(!p || p[3]){
      t.classList.add('lbl-crowd');
      if(call) call.setAttribute('display','none');
      return;
    }
    if(call) call.removeAttribute('display');
    _setTxt(t, p[0], p[1], p[2]);
    if(p[4] && t.dataset.full) t.textContent=t.dataset.full;
    else if(t.dataset.abbr) t.textContent=t.dataset.abbr;
  });
  const leads=plan.lead||{};
  m.querySelectorAll('#g-lb line.lbl-lead').forEach(lead=>{
    const id=lead.getAttribute('data-a')||'';
    const p=leads[id];
    if(!p || p[4]){ lead.classList.add('lbl-crowd'); return; }
    lead.setAttribute('x1', p[0]); lead.setAttribute('y1', p[1]);
    lead.setAttribute('x2', p[2]); lead.setAttribute('y2', p[3]);
  });
  const cts=plan.ct||{};
  m.querySelectorAll('#g-ct .ct').forEach(g=>{
    if(g.classList.contains('hide-lbl') && !g.classList.contains('sample')) return;
    const t=g.querySelector('text'); if(!t) return;
    const key=g.dataset.k||t.textContent;
    const p=cts[key]||cts[t.textContent];
    if(!p || p[3]){ g.classList.add('ct-crowd'); return; }
    _setTxt(t, p[0], p[1], p[2]);
  });
  const aps=plan.ap||{}, apn=plan.apn||{}, chips=plan.chip||{};
  m.querySelectorAll('#g-ap .ap').forEach(g=>{
    const code=g.dataset.code;
    const codeEl=g.querySelector('text.map-label, text:not(.map-name)');
    const nameEl=g.querySelector('text.map-name');
    const chip=g.querySelector('rect.ap-chip');
    const p=aps[code];
    if(codeEl){
      if(!p || p[3]) codeEl.classList.add('ap-code-crowd');
      else _setTxt(codeEl, p[0], p[1], p[2]);
    }
    const n=apn[code];
    if(nameEl){
      if(!n || n[3]) nameEl.classList.add('ap-name-crowd');
      else _setTxt(nameEl, n[0], n[1], n[2]);
    }
    if(chip){
      const c=chips[code];
      if(c && !c[4]){
        chip.setAttribute('x', c[0]); chip.setAttribute('y', c[1]);
        chip.setAttribute('width', c[2]); chip.setAttribute('height', c[3]);
        chip.style.display='';
      } else {
        chip.setAttribute('width','0'); chip.setAttribute('height','0');
      }
    }
  });
  return true;
}
function packUsaLabelsFallback(){
  /* Deterministic user-space packer: precomputed glyph metrics, no layout reads. */
  const m=$('#map'); if(!m) return;
  const metAll=window.USA_LBL_METRICS; if(!metAll) return;
  const opt=currentLbl();
  const met=metAll[opt]; if(!met) return;
  const bucket=_lblBucket();
  const zoomed=!(typeof isFull==='function' && isFull());
  const sizes=met.size[bucket][zoomed?'zoom':'rest'];
  const mapW=m.clientWidth||met.mapW[bucket]||830;
  const v=vb||[0,0,975,610];
  const sx=mapW/v[2]; /* screen px per user unit */
  const k=v[2]/975;
  const iconR=11.3137*k;
  function boxAt(ax,ay,wPx,ascPx,descPx,anchor){
    const w=wPx/sx, asc=ascPx/sx, desc=descPx/sx;
    let l=ax;
    if(anchor==='end') l=ax-w;
    else if(anchor==='middle') l=ax-w/2;
    return {l:l, r:l+w, t:ay-asc, btm:ay+desc};
  }
  function hit(a,b,pad){
    return (Math.min(a.r,b.r)-Math.max(a.l,b.l)>pad && Math.min(a.btm,b.btm)-Math.max(a.t,b.t)>pad);
  }
  const pad=0.4;
  const placed=[];
  const icons=[];
  m.querySelectorAll('#g-ap .ap').forEach(g=>{
    const tr=g.getAttribute('transform')||'';
    const xy=/translate\(\s*([-\d.]+)[,\s]+([-\d.]+)\s*\)/.exec(tr);
    if(!xy) return;
    const x=+xy[1], y=+xy[2];
    const box={l:x-iconR,r:x+iconR,t:y-iconR,btm:y+iconR};
    icons.push({code:g.dataset.code,x,y,box});
    placed.push({box, kind:'icon', code:g.dataset.code});
  });
  m.querySelectorAll('#g-ct .ct circle:not(.ring)').forEach(c=>{
    const x=+c.getAttribute('cx'), y=+c.getAttribute('cy'), r=+(c.getAttribute('r')||3);
    placed.push({box:{l:x-r,r:x+r,t:y-r,btm:y+r}, kind:'dot'});
  });
  m.querySelectorAll('#g-lb rect[id^="cb-"]').forEach(r=>{
    const x=+r.getAttribute('x'), y=+r.getAttribute('y'), w=+r.getAttribute('width'), h=+r.getAttribute('height');
    placed.push({box:{l:x,r:x+w,t:y,btm:y+h}, kind:'pill'});
  });
  function overlaps(box, skipCode){
    for(const p of placed){
      if(skipCode && p.code===skipCode) continue;
      if(hit(box,p.box,pad)) return true;
    }
    return false;
  }
  const SLOTS=[[8,3,'start'],[-8,3,'end'],[10,-8,'start'],[-10,-8,'end'],[0,-12,'middle'],[0,14,'middle'],[14,10,'start'],[-14,10,'end'],[16,3,'start'],[-16,3,'end'],[0,-18,'middle'],[20,6,'start'],[-20,6,'end']];
  m.querySelectorAll('#g-lb line.lbl-lead[data-temp="1"]').forEach(n=>n.remove());
  m.querySelectorAll('.lbl-crowd,.ct-crowd,.ap-crowd,.ap-name-crowd,.ap-code-crowd').forEach(n=>n.classList.remove('lbl-crowd','ct-crowd','ap-crowd','ap-name-crowd','ap-code-crowd'));

  /* Restore authored, then try place. */
  function tryText(el, origX, origY, origTa, wPx, asc, desc, skipCode, isNew){
    const slots=[[0,0,origTa]].concat(SLOTS);
    for(const s of slots){
      const ta=s[2]||origTa||'start';
      const x=origX+s[0], y=origY+s[1];
      const box=boxAt(x,y,wPx,asc,desc,ta);
      if(box.l<1||box.t<1||box.r>974||box.btm>609) continue;
      if(overlaps(box, skipCode)) continue;
      _setTxt(el,x,y,ta);
      placed.push({box, code:skipCode});
      return true;
    }
    return false;
  }
  /* Cities first (few), then airports by rank, then states. */
  const scale= (px)=>px; /* already screen px at this bucket/zoom */
  const stW=met.w.st||{}, ctW=met.w.ct||{}, apW=met.w.ap||{}, apnW=met.w.apn||{};
  const stA=met.asc, stD=met.desc;
  m.querySelectorAll('#g-ct .ct').forEach(g=>{
    if(g.classList.contains('hide-lbl') && !g.classList.contains('sample')) return;
    const t=g.querySelector('text'); if(!t) return;
    _restorePos(t);
    const ox=+(t.dataset.ox!=null?t.dataset.ox:t.getAttribute('x'));
    const oy=+(t.dataset.oy!=null?t.dataset.oy:t.getAttribute('y'));
    const ta=t.dataset.ota||t.getAttribute('text-anchor')||'start';
    const key=g.dataset.k||t.textContent;
    const w=ctW[key]||ctW[t.textContent]||(t.textContent.length*sizes.ct*0.56);
    const kfont=sizes.ct/(met.ref.ct||8);
    if(!tryText(t,ox,oy,ta,w*kfont,(stA.ct||7)*kfont,(stD.ct||3)*kfont,null)) g.classList.add('ct-crowd');
  });
  const apList=[...m.querySelectorAll('#g-ap .ap')].sort((a,b)=>_airportRank(a.dataset.code)-_airportRank(b.dataset.code));
  apList.forEach(g=>{
    const code=g.dataset.code;
    const pin=icons.find(i=>i.code===code);
    const codeEl=g.querySelector('text.map-label, text:not(.map-name)');
    const nameEl=g.querySelector('text.map-name');
    if(codeEl){
      _restorePos(codeEl);
      const ox=+(codeEl.dataset.ox!=null?codeEl.dataset.ox:codeEl.getAttribute('x'));
      const oy=+(codeEl.dataset.oy!=null?codeEl.dataset.oy:codeEl.getAttribute('y'));
      const ta=codeEl.dataset.ota||codeEl.getAttribute('text-anchor')||'start';
      const kf=sizes.ap/(met.ref.ap||7.5);
      const w=(apW[code]||22)*kf;
      const ax=(pin?pin.x:0)+ox, ay=(pin?pin.y:0)+oy;
      /* tryText uses absolute? airport text is in the pin group — x/y are relative */
      const slots=[[ox,oy,ta]].concat(SLOTS.map(s=>[s[0],s[1],s[2]]));
      let found=false;
      for(const s of slots){
        const box=boxAt(pin.x+s[0], pin.y+s[1], w, (stA.ap||7)*kf, (stD.ap||3)*kf, s[2]||ta);
        if(box.l<1||box.r>974||box.t<1||box.btm>609) continue;
        if(overlaps(box, code)) continue;
        _setTxt(codeEl,s[0],s[1],s[2]||ta);
        placed.push({box, code});
        found=true; break;
      }
      if(!found) codeEl.classList.add('ap-code-crowd');
    }
    if(nameEl){
      if(!zoomed){ nameEl.classList.add('ap-name-crowd'); return; }
      _restorePos(nameEl);
      const ox=+(nameEl.dataset.ox!=null?nameEl.dataset.ox:nameEl.getAttribute('x'));
      const oy=+(nameEl.dataset.oy!=null?nameEl.dataset.oy:nameEl.getAttribute('y'));
      const ta=nameEl.dataset.ota||nameEl.getAttribute('text-anchor')||'start';
      const kf=sizes.name/(met.ref.name||7);
      const w=(apnW[code]||40)*kf;
      const slots=[[ox,oy,ta],[ox,oy+10,ta],[-8,14,'end'],[8,14,'start']];
      let found=false;
      for(const s of slots){
        const box=boxAt(pin.x+s[0], pin.y+s[1], w, (stA.apn||6)*kf, (stD.apn||2)*kf, s[2]||ta);
        if(overlaps(box, code)) continue;
        _setTxt(nameEl,s[0],s[1],s[2]||ta);
        placed.push({box, code}); found=true; break;
      }
      if(!found) nameEl.classList.add('ap-name-crowd');
    }
  });
  m.querySelectorAll('#g-lb text.lbl').forEach(t=>{
    _restorePos(t);
    const id=(t.id||'').replace(/^l-/,'');
    if(t.dataset.abbr) t.textContent=(zoomed && opt==='C' && t.dataset.full && !['VT','NH','MA','RI','CT','NJ','DE','MD'].includes(id))?t.dataset.full:t.dataset.abbr;
    const ox=+(t.dataset.ox!=null?t.dataset.ox:t.getAttribute('x'));
    const oy=+(t.dataset.oy!=null?t.dataset.oy:t.getAttribute('y'));
    const ta=t.dataset.ota||t.getAttribute('text-anchor')||'middle';
    const key=t.textContent;
    const kf=sizes.st/(met.ref.st||10.5);
    const table=(zoomed && opt==='C' && t.textContent.length>3)?(met.w.stFull||{}):stW;
    const w=(table[id]||table[key]||(key.length*sizes.st*0.7))*kf;
    if(!tryText(t,ox,oy,ta,w,(stA.st||8)*kf,(stD.st||3)*kf,null)) t.classList.add('lbl-crowd');
  });
}
function resolveLabelOverlaps(){
  if(applyUsaLabelPlan()) return;
  packUsaLabelsFallback();
}
let _lblRaf=0;
function refreshLabels(){
  if(_packSuspended) return;
  if(!applyUsaLabelPlan()){
    /* fallback packer is math-only; run sync so zoom stays under 50ms */
    packUsaLabelsFallback();
  }
}

function applyViewBox(v){vb=v.slice();const m=$("#map");if(!m)return;
 const k=vb[2]/975;m.setAttribute("viewBox",vb.map(n=>+n.toFixed(2)).join(" "));m.style.setProperty("--k",k.toFixed(3));m.style.setProperty("--kt",Math.sqrt(k).toFixed(3));
 /* airport marks keep their screen size: scale each group around its own point (labels: fixed px in CSS) */
 m.querySelectorAll("#g-ap .ap .ap-mark").forEach(g=>{g.setAttribute("transform",k>0.999?"":"scale("+k.toFixed(4)+")")});
 syncZoomUI()}
function isFull(){return vb[2]>=974.5}
function syncZoomUI(){const m=$("#map");if(!m)return;const full=isFull();m.classList.toggle("is-zoomed",!full);
 const zi=$("#zin"),zo=$("#zout"),zr=$("#zreset");
 if(zi)zi.disabled=vb[2]<=MINW+0.5;if(zo)zo.disabled=full;if(zr)zr.disabled=full;
 refreshLabels()}
function stopAnim(){if(animId){cancelAnimationFrame(animId);animId=0}}
function animateTo(t,ms){stopAnim();t=clampVB(t);const f=vb.slice(),t0=performance.now();ms=ms||350;
 _packSuspended=true;
 (function an(n){const k=Math.min(1,(n-t0)/ms),e=k*(2-k);applyViewBox(f.map((v,i)=>v+(t[i]-v)*e));if(k<1){animId=requestAnimationFrame(an)}else{animId=0;_packSuspended=false;refreshLabels()}})(t0)}
/* zoomTo(a): phones (<=900) zoom to the selected state as before. With no state and no selection
   (Show all states) the view goes back to FULL. On desktop a selection keeps the user's free-zoom view. */
function zoomTo(a){let t=null;
 if(a&&innerWidth<=900){const b=$("#s-"+a).getBBox();const w=Math.max(b.width*1.5,220),h=Math.max(b.height*1.5,150);const sc=Math.max(w/975,h/610);const W=975*sc,H=610*sc;t=[b.x+b.width/2-W/2,b.y+b.height/2-H/2,W,H];}
 else if(!cur)t=FULL;
 $("#reset").hidden=!cur;
 if(t)animateTo(t,350);}
/* zoom by factor f (>1 = in) keeping SVG point (px,py) under the same screen spot */
function zoomAt(px,py,f,ms){const w=Math.min(975,Math.max(MINW,vb[2]/f)),s=w/vb[2];
 const t=[px-(px-vb[0])*s,py-(py-vb[1])*s,w,w*610/975];if(ms)animateTo(t,ms);else{stopAnim();applyViewBox(clampVB(t))}}
function hilite(a,key,apCode){zoomTo(a&&a!=="DC"?a:null);
 document.querySelectorAll(".st.sel,.lbl.sel,.ct.sel,.ap.sel").forEach(e=>e.classList.remove("sel"));
 document.querySelectorAll("#grid button.sel").forEach(e=>e.classList.remove("sel"));
 document.querySelectorAll(".ct[data-s]").forEach(e=>{if(!e.classList.contains("sample"))e.classList.toggle("hide-lbl",e.dataset.s!==a)});
 TINY.forEach(t=>{const r=$("#cb-"+t);if(!r)return;r.setAttribute("fill",t===a?"#6d5a2c":tierFill(t));r.classList.toggle("sel",t===a)});
 if(a){$("#s-"+a)?.classList.add("sel");$("#l-"+a)?.classList.add("sel");document.querySelector(`#grid button[data-a="${a}"]`)?.classList.add("sel")}
 if(key)document.querySelector(`.ct[data-k="${CSS.escape(key)}"]`)?.classList.add("sel");
 document.querySelectorAll(".ap,.ap-link").forEach(el=>{
  const mine=!a || (el.dataset.states||"").split(" ").includes(a);
  el.classList.toggle("dim", !!a && !mine);
  const cityHot=!!(key && el.dataset.citykey===key);
  const stateHot=!!a && !key && mine;
  el.classList.toggle("hot", cityHot || stateHot);
 });
 if(apCode) document.querySelector(`.ap[data-code="${CSS.escape(apCode)}"]`)?.classList.add("sel");
 $("#pick").value=a&&a!=="DC"?a:"";
}
function cityButtons(a){return `<div class="citylist">${GEO[a].cities.map(c=>`<button data-s="${a}" data-city="${esc(c.n)}" class="${SAMPLE[a+'|'+c.n]?'sample':''}">${esc(c.n)}${c.cap?" ★cap":""}</button>`).join("").replace(/ ★cap/g," (capital)")}</div>`}
function setHash(a,n){
 const h=n?a+"/"+encodeURIComponent(n):a;
 if(decodeURIComponent(location.hash.replace(/^#/,""))!== (n?a+"/"+n:a)) history.replaceState(null,"","#"+h);
}

/* California state panel only: Transcontinental Pet Movers partner card. */
function caPetMoverCard(){
 const lang=transconUiLang();
 const h2=lang==="it"?"Partner per il trasporto di animali":lang==="es"?"Socio de transporte de mascotas":"Pet mover partner";
 const desc=lang==="it"?"trasferimento di animali da San Francisco (SFO) e Los Angeles (Inglewood, LAX)":lang==="es"?"reubicación de mascotas desde San Francisco (SFO) y Los Angeles (Inglewood, LAX)":"pet relocation from San Francisco (SFO) and Los Angeles (Inglewood, LAX)";
 const logo="https://transconpet.com/?utm_source=petpolicycheck&utm_medium=referral&utm_campaign=partner_listing&utm_content=logo";
 const text="https://transconpet.com/?utm_source=petpolicycheck&utm_medium=referral&utm_campaign=partner_listing&utm_content=text";
 const src="/assets/partners/transcontinental-pet-movers";
 return `<aside class="pet-mover-partner" id="pet-mover-partner"><h3>${esc(h2)}</h3><a class="partner-logo-link" href="${esc(logo)}" target="_blank" rel="sponsored noopener"><picture><source type="image/webp" srcset="${src}.webp"><img src="${src}.png" width="160" height="160" alt="Transcontinental Pet Movers logo"></picture></a><p><a href="${esc(text)}" target="_blank" rel="sponsored noopener">Transcontinental Pet Movers (TC Pet Movers)</a> — ${esc(desc)}</p></aside>`;
}
function selectState(a){
 cur={a};hilite(a);setHash(a);
 const s=GEO[a];
 render(header(a,s.name,`${a} · ${ruleKind(a)} · state law portal`)+
  `<h4 style="font:600 .72rem var(--text);letter-spacing:.1em;text-transform:uppercase;color:var(--gold);margin:4px 0 0">Main cities</h4>${cityButtons(a)}`+
  (a==="CA"?caPetMoverCard():"")+
  lawSection(a)+roadSection(a)+planeSection(a)+hotelSection(s.name)+groomSection());
}
function selectDC(){cur={a:"DC"};hilite(null);setHash("DC");
 render(header("DC","Washington, DC","DC · "+ruleKind("DC")+" · state law portal")+lawSection("DC")+roadSection("DC")+planeSection("DC")+hotelSection("Washington, DC")+groomSection());}
function cityHotelExtra(a,n){
 const S=SAMPLE[a+"|"+n]; if(!S) return "";
 let extra="";
 if(S.guide) extra+=lk("📍","PetPolicyCheck: pet-friendly hotels in "+n,"Chain rules, luxury hotels, dog parks",siteUrl(S.guide),"off").replace("Official","Site");
 return extra;
}
function selectCity(a,n){
 const key=a+"|"+n, S=SAMPLE[key], st=GEO[a];cur={a,n};hilite(a,key);setHash(a,n);
 const crumbs=`<p class="crumbs"><button data-state="${a}">← ${esc(st.name)}</button> · ${esc(n)}</p>`;
 const chips=airportChips(airportsFor(a,n), usaUi().serving(n));
 if(!S){
  render(crumbs+header(a,n,`${esc(st.name)} · city`)+chips+lawSection(a,true,n)+roadSection(a)+planeSection(a,n)+hotelSection(n+", "+a)+groomSection());
  return;
 }
 const L=arr=>arr.map(x=>lk(...x)).join("");
 const city=`<h4>Taxis &amp; rideshare</h4><div class="links">${L(S.taxi)}${RIDES}</div>`+
  `<h4>Trains</h4><p>${AMTRAK_NOTE}</p><div class="links">${lk("🚆","Amtrak: "+S.amtrak[1],"Station page · then book on amtrak.com","https://www.amtrak.com/stations/"+S.amtrak[0],"off")}${lk("🐾","Amtrak: Pets on trains","Reserve the pet spot when you book","https://www.amtrak.com/pets","off")}${L(S.rail)}</div>`+
  `<h4>Buses &amp; local transit</h4><div class="links">${L(S.transit)}${lk("🚌","Greyhound","Service animals only, no pets (carrier policy; verify)","https://www.greyhound.com/","off")}</div>`;
 render(crumbs+header(a,n,`${esc(st.name)} · city booking guide`)+
  `<div class="btnrow" style="margin:0 0 4px"><button class="btn ghost" data-state="${a}">State laws for ${esc(st.name)}</button></div>`+
  chips+lawSection(a,true,n)+roadSection(a,city)+planeSection(a,n)+hotelSection(S.q,cityHotelExtra(a,n))+groomSection());
}
function airHead(ap){
 return `<div class="ph"><div class="ap-badge" aria-hidden="true"><svg viewBox="0 0 24 24" width="28" height="28"><path fill="#d9b765" d="${PLANE}"/></svg><b>${esc(ap.code)}</b></div><div><h2>${esc(ap.code)} — ${esc(ap.metroCity)}</h2><div class="sub">${esc(ap.name)} · ${esc(GEO[ap.placeState].name)}</div></div></div>`;
}
function selectAirport(code){
 const ap=airportByCode(code); if(!ap) return;
 step=3;
 const key=ap.metroState+"|"+ap.metroCity;
 cur={a:ap.metroState, n:ap.metroCity, ap:code};
 hilite(ap.metroState, key, code);
 setHash(ap.metroState, code);
 const st=GEO[ap.metroState];
 const crumbs=`<p class="crumbs"><button type="button" data-state="${ap.metroState}">← ${esc(st.name)}</button> · <button type="button" data-s="${ap.metroState}" data-city="${esc(ap.metroCity)}">${esc(ap.metroCity)}</button> · ${esc(ap.code)}</p>`;
 const q=SAMPLE[key]?SAMPLE[key].q:ap.metroCity+", "+ap.placeState;
 render(crumbs+airHead(ap)+
  `<div class="btnrow" style="margin:0 0 4px"><button type="button" class="btn" data-s="${ap.metroState}" data-city="${esc(ap.metroCity)}">${esc(usaUi().cityPanel(ap.metroCity))}</button></div>`+
  lawSection(ap.placeState,true,ap.metroCity,ap.metroState)+airportRoad(ap)+airportPlane(ap)+hotelSection(q,cityHotelExtra(ap.metroState, ap.metroCity))+groomSection());
 applyStep(true);
}

function usaUiLang(){
  const lang=((document.documentElement.lang||'')+' '+(document.documentElement.getAttribute('data-lang')||'')+' '+(document.documentElement.getAttribute('data-ppc-locale')||'')).toLowerCase();
  let loc='en';
  try{ loc=localStorage.getItem('ppc_lang')||loc; }catch(_){}
  if(/^\/de(?:\/|$)/.test(location.pathname) || /\bde\b/.test(lang)) return 'de';
  if(/\/it(?:\/|$)/.test(location.pathname) || /\bit\b/.test(lang) || loc==='it') return 'it';
  if(/\/es(?:\/|$)/.test(location.pathname) || /\bes\b/.test(lang) || loc==='es') return 'es';
  if(/\/fr(?:\/|$)/.test(location.pathname) || /\bfr\b/.test(lang) || loc==='fr') return 'fr';
  return 'en';
}
function usaUi(){
  const loc=usaUiLang();
  const pack={
    en:{
      pickTitle:'Pick a state or city',
      pickLead:'Click any of the 50 states on the map (or use the list) to open its law portal. Gold cities have the full booking guide. Plane marks are that city’s airports:',
      journey:'Journey order: 1 vet + laws → 2 road/rail → 3 plane → 4 hotel → 5 grooming.',
      choose:'Choose a state…',
      fifty:'50 States',
      serving:n=>'Airports serving '+n,
      cityPanel:n=>'City panel: taxis and hotels in '+n,
      zoomIn:'Zoom in', zoomOut:'Zoom out', resetView:'Reset map view'
    },
    es:{
      pickTitle:'Elija un estado o una ciudad',
      pickLead:'Haga clic en cualquiera de los 50 estados del mapa (o use la lista) para abrir su portal normativo. Las ciudades en dorado tienen la guía de reserva completa. Las marcas de avión son los aeropuertos de esa ciudad:',
      journey:'Orden del viaje: 1 veterinario y leyes → 2 carretera/tren → 3 avión → 4 hotel → 5 peluquería.',
      choose:'Elija un estado…',
      fifty:'50 estados',
      serving:n=>'Aeropuertos que sirven a '+n,
      cityPanel:n=>'Panel de la ciudad: taxis y hoteles en '+n,
      zoomIn:'Acercar', zoomOut:'Alejar', resetView:'Restablecer el mapa'
    },
    it:{
      pickTitle:'Scegli uno Stato o una città',
      pickLead:'Clicca uno dei 50 Stati sulla mappa (o usa l’elenco) per aprire il suo portale normativo. Le città in oro hanno la guida di prenotazione completa. I segni dell’aereo sono gli aeroporti di quella città:',
      journey:'Ordine del viaggio: 1 veterinario e leggi → 2 strada/treno → 3 aereo → 4 hotel → 5 toelettatura.',
      choose:'Scegli uno Stato…',
      fifty:'50 Stati',
      serving:n=>'Aeroporti al servizio di '+n,
      cityPanel:n=>'Pannello città: taxi e hotel a '+n,
      zoomIn:'Ingrandisci', zoomOut:'Riduci', resetView:'Reimposta la mappa'
    },
    fr:{
      pickTitle:'Choisissez un État ou une ville',
      pickLead:'Cliquez sur l’un des 50 États de la carte (ou utilisez la liste) pour ouvrir son portail législatif. Les villes en or ont le guide de réservation complet. Les pictogrammes d’avion indiquent les aéroports de cette ville :',
      journey:'Ordre du voyage : 1 vétérinaire + lois → 2 route/train → 3 avion → 4 hôtel → 5 toilettage.',
      choose:'Choisissez un État…',
      fifty:'50 États',
      serving:n=>'Aéroports desservant '+n,
      cityPanel:n=>'Panneau de la ville : taxis et hôtels à '+n,
      zoomIn:'Zoom avant', zoomOut:'Zoom arrière', resetView:'Réinitialiser la carte'
    },
    de:{
      pickTitle:'Wählen Sie einen Bundesstaat oder eine Stadt',
      pickLead:'Klicken Sie auf einen der 50 Bundesstaaten der Karte (oder nutzen Sie die Liste), um sein Rechtsportal zu öffnen. Goldene Städte haben den vollständigen Buchungsleitfaden. Die Flugzeugsymbole markieren die Flughäfen dieser Stadt:',
      journey:'Reihenfolge der Reise: 1 Tierarzt + Gesetze → 2 Straße/Bahn → 3 Flug → 4 Hotel → 5 Pflege.',
      choose:'Wählen Sie einen Bundesstaat…',
      fifty:'50 Bundesstaaten',
      serving:n=>'Flughäfen für '+n,
      cityPanel:n=>'Stadt-Panel: Taxis und Hotels in '+n,
      zoomIn:'Vergrößern', zoomOut:'Verkleinern', resetView:'Kartenansicht zurücksetzen'
    }
  };
  return pack[loc]||pack.en;
}

function empty(){
 const U=usaUi();
 $("#panel").innerHTML=`<div class="empty"><div class="big">${U.pickTitle}</div><p>${U.pickLead}</p><div class="citylist">${Object.keys(SAMPLE).map(k=>{const[a,n]=k.split("|");return `<button class="sample" data-s="${a}" data-city="${esc(n)}">${esc(n)}</button>`}).join("")}</div><div class="citylist">${AIRPORTS.filter(ap=>ap.pets&&SAMPLE[ap.metroState+"|"+ap.metroCity]).map(ap=>`<button type="button" class="apbtn" data-ap="${esc(ap.code)}">${esc(ap.code)} — ${esc(ap.metroCity)}</button>`).join("")}</div><p class="disc">${U.journey}</p></div>`;
 $("#panel").querySelectorAll("[data-city]").forEach(b=>b.onclick=()=>selectCity(b.dataset.s,b.dataset.city));
 $("#panel").querySelectorAll("[data-ap]").forEach(b=>b.onclick=()=>selectAirport(b.dataset.ap));
}
function applyStep(scroll){
 document.querySelectorAll("#steps button").forEach(b=>b.setAttribute("aria-pressed",+b.dataset.step===step));
 const secs=document.querySelectorAll("#panel .sec");
 secs.forEach(s=>s.classList.toggle("focus",+s.dataset.sec===step));
 if(scroll){const t=document.querySelector(`#panel .sec[data-sec="${step}"]`);if(t){const p=$("#panel");if(innerWidth>900)p.scrollTo({top:p.scrollTop+t.getBoundingClientRect().top-p.getBoundingClientRect().top-6,behavior:"smooth"});else t.scrollIntoView({behavior:"smooth",block:"start"})}}
}
document.querySelectorAll("#steps button").forEach(b=>b.onclick=()=>{step=+b.dataset.step;if(!cur)selectCity("NY","New York City");applyStep(true)});
/* ---------- init ---------- */
/* Back to the full multi-state view: clear selection, zoom, hash and panel. */
function showAllStates(){
 cur=null;hilite(null);/* hilite(null) also runs zoomTo(null) */
 if(location.hash)try{history.replaceState(null,"",location.pathname+location.search)}catch(_){location.hash=""}
 empty();$("#reset").hidden=true;$("#pick").value="";
}
{const r=$("#reset");r.classList.remove("ghost");r.classList.add("reset-all");r.onclick=showAllStates;}
/* capture phase: runs before the site-menu Escape handler, so an open menu keeps Escape */
window.addEventListener("keydown",e=>{
 if(e.key!=="Escape"||!cur||e.defaultPrevented)return;
 const sm=document.getElementById("site-menu");if(sm&&sm.classList.contains("open"))return;
 showAllStates();
},true);
$("#map").addEventListener("click",e=>{if(cur&&e.target===e.currentTarget)showAllStates()});
/* ---------- free zoom & pan (mirrors the world map) ----------
   Desktop: mouse wheel over the map (no modifier needed; trackpad pinch too) zooms toward the cursor; drag moves the map.
   Wheel outside the map scrolls the page as usual (the listener sits on the map SVG only).
   Touch: two fingers pinch-zoom + move; one finger sideways moves the map; one finger vertical keeps page scroll.
   +/- buttons zoom around the view center; the reset-view button returns to the full map without clearing the selection. */
(function initFreeZoom(){const m=$("#map");if(!m)return;
 /* wrapper so the zoom buttons can sit over the map (injected: no HTML change needed) */
 let wrap=m.parentNode;if(!wrap.classList.contains("mapwrap")){wrap=document.createElement("div");wrap.className="mapwrap";m.parentNode.insertBefore(wrap,m);wrap.appendChild(m)}
 if(!$("#zin")){const z=document.createElement("div");z.className="zoom";z.setAttribute("role","group");z.setAttribute("aria-label","Map zoom");
  {const U=usaUi(); z.innerHTML='<button type="button" id="zin" aria-label="'+U.zoomIn+'" title="'+U.zoomIn+'">+</button><button type="button" id="zout" aria-label="'+U.zoomOut+'" title="'+U.zoomOut+'">&minus;</button><button type="button" id="zreset" aria-label="'+U.resetView+'" title="'+U.resetView+'">&#8634;</button>';}
  wrap.appendChild(z)}
 const ctr=()=>[vb[0]+vb[2]/2,vb[1]+vb[3]/2];
 $("#zin").onclick=()=>{const c=ctr();zoomAt(c[0],c[1],1.6,250)};
 $("#zout").onclick=()=>{const c=ctr();zoomAt(c[0],c[1],1/1.6,250)};
 $("#zreset").onclick=()=>animateTo(FULL,300);/* view only: selection stays (Show all states clears it) */
 /* usage hint (only if the page HTML does not already carry it) */
 const note=document.querySelector("#usa-map .mapnote");
 if(note&&!note.querySelector(".mhint")){note.insertAdjacentHTML("afterbegin",'<span class="mhint">Pinch with two fingers to zoom, swipe sideways to move the map. </span><span class="dhint">Scroll over the map to zoom, drag to move. </span>')}
 syncZoomUI();
 const toSVG=(cx,cy)=>{const r=m.getBoundingClientRect();return [vb[0]+(cx-r.left)*vb[2]/r.width,vb[1]+(cy-r.top)*vb[3]/r.height]};
 const perPx=()=>vb[2]/(m.getBoundingClientRect().width||975);
 /* swallow the click that ends a drag, so it neither selects a state nor runs Show all states */
 let eatClick=false;
 m.addEventListener("click",e=>{if(eatClick){eatClick=false;e.stopPropagation();e.preventDefault()}},true);
 const armEat=()=>{eatClick=true;setTimeout(()=>{eatClick=false},350)};
 /* wheel over the map zooms (no Ctrl/Cmd needed). Bound to the map SVG only, so the page still scrolls elsewhere.
    Zooming out while already at the full view is let through so the page can scroll past the map. */
 m.addEventListener("wheel",e=>{if(e.deltaY>0&&isFull()&&!(e.ctrlKey||e.metaKey))return;e.preventDefault();
  const dy=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?400:1);const p=toSVG(e.clientX,e.clientY);
  zoomAt(p[0],p[1],Math.exp(-Math.max(-300,Math.min(300,dy))*0.0025))},{passive:false});
 /* mouse / pen drag (touch handled below) */
 let drag=null;const TH=6;
 m.addEventListener("pointerdown",e=>{if(e.pointerType==="touch"||e.button)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,v:vb.slice(),k:perPx(),on:false}});
 m.addEventListener("pointermove",e=>{if(!drag||e.pointerId!==drag.id)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
  if(!drag.on){if(Math.hypot(dx,dy)<TH)return;drag.on=true;stopAnim();m.classList.add("is-panning");try{m.setPointerCapture(e.pointerId)}catch(_){}}
  applyViewBox(clampVB([drag.v[0]-dx*drag.k,drag.v[1]-dy*drag.k,drag.v[2],drag.v[3]]))});
 const endDrag=e=>{if(!drag||e.pointerId!==drag.id)return;if(drag.on){armEat();m.classList.remove("is-panning");try{m.releasePointerCapture(e.pointerId)}catch(_){}}drag=null};
 m.addEventListener("pointerup",endDrag);m.addEventListener("pointercancel",endDrag);
 /* touch: #map has touch-action:pan-y, so the browser only scrolls vertically; we handle pinch and sideways pan */
 let mode=null,T0,c0,P0;
 const mid=(a,b)=>[(a.clientX+b.clientX)/2,(a.clientY+b.clientY)/2],dist=(a,b)=>Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY)||1;
 function pinch(e){const a=e.touches[0],b=e.touches[1],c=mid(a,b);T0=vb.slice();P0={d:dist(a,b),w:toSVG(c[0],c[1])};mode="pinch";stopAnim()}
 function pan(t){T0=vb.slice();c0=[t.clientX,t.clientY];P0={k:perPx()};mode="pan";stopAnim()}
 m.addEventListener("touchstart",e=>{const n=e.touches.length;if(n>=2)pinch(e);else if(n===1){mode="maybe";c0=[e.touches[0].clientX,e.touches[0].clientY]}},{passive:true});
 m.addEventListener("touchmove",e=>{
  if(mode==="pinch"&&e.touches.length>=2){if(!e.cancelable)return;e.preventDefault();
   const a=e.touches[0],b=e.touches[1],c=mid(a,b),r=m.getBoundingClientRect();
   const w=Math.min(975,Math.max(MINW,T0[2]*P0.d/dist(a,b))),h=w*610/975;
   applyViewBox(clampVB([P0.w[0]-(c[0]-r.left)*w/r.width,P0.w[1]-(c[1]-r.top)*h/r.height,w,h]));return}
  if(mode==="maybe"){const t=e.touches[0],dx=t.clientX-c0[0],dy=t.clientY-c0[1];
   if(Math.abs(dx)<8&&Math.abs(dy)<8)return;
   if(Math.abs(dx)>Math.abs(dy)&&e.cancelable)pan(t);else{mode="scroll";return}}
  if(mode==="pan"){if(!e.cancelable)return;e.preventDefault();const t=e.touches[0];
   applyViewBox(clampVB([T0[0]-(t.clientX-c0[0])*P0.k,T0[1]-(t.clientY-c0[1])*P0.k,T0[2],T0[3]]))}},{passive:false});
 const tend=e=>{const n=e.touches.length;if(mode==="pan"||mode==="pinch")armEat();if(n===0)mode=null;else if(n===1&&mode==="pinch")pan(e.touches[0])};
 m.addEventListener("touchend",tend);m.addEventListener("touchcancel",tend);
})();
window.USA_MAP_READY=new Promise(function(r){ window.__usaMapReady=r; });
applyLblAttr();
setTimeout(function(){
  buildStates();
  setTimeout(function(){
    buildCitiesAndAirports();
    mountLabelLegend();
    refreshLabels();
 (function(){const m=$("#map"); if(!m||typeof ResizeObserver==="undefined"){window.addEventListener("resize",refreshLabels);return;}
  const ro=new ResizeObserver(()=>refreshLabels()); ro.observe(m);})();
 window.PPC_mapView={applyViewBox, refreshLabels, isFull};
    if(window.__usaMapReady) window.__usaMapReady();
    setTimeout(function(){
const pick=$("#pick");ABBRS.forEach(a=>pick.add(new Option(GEO[a].name,a)));pick.onchange=()=>pick.value&&selectState(pick.value);

/* Custom mineral-night state picker — keeps #pick synced for programmatic use */
(function mountUsaStatePicker(){
  const pick = $("#pick"); if(!pick || pick.dataset.spMounted) return;
  pick.dataset.spMounted = "1";
  const wrap = document.createElement("div");
  wrap.className = "state-picker";
  wrap.setAttribute("data-sp", "usa");
  pick.parentNode.insertBefore(wrap, pick);
  wrap.appendChild(pick);
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "state-picker-btn";
  btn.setAttribute("aria-haspopup", "listbox");
  btn.setAttribute("aria-expanded", "false");
  btn.innerHTML = '<span class="sp-label">'+usaUi().choose+'</span><svg class="sp-chev" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7.4 9.5 12 14.1l4.6-4.6 1.4 1.4-6 6-6-6z"/></svg>';
  const menu = document.createElement("ul");
  menu.className = "state-picker-menu";
  menu.setAttribute("role", "listbox");
  menu.setAttribute("tabindex", "-1");
  menu.innerHTML = '<li class="sp-head" aria-hidden="true">'+usaUi().fifty+'</li>' +
    ABBRS.map(a => `<li role="option" data-a="${a}" aria-selected="false"><span class="sp-name">${esc(GEO[a].name)}</span><span class="sp-code">${a}</span></li>`).join("") +
    `<li role="option" data-a="DC" aria-selected="false"><span class="sp-name">Washington, DC</span><span class="sp-code">DC</span></li>`;
  wrap.append(btn, menu);
  const label = btn.querySelector(".sp-label");
  function setOpen(o){
    wrap.classList.toggle("open", o);
    btn.setAttribute("aria-expanded", o ? "true" : "false");
  }
  function syncFromPick(){
    const v = pick.value;
    [...menu.querySelectorAll('[role="option"]')].forEach(li => li.setAttribute("aria-selected", String(li.dataset.a === v)));
    if(!v){ label.textContent = usaUi().choose; return; }
    if(v === "DC"){ label.textContent = "Washington, DC"; return; }
    label.textContent = (GEO[v] && GEO[v].name) || v;
  }
  window.syncUsaStatePicker = syncFromPick;
  btn.addEventListener("click", e => { e.stopPropagation(); setOpen(!wrap.classList.contains("open")); });
  menu.addEventListener("click", e => {
    const li = e.target.closest('[role="option"]'); if(!li) return;
    const a = li.dataset.a;
    if(a === "DC"){ pick.value = ""; selectDC(); }
    else { pick.value = a; selectState(a); }
    syncFromPick(); setOpen(false);
  });
  document.addEventListener("click", e => { if(!wrap.contains(e.target)) setOpen(false); });
  document.addEventListener("keydown", e => { if(e.key === "Escape") setOpen(false); });
  pick.addEventListener("change", syncFromPick);
  // Monkey-patch value setter so hilite/showAllStates keep the button label in sync
  const proto = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value");
  if(proto && proto.set){
    Object.defineProperty(pick, "value", {
      configurable: true,
      get(){ return proto.get.call(this); },
      set(v){ proto.set.call(this, v); syncFromPick(); }
    });
  }
  syncFromPick();
})();

$("#grid").innerHTML=ABBRS.map(a=>`<button data-a="${a}">${mark(a)}<span>${esc(GEO[a].name)}</span></button>`).join("")+`<button data-a="DC">${mark("DC")}<span>Washington, DC</span></button>`;
$("#grid").querySelectorAll("button").forEach(b=>b.onclick=()=>{b.dataset.a==="DC"?selectDC():selectState(b.dataset.a);$("#panel").scrollIntoView({behavior:"smooth",block:"nearest"})});
const raw=decodeURIComponent((location.hash||"").replace(/^#/,"").replace(/\+/g," "));
const slash=raw.indexOf("/");
if(slash>0){const a=raw.slice(0,slash), n=raw.slice(slash+1);
 if(airportByCode(n)) selectAirport(n);
 else if(GEO[a]&&(GEO[a].cities||[]).some(c=>c.n===n)) selectCity(a,n);
 else if(a==="DC") selectDC();
 else if(GEO[a]) selectState(a);
 else empty();
}else if(airportByCode(raw)) selectAirport(raw);
else if(raw==="DC") selectDC();
else if(GEO[raw]) selectState(raw);
else empty();
    },0);
  },0);
},0);
