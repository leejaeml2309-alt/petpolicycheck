/* DE-only region/state display names. Loaded only on /de/ map pages.
   Mutates GEO / USA_RULES / PPC_LABEL_PLAN (including wrap lines) before the map paints.
   EN/ES/IT/FR pages never load this file. */
(function(){
  var M = {
  "Western Australia": "Westaustralien",
  "South Australia": "Südaustralien",
  "Tasmania": "Tasmanien",
  "Scotland": "Schottland",
  "Northern Ireland": "Nordirland",
  "East of England": "Ostengland",
  "North East": "Nordostengland",
  "North West": "Nordwestengland",
  "South East": "Südostengland",
  "South West": "Südwestengland",
  "Bavaria": "Bayern",
  "Lower Saxony": "Niedersachsen",
  "North Rhine-Westphalia": "Nordrhein-Westfalen",
  "Saxony": "Sachsen",
  "Saxony-Anhalt": "Sachsen-Anhalt",
  "Rhineland-Palatinate": "Rheinland-Pfalz",
  "Mecklenburg-Western Pomerania": "Mecklenburg-Vorpommern",
  "Thuringia": "Thüringen",
  "Hesse": "Hessen",
  "Lombardy": "Lombardei",
  "Tuscany": "Toskana",
  "Sicily": "Sizilien",
  "Sardinia": "Sardinien",
  "Piedmont": "Piemont",
  "Apulia": "Apulien",
  "Aosta Valley": "Aostatal",
  "Trentino-South Tyrol": "Trentino-Südtirol",
  "Friuli-Venezia Giulia": "Friaul-Julisch Venetien",
  "Lazio": "Latium",
  "Liguria": "Ligurien",
  "Marche": "Marken",
  "Calabria": "Kalabrien",
  "Campania": "Kampanien",
  "Veneto": "Venetien",
  "Umbria": "Umbrien",
  "Abruzzo": "Abruzzen",
  "Andalusia": "Andalusien",
  "Catalonia": "Katalonien",
  "Asturias": "Asturien",
  "Balearic Islands": "Balearen",
  "Basque Country": "Baskenland",
  "Canary Islands": "Kanarische Inseln",
  "Cantabria": "Kantabrien",
  "Castile and León": "Kastilien und León",
  "Castilla-La Mancha": "Kastilien-La Mancha",
  "Community of Madrid": "Autonome Gemeinschaft Madrid",
  "Galicia": "Galicien",
  "Region of Murcia": "Region Murcia",
  "Valencian Community": "Valencianische Gemeinschaft",
  "Aragon": "Aragonien",
  "Navarre": "Navarra",
  "California": "Kalifornien",
  "Newfoundland and Labrador": "Neufundland und Labrador",
  "Northwest Territories": "Nordwest-Territorien",
  "Quebec": "Québec",
  "Ciudad de México": "Mexiko-Stadt",
  "Corse": "Korsika",
  "North Chungcheong": "Nord-Chungcheong",
  "South Chungcheong": "Süd-Chungcheong",
  "North Gyeongsang": "Nord-Gyeongsang",
  "South Gyeongsang": "Süd-Gyeongsang",
  "North Jeolla": "Nord-Jeolla",
  "South Jeolla": "Süd-Jeolla"
};
  var WRAPS = {
  "Nordrhein-Westfalen": [
    {
      "text": "Nordrhein-",
      "dy": "0"
    },
    {
      "text": "Westfalen",
      "dy": "1.05em"
    }
  ],
  "Mecklenburg-Vorpommern": [
    {
      "text": "Mecklenburg-",
      "dy": "0"
    },
    {
      "text": "Vorpommern",
      "dy": "1.05em"
    }
  ],
  "Sachsen-Anhalt": [
    {
      "text": "Sachsen-",
      "dy": "0"
    },
    {
      "text": "Anhalt",
      "dy": "1.05em"
    }
  ],
  "Rheinland-Pfalz": [
    {
      "text": "Rheinland-",
      "dy": "0"
    },
    {
      "text": "Pfalz",
      "dy": "1.05em"
    }
  ],
  "Trentino-Südtirol": [
    {
      "text": "Trentino-",
      "dy": "0"
    },
    {
      "text": "Südtirol",
      "dy": "1.05em"
    }
  ],
  "Friaul-Julisch Venetien": [
    {
      "text": "Friaul-",
      "dy": "0"
    },
    {
      "text": "Julisch Venetien",
      "dy": "1.05em"
    }
  ],
  "Emilia-Romagna": [
    {
      "text": "Emilia-",
      "dy": "0"
    },
    {
      "text": "Romagna",
      "dy": "1.05em"
    }
  ],
  "Kanarische Inseln": [
    {
      "text": "Kanarische",
      "dy": "0"
    },
    {
      "text": "Inseln",
      "dy": "1.05em"
    }
  ],
  "Kastilien und León": [
    {
      "text": "Kastilien",
      "dy": "0"
    },
    {
      "text": "und León",
      "dy": "1.05em"
    }
  ],
  "Kastilien-La Mancha": [
    {
      "text": "Kastilien-",
      "dy": "0"
    },
    {
      "text": "La Mancha",
      "dy": "1.05em"
    }
  ],
  "Autonome Gemeinschaft Madrid": [
    {
      "text": "Autonome",
      "dy": "0"
    },
    {
      "text": "Gemeinschaft",
      "dy": "1.05em"
    },
    {
      "text": "Madrid",
      "dy": "1.05em"
    }
  ],
  "Valencianische Gemeinschaft": [
    {
      "text": "Valencianische",
      "dy": "0"
    },
    {
      "text": "Gemeinschaft",
      "dy": "1.05em"
    }
  ],
  "Region Murcia": [
    {
      "text": "Region",
      "dy": "0"
    },
    {
      "text": "Murcia",
      "dy": "1.05em"
    }
  ],
  "Neufundland und Labrador": [
    {
      "text": "Neufundland",
      "dy": "0"
    },
    {
      "text": "und Labrador",
      "dy": "1.05em"
    }
  ],
  "Nordwest-Territorien": [
    {
      "text": "Nordwest-",
      "dy": "0"
    },
    {
      "text": "Territorien",
      "dy": "1.05em"
    }
  ],
  "Australian Capital Territory": [
    {
      "text": "Australian",
      "dy": "0"
    },
    {
      "text": "Capital",
      "dy": "1.05em"
    },
    {
      "text": "Territory",
      "dy": "1.05em"
    }
  ],
  "New South Wales": [
    {
      "text": "New South",
      "dy": "0"
    },
    {
      "text": "Wales",
      "dy": "1.05em"
    }
  ],
  "Northern Territory": [
    {
      "text": "Northern",
      "dy": "0"
    },
    {
      "text": "Territory",
      "dy": "1.05em"
    }
  ],
  "Nordostengland": [
    {
      "text": "Nordost-",
      "dy": "0"
    },
    {
      "text": "england",
      "dy": "1.05em"
    }
  ],
  "Nordwestengland": [
    {
      "text": "Nordwest-",
      "dy": "0"
    },
    {
      "text": "england",
      "dy": "1.05em"
    }
  ],
  "Südostengland": [
    {
      "text": "Südost-",
      "dy": "0"
    },
    {
      "text": "england",
      "dy": "1.05em"
    }
  ],
  "Südwestengland": [
    {
      "text": "Südwest-",
      "dy": "0"
    },
    {
      "text": "england",
      "dy": "1.05em"
    }
  ],
  "Yorkshire and the Humber": [
    {
      "text": "Yorkshire and",
      "dy": "0"
    },
    {
      "text": "the Humber",
      "dy": "1.05em"
    }
  ],
  "East Midlands": [
    {
      "text": "East",
      "dy": "0"
    },
    {
      "text": "Midlands",
      "dy": "1.05em"
    }
  ],
  "West Midlands": [
    {
      "text": "West",
      "dy": "0"
    },
    {
      "text": "Midlands",
      "dy": "1.05em"
    }
  ],
  "Greater London": [
    {
      "text": "Greater",
      "dy": "0"
    },
    {
      "text": "London",
      "dy": "1.05em"
    }
  ],
  "Nord-Chungcheong": [
    {
      "text": "Nord-",
      "dy": "0"
    },
    {
      "text": "Chungcheong",
      "dy": "1.05em"
    }
  ],
  "Süd-Chungcheong": [
    {
      "text": "Süd-",
      "dy": "0"
    },
    {
      "text": "Chungcheong",
      "dy": "1.05em"
    }
  ],
  "Nord-Gyeongsang": [
    {
      "text": "Nord-",
      "dy": "0"
    },
    {
      "text": "Gyeongsang",
      "dy": "1.05em"
    }
  ],
  "Süd-Gyeongsang": [
    {
      "text": "Süd-",
      "dy": "0"
    },
    {
      "text": "Gyeongsang",
      "dy": "1.05em"
    }
  ],
  "Nord-Jeolla": [
    {
      "text": "Nord-",
      "dy": "0"
    },
    {
      "text": "Jeolla",
      "dy": "1.05em"
    }
  ],
  "Süd-Jeolla": [
    {
      "text": "Süd-",
      "dy": "0"
    },
    {
      "text": "Jeolla",
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
        if (M[lab.name]) {
          lab.name = M[lab.name];
          if (WRAPS[lab.name]) lab.wrap = WRAPS[lab.name];
          else if (lab.wrap) lab.wrap = null;
        } else if (WRAPS[lab.name]) lab.wrap = WRAPS[lab.name];
      });
    });
  }
})();
