/* Paw Passport · Community, Field Checks & City Scouts Hub (#4 + #9 + #11) — STAGED LAUNCH CANDIDATE.
   Public gallery/submit are customer-ready. Admin chrome (?admin=1 or ?view=moderation) stays hidden.
   Zero backend: visitor submissions download a JSON payload + offer a mailto handoff to contact@petpolicycheck.com
   (no auto-send). Moderators still export approved JSON for the static site merge. */
(function(){
'use strict';
var KEY='ppc_hub_v5', LKEY='ppc_lang';
var $=function(s,r){return (r||document).querySelector(s)}, $$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
var MONTHS={
  en:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
  fr:['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'],
  es:['ene.','feb.','mar.','abr.','may.','jun.','jul.','ago.','sep.','oct.','nov.','dic.'],
  de:['Jan.','Feb.','Mär.','Apr.','Mai','Jun.','Jul.','Aug.','Sep.','Okt.','Nov.','Dez.']
};
function mon(ym){if(!ym)return '';var p=ym.split('-');var m=+p[1]-1;return ((MONTHS[lang]||MONTHS.en)[m])+' '+p[0]}
function nowYM(){var d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')}
var COUNTRIES=['United States','Canada','Mexico','United Kingdom','Germany','Dominican Republic','France'];
var CSHORT={'United States':'USA','Canada':'Canada','Mexico':'Mexico','United Kingdom':'UK','Germany':'Germany','Dominican Republic':'Dominican Rep.','France':'France'};
var TYPES={airline:'Airline',train:'Train / Ferry',hotel:'Hotel / Stay',city:'City / Border Hub',grooming:'Grooming & Care'};
var GUSE={trip:'In-trip / Hotel Mobile Grooming',local:'Resident & Expat Trusted Salon'};
var HUBS=[['Miami','United States'],['San Diego / CBX','United States · Mexico'],['Toronto','Canada'],['CDMX / Cancún','Mexico'],['London + Folkestone','United Kingdom'],['Frankfurt FRA','Germany'],['Punta Cana / Las Terrenas','Dominican Republic'],['Paris','France']];
var MENTION_LABEL={none:'None',winwin:'Gear mention',paid:'Product mention'};
var REJECT=['Policy inaccurate','Copyright music','Unreadable / >30s','Privacy visible','Animal welfare concern'];

/* ---------- i18n (100% EN default; 4-language toggle EN / FR / ES / DE aligned with the site glossary) ---------- */
var LOC={
fr:{tab_gallery:'Guides terrain',tab_submit:'Envoyer un conseil',nav_fg:'Guides terrain',nav_adv:'Contact',
a_dept:'Hub Communauté, Vérifs terrain & City Scouts · une seule porte, sans compte',a_ttl:'Partagez ce qui s’est vraiment passé avec votre animal',
a_lead:'Postez un clip de 30 s, signalez un écart avec la règle officielle ou devenez Founding City Scout. Environ 60 secondes, sans compte. Un humain vérifie tout avant publication, avec crédit à votre nom.',


c_dept:'Paw Passport — Guides de terrain',c_ttl:'Guides de terrain Pet Policy — Principaux corridors de voyage avec animaux',c_lead:'Ces vignettes d\'exemple présentent les règles officielles de voyage avec un animal pour les principaux corridors. Soumettez une astuce de 30 s pour vérification.',c_more:'Épisodes d\'exemple',c_rules:'Exemples de vérification des règles officielles',c_rulessub:'Règles officielles uniquement — ces vignettes sont des exemples.',
c_submit:'Envoyer un conseil 30 s',c_submitn:'Sans compte · relu par un humain',
c_pdept:'',c_ph:'',
c_pp:'Une marque par épisode, affichée « Pet Tip présenté par … » sous le vrai conseil terrain — jamais dans les faits de la règle.',
c_pl1:'Lancement : partenariat matériel gagnant-gagnant (produit pour tests terrain honnêtes + crédit)',c_pl2:'',c_pl3:'',
c_pcta:'',
c_disc:'Exemple : les épisodes d’exemple illustrent de vraies règles.'},
es:{tab_gallery:'Guías de campo',tab_submit:'Enviar un consejo',nav_fg:'Guías de campo',nav_adv:'Contacto',
a_dept:'Hub Comunidad, Verificaciones & City Scouts · una puerta, sin cuenta',a_ttl:'Comparta lo que realmente pasó con su mascota',
a_lead:'Suba un clip de 30 s, avise si el control real difirió de la norma oficial o postúlese como Founding City Scout. Toma unos 60 segundos, sin cuenta. Un humano verifica todo antes de publicar, con crédito a su @usuario.',


c_dept:'Guías de campo Paw Passport',c_ttl:'Guías de campo Pet Policy — Principales corredores para viajar con mascotas',c_lead:'Estas fichas de ejemplo muestran las normas oficiales para viajar con mascotas en los principales corredores. Envíe un consejo de 30 s para su revisión.',c_more:'Episodios de ejemplo',c_rules:'Ejemplos de verificación de normas oficiales',c_rulessub:'Solo normas oficiales: estas fichas son ejemplos.',
c_submit:'Enviar consejo de 30 s',c_submitn:'Sin cuenta · revisado por un humano',
c_pdept:'',c_ph:'',
c_pp:'Una marca por episodio, mostrada como « Pet Tip presentado por … » debajo del consejo real — nunca dentro de la regla oficial.',
c_pl1:'Lanzamiento: alianza win-win de equipamiento (producto para pruebas reales + crédito)',c_pl2:'',c_pl3:'',
c_pcta:'',
c_disc:'Vista previa: episodios de ejemplo basados en reglas reales. Las marcas mostradas son ejemplos ilustrativos.'},
de:{tab_gallery:'Praxis-Guides',tab_submit:'Tipp senden',nav_fg:'Praxis-Guides',nav_adv:'Kontakt',
a_dept:'Community-, Praxischeck- & City-Scouts-Hub · ein Einstieg, kein Konto',a_ttl:'Teile, was mit deinem Haustier wirklich passiert ist',
a_lead:'30-Sek.-Clip senden, Abweichung zur offiziellen Regel melden oder Founding City Scout werden. Dauert ca. 60 Sekunden ohne Registrierung. Jede Einsendung wird vor Veröffentlichung menschlich geprüft — mit Namensnennung.',


c_dept:'Paw Passport Praxisleitfäden',c_ttl:'Pet Policy Praxisleitfäden — Wichtige Reisekorridore mit Haustieren',c_lead:'Die Beispielkacheln zeigen die offiziellen Regeln für Reisen mit Haustieren auf den wichtigsten Korridoren. Reichen Sie einen 30-Sekunden-Tipp zur Prüfung ein.',c_more:'Beispielepisoden',c_rules:'Beispiele für Prüfungen offizieller Regeln',c_rulessub:'Nur offizielle Regeln – diese Kacheln sind Beispiele.',
c_submit:'30-Sek.-Tipp senden',c_submitn:'Ohne Konto · menschlich geprüft',
c_pdept:'',c_ph:'',
c_pp:'Eine Marke pro Episode als „Pet Tip präsentiert von …“ unterhalb des echten Praxistipps — niemals innerhalb der offiziellen Regel.',
c_pl1:'Start: Win-Win-Ausstattungspartnerschaft (Produkt für ehrliche Praxistests + Nennung)',c_pl2:'',c_pl3:'',
c_pcta:'',
c_disc:'Vorschau: Beispielepisoden auf Basis echter Regeln. Genannte Marken dienen nur als Beispiel.'},
ko:{tab_gallery:'필드 가이드',tab_submit:'팁 보내기',nav_fg:'필드 가이드',nav_adv:'문의',
a_dept:'커뮤니티 · 현장 점검 & City Scouts 허브 · 계정 없이 한 곳에서',a_ttl:'반려동물과 실제로 겪은 일을 공유해 주세요',
a_lead:'30초 클립을 올리거나, 공식 규정과 달랐던 점을 알려 주거나, Founding City Scout이 되어 보세요. 약 60초, 계정 불필요. 사람이 공식 규정과 대조한 뒤 게시하며 크레딧을 남겨 드려요.',
a_s1:'클립',a_up:'≤ 30초 영상 업로드',a_ln:'기존 클립 링크',a_drop:'세로 클립을 여기로 드래그',a_or:'또는',a_browse:'찾아보기',a_dropn:'최대 30초 (35초 허용) · 9:16 권장',
a_s2:'무엇을 보여 주나요?',a_type:'유형',a_guse:'그루밍 용도',a_g1:'여행 중 / 호텔 모바일 그루밍',a_g1s:'비행 후 목욕, 숙박 중 그루밍, 호텔 모바일 밴',a_g2:'거주·주재원 신뢰 살롱',a_g2s:'Fear-free · EN/FR · 진정제 없는 고양이 · 견종 노하우',
a_ctry:'국가 / 코리도',a_date:'여행 날짜',a_ent:'정확한 항공사 / 호텔 / 도시 / 살롱',a_s3:'한 문장 현장 팁',a_tipl:'공식 사이트에 없는 실제 체크인·정책 디테일',a_bag:'이동장 / 체중 (선택)',
a_s4:'크레딧 & 권리',a_handle:'@핸들 (클립에 표시)',a_social:'크레딧용 프로필 링크',a_send:'검토용 30초 팁 보내기',a_sendn:'사람 모더레이터에게 전달 · 자동 게시 없음',


c_dept:'Paw Passport 현장 가이드',c_ttl:'Pet Policy 현장 가이드 — 주요 반려동물 여행 노선',c_lead:'예시 타일에서 주요 노선의 공식 반려동물 여행 규정을 확인하실 수 있습니다. 30초 팁을 보내 주시면 검토하겠습니다.',c_more:'예시 에피소드',c_rules:'공식 규정 확인 예시',c_rulessub:'공식 규정만 다룹니다. 이 타일들은 예시입니다.',
c_submit:'30초 팁 보내기',c_submitn:'계정 불필요 · 사람 검토',
c_pdept:'',c_ph:'',
c_pp:'에피소드당 브랜드 하나, 실제 현장 팁 아래 “Pet Tip presented by …”로 표시 — 정책 사실 안에는 넣지 않아요.',
c_pl1:'런칭: 윈윈 장비 파트너십 (정직한 현장 테스트용 제품 + 크레딧)',c_pl2:'',c_pl3:'',
c_pcta:'',
c_disc:'예시 에피소드는 실제 규칙을 보여 줍니다.'},
ja:{tab_gallery:'フィールドガイド',tab_submit:'ヒントを送る',nav_fg:'フィールドガイド',nav_adv:'お問い合わせ',
a_dept:'コミュニティ・現地チェック＆City Scoutsハブ · アカウント不要の一窓口',a_ttl:'ペットとの実体験を共有してください',
a_lead:'30秒クリップの投稿、公式ルールとの違いの報告、Founding City Scoutへの応募。約60秒、アカウント不要。人が公式ルールと照合してから公開し、クレジットを付けます。',
a_s1:'クリップ',a_up:'≤30秒の動画をアップロード',a_ln:'既存クリップのリンク',a_drop:'縦型クリップをここにドラッグ',a_or:'または',a_browse:'参照',a_dropn:'最大30秒（35秒許容）· 9:16推奨',
a_s2:'何を示しますか？',a_type:'種類',a_guse:'グルーミング用途',a_g1:'旅中 / ホテル・モバイル',a_g1s:'到着後の入浴、滞在中のグルーム、ホテルのモバイルバン',a_g2:'住民・駐在員向け信頼サロン',a_g2s:'Fear-free · EN/FR · 鎮静なし猫 · 犬種ノウハウ',
a_ctry:'国 / 回廊',a_date:'旅行日',a_ent:'正確な航空会社 / ホテル / 都市 / サロン',a_s3:'一文の現地ヒント',a_tipl:'公式サイトにない実際のチェックインやポリシーの詳細',a_bag:'キャリア / 体重（任意）',
a_s4:'クレジット＆権利',a_handle:'@ハンドル（クリップ表示）',a_social:'クレジット用プロフィールURL',a_send:'審査用30秒ヒントを送る',a_sendn:'人のモデレーターへ · 自動公開なし',


c_dept:'Paw Passport フィールドガイド',c_ttl:'Pet Policy フィールドガイド — 主なペット渡航ルート',c_lead:'例のタイルでは、主なルートにおけるペット渡航の公式ルールをご紹介しています。30秒のヒントをお寄せください。内容を確認いたします。',c_more:'エピソード例',c_rules:'公式ルール確認の例',c_rulessub:'公式ルールのみを掲載しています。これらのタイルは例です。',
c_submit:'30秒ヒントを送る',c_submitn:'アカウント不要 · 人が確認',
c_pdept:'',c_ph:'',
c_pp:'エピソードにつき1ブランド。「Pet Tip presented by …」として実ヒントの下に表示 — 政策本文の中には入れません。',
c_pl1:'ローンチ：ウィンウィン器材提携（正直な現地テスト用製品＋クレジット）',c_pl2:'',c_pl3:'',
c_pcta:'',
c_disc:'サンプルエピソードは実在のルールを示します。'},
it:{c_dept:'Guide pratiche Paw Passport',c_ttl:'Guide pratiche Pet Policy — Principali corridoi per viaggiare con animali',c_lead:'I riquadri di esempio mostrano le regole ufficiali per viaggiare con animali nei principali corridoi. Invii un consiglio di 30 secondi da sottoporre a revisione.',c_more:'Episodi di esempio',c_rules:'Esempi di verifica delle regole ufficiali',c_rulessub:'Solo regole ufficiali: questi riquadri sono esempi.'}
};
var UI={
en:{example:'Example',filmed:'Filmed by',presented:'Pet Tip presented by',visit:'Visit Partner ↗',mentionNote:'',fv:'Field-Verified',official:'Official rule ↗',openslot:'',opencta:'',all:'All',airlines:'Airlines',ferries:'Ferries & Trains',hotels:'Hotels & Cities',groom:'Grooming & Care',country:'Country',type:'Type',episodes:'episodes',featured:'Featured episode',vbadge:'✓ Verified Corridor Traveler',vtip:'Earned by a traveler whose clip or rule check passed human review. Share your episode — your @handle links back to your profile.',nores:'No approved episode for this filter yet — be the first to submit one.',trip:'Trip',brandother:'Your brand on another episode?',reported:'Reported by',seatopen:'Seat open — apply →'},
fr:{example:'Exemple',filmed:'Filmé par',presented:'Pet Tip présenté par',visit:'Voir le partenaire ↗',mentionNote:'',fv:'Vérifié terrain',official:'Règle officielle ↗',openslot:'',opencta:'',all:'Tous',airlines:'Compagnies',ferries:'Ferries & trains',hotels:'Hôtels & villes',groom:'Toilettage & soins',country:'Pays',type:'Type',episodes:'épisodes',featured:'Épisode à la une',vbadge:'✓ Verified Corridor Traveler',vtip:'Obtenu par un voyageur dont le clip ou la vérif de règle a passé la relecture humaine. Partagez votre épisode : votre @pseudo renvoie vers votre profil.',nores:'Aucun épisode approuvé pour ce filtre — soyez le premier à en envoyer un.',trip:'Voyage',brandother:'Votre marque ici sur un autre épisode ?',reported:'Signalé par',seatopen:'Poste ouvert →'},
es:{example:'Ejemplo',filmed:'Grabado por',presented:'Pet Tip presentado por',visit:'Ver socio ↗',mentionNote:'',fv:'Verificado en campo',official:'Regla oficial ↗',openslot:'',opencta:'',all:'Todos',airlines:'Aerolíneas',ferries:'Ferries y trenes',hotels:'Hoteles y ciudades',groom:'Peluquería y cuidados',country:'País',type:'Tipo',episodes:'episodios',featured:'Episodio destacado',vbadge:'✓ Verified Corridor Traveler',vtip:'Otorgado al viajero cuyo clip o verificación superó la revisión humana. Tu @usuario enlaza a tu perfil.',nores:'Aún no hay episodios aprobados para este filtro.',trip:'Viaje',brandother:'¿Tu marca en otro episodio?',reported:'Reportado por',seatopen:'Plaza abierta →'},
de:{example:'Beispiel',filmed:'Gefilmt von',presented:'Pet Tip präsentiert von',visit:'Partner ansehen ↗',mentionNote:'',fv:'Praxisgeprüft',official:'Offizielle Regel ↗',openslot:'',opencta:'',all:'Alle',airlines:'Airlines',ferries:'Fähren & Züge',hotels:'Hotels & Städte',groom:'Grooming & Pflege',country:'Land',type:'Typ',episodes:'Episoden',featured:'Empfohlene Episode',vbadge:'✓ Verified Corridor Traveler',vtip:'Für Reisende, deren Clip oder Regel-Check die menschliche Prüfung bestanden hat. Dein @Handle verlinkt auf dein Profil.',nores:'Noch keine freigegebene Episode für diesen Filter.',trip:'Reise',brandother:'Ihre Marke in einer anderen Episode?',reported:'Gemeldet von',seatopen:'Platz frei — bewerben →'},
ko:{example:'예시',filmed:'촬영',presented:'Pet Tip 제공',visit:'파트너 보기 ↗',mentionNote:'',fv:'현장 검증',official:'공식 규정 ↗',openslot:'',opencta:'',all:'전체',airlines:'항공사',ferries:'페리 & 기차',hotels:'호텔 & 도시',groom:'그루밍 & 케어',country:'국가',type:'유형',episodes:'에피소드',featured:'추천 에피소드',vbadge:'✓ Verified Corridor Traveler',vtip:'사람 검토를 통과한 여행자. @핸들이 프로필로 연결돼요.',nores:'이 필터에 승인된 에피소드가 아직 없어요.',trip:'여행',brandother:'다른 에피소드에 브랜드를?',reported:'제보',seatopen:'자리 열림 →'},
ja:{example:'例',filmed:'撮影',presented:'Pet Tip 提供',visit:'パートナーを見る ↗',mentionNote:'',fv:'現地検証',official:'公式ルール ↗',openslot:'',opencta:'',all:'すべて',airlines:'航空会社',ferries:'フェリー＆列車',hotels:'ホテル＆都市',groom:'グルーミング＆ケア',country:'国',type:'種類',episodes:'エピソード',featured:'注目エピソード',vbadge:'✓ Verified Corridor Traveler',vtip:'人の確認を通過した旅行者。@ハンドルがプロフィールへリンクします。',nores:'このフィルターの承認エピソードはまだありません。',trip:'旅行',brandother:'別エピソードにブランドを？',reported:'報告',seatopen:'席空き →'},
it:{example:'Esempio',all:'Tutti'}};
var VALID_LANGS=['en','fr','es','de','ko','ja','it'];
var lang=localStorage.getItem(LKEY)||'en';
if(VALID_LANGS.indexOf(lang)<0)lang='en';
var q=new URLSearchParams(location.search); if(q.get('lang')){var ql=q.get('lang').toLowerCase();lang=VALID_LANGS.indexOf(ql)>=0?ql:'en'}
function u(k){return (UI[lang]&&UI[lang][k])||UI.en[k]}
function applyI18n(){
  document.documentElement.lang=lang;
  $$('[data-i18n],[data-i18n-html]').forEach(function(el){
    var html=el.hasAttribute('data-i18n-html'); var k=el.getAttribute(html?'data-i18n-html':'data-i18n');
    if(el._en==null) el._en=html?el.innerHTML:el.textContent;
    var v=(lang!=='en'&&LOC[lang]&&LOC[lang][k])?LOC[lang][k]:el._en; if(html) el.innerHTML=v; else el.textContent=v;
  });
  $$('[data-lang]').forEach(function(b){b.style.background=b.getAttribute('data-lang')===lang?'var(--gold)':'';b.style.color=b.getAttribute('data-lang')===lang?'#0b1719':''});
}

/* ---------- sample data (clearly flagged sample:true → "Example") ---------- */
function seed(){return [
 {id:'c-af',kind:'clip',status:'approved',sample:true,mode:'link',platform:'Instagram Reels',type:'airline',country:'France',entity:'Air France · JFK → CDG (cabin)',route:'JFK → CDG',date:'2026-10',

  official:'Air France: in cabin, pet + carrier max 8 kg; over 8 kg travels in the hold.',officialUrl:'https://petpolicycheck.com/airlines/air-france.html',mention:'paid',brand:'Sleepypod',brandUrl:'https://sleepypod.com/',brandLine:'Under-seat carriers sized for the 8 kg cabin rule.',reviewedAt:'2026-11-03'},
 {id:'c-ls',kind:'clip',status:'approved',sample:true,mode:'upload',platform:'Upload',type:'train',country:'United Kingdom',entity:'LeShuttle (Eurotunnel) · Calais → Folkestone',route:'Calais → Folkestone',date:'2026-10',

  official:'GB entry from the EU: dogs need tapeworm treatment by a vet 1–5 days (24–120 h) before arrival.',officialUrl:'https://www.gov.uk/bring-pet-to-great-britain',mention:'winwin',brand:'Kurgo',brandUrl:'https://kurgo.com/',brandLine:'Crash-tested car harnesses for the drive onto the shuttle.',reviewedAt:'2026-11-02'},
 {id:'c-cdc',kind:'clip',status:'approved',sample:true,mode:'link',platform:'TikTok',type:'airline',country:'United States',entity:'Aeroméxico · MEX → LAX',route:'MEX → LAX',date:'2026-09',

  official:'All dogs entering the US need a CDC Dog Import Form receipt (dog ≥ 6 months, microchipped).',officialUrl:'https://www.cdc.gov/importation/dogs/index.html',mention:'none',reviewedAt:'2026-11-01'},
 {id:'c-gm',kind:'clip',status:'approved',sample:true,mode:'link',platform:'YouTube Shorts',type:'grooming',guse:'trip',country:'United States',entity:'Mobile groomer at a Miami hotel (post-flight bath)',route:'Miami · hotel visit',date:'2026-10',

  official:'Field tip only — no official rule. Look for Fear Free–trained groomers.',officialUrl:'https://fearfreepets.com/',mention:'none',reviewedAt:'2026-11-04'},
 {id:'c-gc',kind:'clip',status:'approved',sample:true,mode:'link',platform:'TikTok',type:'grooming',guse:'trip',country:'Germany',entity:'Calming groom before FRA cabin flight (SAMPLE)',route:'Frankfurt · pre-flight salon',date:'2026-11',

  official:'Field tip only — Example sample. Not a live salon listing. Prefer Fear Free–trained groomers before travel.',officialUrl:'https://fearfreepets.com/',mention:'none',reviewedAt:'2026-11-06'},
 {id:'c-wj',kind:'clip',status:'approved',sample:true,mode:'link',platform:'TikTok',type:'airline',country:'Dominican Republic',entity:'WestJet · YYZ → PUJ',route:'YYZ → PUJ',date:'2026-11',

  official:'WestJet: no pets in the baggage hold to most Dominican Republic airports 15 May–31 Oct (La Romana year-round).',officialUrl:'https://www.westjet.com/en-ca/pets',mention:'none',reviewedAt:'2026-11-05'},
 {id:'c-lh',kind:'clip',status:'pending',sample:true,mode:'upload',platform:'Upload',type:'airline',country:'Germany',entity:'Lufthansa · FRA → MUC (cabin)',route:'FRA → MUC',date:'2026-10',duration:27,

  official:'Lufthansa: in cabin, pet + carrier max 8 kg; carrier max 55×40×23 cm.',officialUrl:'https://www.lufthansa.com/',consentAt:'2026-11-06 20:41 KST',mention:'none',checks:{policy:true,audio:true}},
 {id:'c-gp',kind:'clip',status:'approved',sample:true,mode:'link',platform:'Instagram Reels',type:'grooming',guse:'local',country:'France',entity:'Fear-free cat salon · Paris District 11 (EN/FR spoken)',route:'Paris · resident / expat',date:'2026-10',duration:29,

  official:'Field tip only — no official rule. Fear Free handling guidance.',officialUrl:'https://fearfreepets.com/',mention:'none',reviewedAt:'2026-11-06',note:'SAMPLE content · salon not named; welfare: no sedation, calm handling.'},
 {id:'c-ba',kind:'clip',status:'rejected',sample:true,mode:'link',platform:'TikTok',type:'airline',country:'United Kingdom',entity:'British Airways · LHR → JFK',route:'LHR → JFK',date:'2026-08',duration:31,

  official:'British Airways: no pets in the cabin (except assistance dogs); pets travel in the hold via partners.',officialUrl:'https://petpolicycheck.com/airlines/british-airways.html',consentAt:'2026-11-05 22:10 KST',mention:'none',rejectReason:'Policy inaccurate',note:'Contradicts BA official policy; likely assistance dog — asked contributor to clarify.'},
 {id:'r-sen',kind:'rule',status:'pending',sample:true,country:'Mexico',checkpoint:'Border / customs',route:'LAX → MEX T1 · SENASICA desk',date:'2026-10',
  official:'Mexico: dogs & cats from the US/Canada need no import health certificate; SENASICA inspects the pet on arrival.',officialUrl:'https://www.gob.mx/senasica',
proof:'Blurred photo of the desk sign (attached)',consentAt:'2026-11-06 18:22 KST'},
 {id:'r-cdc',kind:'rule',status:'approved',sample:true,country:'United States',checkpoint:'Airline check-in',route:'CUN → MIA',date:'2026-10',
  official:'All dogs entering the US need a CDC Dog Import Form receipt; airlines may check it before boarding.',officialUrl:'https://www.cdc.gov/importation/dogs/index.html',
reviewedAt:'2026-11-03'},
 {id:'r-uk',kind:'rule',status:'approved',sample:true,country:'United Kingdom',checkpoint:'Border / Pet Reception',route:'Calais Pet Reception',date:'2026-10',
  official:'Dogs entering GB from the EU need tapeworm treatment 24–120 h before arrival, recorded by a vet.',officialUrl:'https://www.gov.uk/bring-pet-to-great-britain',
reviewedAt:'2026-11-02'},
 {id:'r-wj',kind:'rule',status:'approved',sample:true,country:'Dominican Republic',checkpoint:'Airline booking',route:'YYZ → PUJ',date:'2026-11',
  official:'WestJet: no pets in the hold to most DR airports 15 May–31 Oct; La Romana year-round.',officialUrl:'https://www.westjet.com/en-ca/pets',
reviewedAt:'2026-11-05'},
 {id:'s-mia',kind:'scout',status:'pending',sample:true,hub:'Miami',country:'United States',date:'2026-11',consentAt:'2026-11-06 17:05 KST',
  pack:{vet:'USDA-accredited clinic, Coral Gables — issued & explained export health certificate (EN/ES; FR on request)',groom:'Fear-free mobile groomer — post-flight bath at the hotel, calm handling, no muzzle needed',taxi:'XL pet-friendly transfer MIA → South Beach, 29 kg boxer, fixed price confirmed',stay:'Pet-friendly hotel tested: fee and 2-pet limit as published'}},
 {id:'s-lon',kind:'scout',status:'approved',sample:true,hub:'London + Folkestone',country:'United Kingdom',date:'2026-10',reviewedAt:'2026-11-02',badge:'scout',
  pack:{vet:'Export vet, Folkestone — AHC + tapeworm timing, FR spoken',groom:'Fear-free salon, south London — no-sedation cat grooming',taxi:'Big-dog minicab, St Pancras ↔ Folkestone, no surcharge',stay:'Dog-friendly B&B tested near the terminal'}}
];}
function load(){try{var d=JSON.parse(localStorage.getItem(KEY));if(Array.isArray(d)&&d.length)return d}catch(e){}var s=seed();save(s);return s}
function save(d){localStorage.setItem(KEY,JSON.stringify(d))}
var DB=load();
var SESSION_MEDIA={}; /* uploaded File object URLs, session only */

/* ---------- 9:16 poster (SVG) ---------- */
var ICON={airline:'M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5z',
train:'M12 2c-4 0-8 .5-8 4v9.5A3.5 3.5 0 0 0 7.5 19L6 20.5v.5h2l2-2h4l2 2h2v-.5L16.5 19a3.5 3.5 0 0 0 3.5-3.5V6c0-3.5-4-4-8-4zM7.5 17a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm3.5-7H6V6h5zm2 0V6h5v4zm3.5 7a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z',
hotel:'M7 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm12-6h-8v7H3V5H1v15h2v-3h18v3h2v-9a4 4 0 0 0-4-4z',
city:'M15 11V5l-3-3-3 3v2H3v14h18V11zm-8 8H5v-2h2zm0-4H5v-2h2zm0-4H5V9h2zm6 8h-2v-2h2zm0-4h-2v-2h2zm0-4h-2V9h2zm0-4h-2V5h2zm6 12h-2v-2h2zm0-4h-2v-2h2z',
grooming:'M9.6 6.3a3.1 3.1 0 1 0-1 2.2L10.8 10l-6.5 8.6 1.4 1.1L12 12.4l6.3 7.3 1.4-1.1-6.5-8.6 2.2-1.5a3.1 3.1 0 1 0-1-2.2L12 8.2zm-3.1 1A1.2 1.2 0 1 1 6.5 5a1.2 1.2 0 0 1 0 2.4zm11 0a1.2 1.2 0 1 1 0-2.4 1.2 1.2 0 0 1 0 2.4z',
rule:'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zm-1 7V3.5L18.5 9zM8 13h8v2H8zm0 4h8v2H8z',
scout:'M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z'};
var PAL={airline:['#173a46','#0b1719','#d9b765'],train:['#1f2d45','#0b1719','#f0d58c'],hotel:['#3a2f1c','#0b1719','#d9b765'],city:['#203a33','#0b1719','#d9b765'],grooming:['#24413a','#0b1719','#f0d58c']};
function wrap(t,n,max){var w=String(t).split(' '),L=[],c='';w.forEach(function(x){if((c+' '+x).trim().length>n){L.push(c.trim());c=x}else c+=' '+x});if(c.trim())L.push(c.trim());if(L.length>max){L=L.slice(0,max);L[max-1]=L[max-1].replace(/\W*\w*$/,'')+'…'}return L}
var pid=0;
function poster(it){
  var p=PAL[it.type]||PAL.airline, id='g'+(++pid), cap=wrap(it.sample?'':(it.caption||it.tip||''),22,3);
  var capY=330-(cap.length-1)*11;
  var s='<svg class="poster" viewBox="0 0 270 480" preserveAspectRatio="xMidYMid slice" role="img" aria-label="'+esc((it.caption||'')+' — vertical clip poster')+'"><defs>'+
  '<linearGradient id="'+id+'" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="'+p[0]+'"/><stop offset="1" stop-color="'+p[1]+'"/></linearGradient>'+
  '<radialGradient id="'+id+'r" cx=".5" cy=".38" r=".55"><stop offset="0" stop-color="'+p[2]+'" stop-opacity=".32"/><stop offset="1" stop-color="'+p[2]+'" stop-opacity="0"/></radialGradient>'+
  '<linearGradient id="'+id+'b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".78"/></linearGradient></defs>'+
  '<rect width="270" height="480" fill="url(#'+id+')"/><rect width="270" height="480" fill="url(#'+id+'r)"/>';
  for(var i=0;i<7;i++){s+='<line x1="0" y1="'+(250+i*14)+'" x2="270" y2="'+(232+i*17)+'" stroke="'+p[2]+'" stroke-opacity="'+(.05+i*.01)+'"/>'}
  s+='<circle cx="135" cy="176" r="62" fill="none" stroke="'+p[2]+'" stroke-opacity=".35"/><circle cx="135" cy="176" r="82" fill="none" stroke="'+p[2]+'" stroke-opacity=".14"/>'+
  '<g transform="translate(97 138) scale(3.2)"><path d="'+(ICON[it.type]||ICON.airline)+'" fill="'+p[2]+'"/></g>'+
  /* pet silhouette (cat/dog head) */
  '<g transform="translate(196 214)" fill="#0b1719" fill-opacity=".75" stroke="'+p[2]+'" stroke-opacity=".7" stroke-width="1.2"><path d="M0 26c0-14 9-22 20-22s20 8 20 22c0 8-9 12-20 12S0 34 0 26z"/><path d="M3 12 2 -2l11 9M37 12l1-14-11 9"/></g>'+
  '<rect x="12" y="14" rx="11" width="'+Math.min(246,22+String(it.route||'').length*6.4)+'" height="22" fill="#0b1719" fill-opacity=".72" stroke="'+p[2]+'" stroke-opacity=".7"/>'+
  '<text x="23" y="29.5" font-family="Inter,sans-serif" font-size="10.5" font-weight="700" fill="#f0d58c" letter-spacing=".6">'+esc((it.route||'').toUpperCase())+'</text>'+
  '<rect y="250" width="270" height="230" fill="url(#'+id+'b)"/>';
  cap.forEach(function(l,k){var w=l.length*7.6+18;s+='<rect x="'+(135-w/2)+'" y="'+(capY-15+k*22)+'" width="'+w+'" height="21" rx="4" fill="#0b1719" fill-opacity=".86"/><text x="135" y="'+(capY+k*22)+'" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" font-weight="700" fill="#f5ecd6">'+esc(l)+'</text>'});
  /* right rail */
  [300,340,380].forEach(function(y,k){s+='<circle cx="246" cy="'+(y-150)+'" r="12" fill="#0b1719" fill-opacity=".55" stroke="#f5ecd6" stroke-opacity=".45"/>'});
  s+='<path d="M246 156.5l-5-5a3 3 0 0 1 5-3.4 3 3 0 0 1 5 3.4z" fill="#f5ecd6" fill-opacity=".85"/><rect x="240" y="185" width="12" height="9" rx="2" fill="none" stroke="#f5ecd6" stroke-opacity=".85" stroke-width="1.5"/><path d="M241 232l10-3-4 9-1-4z" fill="#f5ecd6" fill-opacity=".85"/>'+
  (it.handle?'<text x="14" y="408" font-family="Inter,sans-serif" font-size="12" font-weight="700" fill="#f5ecd6">'+esc(it.handle)+'</text>':'')+
  '<text x="14" y="424" font-family="Inter,sans-serif" font-size="10" fill="#cfc6b0">'+esc((it.entity||'').slice(0,40))+'</text>'+
  '</svg>';
  return s;
}
function player(it,small){
  var dur=it.duration||28, url=SESSION_MEDIA[it.id];
  var media=url?'<video src="'+url+'" playsinline muted preload="metadata"></video>':(it.thumb?'<img class="poster" src="'+it.thumb+'" alt="">':poster(it));
  return '<div class="v916'+(small?' small':'')+'" data-id="'+it.id+'" data-dur="'+dur+'">'+media+
   (it.sample?'<span class="sample">'+u('example')+'</span>':'')+
   '<button class="play" type="button" aria-label="Play clip"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button>'+
   '<div class="pbar"><div class="trk"><i style="width:'+(small?18:38)+'%"></i></div><span class="tm">0:'+(small?'05':'11')+' / 0:'+String(dur).padStart(2,'0')+'</span></div></div>';
}
var anim=null;
function bindPlay(root){
  $$('.v916 .play',root).forEach(function(b){b.addEventListener('click',function(e){
    e.stopPropagation();var box=b.closest('.v916'),d=+box.getAttribute('data-dur')||28,fill=$('.trk i',box),tm=$('.tm',box),v=$('video',box);
    if(box.classList.contains('playing')){box.classList.remove('playing');if(v)v.pause();cancelAnimationFrame(anim);return}
    box.classList.add('playing');if(v){v.currentTime=0;v.play().catch(function(){})}
    var t0=performance.now();(function step(t){var x=Math.min(1,(t-t0)/(d*1000));fill.style.width=(x*100)+'%';tm.textContent='0:'+String(Math.round(x*d)).padStart(2,'0')+' / 0:'+String(d).padStart(2,'0');if(x<1&&box.classList.contains('playing'))anim=requestAnimationFrame(step);else box.classList.remove('playing')})(t0);
  })});
}
function vbadge(){return '<span class="badge-v" tabindex="0">'+u('vbadge')+'<span class="tip">'+esc(u('vtip'))+'</span></span>'}
function credit(it){
  if(it.sample) return '';
  if(!it.handle) return '<div class="credit">'+vbadge()+'</div>';
  var l=String(it.handle).replace('@','').charAt(0).toUpperCase();
  return '<div class="credit"><span class="avatar" aria-hidden="true">'+esc(l)+'</span><span class="by">'+u('filmed')+'</span> <a class="h" href="'+esc(it.social||'#')+'" title="Contributor profile" rel="nofollow noopener">'+esc(it.handle)+'</a> '+vbadge()+'</div>'}
function logo(name){var c=name.charAt(0);
  return '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="2" y="2" width="44" height="44" rx="11" fill="#0b1719"/><rect x="5" y="5" width="38" height="38" rx="9" fill="none" stroke="#d9b765" stroke-width="1.5"/><text x="24" y="31" text-anchor="middle" font-family="Marcellus,Georgia,serif" font-size="21" fill="#f0d58c">'+esc(c)+'</text><g fill="#d9b765"><circle cx="35" cy="37" r="2.2"/><circle cx="31.5" cy="34" r="1.1"/><circle cx="35" cy="32.6" r="1.1"/><circle cx="38.5" cy="34" r="1.1"/></g></svg>'}
function mentionBlock(it,compact){ return ''; }

/* ---------- zero-backend submission transport (static GitHub Pages safe) ---------- */
/* CRITICAL: localStorage alone never reaches Marc/Veilleur on a visitor's browser.
   On submit we (1) keep a local copy for this browser's demo, (2) download a JSON
   payload the visitor can attach, (3) offer a mailto: handoff to contact@… that the
   visitor must click themselves (no auto-send, no Formspree account required yet).
   Production upgrade path (flagged in LAUNCH-CHECKLIST.md): Formspree / Cloudflare
   Worker / GitHub Issue form — swap INTAKE.endpoint when ready. */
var INTAKE={
  email:'contact@petpolicycheck.com',
  endpoint:null, /* set to Formspree/Worker URL later; null = JSON download + mailto only */
  mode:(q.get('intake')||'mailto-json') /* mailto-json | local-only */
};
function downloadJson(name,obj){
  var blob=new Blob([JSON.stringify(obj,null,2)],{type:'application/json'});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;
  document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},400);
}
function mailtoFor(it){
  var kind=it.kind==='clip'?'30s Field Clip (#4)':(it.kind==='rule'?'Rule Check (#9)':'City Scout Pack (#11)');
  var sub='[Field Guides] New '+kind+' from '+it.handle;
  var body=['Hello PetPolicyCheck team,','','I just submitted a '+kind+' via /field-guides/.','Please find the JSON payload attached (downloaded from my browser) or pasted below.','','Handle: '+it.handle,'Kind: '+it.kind,'Id: '+it.id,'Corridor: '+(it.country||it.hub||''),'Date: '+(it.date||''),'','--- JSON ---',JSON.stringify(it,null,2),'','--- end ---'].join('\n');
  return 'mailto:'+INTAKE.email+'?subject='+encodeURIComponent(sub)+'&body='+encodeURIComponent(body).slice(0,1800);
}
function queueSubmission(it){
  /* Always persist locally so the admin queue on THIS browser can demo moderation. */
  DB.unshift(it);save(DB);
  var packet={generated:new Date().toISOString(),source:'petpolicycheck.com/field-guides',intake:'visitor-submission',status:'pending-L0',item:it};
  var fname='field-guides-submission-'+it.id+'.json';
  var mail=mailtoFor(it);
  if(INTAKE.mode!=='local-only'){ try{downloadJson(fname,packet)}catch(e){} }
  /* Optional future: if(INTAKE.endpoint) fetch(INTAKE.endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(packet)}) */
  return {filename:fname,mailto:mail,packet:packet};
}
function doneMsg(form,k,handoff){
  var d=$('.done',form)||$('#done');d.className='done on';
  var label=(k==='clip'?'30s clip':k==='rule'?'rule check':'City Scout pack');
  var html='✓ Thanks! Your '+label+' is queued for human review (L0, internal only).';
  if(handoff && INTAKE.mode!=='local-only'){
    html+=' <div class="intake-box"><b>How your tip reaches us (static site, zero server):</b><ol>'+
      '<li>A JSON file <code>'+esc(handoff.filename)+'</code> just downloaded — keep it.</li>'+
      '<li><a class="btn gold sm" id="mailHandoff" href="'+esc(handoff.mailto)+'">Email it to '+esc(INTAKE.email)+'</a> <small>(opens your mail app — nothing is sent automatically)</small></li>'+
      '<li>Or paste the JSON into any message to that address. A moderator reviews before anything goes live.</li></ol>'+
      '<p class="mini">Example note: this browser also saved a local copy so Marc can demo <a href="?view=moderation&amp;admin=1">Moderation</a> here. On the live static site, only the JSON / email handoff reaches the team.</p></div>';
  } else {
    html+=' <span class="mini">(local-only mode — nothing left this browser)</span>';
  }
  d.innerHTML=html;
}

/* ---------- views ---------- */
var view=q.get('view')||'gallery'; if(['gallery','submit','moderation'].indexOf(view)<0)view='gallery';
var isAdmin = (q.get('admin')==='1' || view==='moderation');
function applyAdminChrome(){
  document.body.classList.toggle('admin-mode', isAdmin);
  $$('.admin-only').forEach(function(el){el.hidden=!isAdmin});
  /* Public never lands on moderation without an explicit admin URL */
  if(view==='moderation' && q.get('admin')!=='1' && q.get('view')!=='moderation'){view='gallery'}
}
function show(){
  applyAdminChrome();
  if(view==='moderation' && !isAdmin){view='gallery'}
  isAdmin = (q.get('admin')==='1' || view==='moderation');
  applyAdminChrome();
  $$('.view').forEach(function(v){v.hidden=v.id!=='v-'+view});
  $$('.pvbar [data-view], .pubtabs [data-view]').forEach(function(a){if(a.getAttribute('data-view')===view)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
  $$('.top .nav [data-nav]').forEach(function(a){if(a.getAttribute('data-nav')===view)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
  if(view==='gallery')renderGallery(); if(view==='moderation'&&isAdmin)renderQueue();
}

/* (c) gallery */
var gC='all',gT='all',featId=null;
function typeGroup(t){return t==='airline'?'airlines':(t==='train'?'ferries':(t==='grooming'?'groom':'hotels'))}
function renderGallery(){
  var f=$('#filters'),h='<span class="lab">'+u('country')+'</span>';
  [['all',u('all')]].concat(COUNTRIES.map(function(c){return [c,CSHORT[c]]})).forEach(function(c){h+='<button type="button" class="fbtn'+(gC===c[0]?' on':'')+'" data-c="'+esc(c[0])+'">'+esc(c[1])+'</button>'});
  h+='<span class="brk"></span><span class="lab">'+u('type')+'</span>';
  [['all','All'],['airlines',u('airlines')],['ferries',u('ferries')],['hotels',u('hotels')],['groom',u('groom')]].forEach(function(t){h+='<button type="button" class="fbtn'+(gT===t[0]?' on':'')+'" data-t="'+t[0]+'">'+esc(t[1])+'</button>'});
  f.innerHTML=h;
  $$('[data-c]',f).forEach(function(b){b.onclick=function(){gC=b.getAttribute('data-c');featId=null;renderGallery()}});
  $$('[data-t]',f).forEach(function(b){b.onclick=function(){gT=b.getAttribute('data-t');featId=null;renderGallery()}});
  var list=DB.filter(function(x){return x.kind==='clip'&&x.status==='approved'&&(gC==='all'||x.country===gC)&&(gT==='all'||typeGroup(x.type)===gT)});
  list.sort(function(a,b){return (b.mention==='paid')-(a.mention==='paid')||String(b.reviewedAt).localeCompare(a.reviewedAt)});
  $('#gcount').textContent=list.length+' '+u('episodes');
  var fe=list.filter(function(x){return x.id===featId})[0]||list[0];
  if(!fe){$('#feat').innerHTML='<div class="empty" style="grid-column:1/-1">'+u('nores')+'</div>';$('#cards').innerHTML='';}
  else{
    featId=fe.id;
    $('#feat').innerHTML='<div>'+player(fe)+'</div><div>'+
     '<div class="dept">'+u('featured')+' · '+esc(CSHORT[fe.country])+' · '+esc(TYPES[fe.type])+(fe.guse?' · '+esc(GUSE[fe.guse]):'')+(fe.sample?' · <span class="sample">'+u('example')+'</span>':'')+'</div>'+
     '<h2>'+esc(fe.entity)+'</h2>'+(fe.sample||!fe.tip?'':('<p class="tipq">“'+esc(fe.tip)+'”</p>'))+credit(fe)+
     '<div class="fv"><span class="chip off">Official rule</span><span style="flex:1;min-width:240px">'+esc(fe.official)+' <a href="'+esc(fe.officialUrl)+'" target="_blank" rel="noopener">'+u('official')+'</a></span></div>'+
     (fe.sample?'':('<div class="fv"><span class="chip gold">'+u('fv')+' · '+mon((fe.reviewedAt||'').slice(0,7))+'</span><span>'+u('trip')+': '+mon(fe.date)+(fe.bag?' · '+esc(fe.bag):'')+'</span></div>'))+
     mentionBlock(fe,false)+(fe.mention&&fe.mention!=='none'?'<div class="openslot" style="margin-top:10px">'+u('brandother')+' <a href="../contact.html#suggest-a-product">'+u('opencta')+'</a></div>':'')+'</div>';
    bindPlay($('#feat'));
    $('#cards').innerHTML=list.map(function(it){return '<article class="panel card'+(it.id===featId?' sel':'')+'" data-id="'+it.id+'">'+player(it,true)+
     '<div style="display:flex;gap:6px;flex-wrap:wrap">'+(it.sample?'<span class="sample">'+u('example')+'</span>':'')+'<span class="chip">'+esc(CSHORT[it.country])+'</span><span class="chip'+(it.type==='grooming'?' gold':'')+'">'+esc(TYPES[it.type])+'</span></div>'+
     '<h3>'+esc(it.entity)+'</h3>'+credit(it)+(it.sample?'':'<span class="chip gold" style="align-self:flex-start">'+u('fv')+' · '+mon((it.reviewedAt||'').slice(0,7))+'</span>')+mentionBlock(it,true)+'</article>'}).join('');
    $$('#cards .card').forEach(function(c){c.onclick=function(e){if(e.target.closest('a,.badge-v'))return;featId=c.getAttribute('data-id');renderGallery();$('#feat').scrollIntoView({behavior:'smooth',block:'center'})}});
    bindPlay($('#cards'));
  }
  var rules=DB.filter(function(x){return x.kind==='rule'&&x.status==='approved'});
  $('#rules').innerHTML=rules.map(function(r){return '<article class="panel rulecard"><div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center"><span class="kindtag rule">#9 Rule check</span><span class="chip">'+esc(CSHORT[r.country])+'</span><span class="chip">'+esc(r.checkpoint)+'</span>'+(r.sample?'<span class="sample" style="margin-left:auto">'+u('example')+'</span>':'')+'</div>'+
    '<h3>'+esc(r.route)+'</h3><div class="dual"><div class="o"><span class="lab">Official rule</span><br>'+esc(r.official)+'<br><a href="'+esc(r.officialUrl)+'" target="_blank" rel="noopener">Source ↗</a></div>'+
    (r.sample||!r.diff?'':('<div class="f"><span class="lab">'+u('fv')+' · '+mon((r.reviewedAt||'').slice(0,7))+'</span><br>'+esc(r.diff)+'</div>'))+'</div>'+
    (r.sample?'':'<div class="credit">'+(r.handle?'<span class="by">'+u('reported')+'</span> <a class="h" href="#">'+esc(r.handle)+'</a> ':'')+vbadge()+'</div>')+'</article>'}).join('');
  $('#hubgrid').innerHTML=HUBS.map(function(h){var s=DB.filter(function(x){return x.kind==='scout'&&x.hub===h[0]&&x.status==='approved'})[0];
    return '<div class="hubt'+(s?' live':'')+'"><b>'+esc(h[0])+'</b><span>'+esc(h[1])+'</span><span class="dots" title="Vet · Grooming · Big-Dog Taxi · Stay">'+[0,1,2,3].map(function(){return '<i'+(s?' class="on"':'')+'></i>'}).join('')+'</span>'+
    (s?(s.handle?'<span class="badge-s">★ '+esc(s.handle)+'</span>':'')+'<span class="sample">'+u('example')+'</span>':'<a href="?view=submit&amp;mode=scout">'+u('seatopen')+'</a>')+'</div>'}).join('');
  var openN=list.filter(function(x){return !x.mention||x.mention==='none'}).length;
  var slotsEl=$('#slots'); if(slotsEl) slotsEl.innerHTML='<div class="slot"><span class="logo" style="width:34px;height:34px;border-radius:8px;background:#fdf8ef;display:grid;place-items:center">'+logo('S').replace('viewBox','width="28" height="28" viewBox')+'</span><div><b>Example product mention · Sleepypod</b><br><span style="color:var(--mut)">Product mention · Air France 8 kg episode</span></div><span class="chip gold">Sample</span></div>'+
   '<div class="slot"><span class="logo" style="width:34px;height:34px;border-radius:8px;background:#fdf8ef;display:grid;place-items:center">'+logo('K').replace('viewBox','width="28" height="28" viewBox')+'</span><div><b>Example product mention · Kurgo</b><br><span style="color:var(--mut)">Product mention · LeShuttle episode</span></div><span class="chip gold">Sample</span></div>'+
   '<div class="slot"><div><b>'+openN+' open episode slots</b><br><span style="color:var(--mut)">Incl. Grooming &amp; Care, CDC, WestJet heat embargo</span></div><a class="chip" href="../contact.html#suggest-a-product" style="text-decoration:none">'+u('opencta')+'</a></div>';
}

/* (b) moderation */
var fS='all',fCo='all',fTy='all';
var CHECKS=[['policy','Policy accuracy','Checked against the official airline / country rule; kept separate as “Official rule” vs “Field-verified [Mon YYYY]”.'],
['welfare','Animal welfare','Safe carrier & ventilation, no distress or unsafe handling — incl. gentle, fear-free salon handling, no forced sedation.'],
['audio','Audio / music rights','No copyright-blocked commercial music; original voiceover or royalty-safe audio (n/a for text-only checks).'],
['privacy','Quality & privacy','Readable video/captions; luggage tags, passports, boarding-pass QR codes, plates & salon client data blurred.']];
function kindLabel(k){return k==='clip'?'30s Clip #4':(k==='rule'?'Rule Check #9':'City Scout Pack #11')}
function stChip(it){return it.status==='pending'?'<span class="chip pend">Pending L0 · Internal only</span>':(it.status==='approved'?'<span class="chip ok">Approved L2 · Field-Verified '+mon((it.reviewedAt||'').slice(0,7))+'</span>':'<span class="chip no">Rejected'+(it.rejectReason?' · '+esc(it.rejectReason):'')+'</span>')}
function renderQueue(){
  var n={pending:0,approved:0,rejected:0};DB.forEach(function(x){n[x.status]++});
  $('#counts').innerHTML='<button type="button" class="count p'+(fS==='pending'?' on':'')+'" data-s="pending"><b>'+n.pending+'</b><span>Pending L0 · Internal only ('+n.pending+')</span></button>'+
   '<button type="button" class="count a'+(fS==='approved'?' on':'')+'" data-s="approved"><b>'+n.approved+'</b><span>Approved L2 · Field-Verified ('+n.approved+')</span></button>'+
   '<button type="button" class="count r'+(fS==='rejected'?' on':'')+'" data-s="rejected"><b>'+n.rejected+'</b><span>Rejected ('+n.rejected+')</span></button>';
  $$('#counts .count').forEach(function(b){b.onclick=function(){var s=b.getAttribute('data-s');fS=fS===s?'all':s;$('#fStatus').value=fS;renderQueue()}});
  var order={pending:0,approved:1,rejected:2};
  var list=DB.filter(function(x){return (fS==='all'||x.status===fS)&&(fCo==='all'||x.country===fCo)&&(fTy==='all'||(fTy==='grooming'?(x.type==='grooming'||x.kind==='scout'||/groom/i.test(x.checkpoint||'')):x.kind===fTy))});
  list.sort(function(a,b){return order[a.status]-order[b.status]||(a.kind==='clip'?0:a.kind==='rule'?1:2)-(b.kind==='clip'?0:b.kind==='rule'?1:2)});
  if(!list.length){$('#queue').innerHTML='<div class="panel empty">No item for this filter.</div>';return}
  var last=null,SEC={pending:'Pending L0 — internal only, needs human review',approved:'Approved L2 — Field-Verified (live on the static site)',rejected:'Rejected — not published, reason sent to contributor'};
  $('#queue').innerHTML=list.map(function(it){var h=it.status!==last?'<div class="qsec">'+SEC[it.status]+'</div>':'';last=it.status;return h+qItem(it)}).join('');
  bindPlay($('#queue'));
  $$('#queue .qitem').forEach(function(el){
    var it=DB.filter(function(x){return x.id===el.getAttribute('data-id')})[0];
    if(el.classList.contains('compact')){$('.openit',el).onclick=function(){OPEN[it.id]=1;renderQueue()};$('.pend',el).onclick=function(){it.status='pending';it.audit=(it.audit||[]).concat('Back to L0 '+new Date().toLocaleString());save(DB);renderQueue()};return}
    var ap=$('.approve',el), boxes=$$('.ck input',el);
    function upd(){var all=boxes.every(function(b){return b.checked});ap.disabled=!all;ap.title=all?'':'Tick all 4 checks to enable';}
    boxes.forEach(function(b){b.onchange=function(){it.checks=it.checks||{};it.checks[b.name]=b.checked;save(DB);upd()}});upd();
    $('.sp-sel',el)&&($('.sp-sel',el).onchange=function(){it.mention=this.value;save(DB)});
    $('.sp-brand',el)&&($('.sp-brand',el).oninput=function(){it.brand=this.value;save(DB)});
    $('.note',el).oninput=function(){it.note=this.value;save(DB)};
    $('.rsn',el).onchange=function(){it.rejectReason=this.value;save(DB)};
    $('.bdg',el).onchange=function(){it.badge=this.value;save(DB)};
    ap.onclick=function(){it.status='approved';it.reviewedAt=new Date().toISOString().slice(0,10);if(!it.badge||it.badge==='auto')it.badge=it.kind==='scout'?'scout':'traveler';it.audit=(it.audit||[]).concat('Approved L2 '+new Date().toLocaleString());save(DB);renderQueue()};
    $('.reject',el).onclick=function(){var r=$('.rsn',el).value;if(!r){$('.rsn',el).focus();$('.rsn',el).style.borderColor='#f0a3a3';return}it.status='rejected';it.rejectReason=r;it.audit=(it.audit||[]).concat('Rejected '+new Date().toLocaleString());save(DB);renderQueue()};
    $('.pend',el).onclick=function(){it.status='pending';it.audit=(it.audit||[]).concat('Back to L0 '+new Date().toLocaleString());save(DB);renderQueue()};
  });
}
var OPEN={};
function qCompact(it){
  var t=it.kind==='clip'?it.entity:(it.kind==='rule'?it.route:'Founding City Scout · '+it.hub);
  return '<article class="panel qitem compact st-'+it.status+'" data-id="'+it.id+'"><span class="qi"><svg viewBox="0 0 24 24"><path d="'+(it.kind==='clip'?(ICON[it.type]||ICON.airline):ICON[it.kind])+'"/></svg></span><div class="cm"><b>'+esc(t)+'</b><div class="chips"><span class="kindtag '+it.kind+'">'+kindLabel(it.kind)+'</span>'+stChip(it)+'<span class="chip">'+esc(CSHORT[it.country]||it.country)+'</span>'+(it.type==='grooming'||it.kind==='scout'?'<span class="chip gold">Grooming</span>':'')+(it.handle?'<span class="chip">'+esc(it.handle)+' · '+(it.badge==='scout'?'★ Founding City Scout':(it.status==='approved'?'✓ Verified Corridor Traveler':'no badge'))+'</span>':'<span class="chip">'+(it.badge==='scout'?'★ Founding City Scout':(it.status==='approved'?'✓ Verified Corridor Traveler':'no badge'))+'</span>')+(it.kind==='clip'&&it.status==='approved'?'<span class="chip'+(it.mention&&it.mention!=='none'?' gold':'')+'">Mention: '+esc(it.mention&&it.mention!=='none'?MENTION_LABEL[it.mention]+' · '+(it.brand||''):'Contact')+'</span>':'')+(it.sample?'<span class="sample">'+u('example')+'</span>':'')+'</div>'+(it.note?'<div class="audit">Note: '+esc(it.note)+'</div>':'')+'</div><div class="acts"><button class="btn ghost sm openit" type="button">Review details</button><button class="btn ghost sm pend" type="button">Back to L0</button></div></article>'}
function qItem(it){
  if(it.status!=='pending'&&!OPEN[it.id])return qCompact(it);
  var left,meta,isClip=it.kind==='clip';
  if(isClip){left=player(it,true)+'<span class="chip" style="justify-content:center">'+esc(it.platform)+(it.duration?' · 0:'+it.duration:'')+'</span>'}
  else{left='<div class="qicon"><svg viewBox="0 0 24 24"><path d="'+ICON[it.kind]+'"/></svg><b>'+(it.kind==='rule'?'Rule check':'Scout pack')+'</b>'+esc(it.kind==='rule'?it.route:it.hub)+(it.sample?'<span class="sample">'+u('example')+'</span>':'')+'</div>'}
  var chips='<div class="chips"><span class="kindtag '+it.kind+'">'+kindLabel(it.kind)+'</span>'+stChip(it)+'<span class="chip">'+esc(CSHORT[it.country]||it.country)+'</span>'+(isClip?'<span class="chip'+(it.type==='grooming'?' gold':'')+'">'+esc(TYPES[it.type])+(it.guse?' · '+esc(GUSE[it.guse]):'')+'</span>':'')+(it.kind==='rule'?'<span class="chip">'+esc(it.checkpoint)+'</span>':'')+'</div>';
  if(isClip){meta='<h3>'+esc(it.entity)+'</h3>'+chips+'<p class="quote">“'+esc(it.tip)+'”</p>'+
    '<div class="dual"><div class="o"><span class="lab">Official rule</span><br>'+esc(it.official||'—')+(it.officialUrl?'<br><a href="'+esc(it.officialUrl)+'" target="_blank" rel="noopener">Source ↗</a>':'')+'</div><div class="f"><span class="lab">Field note · trip '+mon(it.date)+'</span><br>'+esc(it.caption||'')+(it.bag?'<br><span style="color:var(--mut)">'+esc(it.bag)+'</span>':'')+'</div></div>';}
  else if(it.kind==='rule'){meta='<h3>'+esc(it.route)+'</h3>'+chips+'<div class="dual"><div class="o"><span class="lab">Official rule</span><br>'+esc(it.official)+'<br><a href="'+esc(it.officialUrl)+'" target="_blank" rel="noopener">Source ↗</a></div><div class="f"><span class="lab">What differed · '+mon(it.date)+'</span><br>'+esc(it.diff)+'</div></div>'+(it.proof?'<p style="font-size:.8rem;color:var(--mut);margin:8px 0 0">Light proof: '+esc(it.proof)+'</p>':'')}
  else{var pk=it.pack||{};meta='<h3>Founding City Scout · '+esc(it.hub)+'</h3>'+chips+'<div class="scoutpack"><div><b>1 · Export vet EN/FR</b>'+esc(pk.vet)+'</div><div class="g"><b>2 · Grooming (fear-free)</b>'+esc(pk.groom)+'</div><div><b>3 · Big-dog taxi</b>'+esc(pk.taxi)+'</div><div><b>4 · Stay / park</b>'+esc(pk.stay)+'</div></div>'}
  meta+='<dl>'+(it.handle?'<dt>Contributor</dt><dd><a href="'+esc(it.social||'#')+'" style="color:var(--gold2)">'+esc(it.handle)+'</a></dd>':'')+'<dt>Rights consent</dt><dd>'+(it.consentAt?'✓ Non-exclusive republish licence · '+esc(it.consentAt):'✓ on file')+'</dd><dt>Trip / visit</dt><dd>'+mon(it.date)+'</dd></dl>';
  var c=it.checks||{}, appr=it.status==='approved';
  var g='<div class="grid4"><h4>4 mandatory checks</h4>'+CHECKS.map(function(k){var on=appr||c[k[0]];return '<label class="ck"><input type="checkbox" name="'+k[0]+'"'+(on?' checked':'')+'><span><b>'+k[1]+'</b><span>'+k[2]+'</span></span></label>'}).join('')+
   '<div class="ctl"><div><div class="lbl">Badge on approve</div><select class="bdg"><option value="auto">Auto (by ladder)</option><option value="traveler"'+(it.badge==='traveler'?' selected':'')+'>Verified Corridor Traveler</option><option value="scout"'+(it.badge==='scout'?' selected':'')+(it.kind!=='scout'?' disabled':'')+'>Founding City Scout</option></select></div>'+
   (isClip?'<div><div class="lbl">Product mention</div><select class="sp-sel">'+Object.keys(MENTION_LABEL).map(function(k){return '<option value="'+k+'"'+((it.mention||'none')===k?' selected':'')+'>'+MENTION_LABEL[k]+'</option>'}).join('')+'</select></div>':'<div><div class="lbl">Product mention</div><select disabled><option>n/a (clips only)</option></select></div>')+
   '<div><div class="lbl">Reject reason</div><select class="rsn"><option value="">—</option>'+REJECT.map(function(r){return '<option'+(it.rejectReason===r?' selected':'')+'>'+r+'</option>'}).join('')+'</select></div>'+
   (isClip?'<div><div class="lbl">Partner brand</div><input class="sp-brand" type="text" value="'+esc(it.brand||'')+'" placeholder="e.g. Sleepypod"></div>':'<div></div>')+
   '<div class="full"><div class="lbl">Moderator note</div><input class="note" type="text" value="'+esc(it.note||'')+'" placeholder="Internal note / reason sent to contributor"></div></div>'+
   '<div class="acts"><button class="btn ghost pend" type="button">Pending</button><button class="btn ok approve" type="button">Approve &amp; Publish</button><button class="btn no reject" type="button">Reject</button></div>'+
   (it.audit?'<div class="audit">'+esc(it.audit.slice(-1)[0])+'</div>':'')+'</div>';
  return '<article class="panel qitem st-'+it.status+'" data-id="'+it.id+'"><div class="qposter">'+left+'</div><div class="meta">'+meta+'</div>'+g+'</article>';
}

/* (a) submit */
function initSubmit(){
  var tabs=$$('.hubmodes button');
  function setPane(p){tabs.forEach(function(t){t.classList.toggle('on',t.getAttribute('data-pane')===p);t.setAttribute('aria-selected',t.getAttribute('data-pane')===p)});$$('form.pane').forEach(function(f){f.hidden=f.getAttribute('data-pane')!==p})}
  tabs.forEach(function(t){t.onclick=function(){setPane(t.getAttribute('data-pane'))}});
  var m=q.get('mode'); setPane(m==='rule'||m==='scout'?m:'clip');
  $$('.mode input').forEach(function(r){r.addEventListener('change',function(){$$('input[name="'+r.name+'"]').forEach(function(x){x.closest('.mode').classList.toggle('on',x.checked)});
    if(r.name==='mode'){$('#upBox').hidden=r.value!=='upload';$('#lnBox').hidden=r.value!=='link'}})});
  $$('input[name="type"]').forEach(function(r){r.onchange=function(){$('#groomUse').hidden=r.value!=='grooming'||!r.checked}});
  if(q.get('type')==='grooming'){var g=$('input[name="type"][value="grooming"]');g.checked=true;$('#groomUse').hidden=false}
  var drop=$('#drop'),file=$('#file'),upFile=null,upDur=0,upThumb=null;
  ['dragenter','dragover'].forEach(function(e){drop.addEventListener(e,function(ev){ev.preventDefault();drop.classList.add('drag')})});
  ['dragleave','drop'].forEach(function(e){drop.addEventListener(e,function(ev){ev.preventDefault();drop.classList.remove('drag')})});
  drop.addEventListener('drop',function(ev){if(ev.dataTransfer.files[0])handle(ev.dataTransfer.files[0])});
  file.onchange=function(){if(file.files[0])handle(file.files[0])};
  function handle(f){
    var msg=$('#upMsg');upFile=null;
    if(!/\.(mp4|mov)$/i.test(f.name)&&!/video\/(mp4|quicktime)/.test(f.type)){msg.className='msg no';msg.textContent='Please use an .mp4 or .mov file.';return}
    var url=URL.createObjectURL(f),v=document.createElement('video');v.preload='metadata';v.muted=true;v.src=url;
    v.onloadedmetadata=function(){upDur=Math.round(v.duration);if(v.duration>35){msg.className='msg no';msg.textContent='This clip is '+upDur+' s — please trim it to 30 s (max 35 s).';return}
      v.currentTime=Math.min(.5,v.duration/2)};
    v.onseeked=function(){try{var c=document.createElement('canvas');c.width=180;c.height=320;var x=c.getContext('2d');var r=Math.max(180/v.videoWidth,320/v.videoHeight),w=v.videoWidth*r,h=v.videoHeight*r;x.drawImage(v,(180-w)/2,(320-h)/2,w,h);upThumb=c.toDataURL('image/jpeg',.7)}catch(e){upThumb=null}
      $('#thumb').innerHTML=upThumb?'<img src="'+upThumb+'" alt="Clip preview">':'';upFile={f:f,url:url};msg.className='msg ok';msg.textContent='✓ '+f.name+' · '+upDur+' s · ready';};
    v.onerror=function(){msg.className='msg no';msg.textContent='Could not read this video in the browser — try .mp4 (H.264).'};
  }
  function plat(u){return /tiktok\.com/i.test(u)?'TikTok':(/instagram\.com\/(reel|reels|p)\//i.test(u)?'Instagram Reels':(/(youtube\.com\/shorts|youtu\.be)/i.test(u)?'YouTube Shorts':''))}
  $('#url').oninput=function(){var p=plat(this.value);$('#plat').textContent='Platform: '+(p||'—');$('#plat').className='chip'+(p?' gold':'');$('#lnMsg').className='msg'+(this.value&&!p?' no':'');$('#lnMsg').textContent=this.value&&!p?'Use a TikTok, Instagram Reels or YouTube Shorts link.':''};
  $('#tip').oninput=function(){$('#cnt').textContent=this.value.length};
  $('#rDiff').oninput=function(){$('#rCnt').textContent=this.value.length};
  function handleOk(h){return /^@[A-Za-z0-9._]{2,30}$/.test(h.trim())}
  $('#subForm').onsubmit=function(e){e.preventDefault();var err=[],mode=$('input[name="mode"]:checked').value,type=$('input[name="type"]:checked').value,url=$('#url').value.trim();
    if(mode==='upload'&&!upFile)err.push('add a clip ≤ 30 s');if(mode==='link'&&!plat(url))err.push('paste a TikTok / Reels / Shorts link');
    if(!$('#entity').value.trim())err.push('name the airline / hotel / city / salon');if(!$('#date').value)err.push('trip date');
    if($('#tip').value.trim().length<15)err.push('write your field tip');if(!handleOk($('#handle').value))err.push('@handle');if(!$('#consent').checked)err.push('tick the rights confirmation');
    if(err.length){$('#formErr').textContent='Almost there: '+err.join(' · ')+'.';return}$('#formErr').textContent='';
    var id='c-'+Date.now(),ct=$('#country').value,gu=type==='grooming'?$('input[name="guse"]:checked').value:undefined,ent=$('#entity').value.trim();
    var it={id:id,kind:'clip',status:'pending',mode:mode,platform:mode==='upload'?'Upload':plat(url),url:mode==='link'?url:'',type:type,guse:gu,country:ct,entity:ent,route:ent.split('·').pop().trim().slice(0,30),date:$('#date').value,duration:mode==='upload'?upDur:undefined,
      tip:$('#tip').value.trim(),caption:$('#tip').value.trim().split(/[.:;—]/)[0].slice(0,60),bag:$('#bag').value.trim(),handle:$('#handle').value.trim(),social:$('#social').value.trim(),consentAt:new Date().toLocaleString(),thumb:mode==='upload'?upThumb:null,mention:'none',official:'(moderator to add the official rule + source)'};
    if(upFile)SESSION_MEDIA[id]=upFile.url;
    var handoff=queueSubmission(it);doneMsg(this,'clip',handoff);};
  $('#ruleForm').onsubmit=function(e){e.preventDefault();var err=[];if(!$('#rRoute').value.trim())err.push('place / route');if($('#rDiff').value.trim().length<15)err.push('what differed');if(!handleOk($('#rHandle').value))err.push('@handle');
    var box=$('.err',this);if(err.length){box.textContent='Almost there: '+err.join(' · ')+'.';return}box.textContent='';
    var it={id:'r-'+Date.now(),kind:'rule',status:'pending',country:$('#rCorr').value,checkpoint:$('#rCheck').value.trim(),route:$('#rRoute').value.trim(),date:$('#rDate').value,diff:$('#rDiff').value.trim(),proof:$('#rProof').value.trim(),handle:$('#rHandle').value.trim(),social:$('#rSocial').value.trim(),consentAt:new Date().toLocaleString(),official:'(moderator to paste the official rule + source)',officialUrl:'#'};var handoff=queueSubmission(it);doneMsg(this,'rule',handoff)};
  $('#hubPick').innerHTML=HUBS.map(function(h,i){return '<label><input type="radio" name="hub" value="'+esc(h[0])+'"'+(i===0?' checked':'')+'><span>'+esc(h[0])+'<small>'+esc(h[1])+'</small></span></label>'}).join('');
  $('#scoutForm').onsubmit=function(e){e.preventDefault();var err=[];['sVet','sGroom','sTaxi','sStay'].forEach(function(k,i){if($('#'+k).value.trim().length<5)err.push('check '+(i+1))});if(!handleOk($('#sHandle').value))err.push('@handle');
    var box=$('.err',this);if(err.length){box.textContent='Almost there: '+err.join(' · ')+'.';return}box.textContent='';
    var hub=$('input[name="hub"]:checked').value,h=HUBS.filter(function(x){return x[0]===hub})[0];
    var it={id:'s-'+Date.now(),kind:'scout',status:'pending',hub:hub,country:h[1].split(' · ')[0],date:nowYM(),handle:$('#sHandle').value.trim(),social:$('#sSocial').value.trim(),consentAt:new Date().toLocaleString(),pack:{vet:$('#sVet').value.trim(),groom:$('#sGroom').value.trim(),taxi:$('#sTaxi').value.trim(),stay:$('#sStay').value.trim()}};var handoff=queueSubmission(it);doneMsg(this,'scout',handoff)};
}


/* export */
function exportJson(){
  var ap=DB.filter(function(x){return x.status==='approved'}).map(function(x){var o=JSON.parse(JSON.stringify(x));delete o.thumb;delete o.checks;delete o.note;delete o.audit;o.fieldVerified=(o.reviewedAt||'').slice(0,7);return o});
  var blob=new Blob([JSON.stringify({generated:new Date().toISOString(),source:'PetPolicyCheck Field Guides',items:ap},null,2)],{type:'application/json'});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='field-guides-approved.json';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},500);
}

/* boot */
$$('[data-lang]').forEach(function(b){b.onclick=function(){lang=b.getAttribute('data-lang');localStorage.setItem(LKEY,lang);applyI18n();show();if(window.PPC_LANG)try{window.PPC_LANG.set(lang,true);}catch(e){}}});
window.addEventListener('ppc:lang',function(ev){if(ev.detail&&ev.detail.lang&&ev.detail.lang!==lang){lang=ev.detail.lang;localStorage.setItem(LKEY,lang);applyI18n();show();}});
var rd=$('#resetDemo'); if(rd) rd.onclick=function(){DB=seed();save(DB);show()};
var fs=$('#fStatus'); if(fs) fs.onchange=function(){fS=this.value;renderQueue()};
var fc=$('#fCorr'); if(fc) fc.onchange=function(){fCo=this.value;renderQueue()};
var ft=$('#fType'); if(ft) ft.onchange=function(){fTy=this.value;renderQueue()};
var ej=$('#exportJson'); if(ej) ej.onclick=exportJson;
function goView(v,admin){
  view=v; isAdmin=(admin||v==='moderation'||q.get('admin')==='1');
  var qs='?view='+v+(isAdmin&&v==='moderation'?'':'')+(q.get('admin')==='1'||(admin&&v!=='gallery'&&v!=='submit')?'&admin=1':'');
  if(v==='moderation') qs='?view=moderation';
  else if(q.get('admin')==='1') qs='?view='+v+'&admin=1';
  else qs='?view='+v;
  history.pushState(null,'',qs);
  /* refresh q from URL */
  q=new URLSearchParams(location.search);
  isAdmin=(q.get('admin')==='1'||view==='moderation');
  show();scrollTo(0,0);
}
$$('.pvbar [data-view], .pubtabs [data-view]').forEach(function(a){a.onclick=function(e){e.preventDefault();goView(a.getAttribute('data-view'))}});
window.addEventListener('popstate',function(){q=new URLSearchParams(location.search);view=q.get('view')||'gallery';if(['gallery','submit','moderation'].indexOf(view)<0)view='gallery';isAdmin=(q.get('admin')==='1'||view==='moderation');show()});
initSubmit();applyI18n();show();
})();
