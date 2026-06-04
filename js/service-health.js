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
  var activeService = 'all';
  var activeClass = 'all';
  var currentData = null;
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
    return text ? text.charAt(0).toUpperCase() + text.slice(1) : 'Unknown';
  }

  function plural(count, singular, pluralText) {
    return count + ' ' + (count === 1 ? singular : pluralText);
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

  function slug(value) {
    return String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'service';
  }

  function classificationKey(value) {
    return String(value || '').toLowerCase() === 'incident' ? 'incident' : 'advisory';
  }

  function filterIssues(issues) {
    return issues.filter(function (issue) {
      var serviceMatch = activeService === 'all' || slug(issue.service) === activeService;
      var classMatch = activeClass === 'all' || classificationKey(issue.classification) === activeClass;
      return serviceMatch && classMatch;
    });
  }

  function renderIssueDetails(issue) {
    var rows = [];
    if (issue.id) rows.push(['Issue ID', issue.id]);
    if (issue.featureGroup) rows.push(['Feature group', issue.featureGroup]);
    if (issue.feature) rows.push(['Feature', issue.feature]);
    if (issue.startDateTime) rows.push(['Started', formatDate(issue.startDateTime)]);
    if (issue.endDateTime) rows.push(['Ended', formatDate(issue.endDateTime)]);

    var html = rows.length ? '<dl class="mh-issue-facts">' + rows.map(function (row) {
      return '<div><dt>' + escapeHtml(row[0]) + '</dt><dd>' + escapeHtml(row[1]) + '</dd></div>';
    }).join('') + '</dl>' : '';

    var details = Array.isArray(issue.details) ? issue.details : [];
    if (details.length) {
      html += '<div class="mh-issue-section">' + details.map(function (detail) {
        return '<div class="mh-issue-detail">' +
          (detail.name ? '<strong>' + escapeHtml(detail.name) + '</strong>' : '') +
          (detail.value ? '<p>' + escapeHtml(detail.value) + '</p>' : '') +
          '</div>';
      }).join('') + '</div>';
    }

    var posts = Array.isArray(issue.posts) ? issue.posts : [];
    if (posts.length) {
      html += '<div class="mh-issue-section mh-issue-posts">' + posts.map(function (post) {
        return '<p>' + escapeHtml(post) + '</p>';
      }).join('') + '</div>';
    }

    return html;
  }

  function setLoading() {
    root.classList.add('is-loading');
    activeService = 'all';
    activeClass = 'all';
    if (summary) summary.innerHTML = '<span class="mh-dot is-neutral"></span><strong>Checking Microsoft 365 health...</strong>';
    if (serviceList) serviceList.innerHTML = '<li class="mh-empty">Loading service status...</li>';
    if (issueList) issueList.innerHTML = '<li class="mh-empty">Loading active issues...</li>';
  }

  function renderError(data) {
    root.classList.remove('is-loading');
    var isMissingConfig = data && data.configured === false;
    var message = isMissingConfig
      ? 'Microsoft Graph service health is not connected.'
      : 'Microsoft Graph service health could not be loaded.';
    var detail = isMissingConfig
      ? 'Add the M365_HEALTH_TENANT_ID, M365_HEALTH_CLIENT_ID, and M365_HEALTH_CLIENT_SECRET Worker secrets with ServiceHealth.Read.All admin consent.'
      : (data && (data.detail || data.error)) || 'Check the Worker logs and Microsoft Graph app permissions.';
    if (summary) {
      summary.innerHTML = '<span class="mh-dot is-neutral"></span><strong>' + escapeHtml(message) + '</strong>';
    }
    if (serviceList) {
      serviceList.innerHTML = '<li class="mh-empty">Live service rows will appear after Microsoft Graph is connected.</li>';
    }
    if (issueList) {
      issueList.innerHTML = '<li class="mh-empty">' + escapeHtml(detail) + '</li>';
    }
    if (updated) updated.textContent = 'Not connected';
  }

  function renderIssues(issues, totals) {
    if (!issueList) return;

    var filtered = filterIssues(issues);
    var selectedService = activeService === 'all' ? 'All services' : (filtered[0] && filtered[0].service) || 'Selected service';
    var selectedClass = activeClass === 'all' ? 'All types' : (activeClass === 'incident' ? 'Incidents' : 'Advisories');
    var toolbar = '<div class="mh-issue-filter"><span>' + escapeHtml(selectedService + ' · ' + selectedClass) + '</span>' +
      (activeService !== 'all' || activeClass !== 'all' ? '<button type="button" data-health-clear>Clear</button>' : '') +
      '</div>';

    if (!filtered.length) {
      issueList.innerHTML = '<li class="mh-empty">' + toolbar + '<span>No active issues matched this selection.</span></li>';
      return;
    }

    issueList.innerHTML = '<li class="mh-issue-tools">' + toolbar + '</li>' + filtered.slice(0, 8).map(function (issue, index) {
      var detailHtml = renderIssueDetails(issue);
      return '<li class="mh-issue-card">' +
        '<details' + (index === 0 ? ' open' : '') + '>' +
        '<summary>' +
        '<span class="mh-issue-meta"><span>' + escapeHtml(issue.classification || 'Issue') + '</span><span>' + escapeHtml(issue.status || 'Active') + '</span><span>' + escapeHtml(issue.service) + '</span></span>' +
        '<strong>' + escapeHtml(issue.title) + '</strong>' +
        (issue.impact ? '<p>' + escapeHtml(issue.impact) + '</p>' : '') +
        '<time>' + escapeHtml(formatDate(issue.lastModifiedDateTime)) + '</time>' +
        '</summary>' +
        (detailHtml ? '<div class="mh-issue-body">' + detailHtml + '</div>' : '<div class="mh-issue-body"><p>No additional Microsoft Graph details are available for this issue.</p></div>') +
        '</details>' +
        '</li>';
    }).join('');

    var clear = issueList.querySelector('[data-health-clear]');
    if (clear) {
      clear.addEventListener('click', function () {
        activeService = 'all';
        activeClass = 'all';
        render(currentData);
      });
    }
  }

  function render(data) {
    if (!data) return;
    currentData = data;
    root.classList.remove('is-loading');
    var totals = data.totals || {};
    var issues = Array.isArray(data.issues) ? data.issues : [];
    var services = Array.isArray(data.services) ? data.services : [];
    var matchingIssues = totals.matchingIssues || 0;
    var incidents = totals.incidents || 0;
    var advisories = totals.advisories || 0;
    var issueText = matchingIssues === 1 ? '1 active issue' : matchingIssues + ' active issues';
    var mode = data.regionMode === 'text-match' ? 'regional signal' : 'tenant view';

    if (summary) {
      summary.innerHTML = '<span class="mh-dot ' + (matchingIssues > 0 ? 'is-warning' : 'is-healthy') + '"></span>' +
        '<strong>' + escapeHtml(issueText) + '</strong><span>' +
        escapeHtml(incidents + ' incidents/outages, ' + advisories + ' advisories · ' + mode) + '</span>';
    }

    if (updated) updated.textContent = 'Last checked ' + formatDate(data.fetchedAt);

    if (serviceList) {
      var visibleServices = services.filter(function (service) {
        return service.issueCount > 0 || service.status !== 'NoRegionalMatch';
      }).slice(0, 10);
      if (!visibleServices.length) visibleServices = services.slice(0, 8);
      serviceList.innerHTML = visibleServices.map(function (service) {
        var cls = statusClass(service.status, service.issueCount);
        var serviceSlug = slug(service.service);
        var isActive = activeService === serviceSlug;
        var controls = '';
        if (service.incidents) controls += '<button type="button" class="mh-count-pill is-incident" data-health-service="' + escapeHtml(serviceSlug) + '" data-health-class="incident">' + escapeHtml(plural(service.incidents, 'incident', 'incidents')) + '</button>';
        if (service.advisories) controls += '<button type="button" class="mh-count-pill is-advisory" data-health-service="' + escapeHtml(serviceSlug) + '" data-health-class="advisory">' + escapeHtml(plural(service.advisories, 'advisory', 'advisories')) + '</button>';
        return '<li class="mh-service-row' + (isActive ? ' is-selected' : '') + '">' +
          '<span class="mh-service-name">' + escapeHtml(service.service) + '</span>' +
          '<span class="mh-service-actions">' + (controls || '<button type="button" class="mh-service-status ' + cls + '" data-health-service="' + escapeHtml(serviceSlug) + '" data-health-class="all"><span class="mh-dot ' + cls + '"></span>' + escapeHtml(statusLabel(service.status)) + '</button>') + '</span>' +
          '</li>';
      }).join('');

      serviceList.querySelectorAll('[data-health-service]').forEach(function (control) {
        control.addEventListener('click', function () {
          activeService = control.getAttribute('data-health-service') || 'all';
          activeClass = control.getAttribute('data-health-class') || 'all';
          render(currentData);
        });
      });
    }

    renderIssues(issues, totals);
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
