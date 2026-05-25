(function () {
  'use strict';

  var API_BASE = 'https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev';
  var TOKEN_KEY = 'ocCommentAdminToken';
  var tokenInput = document.getElementById('adminToken');
  var statusEl = document.getElementById('status');
  var listEl = document.getElementById('commentList');

  tokenInput.value = localStorage.getItem(TOKEN_KEY) || '';
  document.getElementById('saveToken').addEventListener('click', function () {
    localStorage.setItem(TOKEN_KEY, tokenInput.value.trim());
    loadPending();
  });

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"]/g, function (char) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char];
    });
  }

  async function request(path, options) {
    var token = localStorage.getItem(TOKEN_KEY) || '';
    options = options || {};
    var response = await fetch(API_BASE + path, Object.assign({}, options, {
      headers: Object.assign({ Authorization: 'Bearer ' + token }, options.headers || {})
    }));
    var data = await response.json().catch(function () { return {}; });
    if (!response.ok) throw new Error(data.error || 'Request failed');
    return data;
  }

  async function moderate(id, action) {
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
          '<div class="comment-meta"><strong>' + escapeHtml(comment.display_name) + '</strong><span>' + escapeHtml(comment.slug) + '</span></div>' +
          '<div class="comment-body">' + escapeHtml(comment.body) + '</div>' +
          '<div class="comment-actions">' +
          '<button data-action="approve" data-id="' + comment.id + '">Approve</button>' +
          '<button class="reject" data-action="reject" data-id="' + comment.id + '">Reject</button>' +
          '</div>' +
          '</article>';
      }).join('');
    } catch (error) {
      statusEl.textContent = error.message || 'Could not load comments.';
    }
  }

  listEl.addEventListener('click', function (event) {
    var button = event.target.closest('button[data-action]');
    if (!button) return;
    moderate(Number(button.dataset.id), button.dataset.action);
  });

  if (tokenInput.value) loadPending();
})();
