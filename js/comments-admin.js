(function () {
  'use strict';

  var API_BASE = 'https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev';
  var TOKEN_KEY = 'ocCommentAdminToken';
  var tokenInput = document.getElementById('adminToken');
  var statusEl = document.getElementById('status');
  var listEl = document.getElementById('commentList');
  var contactStatusEl = document.getElementById('contactStatus');
  var contactListEl = document.getElementById('contactList');

  function getStoredToken() {
    try {
      return localStorage.getItem(TOKEN_KEY) || '';
    } catch (error) {
      return '';
    }
  }

  function setStoredToken(value) {
    try {
      localStorage.setItem(TOKEN_KEY, value);
      return true;
    } catch (error) {
      statusEl.textContent = 'Unable to save the admin token in this browser.';
      return false;
    }
  }

  tokenInput.value = getStoredToken();
  document.getElementById('saveToken').addEventListener('click', function () {
    if (!setStoredToken(tokenInput.value.trim())) return;
    Promise.all([loadPending(), loadContacts()]);
  });

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"]/g, function (char) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char];
    });
  }

  async function request(path, options) {
    var token = getStoredToken();
    options = options || {};
    var response = await fetch(API_BASE + path, Object.assign({}, options, {
      headers: Object.assign({ Authorization: 'Bearer ' + token }, options.headers || {})
    }));
    var data = await response.json().catch(function () { return {}; });
    if (!response.ok) throw new Error(data.error || 'Request failed');
    return data;
  }

  async function moderate(id, action) {
    if (action === 'delete' && !confirm('Delete this comment permanently?')) return;
    await request('/comments/admin/moderate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id, action: action })
    });
    await loadPending();
  }

  async function loadPending() {
    statusEl.textContent = 'Loading pending comments...';
    listEl.innerHTML = '';
    try {
      var data = await request('/comments/admin?status=pending');
      var comments = data.comments || [];
      statusEl.textContent = comments.length ? comments.length + ' pending comment(s).' : 'No pending comments.';
      listEl.innerHTML = comments.map(function (comment) {
        return '<article class="comment-item">' +
          '<div class="comment-meta"><strong>' + escapeHtml(comment.display_name) + '</strong><span>' + escapeHtml(comment.slug) + (comment.parent_id ? ' - reply to #' + comment.parent_id : '') + '</span></div>' +
          '<div class="comment-body">' + escapeHtml(comment.body) + '</div>' +
          '<div class="comment-actions">' +
          '<button data-action="approve" data-id="' + comment.id + '">Approve</button>' +
          '<button class="reject" data-action="reject" data-id="' + comment.id + '">Reject</button>' +
          '<button class="delete" data-action="delete" data-id="' + comment.id + '">Delete</button>' +
          '</div>' +
          '</article>';
      }).join('');
    } catch (error) {
      statusEl.textContent = error.message || 'Could not load comments.';
    }
  }

  async function updateContact(id, status) {
    await request('/contact/admin/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id, status: status })
    });
    await loadContacts();
  }

  async function loadContacts() {
    contactStatusEl.textContent = 'Loading consultation requests...';
    contactListEl.innerHTML = '';
    try {
      var data = await request('/contact/admin?status=new');
      var submissions = data.submissions || [];
      contactStatusEl.textContent = submissions.length ? submissions.length + ' new request(s).' : 'No new consultation requests.';
      contactListEl.innerHTML = submissions.map(function (submission) {
        return '<article class="comment-item">' +
          '<div class="comment-meta"><strong>' + escapeHtml(submission.name) + '</strong><span>' + escapeHtml(submission.created_at) + '</span></div>' +
          '<div class="comment-body"><strong>' + escapeHtml(submission.company) + '</strong> · ' + escapeHtml(submission.service) + ' · ' + escapeHtml(submission.org_size) + '<br>' +
          '<a href="mailto:' + encodeURIComponent(submission.email) + '">' + escapeHtml(submission.email) + '</a><br><br>' + escapeHtml(submission.message) + '</div>' +
          '<div class="comment-actions"><button data-contact-status="read" data-id="' + submission.id + '">Mark read</button>' +
          '<button class="reject" data-contact-status="archived" data-id="' + submission.id + '">Archive</button></div>' +
          '</article>';
      }).join('');
    } catch (error) {
      contactStatusEl.textContent = error.message || 'Could not load consultation requests.';
    }
  }

  listEl.addEventListener('click', function (event) {
    var button = event.target.closest('button[data-action]');
    if (!button) return;
    moderate(Number(button.dataset.id), button.dataset.action);
  });

  contactListEl.addEventListener('click', function (event) {
    var button = event.target.closest('button[data-contact-status]');
    if (!button) return;
    updateContact(Number(button.dataset.id), button.dataset.contactStatus);
  });

  if (tokenInput.value) Promise.all([loadPending(), loadContacts()]);
})();
