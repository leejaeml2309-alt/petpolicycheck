/*! Plan faster + Community preview switch: ?opt=A|B|C (default A). */
(function(){
  try{
    var o=new URLSearchParams(location.search).get('opt');
    if(o && /^[abc]$/i.test(o)) document.documentElement.setAttribute('data-hub', o.toUpperCase());
  }catch(e){}
})();
