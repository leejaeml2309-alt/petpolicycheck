/* Adoptions directory: partners and shelter cards.
   Data lives in /data/adoptions-directory.json (site/ and static/ must stay in sync).
   To add a consented partner, append one object to "partners":
     { "name": "Name", "logo": "../assets/img/adoptions/partners/file.png", "url": "https://example.org", "alt": "Name" }
   To add a consented shelter, append one object to "shelters":
     { "name": "Name", "logo": "../assets/img/adoptions/shelters/file.png", "city": "City", "state": "ST", "url": "https://example.org" }
   Never add a name or logo without that organisation's consent.
   An empty array keeps the designed empty state. */
(function(){
  var root=document.getElementById("shelters-stories");
  if(!root) return;
  var src=root.getAttribute("data-src")||"../data/adoptions-directory.json";

  function el(tag,cls){
    var n=document.createElement(tag);
    if(cls) n.className=cls;
    return n;
  }
  function txt(s){ return document.createTextNode(s==null?"":String(s)); }
  function initials(name){
    var parts=String(name||"").trim().split(/\s+/).filter(Boolean);
    if(!parts.length) return "";
    if(parts.length===1) return parts[0].slice(0,2).toUpperCase();
    return (parts[0].charAt(0)+parts[parts.length-1].charAt(0)).toUpperCase();
  }
  function placeLine(item){
    var city=(item.city||"").trim();
    var state=(item.state||"").trim();
    if(city && state) return city+", "+state;
    return city||state||"";
  }

  function renderPartners(list){
    var grid=document.getElementById("adopt-partners");
    var empty=document.getElementById("adopt-partners-empty");
    if(!grid||!empty) return;
    grid.innerHTML="";
    var items=Array.isArray(list)?list.filter(function(p){ return p&&String(p.name||"").trim(); }):[];
    if(!items.length){
      grid.hidden=true;
      empty.hidden=false;
      return;
    }
    empty.hidden=true;
    grid.hidden=false;
    items.forEach(function(p){
      var name=String(p.name).trim();
      var node=p.url?el("a","adopt-partner"):el("div","adopt-partner");
      if(p.url){
        node.href=p.url;
        node.target="_blank";
        node.rel="noopener noreferrer";
      }
      var mark=el("span","adopt-partner__mark");
      if(p.logo){
        var img=document.createElement("img");
        img.src=p.logo;
        img.alt=p.alt||name;
        img.loading="lazy";
        img.decoding="async";
        mark.appendChild(img);
      } else {
        var fb=el("span","adopt-partner__initials");
        fb.setAttribute("aria-hidden","true");
        fb.appendChild(txt(initials(name)));
        mark.appendChild(fb);
      }
      node.appendChild(mark);
      var cap=el("span","adopt-partner__name");
      cap.appendChild(txt(name));
      node.appendChild(cap);
      grid.appendChild(node);
    });
  }

  function renderShelters(list){
    var grid=document.getElementById("adopt-shelters");
    var empty=document.getElementById("adopt-shelters-empty");
    if(!grid||!empty) return;
    grid.innerHTML="";
    var items=Array.isArray(list)?list.filter(function(s){ return s&&String(s.name||"").trim(); }):[];
    if(!items.length){
      grid.hidden=true;
      empty.hidden=false;
      return;
    }
    empty.hidden=true;
    grid.hidden=false;
    items.forEach(function(s){
      var name=String(s.name).trim();
      var card=el("article","shelter-card");
      var logo=el("div","shelter-card__logo");
      if(s.logo){
        var img=document.createElement("img");
        img.src=s.logo;
        img.alt="";
        img.loading="lazy";
        img.decoding="async";
        logo.appendChild(img);
      } else {
        var fb=el("span","shelter-card__initials");
        fb.setAttribute("aria-hidden","true");
        fb.appendChild(txt(initials(name)));
        logo.appendChild(fb);
      }
      card.appendChild(logo);
      var h=el("h4","shelter-card__name");
      h.appendChild(txt(name));
      card.appendChild(h);
      var place=placeLine(s);
      if(place){
        var loc=el("p","shelter-card__place");
        loc.appendChild(txt(place));
        card.appendChild(loc);
      }
      if(s.url){
        var a=el("a","ppc-btn ppc-btn--pri shelter-card__btn");
        a.href=s.url;
        a.target="_blank";
        a.rel="noopener noreferrer";
        a.appendChild(txt("Official site"));
        card.appendChild(a);
      }
      grid.appendChild(card);
    });
  }

  function emptyAll(){
    renderPartners([]);
    renderShelters([]);
  }

  fetch(src,{credentials:"same-origin"})
    .then(function(r){ if(!r.ok) throw new Error("directory"); return r.json(); })
    .then(function(data){
      renderPartners(data&&data.partners);
      renderShelters(data&&data.shelters);
    })
    .catch(emptyAll);
})();
