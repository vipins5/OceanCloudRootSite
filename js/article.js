/* ═══════════════════════════════════════════════════════════
   article.js — reading progress bar, TOC with scroll-spy,
   dynamic related articles, in-article breadcrumb
   ═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* ── All 19 guide articles ─────────────────────────────── */
  var GUIDES = [
    { topic:'sharepoint',     tag:'SharePoint',          url:'guide-sharepoint-permissions',                  title:'The Complete Guide to SharePoint Permissions in Microsoft 365',                           read:'8 min read'  },
    { topic:'migration',      tag:'Migration',            url:'guide-m365-migration-checklist',                title:'The 10-Step Microsoft 365 Migration Checklist',                                           read:'7 min read'  },
    { topic:'sharepoint',     tag:'SharePoint & Teams',   url:'guide-sharepoint-vs-teams',                     title:'SharePoint vs Microsoft Teams: When to Use Which',                                        read:'6 min read'  },
    { topic:'power-platform', tag:'Power Platform',       url:'guide-power-automate-sharepoint',               title:'5 Power Automate Flows Every SharePoint Admin Should Build',                              read:'8 min read'  },
    { topic:'sharepoint',     tag:'SharePoint',           url:'guide-sharepoint-intranet',                     title:'How to Build a Modern SharePoint Intranet in 2026',                                       read:'9 min read'  },
    { topic:'copilot',        tag:'Copilot',              url:'guide-m365-copilot',                            title:'Microsoft 365 Copilot: The Complete Business Guide',                                      read:'10 min read' },
    { topic:'copilot',        tag:'Copilot',              url:'guide-sharepoint-copilot-ready',                title:'How to Prepare Your SharePoint for Microsoft Copilot',                                    read:'11 min read' },
    { topic:'power-platform', tag:'Power Platform',       url:'guide-power-apps-sharepoint',                   title:'Build Custom Business Apps with Power Apps and SharePoint',                               read:'10 min read' },
    { topic:'teams',          tag:'Teams',                url:'guide-teams-automation',                        title:'5 Microsoft Teams Automations That Save Hours Every Week',                                read:'9 min read'  },
    { topic:'integration',    tag:'Integration',          url:'guide-microsoft-graph-sharepoint',              title:'Microsoft Graph and SharePoint: M365 Integrations for IT Admins',                         read:'11 min read' },
    { topic:'power-platform', tag:'Power Platform',       url:'guide-sharepoint-approval-workflow',            title:'How to Build a SharePoint Approval Workflow with Power Automate',                         read:'10 min read' },
    { topic:'power-platform', tag:'Power Platform',       url:'guide-sharepoint-approval-multiple-approvers',  title:'SharePoint Approval Workflows with Multiple Approvers: Sequential vs Parallel',            read:'10 min read' },
    { topic:'power-platform', tag:'Power Platform',       url:'guide-sharepoint-automation-ideas',             title:'10 SharePoint Automation Ideas Using Power Automate',                                     read:'9 min read'  },
    { topic:'power-platform', tag:'Power Platform',       url:'guide-power-automate-triggers-actions',         title:'Power Automate SharePoint Triggers and Actions Explained',                                read:'10 min read' },
    { topic:'power-platform', tag:'Power Platform',       url:'guide-sharepoint-workflow-migration',           title:'How to Replace Legacy SharePoint Workflows with Power Automate',                          read:'9 min read'  },
    { topic:'copilot',        tag:'Copilot',              url:'guide-sharepoint-copilot-agents',               title:'SharePoint Copilot Agents: Licensing, Limits & Use Cases',                               read:'10 min read' },
    { topic:'integration',    tag:'Integration',          url:'guide-sharepoint-integrations',                 title:'Best SharePoint Integrations: Teams, Power BI, Salesforce & Dynamics 365',               read:'11 min read' },
    { topic:'sharepoint',     tag:'SharePoint',           url:'guide-sharepoint-permissions-best-practices',   title:'SharePoint Permissions Best Practices for Secure Microsoft 365 Sites',                    read:'11 min read' },
    { topic:'admin',          tag:'Admin & Automation',   url:'guide-pnp-entra-app-registration',              title:'PnP PowerShell: Complete Entra App Registration & Certificate Guide',                     read:'15 min read' }
  ];

  /* ── Detect current article slug from URL ─────────────── */
  function currentSlug() {
    var p = window.location.pathname.split('/');
    return p[p.length - 1].replace(/\.html$/, '') || '';
  }

  /* ── Detect topic from .art-tag text ──────────────────── */
  function currentTopic() {
    var el = document.querySelector('.art-tag');
    if (!el) return 'sharepoint';
    var t = el.textContent.trim().toLowerCase();
    if (t.includes('admin'))       return 'admin';
    if (t.includes('copilot'))     return 'copilot';
    if (t.includes('migration'))   return 'migration';
    if (t.includes('teams'))       return 'teams';
    if (t.includes('integration')) return 'integration';
    if (t.includes('power'))       return 'power-platform';
    return 'sharepoint';
  }

  /* ═══════════════════════════════════════════════════════
     1. Reading progress bar
     ═══════════════════════════════════════════════════════ */
  function initProgress() {
    var bar = document.createElement('div');
    bar.id = 'reading-progress';
    document.body.insertBefore(bar, document.body.firstChild);

    window.addEventListener('scroll', function () {
      var st  = window.scrollY || document.documentElement.scrollTop;
      var max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (max > 0 ? Math.min(st / max * 100, 100) : 0) + '%';
    }, { passive: true });
  }

  /* ═══════════════════════════════════════════════════════
     2. Table of contents + scroll-spy
     ═══════════════════════════════════════════════════════ */
  function initTOC() {
    var wrap = document.querySelector('.article-wrap');
    if (!wrap) return;
    var headings = Array.from(wrap.querySelectorAll('h2'));
    if (headings.length < 3) return;

    /* Assign IDs to headings that lack them */
    headings.forEach(function (h, i) {
      if (!h.id) h.id = 'toc-' + i;
    });

    /* SVG icons */
    var SVG_LINES   = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
    var SVG_CHEVRON = '<svg class="toc-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>';

    /* Build shared <ul> factory */
    function buildList() {
      var ul = document.createElement('ul');
      ul.className = 'toc-list';
      headings.forEach(function (h) {
        var li = document.createElement('li');
        var a  = document.createElement('a');
        a.href      = '#' + h.id;
        a.className = 'toc-link';
        a.textContent = h.textContent;
        li.appendChild(a);
        ul.appendChild(li);
      });
      return ul;
    }

    /* ── Desktop sidebar ── */
    var sidebar = document.createElement('nav');
    sidebar.id = 'toc-sidebar';
    sidebar.setAttribute('aria-label', 'Table of contents');

    var lbl = document.createElement('div');
    lbl.className   = 'toc-label';
    lbl.textContent = 'Contents';
    sidebar.appendChild(lbl);

    var desktopUl = buildList();
    sidebar.appendChild(desktopUl);
    document.body.appendChild(sidebar);

    /* Desktop link click → smooth scroll */
    var desktopLinks = Array.from(desktopUl.querySelectorAll('.toc-link'));
    desktopLinks.forEach(function (a, i) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        headings[i].scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.replaceState(null, '', '#' + headings[i].id);
      });
    });

    /* ── Mobile toggle + list (injected before article-meta) ── */
    var meta = wrap.querySelector('.article-meta');
    if (meta) {
      var toggle = document.createElement('button');
      toggle.id = 'toc-toggle';
      toggle.setAttribute('aria-expanded', 'false');
      toggle.innerHTML = SVG_LINES + ' Contents ' + SVG_CHEVRON;

      var mobileDiv = document.createElement('div');
      mobileDiv.id  = 'toc-mobile';
      mobileDiv.hidden = true;

      var mobileUl = buildList();
      mobileDiv.appendChild(mobileUl);
      var mobileLinks = Array.from(mobileUl.querySelectorAll('.toc-link'));

      mobileLinks.forEach(function (a, i) {
        a.addEventListener('click', function (e) {
          e.preventDefault();
          headings[i].scrollIntoView({ behavior: 'smooth', block: 'start' });
          mobileDiv.hidden = true;
          toggle.classList.remove('open');
          toggle.setAttribute('aria-expanded', 'false');
        });
      });

      toggle.addEventListener('click', function () {
        var isOpen = !mobileDiv.hidden;
        mobileDiv.hidden = isOpen;
        toggle.classList.toggle('open', !isOpen);
        toggle.setAttribute('aria-expanded', String(!isOpen));
      });

      wrap.insertBefore(mobileDiv, meta);
      wrap.insertBefore(toggle, mobileDiv);
    }

    /* ── Scroll-spy via IntersectionObserver ── */
    function setActive(idx) {
      desktopLinks.forEach(function (l) { l.classList.remove('active'); });
      if (desktopLinks[idx]) desktopLinks[idx].classList.add('active');

      var mls = document.querySelectorAll('#toc-mobile .toc-link');
      mls.forEach(function (l) { l.classList.remove('active'); });
      if (mls[idx]) mls[idx].classList.add('active');
    }

    setActive(0);

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var idx = headings.indexOf(entry.target);
        if (idx === -1) return;
        if (entry.isIntersecting) {
          lastActive = idx;
          setActive(idx);
        }
      });
    }, { rootMargin: '-10% 0% -80% 0%', threshold: 0 });

    headings.forEach(function (h) { observer.observe(h); });
  }

  /* ═══════════════════════════════════════════════════════
     3. Dynamic related articles (tag-matched, replaces
        hard-coded .related-grid content)
     ═══════════════════════════════════════════════════════ */
  function initRelated() {
    var grid = document.querySelector('.related-grid');
    if (!grid) return;

    var slug  = currentSlug();
    var topic = currentTopic();

    var same  = GUIDES.filter(function (g) { return g.topic === topic && g.url !== slug; });
    var other = GUIDES.filter(function (g) { return g.topic !== topic && g.url !== slug; });
    var picks = same.concat(other).slice(0, 3);
    if (!picks.length) return;

    grid.innerHTML = picks.map(function (g) {
      return '<a class="related-card glass" href="' + g.url + '">' +
        '<span class="rc-topic">' + escHtml(g.tag) + '</span>' +
        '<span class="rc-title">' + escHtml(g.title) + '</span>' +
        '<span class="rc-read">' + g.read + ' →</span>' +
        '</a>';
    }).join('');
  }

  function escHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  /* ═══════════════════════════════════════════════════════
     4. In-article breadcrumb (cloned from hero, injected
        as first element of .article-wrap)
     ═══════════════════════════════════════════════════════ */
  function initBreadcrumb() {
    var wrap = document.querySelector('.article-wrap');
    if (!wrap) return;

    /* Source: the hero breadcrumb already in the page */
    var heroBc = document.querySelector('#main-content .breadcrumb');
    if (!heroBc) return;

    var bc = document.createElement('nav');
    bc.className = 'art-breadcrumb';
    bc.setAttribute('aria-label', 'Breadcrumb');

    heroBc.childNodes.forEach(function (node) {
      if (node.nodeType !== Node.ELEMENT_NODE) return;
      var clone = node.cloneNode(true);
      if (clone.tagName === 'SPAN') {
        clone.className = (clone.textContent.trim() === '/') ? 'bc-sep' : 'bc-current';
      }
      bc.appendChild(clone);
    });

    /* Insert as first child (before TOC toggle, before article-meta) */
    wrap.insertBefore(bc, wrap.firstChild);
  }

  /* ═══════════════════════════════════════════════════════
     Boot
     ═══════════════════════════════════════════════════════ */
  function init() {
    initProgress();
    initTOC();
    initRelated();
    initBreadcrumb();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
