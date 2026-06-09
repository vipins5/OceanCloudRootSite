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

  var allMessages  = [];
  var activeId     = null;
  var filterInbox  = 'active';
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

  function relevance(m) {
    if (m.category === 'preventOrFixIssue') return { level: 'High',   dots: 4 };
    if (m.isMajorChange)                    return { level: 'High',   dots: 4 };
    if (m.category === 'planForChange')     return { level: 'Medium', dots: 2 };
    return                                         { level: 'Normal', dots: 1 };
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

  function normalizeSearchText(s) {
    return String(s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  function filtered() {
    return allMessages.filter(function (m) {
      if (filterInbox === 'active'   &&  m.isArchived) return false;
      if (filterInbox === 'archived' && !m.isArchived) return false;
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

    if (!msgs.length) {
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

      return '<tr class="mc-row' + (isActive ? ' is-active' : '') + '" data-id="' + esc(m.id) + '">' +
        '<td class="mc-col-star"><button class="mc-star-btn" type="button" aria-label="Favourite" tabindex="-1">&#9734;</button></td>' +
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

    var bodyHtml = m.body
      ? m.body.split('\n').filter(function (l) { return l.trim(); })
          .map(function (l) { return '<p>' + esc(l) + '</p>'; }).join('')
      : '<p class="mc-dim">No body content.</p>';

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
        '<button class="mc-close-btn" id="mc-close" aria-label="Close">&#x2715;</button>' +
      '</div>' +
      '<div class="mc-detail-scroll">' +
        '<dl class="mc-detail-facts">' +
          '<div><dt>Service</dt><dd>' + esc(m.services.join(', ') || '-') + '</dd></div>' +
          '<div><dt>Last Updated</dt><dd>' + esc(fmtDateTime(m.lastModifiedDateTime) || '-') + '</dd></div>' +
          '<div><dt>Published</dt><dd>' + esc(fmtDate(m.startDateTime) || '-') + '</dd></div>' +
          (m.actionRequiredByDateTime ? '<div><dt>Act By</dt><dd class="' + (isPast(m.actionRequiredByDateTime) ? 'mc-past' : 'mc-actby') + '">' + esc(fmtDate(m.actionRequiredByDateTime)) + '</dd></div>' : '') +
        '</dl>' +
        '<div class="mc-detail-body">' + bodyHtml + '</div>' +
      '</div>';

    mainArea.classList.add('has-detail');

    var closeBtn = document.getElementById('mc-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        activeId = null;
        renderTable();
        renderDetail(null);
      });
    }
  }

  function selectMessage(id) {
    activeId = id;
    var m = allMessages.find(function (x) { return x.id === id; });
    renderTable();
    renderDetail(m || null);
  }

  function renderSummary(totals) {
    if (!summaryEl || !totals) return;
    var dotCls = totals.actionRequired > 0 ? 'mc-sum-dot warn' : 'mc-sum-dot ok';
    var parts = [totals.total + ' total'];
    if (totals.active !== undefined)   parts.push(totals.active + ' inbox');
    if (totals.archived !== undefined) parts.push(totals.archived + ' archived');
    if (totals.actionRequired > 0)     parts.push(totals.actionRequired + ' action required');
    summaryEl.innerHTML =
      '<span class="' + dotCls + '"></span>' +
      '<div>' +
        '<strong>' + esc(totals.total + ' message' + (totals.total !== 1 ? 's' : '')) + '</strong>' +
        '<span>' + esc(parts.slice(1).join(' · ')) + '</span>' +
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
        }
      })
      .catch(function () {
        if (tbody) tbody.innerHTML = '<tr><td colspan="7" class="mc-empty-row" style="color:#ffb2a1">Could not connect to Message Center.</td></tr>';
        if (updatedEl) updatedEl.textContent = 'Failed';
      });
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

    var inboxBtns = root.querySelectorAll('[data-mc-inbox]');
    inboxBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        filterInbox = btn.getAttribute('data-mc-inbox') || 'active';
        inboxBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        renderTable();
      });
    });

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

    load();
    scheduleRefresh();
  });
}());
