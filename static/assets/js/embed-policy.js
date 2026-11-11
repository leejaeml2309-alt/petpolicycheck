(function(){
  var scripts=document.querySelectorAll('script[src*="embed-policy.js"]');
  var s=scripts[scripts.length-1];
  var airline=(s && s.getAttribute('data-airline'))||'united';
  var theme=(s && s.getAttribute('data-theme'))||'dark';
  var lang=(s && s.getAttribute('data-lang'))||'en';
  var target=(s && s.getAttribute('data-target'));
  var DATA={
    united:{en:'United: in-cabin pets accepted within published carrier sizes; soft-sided 11×18×11 in common max. Confirm fees on united.com.',fr:'United : animaux en cabine selon dimensions publiées. Confirmez les frais sur united.com.',it:"United: animali in cabina accettati entro le dimensioni del trasportino pubblicate; massimo comune per un trasportino morbido 11×18×11 in. Verifichi le tariffe su united.com."},
    delta:{en:'Delta: soft-sided kennel often recommended ~18×11×11 in; fees vary by market. Confirm on delta.com.',fr:'Delta : cage souple souvent ~18×11×11 in. Confirmez sur delta.com.',it:"Delta: spesso consigliato un trasportino morbido di circa 18×11×11 in; le tariffe variano secondo il mercato. Verifichi su delta.com."},
    american:{en:'American: soft-sided ~18×11×11 in recommended on many aircraft. Confirm on aa.com.',fr:'American : ~18×11×11 in souvent recommandé. Confirmez sur aa.com.',it:"American: trasportino morbido di circa 18×11×11 in consigliato su molti aeromobili. Verifichi su aa.com."},
    'air-canada':{en:'Air Canada: soft-sided only on many jets; common mainline 43×40×20 cm. Confirm on aircanada.com.',fr:'Air Canada : souple souvent obligatoire; 43×40×20 cm courant. Confirmez sur aircanada.com.',it:"Air Canada: solo trasportino morbido su molti jet; misura comune sulla rete principale 43×40×20 cm. Verifichi su aircanada.com."},
    'korean-air':{en:'Korean Air: confirm cabin/cargo pathway and APQA documents for Korea corridors on koreanair.com.',fr:'Korean Air : confirmez cabine/cargo et documents APQA sur koreanair.com.',it:"Korean Air: verifichi su koreanair.com il percorso cabina/stiva e i documenti APQA per i corridoi verso la Corea."},
    lufthansa:{en:'Lufthansa: cabin often up to 8 kg pet+carrier; soft 55×40×23 cm. Confirm on lufthansa.com.',fr:'Lufthansa : cabine souvent ≤8 kg; 55×40×23 cm. Confirmez sur lufthansa.com.',it:"Lufthansa: in cabina spesso fino a 8 kg tra animale e trasportino; trasportino morbido 55×40×23 cm. Verifichi su lufthansa.com."}
  };
  var CHROME={
    en:{title:'Pet policy snapshot',link:'Verified on PetPolicyCheck →'},
    it:{title:"Sintesi della policy per animali",link:"Dettagli su PetPolicyCheck →"}
  };
  var IT_OK={"aeromexico":1,"air-canada":1,"air-france":1,"air-premia":1,"alaska":1,"american":1,"ana":1,"asiana":1,"british-airways":1,"delta":1,"frontier":1,"hawaiian":1,"jal":1,"jeju-air":1,"jetblue":1,"korean-air":1,"lufthansa":1,"peach":1,"porter":1,"snub-nosed-breeds":1,"southwest":1,"spirit":1,"tway":1,"united":1,"viva-aerobus":1,"volaris":1,"westjet":1,"zipair":1};
  var pack=DATA[airline]||DATA.united;
  var text=pack[lang]||pack.en;
  var chrome=CHROME[lang]||CHROME.en;
  var path='/airlines/'+airline+'.html';
  if(lang==='it' && IT_OK[airline]) path='/it'+path;
  var dark=theme!=='light';
  var el=document.createElement('aside');
  el.setAttribute('data-ppc-embed','1');
  el.style.cssText='max-width:360px;font:14px/1.45 system-ui,sans-serif;border-radius:12px;padding:14px 16px;border:1px solid '+(dark?'#d9b76555':'#23478533')+';background:'+(dark?'#0b1719':'#f7f3ea')+';color:'+(dark?'#f5efe0':'#1a1a1a');
  el.innerHTML='<div style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#d9b765;margin-bottom:6px">'+chrome.title+'</div><p style="margin:0 0 10px">'+text+'</p><a href="https://petpolicycheck.com'+path+'" style="color:#d9b765;font-weight:700;text-decoration:none">'+chrome.link+'</a>';
  var host=target?document.getElementById(target):null;
  if(host) host.appendChild(el); else s.parentNode.insertBefore(el,s.nextSibling);
})();
