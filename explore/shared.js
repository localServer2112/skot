(function(){
  var reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
  /* reveal on scroll */
  var rv=document.querySelectorAll('.rv');
  if('IntersectionObserver' in window&&!reduce){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.12,rootMargin:'0px 0px -6% 0px'});
    rv.forEach(function(n){io.observe(n)});
  }else rv.forEach(function(n){n.classList.add('in')});
  /* counters: final text is in the HTML; animate from zero when seen */
  var cs=document.querySelectorAll('[data-count]');
  function run(el){
    var to=parseFloat(el.dataset.count),dec=+el.dataset.dec||0,unit=el.dataset.unit||'',plus=el.dataset.plus?'<i>+</i>':'';
    var t0=performance.now(),dur=1700;
    (function f(t){var p=Math.min(1,(t-t0)/dur),e=1-Math.pow(1-p,3);
      el.innerHTML=(to*e).toLocaleString('en',{minimumFractionDigits:dec,maximumFractionDigits:dec})+unit+(p>.98?plus:'');
      if(p<1)requestAnimationFrame(f)})(t0);
  }
  if('IntersectionObserver' in window&&!reduce){
    var co=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){run(e.target);co.unobserve(e.target)}})},{threshold:.6});
    cs.forEach(function(n){co.observe(n)});
  }
  /* scroll-lit sentence */
  document.querySelectorAll('.wf').forEach(function(p){
    var words=p.textContent.trim().split(/\s+/);
    p.innerHTML=words.map(function(w){return '<span>'+w+'</span>'}).join(' ');
    var sp=[].slice.call(p.children);
    function up(){var r=p.getBoundingClientRect(),h=innerHeight,
      prog=Math.min(1,Math.max(0,(h*.82-r.top)/(r.height+h*.34)));
      var n=prog*sp.length;sp.forEach(function(s,i){s.style.color=i<n?'var(--lit)':'var(--dim)'})}
    if(reduce){sp.forEach(function(s){s.style.color='var(--lit)'})}else{addEventListener('scroll',up,{passive:true});addEventListener('resize',up);up()}
  });
  /* list with image preview */
  document.querySelectorAll('[data-x]').forEach(function(box){
    var rows=box.querySelectorAll('[data-i]'),pics=box.querySelectorAll('[data-p]');
    function set(i){rows.forEach(function(r){r.classList.toggle('on',r.dataset.i==i)});pics.forEach(function(p){p.classList.toggle('on',p.dataset.p==i)})}
    rows.forEach(function(r){['mouseenter','focusin'].forEach(function(ev){r.addEventListener(ev,function(){set(r.dataset.i)})})});
    set(0);
  });
})();
