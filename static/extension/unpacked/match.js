/* Domain/URL → PetPolicyCheck record. Shared by popup.js and content.js. No network, no tracking. */
var PPC_MATCH=(function(){
  function hit(host,path,d){var p=d.split('/'),h=p[0],sub=p.slice(1).join('/');
    var ok=host===h||host.slice(-(h.length+1))==='.'+h; if(!ok) return 0;
    if(sub) return path.toLowerCase().indexOf('/'+sub)===0?2:0; return 1;}
  function best(list,host,path){var r=null,s=0;(list||[]).forEach(function(x){x.d.forEach(function(d){var k=hit(host,path,d);if(k>s){s=k;r=x}})});return r}
  function shortFee(f){if(!f) return null;var m=f.match(/(CA\/US\s?\$[\d–-]+|EUR\s?[\d–-]+|\$\d+)/);return m?m[1].replace(/CA\/US\s?\$?/,'CA$'):null}
  function shortDims(d){if(!d) return null;var m=d.match(/^([\d.]+) × ([\d.]+) × ([\d.]+) (in|cm)/);return m?m[1]+'×'+m[2]+'×'+m[3]+(m[4]==='in'?'″':' cm'):null}
  function match(url){var u;try{u=new URL(url)}catch(e){return null}
    var host=u.hostname.replace(/^www\./,''),path=u.pathname;
    var a=best(PPC_RULES.airlines,host,path); if(a) return {type:'airline',theme:'flight',rec:a,pill:(a.cabin?'Pets OK':'No cabin pets')+(a.cabin&&shortFee(a.fee)?' · '+shortFee(a.fee):'')+(a.cabin&&shortDims(a.dims)?' · '+shortDims(a.dims):'')};
    var h=best(PPC_RULES.hotels,host,path); if(h) return {type:'hotel',theme:'hotel',rec:h,pill:'Pets OK · '+(h.fee?(h.fee.length>26?h.fee.split(/[;,(]/)[0]:h.fee):'rules vary')};
    var p=best(PPC_RULES.portals,host,path); if(p) return {type:'portal',theme:'hotel',rec:p,pill:'Check pet rules per hotel'};
    return null}
  return {match:match,shortFee:shortFee,shortDims:shortDims};
})();
