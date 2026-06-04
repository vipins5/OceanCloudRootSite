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
  var activeIssueId = '';
  var detailsCompact = localStorage.getItem('m365HealthCompactDetails') === 'true';
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

  function watchedIssues() {
    try {
      return JSON.parse(localStorage.getItem('m365HealthWatchedIssues') || '{}') || {};
    } catch (err) {
      return {};
    }
  }

  function setWatchedIssue(issue, enabled) {
    var watched = watchedIssues();
    if (!issue || !issue.id) return false;
    if (enabled) {
      watched[issue.id] = {
        title: issue.title || issue.id,
        service: issue.service || 'Microsoft 365',
        lastSeen: issue.lastModifiedDateTime || issue.startDateTime || new Date().toISOString()
      };
    } else {
      delete watched[issue.id];
    }
    try {
      localStorage.setItem('m365HealthWatchedIssues', JSON.stringify(watched));
      return true;
    } catch (err) {
      return false;
    }
  }

  function isWatched(issue) {
    return Boolean(issue && issue.id && watchedIssues()[issue.id]);
  }

  function selectedIssueText(issue) {
    var updates = Array.isArray(issue.posts) ? issue.posts.map(function (post) {
      var content = typeof post === 'string' ? post : post.content;
      var created = typeof post === 'string' ? '' : post.createdDateTime;
      return (created ? formatDate(created) + ': ' : '') + (content || '');
    }).filter(Boolean).join('\n\n') : '';

    return [
      issue.title,
      'Issue ID: ' + (issue.id || 'Not provided'),
      'Service: ' + (issue.service || 'Microsoft 365'),
      'Status: ' + statusLabel(issue.status),
      'Type: ' + (issue.classification || 'Advisory'),
      'Start time: ' + formatDate(issue.startDateTime),
      'Last updated: ' + formatDate(issue.lastModifiedDateTime),
      issue.impact ? '\nUser impact:\n' + issue.impact : '',
      updates ? '\nUpdates:\n' + updates : ''
    ].filter(Boolean).join('\n');
  }

  function showActionMessage(message, type) {
    var messageNode = issueList && issueList.querySelector('[data-health-action-message]');
    if (!messageNode) return;
    messageNode.textContent = message;
    messageNode.className = 'mh-action-message ' + (type || '');
  }

  function copyText(value) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(value);
    }
    var textarea = document.createElement('textarea');
    textarea.value = value;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    var copied = document.execCommand('copy');
    document.body.removeChild(textarea);
    return copied ? Promise.resolve() : Promise.reject(new Error('Copy failed'));
  }

  function notifyForIssue(issue) {
    if (!('Notification' in window)) {
      showActionMessage('Browser notifications are not supported here.', 'is-error');
      return;
    }
    if (!issue || !issue.id) {
      showActionMessage('This issue cannot be tracked because Microsoft did not provide an issue ID.', 'is-error');
      return;
    }
    var currentlyWatched = isWatched(issue);
    if (currentlyWatched) {
      setWatchedIssue(issue, false);
      render(currentData);
      showActionMessage('Notifications removed for this issue.', 'is-success');
      return;
    }

    function enableNotification() {
      if (!setWatchedIssue(issue, true)) {
        showActionMessage('Could not save notification preference in this browser.', 'is-error');
        return;
      }
      try {
        new Notification('OceanCloud status notification enabled', {
          body: (issue.service || 'Microsoft 365') + ': ' + (issue.title || issue.id),
          tag: 'oceancloud-status-' + issue.id
        });
      } catch (err) {}
      render(currentData);
      showActionMessage('Notifications enabled for this issue on this browser.', 'is-success');
    }

    if (Notification.permission === 'granted') {
      enableNotification();
      return;
    }
    if (Notification.permission === 'denied') {
      showActionMessage('Notifications are blocked for this browser. Enable them in site settings.', 'is-error');
      return;
    }
    Notification.requestPermission().then(function (permission) {
      if (permission === 'granted') enableNotification();
      else showActionMessage('Notification permission was not granted.', 'is-error');
    });
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

  function issueKey(issue, index) {
    return issue.id || slug(issue.title || 'issue-' + index);
  }

  function findDetail(issue, names) {
    var details = Array.isArray(issue.details) ? issue.details : [];
    var keys = names.map(function (name) { return String(name).toLowerCase(); });
    var match = details.find(function (detail) {
      var name = String(detail.name || '').toLowerCase();
      return keys.some(function (key) { return name.includes(key); });
    });
    return match && match.value ? match.value : '';
  }

  function setDetailsCompact(value) {
    detailsCompact = Boolean(value);
    try {
      localStorage.setItem('m365HealthCompactDetails', detailsCompact ? 'true' : 'false');
    } catch (err) {}
  }

  function renderDetailSection(title, body, className) {
    if (!body) return '';
    return '<section class="mh-detail-section ' + escapeHtml(className || '') + '"><h4>' + escapeHtml(title) + '</h4><p>' + escapeHtml(body) + '</p></section>';
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
        var content = typeof post === 'string' ? post : post.content;
        var created = typeof post === 'string' ? '' : post.createdDateTime;
        return '<p>' + (created ? '<time>' + escapeHtml(formatDate(created)) + '</time>' : '') + escapeHtml(content) + '</p>';
      }).join('') + '</div>';
    }

    return html;
  }

  function renderIssueDetailPane(issue) {
    if (!issue) {
      return '<div class="mh-detail-empty">Select an issue to view Microsoft Graph details.</div>';
    }

    var userImpact = issue.impact || findDetail(issue, ['user impact', 'impact']);
    var moreInfo = findDetail(issue, ['more info', 'more information', 'additional information']);
    var scope = findDetail(issue, ['scope']);
    var rootCause = findDetail(issue, ['root cause']);
    var nextSteps = findDetail(issue, ['next step', 'current status', 'latest update']);
    var fallbackDetails = renderIssueDetails(issue);
    var posts = Array.isArray(issue.posts) ? issue.posts : [];
    var watched = isWatched(issue);

    var updateHtml = posts.length ? '<section class="mh-detail-section mh-detail-updates"><h4>Updates</h4>' + posts.map(function (post) {
      var content = typeof post === 'string' ? post : post.content;
      var created = typeof post === 'string' ? '' : post.createdDateTime;
      return '<article><time>' + escapeHtml(created ? formatDate(created) : formatDate(issue.lastModifiedDateTime)) + '</time><p>' + escapeHtml(content) + '</p></article>';
    }).join('') + '</section>' : '';

    return '<article class="mh-detail-pane' + (detailsCompact ? ' is-compact' : '') + '">' +
      '<header class="mh-detail-head">' +
      '<div><span>' + escapeHtml(issue.classification || 'Issue') + '</span><h3>' + escapeHtml(issue.title) + '</h3></div>' +
      '<div class="mh-detail-actions" aria-label="Issue actions">' +
      '<button type="button" data-health-compact="details" aria-pressed="' + (detailsCompact ? 'true' : 'false') + '">' + (detailsCompact ? 'Show full details' : 'Compact details') + '</button>' +
      '<button type="button" data-health-notify="issue">' + (watched ? 'Notifications on' : 'Notify me') + '</button>' +
      '<button type="button" data-health-copy="text">Copy text</button>' +
      '<button type="button" data-health-copy="link">Copy link</button>' +
      '<span class="mh-action-message" data-health-action-message aria-live="polite"></span>' +
      '</div>' +
      '</header>' +
      '<div class="mh-detail-layout">' +
      '<div class="mh-detail-main">' +
      renderDetailSection('User impact', userImpact, 'is-primary') +
      renderDetailSection('More info', moreInfo) +
      renderDetailSection('Scope of impact', scope) +
      renderDetailSection('Root cause', rootCause) +
      renderDetailSection('Current status', nextSteps) +
      (!moreInfo && !scope && !rootCause && !nextSteps ? '<section class="mh-detail-section"><h4>Microsoft Graph details</h4>' + fallbackDetails + '</section>' : '') +
      updateHtml +
      '</div>' +
      '<aside class="mh-detail-side">' +
      '<dl>' +
      '<div><dt>Issue ID</dt><dd>' + escapeHtml(issue.id || 'Not provided') + '</dd></div>' +
      '<div><dt>Affected service</dt><dd>' + escapeHtml(issue.service || 'Microsoft 365') + '</dd></div>' +
      '<div><dt>Status</dt><dd>' + escapeHtml(statusLabel(issue.status)) + '</dd></div>' +
      '<div><dt>Start time</dt><dd>' + escapeHtml(formatDate(issue.startDateTime)) + '</dd></div>' +
      '<div><dt>Last updated</dt><dd>' + escapeHtml(formatDate(issue.lastModifiedDateTime)) + '</dd></div>' +
      '<div><dt>Issue type</dt><dd>' + escapeHtml(issue.classification || 'Advisory') + '</dd></div>' +
      '</dl>' +
      '</aside>' +
      '</div>' +
      '</article>';
  }

  function setLoading() {
    root.classList.add('is-loading');
    activeService = 'all';
    activeClass = 'all';
    activeIssueId = '';
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

  function renderIssues(issues) {
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

    if (!filtered.some(function (issue, index) { return issueKey(issue, index) === activeIssueId; })) {
      activeIssueId = issueKey(filtered[0], 0);
    }
    var selectedIssue = filtered.find(function (issue, index) { return issueKey(issue, index) === activeIssueId; }) || filtered[0];

    var issueRows = filtered.slice(0, 12).map(function (issue, index) {
      var key = issueKey(issue, index);
      return '<li><button type="button" class="mh-issue-row' + (key === activeIssueId ? ' is-active' : '') + '" data-health-issue="' + escapeHtml(key) + '">' +
        '<span class="mh-issue-type ' + escapeHtml(classificationKey(issue.classification)) + '">' + escapeHtml(issue.classification || 'Issue') + '</span>' +
        '<strong>' + escapeHtml(issue.title) + '</strong>' +
        '<span>' + escapeHtml(issue.service || 'Microsoft 365') + ' · ' + escapeHtml(formatDate(issue.lastModifiedDateTime)) + '</span>' +
        '</button></li>';
    }).join('');

    issueList.innerHTML = '<li class="mh-issue-tools">' + toolbar + '</li>' +
      '<li class="mh-issue-browser"><div class="mh-issue-index"><div class="mh-subtitle">Issue title</div><ul>' + issueRows + '</ul></div>' +
      '<div class="mh-issue-detail-host">' + renderIssueDetailPane(selectedIssue) + '</div></li>';

    var clear = issueList.querySelector('[data-health-clear]');
    if (clear) {
      clear.addEventListener('click', function () {
        activeService = 'all';
        activeClass = 'all';
        activeIssueId = '';
        render(currentData);
      });
    }
    issueList.querySelectorAll('[data-health-issue]').forEach(function (control) {
      control.addEventListener('click', function () {
        activeIssueId = control.getAttribute('data-health-issue') || '';
        render(currentData);
      });
    });
    issueList.querySelectorAll('[data-health-copy]').forEach(function (control) {
      control.addEventListener('click', function () {
        if (!selectedIssue) return;
        var mode = control.getAttribute('data-health-copy');
        var text = mode === 'link'
          ? location.href.split('#')[0] + '#m365-health?issue=' + encodeURIComponent(selectedIssue.id || activeIssueId)
          : selectedIssueText(selectedIssue);
        copyText(text)
          .then(function () { showActionMessage(mode === 'link' ? 'Issue link copied.' : 'Issue details copied.'); })
          .catch(function () { showActionMessage('Copy failed. Your browser may be blocking clipboard access.', 'is-error'); });
      });
    });
    var notify = issueList.querySelector('[data-health-notify]');
    if (notify) {
      notify.addEventListener('click', function () { notifyForIssue(selectedIssue); });
    }
    var compact = issueList.querySelector('[data-health-compact]');
    if (compact) {
      compact.addEventListener('click', function () {
        setDetailsCompact(!detailsCompact);
        render(currentData);
        showActionMessage(detailsCompact ? 'Compact details enabled.' : 'Full details restored.', 'is-success');
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
          activeIssueId = '';
          render(currentData);
        });
      });
    }

    renderIssues(issues);
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
