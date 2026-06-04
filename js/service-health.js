(function () {
  'use strict';

  var HEALTH_ENDPOINT = 'https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev/m365/service-health';
  var root = document.getElementById('m365-health');
  if (!root) return;

  var buttons = root.querySelectorAll('[data-health-region]');
  var serviceList = document.getElementById('m365-health-services');
  var issueList = document.getElementById('m365-health-issues');
  var summary = document.getElementById('m365-health-summary');
  var updated = document.getElementById('m365-health-updated');
  var refresh = document.getElementById('m365-health-refresh');
  var activeRegion = root.getAttribute('data-default-region') || 'global';
  var controller = null;

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"']/g, function (char) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char] || char;
    });
  }

  function statusLabel(status) {
    var text = String(status || '').replace(/([a-z])([A-Z])/g, '$1 $2');
    if (status === 'NoRegionalMatch') return 'No regional issue match';
    if (status === 'IssueReported') return 'Issue reported';
    return text || 'Unknown';
  }

  function statusClass(status, count) {
    var value = String(status || '').toLowerCase();
    if (count > 0 || value.includes('degradation') || value.includes('interruption') || value.includes('issue')) return 'is-warning';
    if (value.includes('restored') || value.includes('operational') || value.includes('noregionalmatch')) return 'is-healthy';
    return 'is-neutral';
  }

  function formatDate(value) {
    if (!value) return 'Not checked yet';
    var date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
  }

  function setLoading() {
    root.classList.add('is-loading');
    if (summary) summary.innerHTML = '<span class="mh-dot is-neutral"></span><strong>Checking Microsoft 365 health...</strong>';
    if (serviceList) serviceList.innerHTML = '<li class="mh-empty">Loading service status...</li>';
    if (issueList) issueList.innerHTML = '<li class="mh-empty">Loading active issues...</li>';
  }

  function renderError(data) {
    root.classList.remove('is-loading');
    var message = data && data.configured === false
      ? 'Connect Microsoft Graph app secrets to enable live tenant service health.'
      : 'Service health is temporarily unavailable.';
    if (summary) summary.innerHTML = '<span class="mh-dot is-neutral"></span><strong>' + escapeHtml(message) + '</strong>';
    if (serviceList) serviceList.innerHTML = '<li class="mh-empty">Official Microsoft Graph data will appear here after configuration.</li>';
    if (issueList) issueList.innerHTML = '<li class="mh-empty">No live issue data loaded.</li>';
    if (updated) updated.textContent = 'Not connected';
  }

  function render(data) {
    root.classList.remove('is-loading');
    var totals = data.totals || {};
    var issues = Array.isArray(data.issues) ? data.issues : [];
    var services = Array.isArray(data.services) ? data.services : [];
    var issueText = totals.matchingIssues === 1 ? '1 active issue' : (totals.matchingIssues || 0) + ' active issues';
    var mode = data.regionMode === 'text-match' ? 'regional signal' : 'tenant view';

    if (summary) {
      summary.innerHTML = '<span class="mh-dot ' + (totals.matchingIssues > 0 ? 'is-warning' : 'is-healthy') + '"></span>' +
        '<strong>' + escapeHtml(issueText) + '</strong><span>' + escapeHtml(mode) + '</span>';
    }

    if (updated) updated.textContent = 'Last checked ' + formatDate(data.fetchedAt);

    if (serviceList) {
      var visibleServices = services.filter(function (service) {
        return service.issueCount > 0 || service.status !== 'NoRegionalMatch';
      }).slice(0, 10);
      if (!visibleServices.length) visibleServices = services.slice(0, 8);
      serviceList.innerHTML = visibleServices.map(function (service) {
        var cls = statusClass(service.status, service.issueCount);
        var counts = [];
        if (service.incidents) counts.push(service.incidents + ' incident' + (service.incidents === 1 ? '' : 's'));
        if (service.advisories) counts.push(service.advisories + ' advisories');
        return '<li class="mh-service-row">' +
          '<span class="mh-service-name">' + escapeHtml(service.service) + '</span>' +
          '<span class="mh-service-status ' + cls + '"><span class="mh-dot ' + cls + '"></span>' +
          escapeHtml(counts.length ? counts.join(', ') : statusLabel(service.status)) + '</span>' +
          '</li>';
      }).join('');
    }

    if (issueList) {
      if (!issues.length) {
        issueList.innerHTML = '<li class="mh-empty">No active issues matched this region.</li>';
      } else {
        issueList.innerHTML = issues.slice(0, 6).map(function (issue) {
          return '<li class="mh-issue-card">' +
            '<div class="mh-issue-meta"><span>' + escapeHtml(issue.classification) + '</span><span>' + escapeHtml(issue.service) + '</span></div>' +
            '<strong>' + escapeHtml(issue.title) + '</strong>' +
            (issue.impact ? '<p>' + escapeHtml(issue.impact) + '</p>' : '') +
            '<time>' + escapeHtml(formatDate(issue.lastModifiedDateTime)) + '</time>' +
            '</li>';
        }).join('');
      }
    }
  }

  function load(region) {
    activeRegion = region || activeRegion;
    buttons.forEach(function (button) {
      button.classList.toggle('active', button.getAttribute('data-health-region') === activeRegion);
    });
    if (controller) controller.abort();
    controller = new AbortController();
    setLoading();
    fetch(HEALTH_ENDPOINT + '?region=' + encodeURIComponent(activeRegion), {
      cache: 'no-store',
      signal: controller.signal
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) throw data;
          return data;
        });
      })
      .then(render)
      .catch(function (err) {
        if (err && err.name === 'AbortError') return;
        renderError(err || {});
      });
  }

  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      load(button.getAttribute('data-health-region'));
    });
  });

  if (refresh) {
    refresh.addEventListener('click', function () { load(activeRegion); });
  }

  load(activeRegion);
})();
