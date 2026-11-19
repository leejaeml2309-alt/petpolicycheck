/* Adoptions 6-step guide: progressive enhancement.
   Without JS, every step stays visible and stacked. */
(function(){
  var root=document.querySelector("[data-adopt-guide]");
  if(!root) return;
  var steps=[].slice.call(root.querySelectorAll(".adopt-step"));
  if(!steps.length) return;
  var n=steps.length;
  var bar=root.querySelector("[data-progress-bar]");
  var label=root.querySelector("[data-progress-label]");
  var prev=root.querySelector("[data-prev]");
  var next=root.querySelector("[data-next]");
  var prog=root.querySelector(".adopt-progress");
  var nav=root.querySelector(".adopt-guide__nav");
  var i=0;

  function stepFromHash(){
    var m=(location.hash||"").match(/^#step-(\d+)$/);
    if(!m) return 0;
    var v=parseInt(m[1],10);
    return (v>=1&&v<=n)?v-1:0;
  }
  function show(idx, moveFocus, pushHash){
    i=Math.max(0,Math.min(n-1,idx));
    steps.forEach(function(s,k){
      var on=k===i;
      s.classList.toggle("is-current",on);
      if(on) s.setAttribute("aria-current","step");
      else s.removeAttribute("aria-current");
    });
    if(bar){
      bar.style.width=((i+1)/n*100)+"%";
      bar.parentElement.setAttribute("aria-valuenow", String(i+1));
    }
    if(label) label.textContent="Step "+(i+1)+" of "+n;
    if(prev) prev.disabled=i===0;
    if(next) next.disabled=i===n-1;
    if(pushHash){
      try{ history.replaceState(null,"",location.pathname+location.search+"#step-"+(i+1)); }catch(e){}
    }
    if(moveFocus){
      var h=steps[i].querySelector("h2");
      if(h){ if(!h.hasAttribute("tabindex")) h.setAttribute("tabindex","-1"); h.focus({preventScroll:false}); }
    }
  }

  root.classList.add("is-stepper");
  if(prog) prog.hidden=false;
  if(nav) nav.hidden=false;
  if(prev) prev.addEventListener("click",function(){ if(i>0) show(i-1,true,true); });
  if(next) next.addEventListener("click",function(){ if(i<n-1) show(i+1,true,true); });
  window.addEventListener("hashchange",function(){ show(stepFromHash(),false,false); });
  show(stepFromHash(),false,false);
})();
