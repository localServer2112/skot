/* SKOT Communications — interaction layer */
(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var one = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var all = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* Mega menu */
  var items = all('.navitem');
  var closeAll = function (except) {
    items.forEach(function (it) {
      if (it === except) return;
      it.dataset.open = 'false';
      var b = one('button', it);
      b.setAttribute('aria-expanded', 'false');
      var m = document.getElementById(b.getAttribute('aria-controls'));
      if (m) m.dataset.open = 'false';
    });
  };
  items.forEach(function (it) {
    var btn = one('button', it);
    var mega = document.getElementById(btn.getAttribute('aria-controls'));
    if (!mega) return;
    var open = function (state) {
      closeAll(it);
      it.dataset.open = String(state);
      btn.setAttribute('aria-expanded', String(state));
      mega.dataset.open = String(state);
    };
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      open(btn.getAttribute('aria-expanded') !== 'true');
    });
    it.addEventListener('mouseenter', function () { open(true); });
    var leave = function (e) {
      var to = e.relatedTarget;
      if (to && (it.contains(to) || mega.contains(to))) return;
      open(false);
    };
    it.addEventListener('mouseleave', leave);
    mega.addEventListener('mouseleave', leave);
  });
  document.addEventListener('click', function () { closeAll(null); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeAll(null); });

  /* Mobile navigation */
  var toggle = one('#navToggle'), panel = one('#navMobile');
  if (toggle && panel) {
    var setMenu = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      panel.hidden = !open;
    };
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });
    panel.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { setMenu(false); toggle.focus(); }
    });
    window.addEventListener('resize', function () { if (window.innerWidth > 900) setMenu(false); });
  }

  /* Filterable + searchable card grids (case studies, insights) */
  var filterGrid = function (cfg) {
    var grid = one(cfg.grid);
    if (!grid) return;
    var cards = all(cfg.item, grid);
    var filters = all(cfg.filters + ' button');
    var countEl = one(cfg.count);
    var emptyEl = one(cfg.empty);
    var search = one(cfg.search);
    var active = 'All';

    var apply = function () {
      var q = ((search && search.value) || '').trim().toLowerCase();
      var shown = 0;
      cards.forEach(function (card) {
        var okFilter = active === 'All' || card.dataset[cfg.key] === active;
        var okSearch = !q || (card.dataset.search || '').indexOf(q) !== -1;
        var show = okFilter && okSearch;
        card.hidden = !show;
        if (show) shown++;
      });
      if (countEl) countEl.textContent = shown;
      if (emptyEl) emptyEl.hidden = shown !== 0;
    };

    filters.forEach(function (b) {
      b.addEventListener('click', function () {
        active = b.dataset.filter;
        filters.forEach(function (o) { o.setAttribute('aria-pressed', String(o === b)); });
        apply();
      });
    });
    if (search) search.addEventListener('input', apply);
    apply();
  };

  filterGrid({ grid: '#caseGrid', item: '.card', key: 'discipline', filters: '#caseFilters',
               count: '#caseCount', empty: '#caseEmpty', search: '#caseSearch' });
  filterGrid({ grid: '#postGrid', item: '.post', key: 'category', filters: '#postFilters',
               count: '#postCount', empty: '#postEmpty', search: '#postSearch' });

  /* Expertise tabs — advances on its own, click or arrow-key to jump */
  all('[data-xp]').forEach(function (xp) {
    var tabs = all('.xp-tab', xp);
    if (tabs.length < 2) return;
    var panels = tabs.map(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });
    var current = 0;
    var hovered = false, onscreen = true;

    var sync = function () { xp.dataset.paused = String(hovered || !onscreen); };
    var select = function (n) {
      current = (n + tabs.length) % tabs.length;
      tabs.forEach(function (t, k) {
        var on = k === current;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        if (panels[k]) panels[k].hidden = !on;
      });
    };

    tabs.forEach(function (t, k) { t.addEventListener('click', function () { select(k); }); });

    one('.xp-tabs', xp).addEventListener('keydown', function (e) {
      var step = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!step) return;
      e.preventDefault();
      select(current + step);
      tabs[current].focus();
    });

    /* the scarlet bar finishing its run is what moves us on */
    if (!reduced) {
      xp.addEventListener('animationend', function (e) {
        if (e.animationName === 'xpFill') select(current + 1);
      });
      xp.addEventListener('mouseenter', function () { hovered = true; sync(); });
      xp.addEventListener('mouseleave', function () { hovered = false; sync(); });
      xp.addEventListener('focusin', function () { hovered = true; sync(); });
      xp.addEventListener('focusout', function () { hovered = false; sync(); });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) {
          onscreen = entries[0].isIntersecting;
          sync();
        }, { threshold: 0.25 }).observe(xp);
      }
    }

    select(0);
    sync();
  });

  /* Results and stat strips: count each figure up whenever its section comes into focus, and
     again every time it comes back. It resets once fully out of view, so each return starts from
     zero. The final value is already in the markup, so no-JS and reduced-motion readers just see it. */
  var counters = all('[data-count]');
  if (counters.length && !reduced && 'IntersectionObserver' in window) {
    var paint = function (el, n) {
      var dec = +el.dataset.dec;
      var txt = n.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec, useGrouping: false });
      el.innerHTML = txt + el.dataset.unit + (el.dataset.plus ? '<i>+</i>' : '');
    };
    var stop = function (el) { if (el._raf) { cancelAnimationFrame(el._raf); el._raf = 0; } };
    var run = function (el) {
      stop(el);
      var to = parseFloat(el.dataset.count), t0 = null, dur = 1500;
      var tick = function (t) {
        if (t0 === null) t0 = t;
        var k = Math.min(1, (t - t0) / dur);
        paint(el, to * (1 - Math.pow(1 - k, 3)));
        if (k < 1) el._raf = requestAnimationFrame(tick); else { el._raf = 0; paint(el, to); }
      };
      paint(el, 0);
      el._raf = requestAnimationFrame(tick);
    };
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var el = en.target;
        if (en.intersectionRatio >= 0.6) {
          if (!el._in) { el._in = true; run(el); }
        } else if (en.intersectionRatio === 0) {
          el._in = false; stop(el); paint(el, 0);
        }
      });
    }, { threshold: [0, 0.6] });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* Motion. Entrance animation is added here, never in the markup, so a page with no JS or
     with reduced motion simply shows its content. Two things animate:
       .reveal  - fades and rises; siblings that arrive together are staggered
       .split   - headlines, whose words rise out of a mask
     Visual timing lives in the CSS; this only decides what animates and in what order. */
  var REVEAL = [
    '.vhero-cta > *', '.vhero-rail',
    '.phero .eyebrow', '.phero .lede', '.phero-side .btn',
    '.sec-head .label', '.sec-split .label', '.sec-head > .alink', '.sec-head p.lede',
    '.sec-split .body-copy', '.sec-split .alink',
    '.xp-tab', '.res-lead', '.res-row', '.mw-card', '.trust-row > a',
    '.card-grid > .card', '.post-grid > .post', '.ins-card',
    '.stats > div', '.cells > *', '.caps li', '.case-sections > *',
    '.pg-aside', '.pg-main .btn', '.pg-strip img', '.footer-col'
  ];

  /* Wrap each word of a heading in a clipping mask. Inline elements (the scarlet "...") ride
     with the word before them so punctuation never wraps onto a line of its own. */
  var splitWords = function (el) {
    var n = 0, last = null;
    var unit = function (child) {
      var w = document.createElement('span'), i = document.createElement('i');
      w.className = 'w';
      i.style.setProperty('--i', n++);
      i.appendChild(child);
      w.appendChild(i);
      last = i;
      return w;
    };
    Array.prototype.slice.call(el.childNodes).forEach(function (node) {
      if (node.nodeType === 3) {
        var frag = document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach(function (part) {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); last = null; }
          else frag.appendChild(unit(document.createTextNode(part)));
        });
        el.replaceChild(frag, node);
      } else if (node.nodeType === 1) {
        if (node.tagName === 'BR') { last = null; return; }
        if (last) last.appendChild(node);
        else el.replaceChild(unit(node.cloneNode(true)), node);
      }
    });
    el.classList.add('split');
  };

  if (!reduced && 'IntersectionObserver' in window) {
    var heads = all('h1, .h2').filter(function (h) { return h.textContent.trim() && !h.closest('.xp-panel'); });
    heads.forEach(splitWords);
    var revealEls = all(REVEAL.join(',')).filter(function (el) { return !el.closest('.xp-panel'); });
    revealEls.forEach(function (el) { el.classList.add('reveal'); });

    var mio = new IntersectionObserver(function (entries) {
      var seen = new Map();            /* parent -> how many siblings already released this batch */
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        if (el.classList.contains('reveal')) {
          var k = seen.get(el.parentNode) || 0;
          seen.set(el.parentNode, k + 1);
          el.style.setProperty('--d', k * 90 + 'ms');
        }
        el.classList.add('in');
        mio.unobserve(el);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    heads.concat(revealEls).forEach(function (el) { mio.observe(el); });
  }

  var yr = one('#yr');
  if (yr) yr.textContent = new Date().getFullYear();

  /* Contact form: this is a static site with nowhere to send a POST, so submitting hands the
     message to the visitor's own email client, addressed and filled in, for them to send. */
  var cform = one('#contactForm');
  if (cform) {
    cform.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = function (name) { return (cform.elements[name].value || '').trim(); };
      var subject = v('subject') + ' — ' + v('name');
      var body = v('message') + '\n\n—\n' + v('name') +
        (v('company') ? ' · ' + v('company') : '') + '\n' + v('email');
      window.location.href = 'mailto:info@skotcomms.com?subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(body);
      var note = one('#cfNote');
      if (note) note.hidden = false;
    });
  }
})();
