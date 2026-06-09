(function () {
  'use strict';

  var MC_ENDPOINT = 'https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev/m365/message-center';
  var REFRESH_MS  = 15 * 60 * 1000;

  var root      = document.getElementById('mc-shell');
  if (!root) return;

  var tbody     = document.getElementById('mc-tbody');
  var detailEl  = document.getElementById('mc-detail');
  var mainArea  = document.getElementById('mc-main-area');
  var summaryEl = document.getElementById('mc-summary');
  var updatedEl = document.getElementById('mc-updated');
  var countEl   = document.getElementById('mc-count');
  var searchEl  = document.getElementById('mc-search');
  var hintEl    = document.getElementById('mc-search-hint');

  var allMessages  = [];
  var activeId     = null;
  var filterCat    = 'all';
  var filterSvc    = 'all';
  var filterTag    = 'all';
  var searchQuery  = '';
  var autoOn       = true;
  var lookedUpId   = '';
  var timer        = null;

  var CAT_LABELS = {
    stayInformed:      'Stay Informed',
    planForChange:     'Plan for Change',
    preventOrFixIssue: 'Action Required',
  };

  function tagClass(tag) {
    var t = (tag || '').toLowerCase();
    if (t.includes('new feature'))  return 'mc-tag-feature';
    if (t.includes('user impact'))  return 'mc-tag-user';
    if (t.includes('admin impact')) return 'mc-tag-admin';
    if (t.includes('major change')) return 'mc-tag-major';
    return 'mc-tag-default';
  }

  // Relevance is driven primarily by Microsoft's authoritative `severity`
  // field (normal | high | critical), falling back to category/major-change.
  function relevance(m) {
    var sev = String(m.severity || '').toLowerCase();
    if (sev === 'critical' || sev === 'high') return { level: 'High',   dots: 4 };
    if (m.category === 'preventOrFixIssue')   return { level: 'High',   dots: 4 };
    if (m.isMajorChange)                      return { level: 'High',   dots: 4 };
    if (m.category === 'planForChange')       return { level: 'Medium', dots: 2 };
    return                                           { level: 'Normal', dots: 1 };
  }

  function relHtml(m) {
    var r = relevance(m);
    var dots = '';
    for (var i = 0; i < 4; i++) {
      dots += '<span class="mc-rel-dot' + (i < r.dots ? ' on' : '') + '"></span>';
    }
    return '<span class="mc-rel mc-rel-' + r.level.toLowerCase() + '">' + dots + r.level + '</span>';
  }

  function categoryClass(category) {
    if (category === 'preventOrFixIssue') return 'mc-cat-action';
    if (category === 'planForChange') return 'mc-cat-plan';
    return 'mc-cat-info';
  }

  function fmtDate(iso) {
    if (!iso) return '';
    try { return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }); }
    catch (e) { return iso.slice(0, 10); }
  }

  function fmtDateTime(iso) {
    if (!iso) return '';
    try { return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }); }
    catch (e) { return iso; }
  }

  function isPast(iso) { return iso && new Date(iso) < new Date(); }

  function esc(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // Microsoft 365 Roadmap deep link for a given feature ID.
  function roadmapUrl(id) {
    return 'https://www.microsoft.com/microsoft-365/roadmap?searchterms=' + encodeURIComponent(id);
  }

  // Build a shareable deep link to a specific message on this page.
  function shareUrlFor(id) {
    return location.origin + location.pathname + '?id=' + encodeURIComponent(id);
  }

  // Persisted reading-pane width (as a CSS width value like "48%").
  var MC_WIDTH_KEY = 'mcDetailWidth';
  var MC_MIN_PCT = 32;
  var MC_MAX_PCT = 82;

  function getStoredDetailWidth() {
    try {
      var v = localStorage.getItem(MC_WIDTH_KEY);
      if (v && /^\d+(\.\d+)?%$/.test(v)) return v;
    } catch (e) { /* ignore */ }
    return '48%';
  }

  function storeDetailWidth(value) {
    try { localStorage.setItem(MC_WIDTH_KEY, value); } catch (e) { /* ignore */ }
  }

  function clampPct(pct) {
    return Math.max(MC_MIN_PCT, Math.min(MC_MAX_PCT, pct));
  }

  // Briefly show feedback text on an action button after copy/share.
  function flashActionButton(btn, text) {
    if (!btn) return;
    var label = btn.querySelector('.mc-action-label');
    if (!label) return;
    var original = label.getAttribute('data-original') || label.textContent;
    label.setAttribute('data-original', original);
    label.textContent = text;
    btn.classList.add('is-done');
    clearTimeout(btn._flashTimer);
    btn._flashTimer = setTimeout(function () {
      label.textContent = original;
      btn.classList.remove('is-done');
    }, 1600);
  }

  // Copy text to the clipboard with a graceful fallback for older browsers.
  function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      try {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'absolute';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        resolve();
      } catch (e) { reject(e); }
    });
  }

  // Pull roadmap feature IDs out of the message body, e.g.
  // "This message is associated with Microsoft 365 Roadmap ID 483158."
  function extractRoadmapIds(body) {
    var ids = [];
    var re = /Roadmap ID[s]?\s*:?\s*((?:\d{4,}\s*,\s*)*\d{4,})/gi;
    var match;
    while ((match = re.exec(String(body || '')))) {
      match[1].split(/[,\s]+/).forEach(function (n) {
        n = n.trim();
        if (n && ids.indexOf(n) === -1) ids.push(n);
      });
    }
    return ids;
  }

  // Turn "Roadmap ID 483158" mentions inside already-escaped body text into
  // clickable links to the Microsoft 365 Roadmap.
  function linkifyRoadmap(escapedLine) {
    return escapedLine.replace(
      /(Roadmap ID[s]?\s*:?\s*)((?:\d{4,}\s*,\s*)*\d{4,})/gi,
      function (whole, label, nums) {
        var linked = nums.replace(/\d{4,}/g, function (n) {
          return '<a class="mc-roadmap-link" href="' + roadmapUrl(n) +
            '" target="_blank" rel="noopener noreferrer">' + n + '</a>';
        });
        return label + linked;
      }
    );
  }

  // Linkify roadmap IDs inside rendered HTML by walking text nodes only, so we
  // never touch existing anchors, attributes or tag names.
  function linkifyRoadmapInElement(root) {
    if (!root) return;
    var re = /Roadmap ID[s]?\s*:?\s*(?:\d{4,}[\s,]*)*\d{4,}/i;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var targets = [];
    var node;
    while ((node = walker.nextNode())) {
      if (node.parentNode && node.parentNode.closest && node.parentNode.closest('a')) continue;
      if (re.test(node.nodeValue)) targets.push(node);
    }
    targets.forEach(function (textNode) {
      var span = document.createElement('span');
      span.innerHTML = linkifyRoadmap(esc(textNode.nodeValue));
      textNode.parentNode.replaceChild(span, textNode);
    });
  }

  function normalizeSearchText(s) {
    return String(s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  // Local (browser-only) favourites. Microsoft's `viewPoint.isFavorited` is
  // null under application permissions, so we persist favourites in this
  // browser instead.
  function getFavourites() {
    try { return JSON.parse(localStorage.getItem('mcFavourites') || '{}') || {}; }
    catch (e) { return {}; }
  }
  function isFavourite(id) { return Boolean(id && getFavourites()[id]); }
  function toggleFavourite(id) {
    if (!id) return false;
    var favs = getFavourites();
    if (favs[id]) { delete favs[id]; } else { favs[id] = true; }
    try { localStorage.setItem('mcFavourites', JSON.stringify(favs)); } catch (e) {}
    return Boolean(favs[id]);
  }

  function filtered() {
    return allMessages.filter(function (m) {
      if (filterCat !== 'all' && m.category !== filterCat) return false;
      if (filterSvc !== 'all' && !m.services.includes(filterSvc)) return false;
      if (filterTag !== 'all' && !m.tags.some(function (t) { return t === filterTag; })) return false;
      if (searchQuery) {
        var q = searchQuery.toLowerCase();
        var nq = normalizeSearchText(searchQuery);
        var matchesText = m.title.toLowerCase().includes(q) ||
          m.body.toLowerCase().includes(q) ||
          m.services.join(' ').toLowerCase().includes(q) ||
          m.tags.join(' ').toLowerCase().includes(q) ||
          String(m.category || '').toLowerCase().includes(q) ||
          String(m.id || '').toLowerCase().includes(q);
        var matchesNormalizedId = nq && normalizeSearchText(m.id).includes(nq);
        if (!matchesText && !matchesNormalizedId) return false;
      }
      return true;
    });
  }

  function buildFilters(messages) {
    var svcs = {}, tags = {};
    messages.forEach(function (m) {
      m.services.forEach(function (s) { svcs[s] = true; });
      m.tags.forEach(function (t) { tags[t] = true; });
    });
    return { services: Object.keys(svcs).sort(), tags: Object.keys(tags).sort() };
  }

  function buildDropdownMenu(menuEl, labelEl, items, current, onSelect) {
    menuEl.innerHTML = '<li><button class="mc-dropdown-opt' + (current === 'all' ? ' active' : '') + '" data-value="all" type="button">All</button></li>' +
      items.map(function (v) {
        return '<li><button class="mc-dropdown-opt' + (current === v ? ' active' : '') + '" data-value="' + esc(v) + '" type="button">' + esc(v) + '</button></li>';
      }).join('');
    menuEl.querySelectorAll('.mc-dropdown-opt').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var val = btn.getAttribute('data-value');
        labelEl.textContent = val === 'all' ? (menuEl.id === 'mc-svc-menu' ? 'All Services' : 'All Tags') : val;
        menuEl.querySelectorAll('.mc-dropdown-opt').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var dd = menuEl.closest('.mc-dropdown');
        if (dd) { dd.classList.remove('open'); dd.querySelector('.mc-dropdown-btn').setAttribute('aria-expanded', 'false'); }
        onSelect(val);
      });
    });
  }

  function renderFilterDropdowns(messages) {
    var svcMenu  = document.getElementById('mc-svc-menu');
    var tagMenu  = document.getElementById('mc-tag-menu');
    var svcLabel = document.getElementById('mc-svc-label');
    var tagLabel = document.getElementById('mc-tag-label');
    if (!svcMenu || !tagMenu) return;
    var opts = buildFilters(messages);
    buildDropdownMenu(svcMenu, svcLabel, opts.services, filterSvc, function (val) { filterSvc = val; renderTable(); });
    buildDropdownMenu(tagMenu, tagLabel, opts.tags,     filterTag, function (val) { filterTag = val; renderTable(); });
  }

  function renderTable() {
    if (!tbody) return;
    var msgs = filtered();
    if (countEl) countEl.textContent = msgs.length + ' message' + (msgs.length !== 1 ? 's' : '');
    if (hintEl) {
      hintEl.classList.add('is-empty');
      hintEl.innerHTML = '';
    }

    if (!msgs.length) {
      if (hintEl) {
        hintEl.classList.remove('is-empty');
        hintEl.textContent = 'No messages match the current filters.';
      }
      tbody.innerHTML = '<tr><td colspan="7" class="mc-empty-row">No messages match the current filters.</td></tr>';
      return;
    }

    tbody.innerHTML = msgs.map(function (m) {
      var isActive = m.id === activeId;
      var actBy    = m.actionRequiredByDateTime;
      var actByHtml = actBy
        ? '<span class="' + (isPast(actBy) ? 'mc-past' : 'mc-actby') + '">' + esc(fmtDate(actBy)) + '</span>'
        : '<span class="mc-dim">-</span>';
      var tagsHtml = m.tags.slice(0, 2).map(function (t) {
        return '<span class="mc-tag ' + tagClass(t) + '">' + esc(t) + '</span>';
      }).join('');
      var svc = m.services.slice(0, 2).join(', ');
      var fav = isFavourite(m.id);

      return '<tr class="mc-row' + (isActive ? ' is-active' : '') + '" data-id="' + esc(m.id) + '">' +
        '<td class="mc-col-star"><button class="mc-star-btn' + (fav ? ' is-on' : '') + '" type="button" data-star="' + esc(m.id) + '" aria-label="' + (fav ? 'Remove favourite' : 'Favourite') + '" aria-pressed="' + (fav ? 'true' : 'false') + '">' + (fav ? '&#9733;' : '&#9734;') + '</button></td>' +
        '<td class="mc-col-title">' +
          '<div class="mc-row-id">' + esc(m.id) + '</div>' +
          '<div class="mc-row-title">' + esc(m.title) + '</div>' +
          (m.isMajorChange ? '<span class="mc-badge-major">Major change</span>' : '') +
        '</td>' +
        '<td class="mc-col-svc">' + esc(svc || 'Microsoft 365') + '</td>' +
        '<td class="mc-col-date">' + esc(fmtDate(m.lastModifiedDateTime)) + '</td>' +
        '<td class="mc-col-actby">' + actByHtml + '</td>' +
        '<td class="mc-col-rel">' + relHtml(m) + '</td>' +
        '<td class="mc-col-tags">' + tagsHtml + '</td>' +
      '</tr>';
    }).join('');

    tbody.querySelectorAll('tr[data-id]').forEach(function (row) {
      row.addEventListener('click', function () {
        selectMessage(row.getAttribute('data-id'));
      });
    });

    tbody.querySelectorAll('.mc-star-btn[data-star]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var on = toggleFavourite(btn.getAttribute('data-star'));
        btn.classList.toggle('is-on', on);
        btn.innerHTML = on ? '&#9733;' : '&#9734;';
        btn.setAttribute('aria-pressed', on ? 'true' : 'false');
        btn.setAttribute('aria-label', on ? 'Remove favourite' : 'Favourite');
      });
    });
  }

  function renderDetail(m) {
    if (!m) {
      mainArea.classList.remove('has-detail');
      detailEl.innerHTML = '';
      return;
    }

    var catLabel = CAT_LABELS[m.category] || m.category;
    var tagsHtml = m.tags.map(function (t) {
      return '<span class="mc-tag ' + tagClass(t) + '">' + esc(t) + '</span>';
    }).join('');

    // Prefer the worker-sanitized rich HTML (keeps headings, lists, links and
    // images like the Microsoft 365 admin center). Fall back to plain-text
    // paragraphs for older payloads that only carry `body`.
    var bodyHtml;
    if (m.bodyHtml) {
      bodyHtml = m.bodyHtml;
    } else if (m.body) {
      bodyHtml = m.body.split('\n').filter(function (l) { return l.trim(); })
        .map(function (l) { return '<p>' + linkifyRoadmap(esc(l)) + '</p>'; }).join('');
    } else {
      bodyHtml = '<p class="mc-dim">No body content.</p>';
    }

    var roadmapIds = extractRoadmapIds(m.body || m.bodyHtml);
    var roadmapHtml = roadmapIds.length
      ? '<div><dt>Roadmap ID</dt><dd>' + roadmapIds.map(function (rid) {
          return '<a class="mc-roadmap-link" href="' + roadmapUrl(rid) +
            '" target="_blank" rel="noopener noreferrer">' + esc(rid) + '</a>';
        }).join(', ') + '</dd></div>'
      : '';

    detailEl.innerHTML =
      '<div class="mc-detail-head">' +
        '<div>' +
          '<div class="mc-detail-meta">' +
            '<span class="mc-detail-id">' + esc(m.id) + '</span>' +
            '<span class="mc-detail-cat mc-cat-' + esc(m.category) + '">' + esc(catLabel) + '</span>' +
          '</div>' +
          '<h2 class="mc-detail-title">' + esc(m.title) + '</h2>' +
          (tagsHtml ? '<div class="mc-detail-tags">' + tagsHtml + '</div>' : '') +
        '</div>' +
        '<div class="mc-detail-head-btns">' +
          '<button class="mc-close-btn mc-expand-btn" id="mc-expand" aria-label="Expand reading pane" title="Expand / restore reading pane">' +
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>' +
          '</button>' +
          '<button class="mc-close-btn" id="mc-close" aria-label="Close">&#x2715;</button>' +
        '</div>' +
      '</div>' +
      '<div class="mc-detail-scroll">' +
        '<div class="mc-detail-actions">' +
          '<button type="button" class="mc-action-btn" id="mc-copy-link" data-id="' + esc(m.id) + '">' +
            '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>' +
            '<span class="mc-action-label">Copy link</span>' +
          '</button>' +
          '<button type="button" class="mc-action-btn" id="mc-share" data-id="' + esc(m.id) + '">' +
            '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>' +
            '<span class="mc-action-label">Share</span>' +
          '</button>' +
        '</div>' +
        '<dl class="mc-detail-facts">' +
          '<div><dt>Service</dt><dd>' + esc(m.services.join(', ') || '-') + '</dd></div>' +
          '<div><dt>Last Updated</dt><dd>' + esc(fmtDateTime(m.lastModifiedDateTime) || '-') + '</dd></div>' +
          '<div><dt>Published</dt><dd>' + esc(fmtDate(m.startDateTime) || '-') + '</dd></div>' +
          (m.actionRequiredByDateTime ? '<div><dt>Act By</dt><dd class="' + (isPast(m.actionRequiredByDateTime) ? 'mc-past' : 'mc-actby') + '">' + esc(fmtDate(m.actionRequiredByDateTime)) + '</dd></div>' : '') +
          roadmapHtml +
        '</dl>' +
        '<div class="mc-detail-body">' + bodyHtml + '</div>' +
      '</div>';

    mainArea.classList.add('has-detail');

    // For the rich HTML body, links/numbers are already inside markup, so make
    // roadmap mentions clickable via a safe text-node pass.
    if (m.bodyHtml) {
      linkifyRoadmapInElement(detailEl.querySelector('.mc-detail-body'));
    }

    var closeBtn = document.getElementById('mc-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        activeId = null;
        renderTable();
        renderDetail(null);
        try { history.replaceState(null, '', location.origin + location.pathname); } catch (e) { /* no-op */ }
      });
    }

    var copyBtn = document.getElementById('mc-copy-link');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        copyToClipboard(shareUrlFor(m.id))
          .then(function () { flashActionButton(copyBtn, 'Link copied'); })
          .catch(function () { flashActionButton(copyBtn, 'Copy failed'); });
      });
    }

    var shareBtn = document.getElementById('mc-share');
    if (shareBtn) {
      shareBtn.addEventListener('click', function () {
        var url = shareUrlFor(m.id);
        if (navigator.share) {
          navigator.share({ title: m.title, text: m.id + ' · ' + m.title, url: url })
            .catch(function () { /* user cancelled or share failed */ });
        } else {
          copyToClipboard(url)
            .then(function () { flashActionButton(shareBtn, 'Link copied'); })
            .catch(function () { flashActionButton(shareBtn, 'Copy failed'); });
        }
      });
    }

    var expandBtn = document.getElementById('mc-expand');
    if (expandBtn) {
      syncExpandBtn(expandBtn);
      expandBtn.addEventListener('click', function () {
        var expanded = mainArea.classList.toggle('is-expanded');
        if (expanded) {
          mainArea.style.setProperty('--mc-detail-w', '82%');
        } else {
          mainArea.style.setProperty('--mc-detail-w', getStoredDetailWidth());
        }
        syncExpandBtn(expandBtn);
      });
    }
  }

  // Keep the expand button's pressed state/label in sync with the layout.
  function syncExpandBtn(btn) {
    var expanded = mainArea.classList.contains('is-expanded');
    btn.setAttribute('aria-pressed', String(expanded));
    btn.setAttribute('aria-label', expanded ? 'Restore reading pane' : 'Expand reading pane');
  }

  function selectMessage(id) {
    activeId = id;
    var m = allMessages.find(function (x) { return x.id === id; });
    renderTable();
    renderDetail(m || null);
    if (id) {
      try { history.replaceState(null, '', shareUrlFor(id)); } catch (e) { /* no-op */ }
    }
  }

  function renderSummary(totals) {
    if (!summaryEl || !totals) return;
    var dotCls = totals.actionRequired > 0 ? 'mc-sum-dot warn' : 'mc-sum-dot ok';
    var parts = [];
    if (totals.actionRequired > 0) parts.push(totals.actionRequired + ' action required');
    if (totals.planForChange)      parts.push(totals.planForChange + ' plan for change');
    summaryEl.innerHTML =
      '<span class="' + dotCls + '"></span>' +
      '<div>' +
        '<strong>' + esc(totals.total + ' message' + (totals.total !== 1 ? 's' : '')) + '</strong>' +
        '<span>' + esc(parts.join(' · ')) + '</span>' +
      '</div>';
  }

  function load() {
    lookedUpId = '';
    if (updatedEl) updatedEl.textContent = 'Refreshing…';
    fetch(MC_ENDPOINT)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data.ok) {
          if (tbody) tbody.innerHTML = '<tr><td colspan="7" class="mc-empty-row" style="color:#ffb2a1">' +
            '<strong>' + esc(data.error || 'Failed to load') + '</strong>' +
            (data.detail && data.detail.indexOf('403') !== -1 ? '<br><small>Azure app needs ServiceMessage.Read.All permission.</small>' : '') +
            '</td></tr>';
          if (updatedEl) updatedEl.textContent = 'Error loading';
          return;
        }
        allMessages = data.messages || [];
        renderFilterDropdowns(allMessages);
        renderSummary(data.totals);
        if (updatedEl) updatedEl.textContent = 'Updated ' + new Date().toLocaleTimeString();
        renderTable();
        if (activeId) {
          var m = allMessages.find(function (x) { return x.id === activeId; });
          renderDetail(m || null);
        } else {
          openFromUrl();
        }
      })
      .catch(function () {
        if (tbody) tbody.innerHTML = '<tr><td colspan="7" class="mc-empty-row" style="color:#ffb2a1">Could not connect to Message Center.</td></tr>';
        if (updatedEl) updatedEl.textContent = 'Failed';
      });
  }

  // Open a message automatically when the page is loaded with ?id=MC###### so
  // shared/copied links land directly on that notification.
  function openFromUrl() {
    var wanted = '';
    try { wanted = String(new URLSearchParams(location.search).get('id') || '').trim().toUpperCase(); }
    catch (e) { return; }
    if (!/^MC\d+$/.test(wanted)) return;

    var existing = allMessages.find(function (m) { return String(m.id || '').toUpperCase() === wanted; });
    if (existing) { selectMessage(existing.id); return; }

    fetch(MC_ENDPOINT + '?id=' + encodeURIComponent(wanted))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.ok || !Array.isArray(data.messages)) return;
        allMessages = data.messages;
        renderFilterDropdowns(allMessages);
        renderSummary(data.totals);
        renderTable();
        var found = allMessages.find(function (m) { return String(m.id || '').toUpperCase() === wanted; });
        if (found) selectMessage(found.id);
      })
      .catch(function () { /* ignore deep-link lookup failures */ });
  }

  function maybeLookupMessageId() {
    var wanted = String(searchQuery || '').trim().toUpperCase();
    if (!/^MC\d+$/.test(wanted)) return;
    if (lookedUpId === wanted) return;
    if (allMessages.some(function (m) { return String(m.id || '').toUpperCase() === wanted; })) {
      lookedUpId = wanted;
      return;
    }

    fetch(MC_ENDPOINT + '?id=' + encodeURIComponent(wanted))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.ok || !Array.isArray(data.messages)) return;
        allMessages = data.messages;
        lookedUpId = wanted;
        renderFilterDropdowns(allMessages);
        renderSummary(data.totals);
        renderTable();
      })
      .catch(function () {
        // Keep current table state if lookup fails.
      });
  }

  function scheduleRefresh() {
    if (timer) clearTimeout(timer);
    if (autoOn) timer = setTimeout(function () { load(); scheduleRefresh(); }, REFRESH_MS);
  }

  // Drag-to-resize the reading pane (and keyboard support on the divider).
  function setupResizer() {
    var resizer = document.getElementById('mc-resizer');
    if (!resizer || !mainArea) return;

    // Apply any previously saved width.
    mainArea.style.setProperty('--mc-detail-w', getStoredDetailWidth());

    function widthFromClientX(clientX) {
      var rect = mainArea.getBoundingClientRect();
      if (rect.width <= 0) return null;
      var pct = ((rect.right - clientX) / rect.width) * 100;
      return clampPct(pct);
    }

    function applyPct(pct) {
      var value = pct.toFixed(1) + '%';
      mainArea.classList.remove('is-expanded');
      mainArea.style.setProperty('--mc-detail-w', value);
      storeDetailWidth(value);
      var expandBtn = document.getElementById('mc-expand');
      if (expandBtn) syncExpandBtn(expandBtn);
    }

    function onPointerMove(e) {
      var pct = widthFromClientX(e.clientX);
      if (pct != null) {
        mainArea.style.setProperty('--mc-detail-w', pct.toFixed(1) + '%');
      }
    }

    function onPointerUp(e) {
      resizer.classList.remove('is-dragging');
      mainArea.classList.remove('is-resizing');
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerup', onPointerUp);
      var pct = widthFromClientX(e.clientX);
      if (pct != null) applyPct(pct);
    }

    resizer.addEventListener('pointerdown', function (e) {
      if (!mainArea.classList.contains('has-detail')) return;
      e.preventDefault();
      resizer.classList.add('is-dragging');
      mainArea.classList.add('is-resizing');
      window.addEventListener('pointermove', onPointerMove);
      window.addEventListener('pointerup', onPointerUp);
    });

    // Keyboard: arrow keys nudge the divider by 4% steps.
    resizer.addEventListener('keydown', function (e) {
      if (!mainArea.classList.contains('has-detail')) return;
      var current = parseFloat(getStoredDetailWidth()) || 48;
      if (e.key === 'ArrowLeft')  { applyPct(clampPct(current + 4)); e.preventDefault(); }
      if (e.key === 'ArrowRight') { applyPct(clampPct(current - 4)); e.preventDefault(); }
    });

    // Double-click the divider to reset to the default width.
    resizer.addEventListener('dblclick', function () { applyPct(48); });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var refreshBtn = document.getElementById('mc-refresh');
    var autoBtn    = document.getElementById('mc-auto-refresh');
    var catBtns    = root.querySelectorAll('[data-mc-cat]');
    var svcBtn     = document.getElementById('mc-svc-btn');
    var tagBtn     = document.getElementById('mc-tag-btn');
    var svcDd      = document.getElementById('mc-svc-dropdown');
    var tagDd      = document.getElementById('mc-tag-dropdown');

    if (refreshBtn) refreshBtn.addEventListener('click', function () { load(); scheduleRefresh(); });

    if (autoBtn) {
      autoBtn.addEventListener('click', function () {
        autoOn = !autoOn;
        autoBtn.setAttribute('aria-pressed', String(autoOn));
        autoBtn.textContent = autoOn ? 'Auto refresh on' : 'Auto refresh off';
        scheduleRefresh();
      });
    }

    catBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        filterCat = btn.getAttribute('data-mc-cat') || 'all';
        catBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        renderTable();
      });
    });

    // Custom dropdown toggle
    function toggleDropdown(dd, btn) {
      var isOpen = dd.classList.contains('open');
      document.querySelectorAll('.mc-dropdown.open').forEach(function (d) {
        d.classList.remove('open');
        d.querySelector('.mc-dropdown-btn').setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        dd.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      }
    }
    if (svcBtn && svcDd) svcBtn.addEventListener('click', function (e) { e.stopPropagation(); toggleDropdown(svcDd, svcBtn); });
    if (tagBtn && tagDd) tagBtn.addEventListener('click', function (e) { e.stopPropagation(); toggleDropdown(tagDd, tagBtn); });

    // Close dropdowns on outside click
    document.addEventListener('click', function () {
      document.querySelectorAll('.mc-dropdown.open').forEach(function (d) {
        d.classList.remove('open');
        d.querySelector('.mc-dropdown-btn').setAttribute('aria-expanded', 'false');
      });
    });

    if (searchEl) searchEl.addEventListener('input', function () {
      searchQuery = searchEl.value.trim();
      renderTable();
      maybeLookupMessageId();
    });

    setupResizer();
    load();
    scheduleRefresh();
  });
}());
