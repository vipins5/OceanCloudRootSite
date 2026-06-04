(function () {
  'use strict';

  var MC_ENDPOINT = 'https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev/m365/message-center';
  var REFRESH_MS = 15 * 60 * 1000;

  var root        = document.getElementById('mc-shell');
  if (!root) return;

  var listEl      = document.getElementById('mc-list');
  var detailEl    = document.getElementById('mc-detail');
  var summaryEl   = document.getElementById('mc-summary');
  var updatedEl   = document.getElementById('mc-updated');
  var searchEl    = document.getElementById('mc-search');
  var countEl     = document.getElementById('mc-count');

  var allMessages  = [];
  var activeId     = null;
  var filterCat    = 'all';
  var filterSvc    = 'all';
  var filterTag    = 'all';
  var searchQuery  = '';
  var autoOn       = true;
  var timer        = null;

  // ── Category config ──────────────────────────────────────────────────────────
  var CAT_LABELS = {
    stayInformed:      'Stay Informed',
    planForChange:     'Plan for Change',
    preventOrFixIssue: 'Action Required',
  };
  var CAT_CLASS = {
    stayInformed:      'mc-cat-info',
    planForChange:     'mc-cat-plan',
    preventOrFixIssue: 'mc-cat-action',
  };

  // ── Tag colours ──────────────────────────────────────────────────────────────
  function tagClass(tag) {
    var t = (tag || '').toLowerCase();
    if (t.includes('new feature'))   return 'mc-tag-feature';
    if (t.includes('user impact'))   return 'mc-tag-user';
    if (t.includes('admin impact'))  return 'mc-tag-admin';
    if (t.includes('major change'))  return 'mc-tag-major';
    return 'mc-tag-default';
  }

  // ── Date helpers ─────────────────────────────────────────────────────────────
  function fmtDate(iso) {
    if (!iso) return '';
    try {
      return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch (e) { return iso.slice(0, 10); }
  }
  function fmtDateTime(iso) {
    if (!iso) return '';
    try {
      return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
    } catch (e) { return iso; }
  }
  function isPast(iso) {
    return iso && new Date(iso) < new Date();
  }

  // ── Escape ───────────────────────────────────────────────────────────────────
  function esc(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // ── Filtered messages ────────────────────────────────────────────────────────
  function filtered() {
    return allMessages.filter(function (m) {
      if (filterCat !== 'all' && m.category !== filterCat) return false;
      if (filterSvc !== 'all' && !m.services.includes(filterSvc)) return false;
      if (filterTag !== 'all' && !m.tags.some(function (t) { return t === filterTag; })) return false;
      if (searchQuery) {
        var q = searchQuery.toLowerCase();
        if (!m.title.toLowerCase().includes(q) &&
            !m.body.toLowerCase().includes(q) &&
            !m.services.join(' ').toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }

  // ── Build service/tag filter options ─────────────────────────────────────────
  function buildFilters(messages) {
    var svcs = {}, tags = {};
    messages.forEach(function (m) {
      m.services.forEach(function (s) { svcs[s] = true; });
      m.tags.forEach(function (t) { tags[t] = true; });
    });
    return { services: Object.keys(svcs).sort(), tags: Object.keys(tags).sort() };
  }

  function renderFilterBar(messages) {
    var opts = buildFilters(messages);
    var svcEl = document.getElementById('mc-filter-svc');
    var tagEl = document.getElementById('mc-filter-tag');
    if (!svcEl || !tagEl) return;

    svcEl.innerHTML = '<option value="all">All Services</option>' +
      opts.services.map(function (s) {
        return '<option value="' + esc(s) + '"' + (filterSvc === s ? ' selected' : '') + '>' + esc(s) + '</option>';
      }).join('');

    tagEl.innerHTML = '<option value="all">All Tags</option>' +
      opts.tags.map(function (t) {
        return '<option value="' + esc(t) + '"' + (filterTag === t ? ' selected' : '') + '>' + esc(t) + '</option>';
      }).join('');
  }

  // ── Render message list ───────────────────────────────────────────────────────
  function renderList() {
    var msgs = filtered();
    if (countEl) countEl.textContent = msgs.length + ' message' + (msgs.length !== 1 ? 's' : '');

    if (!msgs.length) {
      listEl.innerHTML = '<li class="mc-empty"><span>No messages match the current filters.</span></li>';
      return;
    }

    listEl.innerHTML = msgs.map(function (m) {
      var isActive = m.id === activeId;
      var actBy    = m.actionRequiredByDateTime;
      var catCls   = CAT_CLASS[m.category] || 'mc-cat-info';
      var tagHtml  = m.tags.slice(0, 3).map(function (t) {
        return '<span class="mc-tag ' + tagClass(t) + '">' + esc(t) + '</span>';
      }).join('');

      return '<li>' +
        '<button class="mc-row' + (isActive ? ' is-active' : '') + '" data-id="' + esc(m.id) + '">' +
          '<div class="mc-row-top">' +
            '<span class="mc-row-cat ' + catCls + '">' + esc(CAT_LABELS[m.category] || m.category) + '</span>' +
            (actBy && !isPast(actBy) ? '<span class="mc-act-badge">Act by ' + esc(fmtDate(actBy)) + '</span>' : '') +
          '</div>' +
          '<strong class="mc-row-title">' + esc(m.title) + '</strong>' +
          '<div class="mc-row-meta">' +
            '<span class="mc-row-svc">' + esc(m.services.slice(0, 2).join(', ')) + '</span>' +
            '<span class="mc-row-date">' + esc(fmtDate(m.lastModifiedDateTime)) + '</span>' +
          '</div>' +
          (tagHtml ? '<div class="mc-row-tags">' + tagHtml + '</div>' : '') +
        '</button>' +
      '</li>';
    }).join('');

    listEl.querySelectorAll('[data-id]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        selectMessage(btn.getAttribute('data-id'));
      });
    });
  }

  // ── Render detail pane ───────────────────────────────────────────────────────
  function renderDetail(m) {
    if (!m) {
      detailEl.innerHTML = '<div class="mc-detail-empty"><p>Select a message to read it.</p></div>';
      return;
    }

    var catCls  = CAT_CLASS[m.category] || 'mc-cat-info';
    var tagHtml = m.tags.map(function (t) {
      return '<span class="mc-tag ' + tagClass(t) + '">' + esc(t) + '</span>';
    }).join('');

    var bodyHtml = m.body
      ? m.body.split('\n').filter(function (l) { return l.trim(); }).map(function (l) {
          return '<p>' + esc(l) + '</p>';
        }).join('')
      : '<p class="mc-no-body">No body content available.</p>';

    detailEl.innerHTML =
      '<div class="mc-detail-head">' +
        '<div>' +
          '<div class="mc-detail-cats">' +
            '<span class="mc-row-cat ' + catCls + '">' + esc(CAT_LABELS[m.category] || m.category) + '</span>' +
            (m.isMajorChange ? '<span class="mc-tag mc-tag-major">Major Change</span>' : '') +
          '</div>' +
          '<h2 class="mc-detail-title">' + esc(m.title) + '</h2>' +
          (tagHtml ? '<div class="mc-detail-tags">' + tagHtml + '</div>' : '') +
        '</div>' +
        '<button class="mc-close-btn" id="mc-close" aria-label="Close detail">&#x2715;</button>' +
      '</div>' +
      '<div class="mc-detail-layout">' +
        '<div class="mc-detail-body">' + bodyHtml + '</div>' +
        '<div class="mc-detail-side">' +
          '<dl>' +
            '<div><dt>Message ID</dt><dd>' + esc(m.id) + '</dd></div>' +
            '<div><dt>Services</dt><dd>' + esc(m.services.join(', ') || '—') + '</dd></div>' +
            '<div><dt>Last Updated</dt><dd>' + esc(fmtDateTime(m.lastModifiedDateTime) || '—') + '</dd></div>' +
            '<div><dt>Published</dt><dd>' + esc(fmtDate(m.startDateTime) || '—') + '</dd></div>' +
            (m.actionRequiredByDateTime
              ? '<div><dt>Act By</dt><dd class="' + (isPast(m.actionRequiredByDateTime) ? 'mc-past' : 'mc-act-date') + '">' + esc(fmtDate(m.actionRequiredByDateTime)) + '</dd></div>'
              : '') +
          '</dl>' +
        '</div>' +
      '</div>';

    var closeBtn = document.getElementById('mc-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        activeId = null;
        renderList();
        renderDetail(null);
      });
    }
  }

  function selectMessage(id) {
    activeId = id;
    var m = allMessages.find(function (x) { return x.id === id; });
    renderList();
    renderDetail(m || null);
  }

  // ── Render summary pill ───────────────────────────────────────────────────────
  function renderSummary(totals) {
    if (!summaryEl || !totals) return;
    var parts = [totals.total + ' message' + (totals.total !== 1 ? 's' : '')];
    if (totals.actionRequired > 0) {
      parts.push(totals.actionRequired + ' requiring action');
    }
    if (totals.planForChange > 0) {
      parts.push(totals.planForChange + ' change' + (totals.planForChange !== 1 ? 's' : '') + ' planned');
    }
    summaryEl.innerHTML =
      '<span class="mc-sum-dot"></span>' +
      '<div><strong>' + esc(parts[0]) + '</strong>' +
      (parts.length > 1 ? '<span>' + esc(parts.slice(1).join(' · ')) + '</span>' : '') +
      '</div>';
  }

  // ── Fetch & render ────────────────────────────────────────────────────────────
  function load() {
    if (updatedEl) updatedEl.textContent = 'Refreshing…';
    fetch(MC_ENDPOINT)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data.ok) {
          listEl.innerHTML = '<li class="mc-empty"><span>' + esc(data.error || 'Unable to load messages.') + '</span></li>';
          return;
        }
        allMessages = data.messages || [];
        renderFilterBar(allMessages);
        renderSummary(data.totals);
        if (updatedEl) updatedEl.textContent = 'Updated ' + new Date().toLocaleTimeString();
        renderList();
        if (activeId) {
          var m = allMessages.find(function (x) { return x.id === activeId; });
          renderDetail(m || null);
        } else {
          renderDetail(null);
        }
      })
      .catch(function () {
        listEl.innerHTML = '<li class="mc-empty"><span>Could not connect to Message Center.</span></li>';
        if (updatedEl) updatedEl.textContent = 'Failed to refresh';
      });
  }

  function scheduleRefresh() {
    if (timer) clearTimeout(timer);
    if (autoOn) timer = setTimeout(function () { load(); scheduleRefresh(); }, REFRESH_MS);
  }

  // ── Event wiring ──────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    var refreshBtn = document.getElementById('mc-refresh');
    var autoBtn    = document.getElementById('mc-auto-refresh');
    var catBtns    = root.querySelectorAll('[data-mc-cat]');
    var svcEl2     = document.getElementById('mc-filter-svc');
    var tagEl2     = document.getElementById('mc-filter-tag');

    if (refreshBtn) {
      refreshBtn.addEventListener('click', function () { load(); scheduleRefresh(); });
    }

    if (autoBtn) {
      autoBtn.addEventListener('click', function () {
        autoOn = !autoOn;
        autoBtn.setAttribute('aria-pressed', autoOn ? 'true' : 'false');
        autoBtn.textContent = autoOn ? 'Auto refresh on' : 'Auto refresh off';
        scheduleRefresh();
      });
    }

    catBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        filterCat = btn.getAttribute('data-mc-cat') || 'all';
        catBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        renderList();
      });
    });

    if (svcEl2) {
      svcEl2.addEventListener('change', function () { filterSvc = svcEl2.value; renderList(); });
    }
    if (tagEl2) {
      tagEl2.addEventListener('change', function () { filterTag = tagEl2.value; renderList(); });
    }
    if (searchEl) {
      searchEl.addEventListener('input', function () { searchQuery = searchEl.value.trim(); renderList(); });
    }

    load();
    scheduleRefresh();
  });
}());
