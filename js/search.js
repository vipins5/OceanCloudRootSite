/* =========================================================
   OceanCloud Search
   Three modes: Articles (client-side), Web (Google CSE), AI (Perplexity)
   ========================================================= */

/* ── CONFIG ───────────────────────────────────────────────
   Paste your Google Custom Search Engine ID below.
   Get one free at: https://programmablesearchengine.google.com/
   Create a search engine, add oceancloudconsults.com as the site,
   then copy the "Search engine ID" (looks like: a1b2c3d4e5f6g7h8i)
   ─────────────────────────────────────────────────────── */
var GOOGLE_CSE_ID = '1245cccaad091448b';

/* ── ARTICLE INDEX ───────────────────────────────────────
   Covers: News articles, Archive items, Case Studies, Site pages.
   Add new entries here whenever new content is published.
   ─────────────────────────────────────────────────────── */
var ARTICLES = [
  /* ── Site Pages ── */
  { id: 'p1', type: 'page', tag: 'Page', topic: 'general',
    title: 'SharePoint Consulting & M365 Migration',
    excerpt: 'Microsoft Solutions Partner offering SharePoint consulting, M365 migration, Power Platform and Teams services across the United States.',
    url: '/', dateDisplay: '', dateSort: '' },
  { id: 'p2', type: 'page', tag: 'Page', topic: 'general',
    title: 'Our Services — SharePoint, M365, Teams, Power Platform, Security',
    excerpt: 'Full range of Microsoft 365 services: SharePoint Online builds, M365 migration, Microsoft Teams & Viva rollouts, Power Platform automation, and security & compliance.',
    url: 'services', dateDisplay: '', dateSort: '' },
  { id: 'p3', type: 'page', tag: 'Page', topic: 'general',
    title: 'About OceanCloud — Microsoft Solutions Partner',
    excerpt: 'Meet the OceanCloud team — certified Microsoft consultants specialising in SharePoint, M365, and digital workplace transformation.',
    url: 'about', dateDisplay: '', dateSort: '' },
  { id: 'p4', type: 'page', tag: 'Page', topic: 'general',
    title: 'Contact OceanCloud — Book a Free Consultation',
    excerpt: 'Get in touch for a free 60-minute consultation. SharePoint, M365 migration, Power Platform, Teams — we are ready to help.',
    url: 'contact', dateDisplay: '', dateSort: '' },

  /* ── Case Studies ── */
  { id: 'c1', type: 'casestudy', tag: 'Case Study', topic: 'sharepoint',
    title: 'Meridian Group — Global Intranet Rebuild',
    excerpt: 'Replaced a decade-old intranet with a modern SharePoint Online hub serving 3,500 employees across 8 countries in 10 weeks. 94% adoption in 30 days.',
    url: 'case-studies', dateDisplay: '', dateSort: '' },
  { id: 'c2', type: 'casestudy', tag: 'Case Study', topic: 'migration',
    title: 'Hartwell NHS Trust — Zero-Downtime M365 Migration',
    excerpt: 'Migrated 2,400 mailboxes, 18TB of file share data, and legacy SharePoint 2013 to Microsoft 365 in a 24/7 healthcare environment with zero data loss.',
    url: 'case-studies', dateDisplay: '', dateSort: '' },
  { id: 'c3', type: 'casestudy', tag: 'Case Study', topic: 'power-platform',
    title: 'BrightCore Finance — Automated Compliance Reporting',
    excerpt: 'Built Power Apps and Power Automate flows that replaced 12 hours of weekly manual reporting with a single-click dashboard, saving $120k annually.',
    url: 'case-studies', dateDisplay: '', dateSort: '' },
  { id: 'c4', type: 'casestudy', tag: 'Case Study', topic: 'security',
    title: 'Nexus Legal — Zero Trust Security Transformation',
    excerpt: 'Deployed a full Zero Trust architecture with Entra ID, Conditional Access, and Microsoft Purview for a 600-seat law firm. Achieved ISO 27001.',
    url: 'case-studies', dateDisplay: '', dateSort: '' },
  { id: 'c5', type: 'casestudy', tag: 'Case Study', topic: 'teams',
    title: 'Summit Retail — Frontline Worker Enablement',
    excerpt: 'Rolled out Microsoft Teams and Viva Connections to 1,800 frontline retail workers across 42 stores, reducing HR query volume by 38%.',
    url: 'case-studies', dateDisplay: '', dateSort: '' },
  { id: 'c6', type: 'casestudy', tag: 'Case Study', topic: 'sharepoint',
    title: 'Portway Council — SharePoint Governance & Lifecycle Management',
    excerpt: 'Tamed a sprawling SharePoint Online environment of 4,200 sites with automated lifecycle policies, sensitivity labelling, and a centralised governance framework.',
    url: 'case-studies', dateDisplay: '', dateSort: '' },
  { id: 'c7', type: 'casestudy', tag: 'Case Study', topic: 'copilot',
    title: 'Vantage Capital — M365 Copilot Readiness & Rollout',
    excerpt: 'Prepared and deployed Microsoft 365 Copilot for a 450-seat financial services firm. Eliminated oversharing risks and achieved 31% productivity uplift within 90 days.',
    url: 'case-studies', dateDisplay: '', dateSort: '' },
  { id: 'c8', type: 'casestudy', tag: 'Case Study', topic: 'teams',
    title: 'Castlefield Academy Trust — M365 Adoption Across 14 Schools',
    excerpt: 'Delivered a structured Microsoft 365 adoption programme for 1,200 teaching staff across a multi-academy trust — doubled Teams Daily Active Users in 60 days.',
    url: 'case-studies', dateDisplay: '', dateSort: '' },

  /* ── News & Blog ── */
  { id: 'n1', type: 'blog', tag: 'SharePoint Blog', topic: 'sharepoint',
    title: 'Proven intranet framework - Involv Intranet - SharePoint Partner Showcase',
    excerpt: 'Tim Bogemans and Pascal Herreweghe from Involv Intranet join Vesa Juvonen from Microsoft to highlight capabilities built for SharePoint in Microsoft 365.',
    url: 'https://techcommunity.microsoft.com/t5/microsoft-sharepoint-blog/proven-intranet-framework-involv-intranet-sharepoint-partner/ba-p/4519241',
    dateDisplay: 'May 13, 2026', dateSort: '2026-05-13', external: true },
  { id: 'n2', type: 'blog', tag: 'SharePoint Blog', topic: 'sharepoint',
    title: 'Microsoft named a Leader in the 2026 Gartner® Magic Quadrant™ for Document Management',
    excerpt: 'AI is raising the bar for document management — content needs to be governed, structured, and connected to the way teams work so AI can reason over it responsibly.',
    url: 'https://techcommunity.microsoft.com/t5/microsoft-sharepoint-blog/microsoft-named-a-leader-in-the-2026-gartner-magic-quadrant-for/ba-p/4516252',
    dateDisplay: 'April 30, 2026', dateSort: '2026-04-30', external: true },
  { id: 'n3', type: 'blog', tag: 'SharePoint Blog', topic: 'sharepoint',
    title: 'SharePoint Showcase: AI-Forward Content Creation & Curation for the Modern Intranet',
    excerpt: 'From the Microsoft 365 Community Conference in Orlando — how SharePoint is evolving with AI-forward content creation and curation for the modern intranet.',
    url: 'https://techcommunity.microsoft.com/t5/microsoft-sharepoint-blog/sharepoint-showcase-ai-forward-content-creation-curation-for-the/ba-p/4515947',
    dateDisplay: 'April 30, 2026', dateSort: '2026-04-30', external: true },
  { id: 'n4', type: 'blog', tag: 'SharePoint Blog', topic: 'sharepoint',
    title: 'Solutions for document-centric business processes - Portal Systems - SharePoint Partner Showcase',
    excerpt: 'Patrick Carl from Portal Systems AG showcases different features and capabilities built for Microsoft 365 — focused on document-centric business workflows.',
    url: 'https://techcommunity.microsoft.com/t5/microsoft-sharepoint-blog/solutions-for-document-centric-business-processes-portal-systems/ba-p/4515217',
    dateDisplay: 'April 29, 2026', dateSort: '2026-04-29', external: true },
  { id: 'n5', type: 'blog', tag: 'SharePoint Blog', topic: 'sharepoint',
    title: 'Building a modern digital workplace on Microsoft 365 - WebVine - SharePoint Partner Showcase',
    excerpt: 'Chloe Dervin and James Dellow from WebVine showcase features built for Microsoft 365 — focused on building a modern digital workplace experience.',
    url: 'https://techcommunity.microsoft.com/t5/microsoft-sharepoint-blog/building-a-modern-digital-workplace-on-microsoft-365-webvine/ba-p/4511679',
    dateDisplay: 'April 27, 2026', dateSort: '2026-04-27', external: true },
  { id: 'n6', type: 'blog', tag: 'SharePoint Blog', topic: 'sharepoint',
    title: 'AI Skills Are Now in Public Preview: Teaching AI in SharePoint What to Know and How to Act',
    excerpt: 'SharePoint is transforming how teams build solutions and publish content using AI — describe intent in natural language and move directly to working solutions.',
    url: 'https://techcommunity.microsoft.com/t5/microsoft-sharepoint-blog/ai-skills-are-now-in-public-preview-teaching-ai-in-sharepoint/ba-p/4512532',
    dateDisplay: 'April 21, 2026', dateSort: '2026-04-21', external: true },

  /* ── M365 Roadmap ── */
  { id: 'r1', type: 'roadmap', tag: 'M365 Roadmap', topic: 'teams',
    title: 'Microsoft Teams: Interpreter agent support in Teams Rooms on Android',
    excerpt: 'The Interpreter agent acts as a translator in Microsoft Teams meetings, allowing participants to listen in their chosen language with real-time translation.',
    url: 'https://www.microsoft.com/microsoft-365/roadmap?id=562665',
    dateDisplay: 'May 20, 2026', dateSort: '2026-05-20', external: true },
  { id: 'r2', type: 'roadmap', tag: 'M365 Roadmap', topic: 'purview',
    title: 'Microsoft Purview: Information Protection – Auto-labeling Simulation Evaluation',
    excerpt: 'The Simulation Grader helps admins understand and improve auto-labeling accuracy before enforcing a policy using AI to determine true vs. false positives.',
    url: 'https://www.microsoft.com/microsoft-365/roadmap?id=560707',
    dateDisplay: 'May 20, 2026', dateSort: '2026-05-20', external: true },
  { id: 'r3', type: 'roadmap', tag: 'M365 Roadmap', topic: 'teams',
    title: 'Microsoft Teams: Support human interpreter listening mode in Teams Rooms on Windows',
    excerpt: 'Teams Rooms on Windows now supports human interpreter listening mode, allowing room participants to select a language and hear interpreter audio. GA: July 2026.',
    url: 'https://www.microsoft.com/microsoft-365/roadmap?id=562050',
    dateDisplay: 'May 18, 2026', dateSort: '2026-05-18', external: true },
  { id: 'r4', type: 'roadmap', tag: 'M365 Roadmap', topic: 'teams',
    title: 'Microsoft Teams: Searchable keyboard shortcuts from the dialog in Teams',
    excerpt: 'Easily find keyboard shortcuts with a new searchable experience in Microsoft Teams — search by name or key combination. GA: June 2026.',
    url: 'https://www.microsoft.com/microsoft-365/roadmap?id=562413',
    dateDisplay: 'May 15, 2026', dateSort: '2026-05-15', external: true },
  { id: 'r5', type: 'roadmap', tag: 'M365 Roadmap', topic: 'purview',
    title: 'Microsoft Purview: Data Lifecycle Management - DLM Meter Change',
    excerpt: 'Data Lifecycle Management billing will be based on the volume of data retained — billed at $0.25 per GB per month for non-Microsoft 365 generative AI prompts.',
    url: 'https://www.microsoft.com/microsoft-365/roadmap?id=560324',
    dateDisplay: 'May 15, 2026', dateSort: '2026-05-15', external: true },
  { id: 'r6', type: 'roadmap', tag: 'M365 Roadmap', topic: 'teams',
    title: 'Microsoft Teams: Preloaded video for Teams Events and Meetings',
    excerpt: 'Users can upload videos from OneDrive directly into a Teams event or meeting for smoother high-quality playback when Manage What Attendees See mode is enabled.',
    url: 'https://www.microsoft.com/microsoft-365/roadmap?id=562340',
    dateDisplay: 'May 14, 2026', dateSort: '2026-05-14', external: true }
];

/* ── TAG COLOURS ─────────────────────────────────────────── */
var TAG_CLASS = {
  blog:      'tag-blog',
  roadmap:   'tag-roadmap',
  casestudy: 'tag-case',
  page:      'tag-page'
};

/* ── STATE ───────────────────────────────────────────────── */
var currentTab   = 'articles';
var currentQuery = '';
var cseInjected  = false;

/* ── DOM REFS (set on DOMContentLoaded) ─────────────────── */
var inputEl, panelArticles, panelWeb, panelAI, resultsEl;
var tabBtns;

/* ── INIT ────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  inputEl       = document.getElementById('search-q');
  panelArticles = document.getElementById('panel-articles');
  panelWeb      = document.getElementById('panel-web');
  panelAI       = document.getElementById('panel-ai');
  resultsEl     = document.getElementById('articles-results');
  tabBtns       = document.querySelectorAll('.stab');

  /* read ?q= from URL */
  var params = new URLSearchParams(window.location.search);
  var initQ  = (params.get('q') || '').trim();
  if (initQ) {
    inputEl.value = initQ;
    currentQuery  = initQ;
  }

  /* render initial state */
  renderArticles();
  updatePerplexityLink();

  /* search input events */
  inputEl.addEventListener('input', function () {
    currentQuery = inputEl.value.trim();
    if (currentTab === 'articles') renderArticles();
    updatePerplexityLink();
  });

  inputEl.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      currentQuery = inputEl.value.trim();
      switchTab(currentTab);
      updateURL();
    }
  });

  document.getElementById('search-submit').addEventListener('click', function () {
    currentQuery = inputEl.value.trim();
    switchTab(currentTab);
    updateURL();
  });

  /* tab buttons */
  tabBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      switchTab(btn.getAttribute('data-tab'));
    });
  });
});

/* ── TAB SWITCHING ───────────────────────────────────────── */
function switchTab(tab) {
  currentTab = tab;
  tabBtns.forEach(function (b) {
    b.classList.toggle('active', b.getAttribute('data-tab') === tab);
  });
  panelArticles.classList.toggle('active', tab === 'articles');
  panelWeb.classList.toggle('active',      tab === 'web');
  panelAI.classList.toggle('active',       tab === 'ai');

  if (tab === 'articles') renderArticles();
  if (tab === 'web')      renderWeb();
  if (tab === 'ai')       updatePerplexityLink();
}

/* ── URL UPDATE ──────────────────────────────────────────── */
function updateURL() {
  if (!history.replaceState) return;
  var url = window.location.pathname;
  if (currentQuery) url += '?q=' + encodeURIComponent(currentQuery);
  history.replaceState(null, '', url);
}

/* ── ARTICLE SEARCH ──────────────────────────────────────── */
function renderArticles() {
  var q = currentQuery.toLowerCase();
  var words = q ? q.split(/\s+/).filter(Boolean) : [];
  var results;

  if (!words.length) {
    /* no query — show news and case studies sorted by date */
    results = ARTICLES.filter(function (a) {
      return a.type !== 'page';
    }).sort(function (a, b) {
      return (b.dateSort || '').localeCompare(a.dateSort || '');
    });
  } else {
    results = ARTICLES.map(function (a) {
      var haystack = (a.title + ' ' + a.excerpt + ' ' + a.topic + ' ' + a.tag).toLowerCase();
      var score = 0;
      var allMatch = words.every(function (w) {
        if (haystack.indexOf(w) !== -1) {
          score += (a.title.toLowerCase().indexOf(w) !== -1) ? 3 : 1;
          return true;
        }
        return false;
      });
      return allMatch ? { article: a, score: score } : null;
    })
    .filter(Boolean)
    .sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score;
      return (b.article.dateSort || '').localeCompare(a.article.dateSort || '');
    })
    .map(function (r) { return r.article; });
  }

  if (!results.length) {
    resultsEl.innerHTML =
      '<div class="sr-empty">' +
        '<div class="sr-empty-icon">&#128269;</div>' +
        '<p>No articles found for <strong>"' + escHtml(currentQuery) + '"</strong></p>' +
        '<p class="sr-empty-sub">Try the <button class="sr-tab-link" data-tab="web">Web</button> or <button class="sr-tab-link" data-tab="ai">AI</button> tab for broader results.</p>' +
      '</div>';
    resultsEl.querySelectorAll('.sr-tab-link').forEach(function (btn) {
      btn.addEventListener('click', function () { switchTab(btn.getAttribute('data-tab')); });
    });
    return;
  }

  var html = '<p class="sr-count">' +
    (words.length ? results.length + ' result' + (results.length !== 1 ? 's' : '') + ' for <strong>"' + escHtml(currentQuery) + '"</strong>' : 'Latest articles &amp; case studies') +
    '</p>';
  html += '<div class="sr-list">';
  results.forEach(function (a) {
    var tagCls  = TAG_CLASS[a.type] || 'tag-page';
    var isExt   = a.external;
    var excerpt = words.length ? highlight(a.excerpt, words) : escHtml(a.excerpt);
    var titleH  = words.length ? highlight(a.title, words) : escHtml(a.title);
    html +=
      '<div class="sr-card">' +
        '<div class="sr-meta">' +
          '<span class="nc-tag ' + tagCls + '">' + escHtml(a.tag) + '</span>' +
          (a.dateDisplay ? '<span class="sr-date">' + escHtml(a.dateDisplay) + '</span>' : '') +
        '</div>' +
        '<h3 class="sr-title"><a href="' + escHtml(a.url) + '"' + (isExt ? ' target="_blank" rel="noopener noreferrer"' : '') + '>' + titleH + (isExt ? ' <span class="sr-ext">&#8599;</span>' : '') + '</a></h3>' +
        '<p class="sr-excerpt">' + excerpt + '</p>' +
      '</div>';
  });
  html += '</div>';
  resultsEl.innerHTML = html;
}

/* ── WEB SEARCH (Google CSE) ─────────────────────────────── */
function renderWeb() {
  var container = document.getElementById('gcs-container');

  if (!GOOGLE_CSE_ID) {
    container.innerHTML =
      '<div class="gcs-setup">' +
        '<div class="gcs-setup-icon">&#128640;</div>' +
        '<h3>Google Custom Search — Setup Required</h3>' +
        '<p>To enable in-page web search, create a free Google Custom Search Engine and add your ID to <code>js/search.js</code>:</p>' +
        '<ol class="gcs-steps">' +
          '<li>Go to <strong>programmablesearchengine.google.com</strong></li>' +
          '<li>Click <em>Add</em>, enter <code>oceancloudconsults.com</code> as the site</li>' +
          '<li>Copy the <em>Search engine ID</em></li>' +
          '<li>Open <code>js/search.js</code> and set <code>GOOGLE_CSE_ID = \'your-id-here\'</code></li>' +
        '</ol>' +
        '<p class="gcs-fallback">For now, <a class="gcs-google-link" href="#" id="google-fallback" target="_blank" rel="noopener noreferrer">search Google &#8599;</a> for your query.</p>' +
      '</div>';
    var fallback = document.getElementById('google-fallback');
    if (fallback) {
      var gq = currentQuery || 'SharePoint consulting';
      fallback.href = 'https://www.google.com/search?q=' + encodeURIComponent(gq + ' site:oceancloudconsults.com OR ' + gq + ' SharePoint M365');
    }
    return;
  }

  /* inject CSE script once */
  if (!cseInjected) {
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://cse.google.com/cse.js?cx=' + encodeURIComponent(GOOGLE_CSE_ID);
    document.head.appendChild(script);
    cseInjected = true;
  }

  container.innerHTML =
    '<div class="gcse-searchbox-only" data-autoSearchOnLoad="' + (currentQuery ? 'true' : 'false') + '" data-defaultToImageSearch="false" data-queryParameterName="q"></div>' +
    '<div class="gcse-searchresults-only" data-queryParameterName="q"></div>';

  /* pre-fill query in CSE box after it renders */
  if (currentQuery) {
    var attempts = 0;
    var poller = setInterval(function () {
      var cseInput = container.querySelector('input[name="q"]');
      if (cseInput) {
        cseInput.value = currentQuery;
        clearInterval(poller);
        var form = cseInput.closest('form');
        if (form) form.submit();
      }
      if (++attempts > 30) clearInterval(poller);
    }, 200);
  }
}

/* ── AI (Perplexity) ─────────────────────────────────────── */
function updatePerplexityLink() {
  var q   = currentQuery || 'SharePoint M365 consulting';
  var url = 'https://www.perplexity.ai/search?q=' + encodeURIComponent(q);
  var link = document.getElementById('perplexity-link');
  if (link) link.href = url;
  var preview = document.getElementById('ai-query-preview');
  if (preview) preview.textContent = currentQuery || '';
  var previewWrap = document.getElementById('ai-query-wrap');
  if (previewWrap) previewWrap.style.display = currentQuery ? 'flex' : 'none';
}

/* ── HELPERS ─────────────────────────────────────────────── */
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function highlight(text, words) {
  var escaped = escHtml(text);
  words.forEach(function (w) {
    var re = new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    escaped = escaped.replace(re, '<mark>$1</mark>');
  });
  return escaped;
}
