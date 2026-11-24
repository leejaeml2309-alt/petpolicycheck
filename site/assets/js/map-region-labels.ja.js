/* JA-only region/state display names. Loaded only on /ja/ map pages.
   Mutates GEO / USA_RULES / PPC_LABEL_PLAN (including wrap lines) before the map paints.
   EN/ES/IT/FR/DE pages never load this file. */
(function(){
  var M = {
  "Abruzzo": "アブルッツォ",
  "Aguascalientes": "アグアスカリエンテス",
  "Aichi": "愛知県",
  "Akita": "秋田県",
  "Alabama": "アラバマ",
  "Alaska": "アラスカ",
  "Alberta": "アルバータ",
  "Andalusia": "アンダルシア",
  "Aomori": "青森県",
  "Aosta Valley": "ヴァッレ・ダオスタ",
  "Apulia": "プーリア",
  "Aragon": "アラゴン",
  "Arizona": "アリゾナ",
  "Arkansas": "アーカンソー",
  "Asturias": "アストゥリアス",
  "Australian Capital Territory": "オーストラリア首都特別地域",
  "Auvergne-Rhône-Alpes": "オーヴェルニュ＝ローヌ＝アルプ",
  "Baden-Württemberg": "バーデン＝ヴュルテンベルク",
  "Baja California": "バハ・カリフォルニア",
  "Baja California Sur": "バハ・カリフォルニア・スル",
  "Balearic Islands": "バレアレス諸島",
  "Basilicata": "バジリカータ",
  "Basque Country": "バスク",
  "Bavaria": "バイエルン",
  "Berlin": "ベルリン",
  "Bourgogne-Franche-Comté": "ブルゴーニュ＝フランシュ＝コンテ",
  "Brandenburg": "ブランデンブルク",
  "Bremen": "ブレーメン",
  "Bretagne": "ブルターニュ",
  "British Columbia": "ブリティッシュコロンビア",
  "Busan": "釜山",
  "Calabria": "カラブリア",
  "California": "カリフォルニア",
  "Campania": "カンパニア",
  "Campeche": "カンペチェ",
  "Canary Islands": "カナリア諸島",
  "Cantabria": "カンタブリア",
  "Castile and León": "カスティーリャ・イ・レオン",
  "Castilla-La Mancha": "カスティーリャ＝ラ・マンチャ",
  "Catalonia": "カタルーニャ",
  "Centre-Val de Loire": "サントル＝ヴァル・ド・ロワール",
  "Ceuta": "セウタ",
  "Chiapas": "チアパス",
  "Chiba": "千葉県",
  "Chihuahua": "チワワ",
  "Ciudad de México": "メキシコシティ",
  "Coahuila": "コアウイラ",
  "Colima": "コリマ",
  "Colorado": "コロラド",
  "Community of Madrid": "マドリード州",
  "Connecticut": "コネチカット",
  "Corse": "コルシカ",
  "Daegu": "大邱",
  "Daejeon": "大田",
  "Delaware": "デラウェア",
  "District of Columbia": "コロンビア特別区",
  "Durango": "ドゥランゴ",
  "East Midlands": "イースト・ミッドランズ",
  "East of England": "イースト・オブ・イングランド",
  "Ehime": "愛媛県",
  "Emilia-Romagna": "エミリア＝ロマーニャ",
  "Extremadura": "エストレマドゥーラ",
  "Florida": "フロリダ",
  "Friuli-Venezia Giulia": "フリウリ＝ヴェネツィア・ジュリア",
  "Fukui": "福井県",
  "Fukuoka": "福岡県",
  "Fukushima": "福島県",
  "Galicia": "ガリシア",
  "Gangwon": "江原",
  "Georgia": "ジョージア",
  "Gifu": "岐阜県",
  "Grand Est": "グラン・テスト",
  "Greater London": "グレーター・ロンドン",
  "Guanajuato": "グアナフアト",
  "Guerrero": "ゲレロ",
  "Gunma": "群馬県",
  "Gwangju": "光州",
  "Gyeonggi": "京畿道",
  "Hamburg": "ハンブルク",
  "Hauts-de-France": "オー＝ド＝フランス",
  "Hawaii": "ハワイ",
  "Hesse": "ヘッセン",
  "Hidalgo": "イダルゴ",
  "Hiroshima": "広島県",
  "Hokkaido": "北海道",
  "Hyogo": "兵庫県",
  "Ibaraki": "茨城県",
  "Idaho": "アイダホ",
  "Illinois": "イリノイ",
  "Incheon": "仁川",
  "Indiana": "インディアナ",
  "Iowa": "アイオワ",
  "Ishikawa": "石川県",
  "Iwate": "岩手県",
  "Jalisco": "ハリスコ",
  "Jeju": "済州",
  "Kagawa": "香川県",
  "Kagoshima": "鹿児島県",
  "Kanagawa": "神奈川県",
  "Kansas": "カンザス",
  "Kentucky": "ケンタッキー",
  "Kochi": "高知県",
  "Kumamoto": "熊本県",
  "Kyoto": "京都府",
  "La Rioja": "ラ・リオハ",
  "Lazio": "ラツィオ",
  "Liguria": "リグーリア",
  "Lombardy": "ロンバルディア",
  "Louisiana": "ルイジアナ",
  "Lower Saxony": "ニーダーザクセン",
  "Maine": "メイン",
  "Manitoba": "マニトバ",
  "Marche": "マルケ",
  "Maryland": "メリーランド",
  "Massachusetts": "マサチューセッツ",
  "Mecklenburg-Western Pomerania": "メクレンブルク＝フォアポンメルン",
  "Melilla": "メリリャ",
  "Michigan": "ミシガン",
  "Michoacán": "ミチョアカン",
  "Mie": "三重県",
  "Minnesota": "ミネソタ",
  "Mississippi": "ミシシッピ",
  "Missouri": "ミズーリ",
  "Miyagi": "宮城県",
  "Miyazaki": "宮崎県",
  "Molise": "モリーゼ",
  "Montana": "モンタナ",
  "Morelos": "モレロス",
  "México": "メキシコ州",
  "Nagano": "長野県",
  "Nagasaki": "長崎県",
  "Nara": "奈良県",
  "Navarre": "ナバラ",
  "Nayarit": "ナヤリット",
  "Nebraska": "ネブラスカ",
  "Nevada": "ネバダ",
  "New Brunswick": "ニューブランズウィック",
  "New Hampshire": "ニューハンプシャー",
  "New Jersey": "ニュージャージー",
  "New Mexico": "ニューメキシコ",
  "New South Wales": "ニューサウスウェールズ",
  "New York": "ニューヨーク",
  "Newfoundland and Labrador": "ニューファンドランド・ラブラドール",
  "Niigata": "新潟県",
  "Normandie": "ノルマンディー",
  "North Carolina": "ノースカロライナ",
  "North Chungcheong": "忠清北道",
  "North Dakota": "ノースダコタ",
  "North East": "ノース・イースト",
  "North Gyeongsang": "慶尚北道",
  "North Jeolla": "全羅北道",
  "North Rhine-Westphalia": "ノルトライン＝ヴェストファーレン",
  "North West": "ノース・ウエスト",
  "Northern Ireland": "北アイルランド",
  "Northern Territory": "ノーザンテリトリー",
  "Northwest Territories": "ノースウエスト準州",
  "Nouvelle-Aquitaine": "ヌーヴェル＝アキテーヌ",
  "Nova Scotia": "ノバスコシア",
  "Nuevo León": "ヌエボ・レオン",
  "Nunavut": "ヌナブト準州",
  "Oaxaca": "オアハカ",
  "Occitanie": "オクシタニー",
  "Ohio": "オハイオ",
  "Oita": "大分県",
  "Okayama": "岡山県",
  "Okinawa": "沖縄県",
  "Oklahoma": "オクラホマ",
  "Ontario": "オンタリオ",
  "Oregon": "オレゴン",
  "Osaka": "大阪府",
  "Pays de la Loire": "ペイ・ド・ラ・ロワール",
  "Pennsylvania": "ペンシルベニア",
  "Piedmont": "ピエモンテ",
  "Prince Edward Island": "プリンスエドワードアイランド",
  "Provence-Alpes-Côte d'Azur": "プロヴァンス＝アルプ＝コート・ダジュール",
  "Puebla": "プエブラ",
  "Quebec": "ケベック",
  "Queensland": "クイーンズランド",
  "Querétaro": "ケレタロ",
  "Quintana Roo": "キンタナ・ロー",
  "Region of Murcia": "ムルシア州",
  "Rhineland-Palatinate": "ラインラント＝プファルツ",
  "Rhode Island": "ロードアイランド",
  "Saarland": "ザールラント",
  "Saga": "佐賀県",
  "Saitama": "埼玉県",
  "San Luis Potosí": "サン・ルイス・ポトシ",
  "Sardinia": "サルデーニャ",
  "Saskatchewan": "サスカチュワン",
  "Saxony": "ザクセン",
  "Saxony-Anhalt": "ザクセン＝アンハルト",
  "Schleswig-Holstein": "シュレースヴィヒ＝ホルシュタイン",
  "Scotland": "スコットランド",
  "Sejong": "世宗",
  "Seoul": "ソウル",
  "Shiga": "滋賀県",
  "Shimane": "島根県",
  "Shizuoka": "静岡県",
  "Sicily": "シチリア",
  "Sinaloa": "シナロア",
  "Sonora": "ソノラ",
  "South Australia": "南オーストラリア",
  "South Carolina": "サウスカロライナ",
  "South Chungcheong": "忠清南道",
  "South Dakota": "サウスダコタ",
  "South East": "サウス・イースト",
  "South Gyeongsang": "慶尚南道",
  "South Jeolla": "全羅南道",
  "South West": "サウス・ウエスト",
  "Tabasco": "タバスコ",
  "Tamaulipas": "タマウリパス",
  "Tasmania": "タスマニア",
  "Tennessee": "テネシー",
  "Texas": "テキサス",
  "Thuringia": "テューリンゲン",
  "Tlaxcala": "トラスカラ",
  "Tochigi": "栃木県",
  "Tokushima": "徳島県",
  "Tokyo": "東京都",
  "Tottori": "鳥取県",
  "Toyama": "富山県",
  "Trentino-South Tyrol": "トレンティーノ＝アルト・アディジェ",
  "Tuscany": "トスカーナ",
  "Ulsan": "蔚山",
  "Umbria": "ウンブリア",
  "Utah": "ユタ",
  "Valencian Community": "バレンシア州",
  "Veneto": "ヴェネト",
  "Veracruz": "ベラクルス",
  "Vermont": "バーモント",
  "Victoria": "ビクトリア",
  "Virginia": "バージニア",
  "Wakayama": "和歌山県",
  "Wales": "ウェールズ",
  "Washington": "ワシントン",
  "West Midlands": "ウェスト・ミッドランズ",
  "West Virginia": "ウェストバージニア",
  "Western Australia": "西オーストラリア",
  "Wisconsin": "ウィスコンシン",
  "Wyoming": "ワイオミング",
  "Yamagata": "山形県",
  "Yamaguchi": "山口県",
  "Yamanashi": "山梨県",
  "Yorkshire and the Humber": "ヨークシャー・アンド・ザ・ハンバー",
  "Yucatán": "ユカタン",
  "Yukon": "ユーコン準州",
  "Zacatecas": "サカテカス",
  "Île-de-France": "イル＝ド＝フランス"
};
  var WRAPS = {
  "アグアスカリエンテス": [
    {
      "text": "アグアスカ",
      "dy": "0"
    },
    {
      "text": "リエンテス",
      "dy": "1.05em"
    }
  ],
  "ヴァッレ・ダオスタ": [
    {
      "text": "ヴァッレ・",
      "dy": "0"
    },
    {
      "text": "ダオスタ",
      "dy": "1.05em"
    }
  ],
  "オーストラリア首都特別地域": [
    {
      "text": "オーストラリ",
      "dy": "0"
    },
    {
      "text": "ア首都特別地域",
      "dy": "1.05em"
    }
  ],
  "オーヴェルニュ＝ローヌ＝アルプ": [
    {
      "text": "オーヴェルニュ＝",
      "dy": "0"
    },
    {
      "text": "ローヌ＝アルプ",
      "dy": "1.05em"
    }
  ],
  "バーデン＝ヴュルテンベルク": [
    {
      "text": "バーデン＝",
      "dy": "0"
    },
    {
      "text": "ヴュルテンベルク",
      "dy": "1.05em"
    }
  ],
  "バハ・カリフォルニア": [
    {
      "text": "バハ・",
      "dy": "0"
    },
    {
      "text": "カリフォルニア",
      "dy": "1.05em"
    }
  ],
  "バハ・カリフォルニア・スル": [
    {
      "text": "バハ・カリフォルニア・",
      "dy": "0"
    },
    {
      "text": "スル",
      "dy": "1.05em"
    }
  ],
  "ブルゴーニュ＝フランシュ＝コンテ": [
    {
      "text": "ブルゴーニュ＝",
      "dy": "0"
    },
    {
      "text": "フランシュ＝コンテ",
      "dy": "1.05em"
    }
  ],
  "ブリティッシュコロンビア": [
    {
      "text": "ブリティッシ",
      "dy": "0"
    },
    {
      "text": "ュコロンビア",
      "dy": "1.05em"
    }
  ],
  "カスティーリャ・イ・レオン": [
    {
      "text": "カスティーリャ・",
      "dy": "0"
    },
    {
      "text": "イ・レオン",
      "dy": "1.05em"
    }
  ],
  "カスティーリャ＝ラ・マンチャ": [
    {
      "text": "カスティーリャ＝",
      "dy": "0"
    },
    {
      "text": "ラ・マンチャ",
      "dy": "1.05em"
    }
  ],
  "サントル＝ヴァル・ド・ロワール": [
    {
      "text": "サントル＝ヴァル・",
      "dy": "0"
    },
    {
      "text": "ド・ロワール",
      "dy": "1.05em"
    }
  ],
  "イースト・ミッドランズ": [
    {
      "text": "イースト・",
      "dy": "0"
    },
    {
      "text": "ミッドランズ",
      "dy": "1.05em"
    }
  ],
  "イースト・オブ・イングランド": [
    {
      "text": "イースト・オブ・",
      "dy": "0"
    },
    {
      "text": "イングランド",
      "dy": "1.05em"
    }
  ],
  "エミリア＝ロマーニャ": [
    {
      "text": "エミリア＝",
      "dy": "0"
    },
    {
      "text": "ロマーニャ",
      "dy": "1.05em"
    }
  ],
  "エストレマドゥーラ": [
    {
      "text": "エストレ",
      "dy": "0"
    },
    {
      "text": "マドゥーラ",
      "dy": "1.05em"
    }
  ],
  "フリウリ＝ヴェネツィア・ジュリア": [
    {
      "text": "フリウリ＝ヴェネツィア・",
      "dy": "0"
    },
    {
      "text": "ジュリア",
      "dy": "1.05em"
    }
  ],
  "グレーター・ロンドン": [
    {
      "text": "グレーター・",
      "dy": "0"
    },
    {
      "text": "ロンドン",
      "dy": "1.05em"
    }
  ],
  "オー＝ド＝フランス": [
    {
      "text": "オー＝ド＝",
      "dy": "0"
    },
    {
      "text": "フランス",
      "dy": "1.05em"
    }
  ],
  "メクレンブルク＝フォアポンメルン": [
    {
      "text": "メクレンブルク＝",
      "dy": "0"
    },
    {
      "text": "フォアポンメルン",
      "dy": "1.05em"
    }
  ],
  "ニューブランズウィック": [
    {
      "text": "ニューブラ",
      "dy": "0"
    },
    {
      "text": "ンズウィック",
      "dy": "1.05em"
    }
  ],
  "ニューハンプシャー": [
    {
      "text": "ニューハ",
      "dy": "0"
    },
    {
      "text": "ンプシャー",
      "dy": "1.05em"
    }
  ],
  "ニューサウスウェールズ": [
    {
      "text": "ニューサウ",
      "dy": "0"
    },
    {
      "text": "スウェールズ",
      "dy": "1.05em"
    }
  ],
  "ニューファンドランド・ラブラドール": [
    {
      "text": "ニューファンドランド・",
      "dy": "0"
    },
    {
      "text": "ラブラドール",
      "dy": "1.05em"
    }
  ],
  "ノルトライン＝ヴェストファーレン": [
    {
      "text": "ノルトライン＝",
      "dy": "0"
    },
    {
      "text": "ヴェストファーレン",
      "dy": "1.05em"
    }
  ],
  "ノーザンテリトリー": [
    {
      "text": "ノーザン",
      "dy": "0"
    },
    {
      "text": "テリトリー",
      "dy": "1.05em"
    }
  ],
  "ノースウエスト準州": [
    {
      "text": "ノースウ",
      "dy": "0"
    },
    {
      "text": "エスト準州",
      "dy": "1.05em"
    }
  ],
  "ヌーヴェル＝アキテーヌ": [
    {
      "text": "ヌーヴェル＝",
      "dy": "0"
    },
    {
      "text": "アキテーヌ",
      "dy": "1.05em"
    }
  ],
  "ペイ・ド・ラ・ロワール": [
    {
      "text": "ペイ・ド・ラ・",
      "dy": "0"
    },
    {
      "text": "ロワール",
      "dy": "1.05em"
    }
  ],
  "プリンスエドワードアイランド": [
    {
      "text": "プリンスエドワ",
      "dy": "0"
    },
    {
      "text": "ードアイランド",
      "dy": "1.05em"
    }
  ],
  "プロヴァンス＝アルプ＝コート・ダジュール": [
    {
      "text": "プロヴァンス＝アルプ＝",
      "dy": "0"
    },
    {
      "text": "コート・ダジュール",
      "dy": "1.05em"
    }
  ],
  "ラインラント＝プファルツ": [
    {
      "text": "ラインラント＝",
      "dy": "0"
    },
    {
      "text": "プファルツ",
      "dy": "1.05em"
    }
  ],
  "サン・ルイス・ポトシ": [
    {
      "text": "サン・ルイス・",
      "dy": "0"
    },
    {
      "text": "ポトシ",
      "dy": "1.05em"
    }
  ],
  "ザクセン＝アンハルト": [
    {
      "text": "ザクセン＝",
      "dy": "0"
    },
    {
      "text": "アンハルト",
      "dy": "1.05em"
    }
  ],
  "シュレースヴィヒ＝ホルシュタイン": [
    {
      "text": "シュレースヴィヒ＝",
      "dy": "0"
    },
    {
      "text": "ホルシュタイン",
      "dy": "1.05em"
    }
  ],
  "トレンティーノ＝アルト・アディジェ": [
    {
      "text": "トレンティーノ＝",
      "dy": "0"
    },
    {
      "text": "アルト・アディジェ",
      "dy": "1.05em"
    }
  ],
  "ウェスト・ミッドランズ": [
    {
      "text": "ウェスト・",
      "dy": "0"
    },
    {
      "text": "ミッドランズ",
      "dy": "1.05em"
    }
  ],
  "ウェストバージニア": [
    {
      "text": "ウェスト",
      "dy": "0"
    },
    {
      "text": "バージニア",
      "dy": "1.05em"
    }
  ],
  "ヨークシャー・アンド・ザ・ハンバー": [
    {
      "text": "ヨークシャー・アンド・",
      "dy": "0"
    },
    {
      "text": "ザ・ハンバー",
      "dy": "1.05em"
    }
  ],
  "イル＝ド＝フランス": [
    {
      "text": "イル＝ド＝",
      "dy": "0"
    },
    {
      "text": "フランス",
      "dy": "1.05em"
    }
  ]
};  function fix(o){
    if (!o || typeof o !== 'object') return;
    if (typeof o.name === 'string' && M[o.name]) o.name = M[o.name];
  }
  function walkGeo(geo){
    if (!geo) return;
    Object.keys(geo).forEach(function(k){ fix(geo[k]); });
  }
  walkGeo(window.GEO);
  walkGeo(window.AU_GEO);
  walkGeo(window.FR_GEO);
  walkGeo(window.DE_GEO);
  walkGeo(window.UK_GEO);
  walkGeo(window.IT_GEO);
  walkGeo(window.ES_GEO);
  walkGeo(window.CA_GEO);
  walkGeo(window.MX_GEO);
  walkGeo(window.JP_GEO);
  walkGeo(window.KR_GEO);
  if (window.PPC_MAP && window.PPC_MAP.geo) walkGeo(window.PPC_MAP.geo);
  if (window.USA_RULES) walkGeo(window.USA_RULES);
  var plan = window.PPC_LABEL_PLAN;
  if (plan && Array.isArray(plan.tiers)){
    plan.tiers.forEach(function(tier){
      (tier.labels || []).forEach(function(lab){
        if (!lab || lab.typ !== 'region') return;
        if (M[lab.name]) lab.name = M[lab.name];
        if (WRAPS[lab.name]) lab.wrap = WRAPS[lab.name];
        else if (lab.wrap) lab.wrap = null;
      });
    });
  }
})();
