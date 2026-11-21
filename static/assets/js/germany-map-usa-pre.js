/* Germany map — USA density + cropped view. Must run BEFORE country-map.js. */
(function(){
  var VIEW=[210, 18, 460, 590];
  var CFG=window.PPC_MAP=window.PPC_MAP||{};
  CFG.view=VIEW.slice();
  var svg=document.getElementById('map');
  if(svg) svg.setAttribute('viewBox', VIEW.join(' '));

  var GEO=window.DE_GEO||CFG.geo||{};
  var APS=window.DE_GEO_AIRPORTS||CFG.airports||[];
  var DATA=window.DE_MAP_DATA||CFG.data||{};
  var hubs={};
  if(DATA.provHub) Object.keys(DATA.provHub).forEach(function(k){ hubs[k]=1; });
  if(DATA.stateHub) Object.keys(DATA.stateHub).forEach(function(k){ hubs[k]=1; });

  /* 2-letter codes in empty interior spots (never clipped, away from cities/airports). */
  var LAND_XY={
    SH:[421.3, 112.7],
    MV:[558, 118],
    HH:[442, 172],
    HB:[348, 176],
    NI:[345, 222],
    NW:[298, 282],
    ST:[468, 278],
    BE:[569, 218],
    BB:[618, 205],
    HE:[400, 348],
    TH:[502, 360],
    SN:[558, 362],
    RP:[272, 398],
    SL:[268, 448],
    BY:[532, 452],
    BW:[408, 530]
  };
  Object.keys(LAND_XY).forEach(function(a){
    if(!GEO[a]) return;
    GEO[a].callout=false;
    GEO[a].lx=LAND_XY[a][0];
    GEO[a].ly=LAND_XY[a][1];
  });
  window.PPC_DE_LAND_XY=LAND_XY;

  function score(a){
    var s=0;
    var apN=APS.filter(function(ap){ return (ap.province||ap.state)===a; }).length;
    s+=apN*2;
    var cities=((GEO[a]&&GEO[a].cities)||[]).length;
    s+=cities*0.5;
    if(hubs[a]) s+=3;
    if(DATA.lastChecked) s+=1;
    if(DATA.special && DATA.special[a]) s+=1.5;
    if(DATA.alertStates && DATA.alertStates.indexOf(a)!==-1) s+=1.5;
    return s;
  }
  /* Frozen 5-step amber ramp, same grouping logic as the live scores
     (airports×2 + cities×0.5 + hub +3). USA also freezes its tiers. */
  var FROZEN={
    NW:'st-t5',
    BY:'st-t4', BW:'st-t4', HE:'st-t4',
    BB:'st-t3', HH:'st-t3', SN:'st-t3',
    HB:'st-t2', TH:'st-t2', NI:'st-t2', SL:'st-t2', RP:'st-t2', SH:'st-t2',
    BE:'st-t1', MV:'st-t1', ST:'st-t1'
  };
  var scores={};
  Object.keys(GEO).forEach(function(a){ scores[a]=score(a); });
  DATA.tones=FROZEN;
  window.PPC_DE_DENSITY={scores:scores, tones:FROZEN, view:VIEW};

  var de=false;
  try{
    var path=location.pathname||'';
    de=path==='/de'||path.indexOf('/de/')===0||document.documentElement.getAttribute('data-ppc-locale')==='de';
  }catch(_){}
  var CITY={
    Berlin:'Berlin', Bremen:'Bremen', Hamburg:'Hamburg', Frankfurt:'Frankfurt',
    Munich:de?'München':'Munich', Dusseldorf:de?'Düsseldorf':'Düsseldorf',
    Düsseldorf:de?'Düsseldorf':'Düsseldorf', Cologne:de?'Köln':'Cologne',
    Hanover:de?'Hannover':'Hanover', Hannover:de?'Hannover':'Hanover',
    Nuremberg:de?'Nürnberg':'Nuremberg', Nürnberg:de?'Nürnberg':'Nuremberg',
    Stuttgart:'Stuttgart', Dresden:'Dresden', Leipzig:'Leipzig', Erfurt:'Erfurt',
    Munster:de?'Münster':'Münster', Münster:de?'Münster':'Münster',
    Saarbrucken:de?'Saarbrücken':'Saarbrücken', Saarbrücken:de?'Saarbrücken':'Saarbrücken',
    Dortmund:'Dortmund', Hahn:'Hahn', Friedrichshafen:'Friedrichshafen',
    'Baden-Baden':'Baden-Baden', Lubeck:de?'Lübeck':'Lübeck', Lübeck:de?'Lübeck':'Lübeck',
    Paderborn:'Paderborn', Weeze:'Weeze'
  };
  /* Nudges in SVG user units (default ldy is 16 below the pad). */
  var OFF={
    BER:{ldx:20, ldy:12, anchor:'start'},
    DUS:{ldx:0, ldy:-16, anchor:'middle'},
    FRA:{ldx:18, ldy:10, anchor:'start'},
    HAM:{ldx:-16, ldy:5, anchor:'end'},
    CGN:{ldx:18, ldy:12, anchor:'start'},
    MUC:{ldx:18, ldy:8, anchor:'start'},
    STR:{ldx:-18, ldy:10, anchor:'end'},
    BRE:{ldx:-16, ldy:8, anchor:'end'},
    DRS:{ldx:16, ldy:-10, anchor:'start'},
    ERF:{ldx:16, ldy:12, anchor:'start'},
    HAJ:{ldx:-16, ldy:8, anchor:'end'},
    LEJ:{ldx:-16, ldy:10, anchor:'end'},
    FMO:{ldx:-16, ldy:8, anchor:'end'},
    NUE:{ldx:16, ldy:10, anchor:'start'},
    SCN:{ldx:-16, ldy:8, anchor:'end'},
    DTM:{ldx:16, ldy:-10, anchor:'start'},
    HHN:{ldx:-16, ldy:10, anchor:'end'},
    FDH:{ldx:14, ldy:10, anchor:'start'},
    FKB:{ldx:-20, ldy:-12, anchor:'end'},
    LBC:{ldx:-16, ldy:-8, anchor:'end'},
    PAD:{ldx:16, ldy:10, anchor:'start'},
    NRN:{ldx:-16, ldy:-10, anchor:'end'}
  };
  APS.forEach(function(ap){
    var city=CITY[ap.city]||ap.city;
    ap.mapLabel=ap.code+' · '+city;
    ap.mapName='';
    var o=OFF[ap.code];
    if(o){ ap.ldx=o.ldx; ap.ldy=o.ldy; ap.anchor=o.anchor; }
    if(ap.major) ap.pinLabel=true;
  });
})();
