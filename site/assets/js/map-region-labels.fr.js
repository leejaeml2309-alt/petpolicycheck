/* FR-only region/state display names. Loaded only on /fr/ map pages.
   Mutates GEO / USA_RULES / PPC_LABEL_PLAN (including wrap lines) before the map paints.
   EN/ES/IT pages never load this file. */
(function(){
  var M = {
  "Western Australia": "Australie-Occidentale",
  "New South Wales": "Nouvelle-Galles du Sud",
  "Northern Territory": "Territoire du Nord",
  "South Australia": "Australie-Méridionale",
  "Tasmania": "Tasmanie",
  "Australian Capital Territory": "Territoire de la capitale australienne",
  "Scotland": "Écosse",
  "Wales": "Pays de Galles",
  "Northern Ireland": "Irlande du Nord",
  "Greater London": "Grand Londres",
  "East Midlands": "Midlands de l’Est",
  "West Midlands": "Midlands de l’Ouest",
  "East of England": "Est de l’Angleterre",
  "North East": "Nord-Est",
  "North West": "Nord-Ouest",
  "South East": "Sud-Est",
  "South West": "Sud-Ouest",
  "Yorkshire and the Humber": "Yorkshire-et-Humber",
  "Bavaria": "Bavière",
  "Lower Saxony": "Basse-Saxe",
  "North Rhine-Westphalia": "Rhénanie-du-Nord-Westphalie",
  "Saxony": "Saxe",
  "Saxony-Anhalt": "Saxe-Anhalt",
  "Rhineland-Palatinate": "Rhénanie-Palatinat",
  "Saarland": "Sarre",
  "Baden-Württemberg": "Bade-Wurtemberg",
  "Brandenburg": "Brandebourg",
  "Mecklenburg-Western Pomerania": "Mecklembourg-Poméranie-Occidentale",
  "Bremen": "Brême",
  "Hamburg": "Hambourg",
  "Thuringia": "Thuringe",
  "Lombardy": "Lombardie",
  "Tuscany": "Toscane",
  "Sicily": "Sicile",
  "Sardinia": "Sardaigne",
  "Piedmont": "Piémont",
  "Apulia": "Pouilles",
  "Aosta Valley": "Val d’Aoste",
  "Trentino-South Tyrol": "Trentin-Haut-Adige",
  "Emilia-Romagna": "Émilie-Romagne",
  "Friuli-Venezia Giulia": "Frioul-Vénétie julienne",
  "Lazio": "Latium",
  "Liguria": "Ligurie",
  "Marche": "Marches",
  "Calabria": "Calabre",
  "Campania": "Campanie",
  "Veneto": "Vénétie",
  "Umbria": "Ombrie",
  "Basilicata": "Basilicate",
  "Abruzzo": "Abruzzes",
  "Andalusia": "Andalousie",
  "Catalonia": "Catalogne",
  "Asturias": "Asturies",
  "Balearic Islands": "Îles Baléares",
  "Basque Country": "Pays basque",
  "Canary Islands": "Îles Canaries",
  "Cantabria": "Cantabrie",
  "Castile and León": "Castille-et-León",
  "Castilla-La Mancha": "Castille-La Manche",
  "Community of Madrid": "Communauté de Madrid",
  "Extremadura": "Estrémadure",
  "Galicia": "Galice",
  "Region of Murcia": "Région de Murcie",
  "Valencian Community": "Communauté valencienne",
  "California": "Californie",
  "Florida": "Floride",
  "North Carolina": "Caroline du Nord",
  "South Carolina": "Caroline du Sud",
  "New Mexico": "Nouveau-Mexique",
  "Pennsylvania": "Pennsylvanie",
  "Georgia": "Géorgie",
  "Virginia": "Virginie",
  "West Virginia": "Virginie-Occidentale",
  "Louisiana": "Louisiane",
  "Hawaii": "Hawaï",
  "South Dakota": "Dakota du Sud",
  "North Dakota": "Dakota du Nord",
  "District of Columbia": "District de Columbia",
  "British Columbia": "Colombie-Britannique",
  "Quebec": "Québec",
  "Newfoundland and Labrador": "Terre-Neuve-et-Labrador",
  "Nova Scotia": "Nouvelle-Écosse",
  "New Brunswick": "Nouveau-Brunswick",
  "Prince Edward Island": "Île-du-Prince-Édouard",
  "Northwest Territories": "Territoires du Nord-Ouest",
  "Baja California": "Basse-Californie",
  "Baja California Sur": "Basse-Californie du Sud",
  "Ciudad de México": "Ville de Mexico",
  "North Chungcheong": "Chungcheong du Nord",
  "South Chungcheong": "Chungcheong du Sud",
  "North Gyeongsang": "Gyeongsang du Nord",
  "South Gyeongsang": "Gyeongsang du Sud",
  "North Jeolla": "Jeolla du Nord",
  "South Jeolla": "Jeolla du Sud"
};
  var WRAPS = {
  "Australie-Occidentale": [
    {
      "text": "Australie-",
      "dy": "0"
    },
    {
      "text": "Occidentale",
      "dy": "1.05em"
    }
  ],
  "Nouvelle-Galles du Sud": [
    {
      "text": "Nouvelle-",
      "dy": "0"
    },
    {
      "text": "Galles du Sud",
      "dy": "1.05em"
    }
  ],
  "Territoire du Nord": [
    {
      "text": "Territoire",
      "dy": "0"
    },
    {
      "text": "du Nord",
      "dy": "1.05em"
    }
  ],
  "Australie-Méridionale": [
    {
      "text": "Australie-",
      "dy": "0"
    },
    {
      "text": "Méridionale",
      "dy": "1.05em"
    }
  ],
  "Territoire de la capitale australienne": [
    {
      "text": "Territoire de",
      "dy": "0"
    },
    {
      "text": "la capitale",
      "dy": "1.05em"
    },
    {
      "text": "australienne",
      "dy": "1.05em"
    }
  ],
  "Val d’Aoste": [
    {
      "text": "Val",
      "dy": "0"
    },
    {
      "text": "d’Aoste",
      "dy": "1.05em"
    }
  ],
  "Émilie-Romagne": [
    {
      "text": "Émilie-",
      "dy": "0"
    },
    {
      "text": "Romagne",
      "dy": "1.05em"
    }
  ],
  "Frioul-Vénétie julienne": [
    {
      "text": "Frioul-",
      "dy": "0"
    },
    {
      "text": "Vénétie julienne",
      "dy": "1.05em"
    }
  ],
  "Trentin-Haut-Adige": [
    {
      "text": "Trentin-",
      "dy": "0"
    },
    {
      "text": "Haut-Adige",
      "dy": "1.05em"
    }
  ],
  "Chungcheong du Nord": [
    {
      "text": "Chungcheong",
      "dy": "0"
    },
    {
      "text": "du Nord",
      "dy": "1.05em"
    }
  ],
  "Chungcheong du Sud": [
    {
      "text": "Chungcheong",
      "dy": "0"
    },
    {
      "text": "du Sud",
      "dy": "1.05em"
    }
  ],
  "Gyeongsang du Nord": [
    {
      "text": "Gyeongsang",
      "dy": "0"
    },
    {
      "text": "du Nord",
      "dy": "1.05em"
    }
  ],
  "Gyeongsang du Sud": [
    {
      "text": "Gyeongsang",
      "dy": "0"
    },
    {
      "text": "du Sud",
      "dy": "1.05em"
    }
  ],
  "Jeolla du Nord": [
    {
      "text": "Jeolla",
      "dy": "0"
    },
    {
      "text": "du Nord",
      "dy": "1.05em"
    }
  ],
  "Jeolla du Sud": [
    {
      "text": "Jeolla",
      "dy": "0"
    },
    {
      "text": "du Sud",
      "dy": "1.05em"
    }
  ],
  "Îles Baléares": [
    {
      "text": "Îles",
      "dy": "0"
    },
    {
      "text": "Baléares",
      "dy": "1.05em"
    }
  ],
  "Pays basque": [
    {
      "text": "Pays",
      "dy": "0"
    },
    {
      "text": "basque",
      "dy": "1.05em"
    }
  ],
  "Îles Canaries": [
    {
      "text": "Îles",
      "dy": "0"
    },
    {
      "text": "Canaries",
      "dy": "1.05em"
    }
  ],
  "Castille-et-León": [
    {
      "text": "Castille-",
      "dy": "0"
    },
    {
      "text": "et-León",
      "dy": "1.05em"
    }
  ],
  "Castille-La Manche": [
    {
      "text": "Castille-",
      "dy": "0"
    },
    {
      "text": "La Manche",
      "dy": "1.05em"
    }
  ],
  "Communauté de Madrid": [
    {
      "text": "Communauté",
      "dy": "0"
    },
    {
      "text": "de Madrid",
      "dy": "1.05em"
    }
  ],
  "Région de Murcie": [
    {
      "text": "Région",
      "dy": "0"
    },
    {
      "text": "de Murcie",
      "dy": "1.05em"
    }
  ],
  "Communauté valencienne": [
    {
      "text": "Communauté",
      "dy": "0"
    },
    {
      "text": "valencienne",
      "dy": "1.05em"
    }
  ],
  "Midlands de l’Est": [
    {
      "text": "Midlands",
      "dy": "0"
    },
    {
      "text": "de l’Est",
      "dy": "1.05em"
    }
  ],
  "Midlands de l’Ouest": [
    {
      "text": "Midlands",
      "dy": "0"
    },
    {
      "text": "de l’Ouest",
      "dy": "1.05em"
    }
  ],
  "Est de l’Angleterre": [
    {
      "text": "Est de",
      "dy": "0"
    },
    {
      "text": "l’Angleterre",
      "dy": "1.05em"
    }
  ],
  "Irlande du Nord": [
    {
      "text": "Irlande",
      "dy": "0"
    },
    {
      "text": "du Nord",
      "dy": "1.05em"
    }
  ],
  "Pays de Galles": [
    {
      "text": "Pays de",
      "dy": "0"
    },
    {
      "text": "Galles",
      "dy": "1.05em"
    }
  ],
  "Yorkshire-et-Humber": [
    {
      "text": "Yorkshire-",
      "dy": "0"
    },
    {
      "text": "et-Humber",
      "dy": "1.05em"
    }
  ],
  "Grand Londres": [
    {
      "text": "Grand",
      "dy": "0"
    },
    {
      "text": "Londres",
      "dy": "1.05em"
    }
  ],
  "Nord-Est": [
    {
      "text": "Nord-",
      "dy": "0"
    },
    {
      "text": "Est",
      "dy": "1.05em"
    }
  ],
  "Nord-Ouest": [
    {
      "text": "Nord-",
      "dy": "0"
    },
    {
      "text": "Ouest",
      "dy": "1.05em"
    }
  ],
  "Sud-Est": [
    {
      "text": "Sud-",
      "dy": "0"
    },
    {
      "text": "Est",
      "dy": "1.05em"
    }
  ],
  "Sud-Ouest": [
    {
      "text": "Sud-",
      "dy": "0"
    },
    {
      "text": "Ouest",
      "dy": "1.05em"
    }
  ]
};
  function fix(o){
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
