(function () {
  'use strict';

  var API_BASE = 'https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev';
  var TOKEN_KEY = 'ocCommentToken';
  var config = null;
  var session = { authenticated: false };
  var turnstileToken = '';
  var turnstileWidgetId = null;

  function slug() {
    var part = window.location.pathname.split('/').pop() || '';
    return part.replace(/\.html$/, '');
  }

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"]/g, function (char) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char];
    });
  }

  function tokenFromHash() {
    var match = window.location.hash.match(/oc_comment_token=([^&]+)/);
    if (!match) return;
    localStorage.setItem(TOKEN_KEY, decodeURIComponent(match[1]));
    history.replaceState(null, '', window.location.pathname + window.location.search);
  }

  function authHeaders() {
    var token = localStorage.getItem(TOKEN_KEY) || '';
    return token ? { Authorization: 'Bearer ' + token } : {};
  }

  async function api(path, options) {
    options = options || {};
    var response = await fetch(API_BASE + path, Object.assign({}, options, {
      headers: Object.assign({}, authHeaders(), options.headers || {}),
    }));
    var data = await response.json().catch(function () { return {}; });
    if (!response.ok) throw new Error(data.error || 'Request failed');
    return data;
  }

  function ensureStyles() {
    if (document.querySelector('link[data-oc-comments]')) return;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '../css/comments.css?v=1';
    link.setAttribute('data-oc-comments', 'true');
    document.head.appendChild(link);
  }

  function ensureTurnstileScript() {
    if (!config || !config.turnstileSiteKey || window.turnstile || document.querySelector('script[data-oc-turnstile]')) return;
    var script = document.createElement('script');
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
    script.async = true;
    script.defer = true;
    script.setAttribute('data-oc-turnstile', 'true');
    script.onload = renderTurnstile;
    document.head.appendChild(script);
  }

  function renderTurnstile() {
    var target = document.getElementById('oc-turnstile');
    if (!target || !config || !config.turnstileSiteKey || !window.turnstile || turnstileWidgetId !== null) return;
    turnstileWidgetId = window.turnstile.render(target, {
      sitekey: config.turnstileSiteKey,
      callback: function (token) { turnstileToken = token; },
      'expired-callback': function () { turnstileToken = ''; },
    });
  }

  function resetTurnstile() {
    turnstileToken = '';
    if (window.turnstile && turnstileWidgetId !== null) window.turnstile.reset(turnstileWidgetId);
  }

  function signInUrl() {
    return API_BASE + '/comments/auth/microsoft/start?return_to=' + encodeURIComponent(window.location.href.split('#')[0]);
  }

  function renderShell(root) {
    root.innerHTML = [
      '<section class="oc-comments" aria-labelledby="oc-comments-title">',
      '  <div class="oc-comments-head">',
      '    <p class="oc-comments-label">Discussion</p>',
      '    <h2 id="oc-comments-title">Comments</h2>',
      '    <p>Sign in with a verified Microsoft account to comment. Comments appear only after approval.</p>',
      '  </div>',
      '  <div id="oc-comments-list" class="oc-comments-list"></div>',
      '  <div id="oc-comments-form" class="oc-comments-form"></div>',
      '</section>'
    ].join('');
  }

  function renderComments(items) {
    var list = document.getElementById('oc-comments-list');
    if (!list) return;
    if (!items.length) {
      list.innerHTML = '<p class="oc-comments-empty">No approved comments yet.</p>';
      return;
    }
    list.innerHTML = items.map(function (item) {
      return '<article class="oc-comment">' +
        '<div class="oc-comment-meta"><strong>' + escapeHtml(item.display_name) + '</strong><span>' + escapeHtml(new Date(item.created_at).toLocaleDateString()) + '</span></div>' +
        '<p>' + escapeHtml(item.body).replace(/\n/g, '<br>') + '</p>' +
        '</article>';
    }).join('');
  }

  function renderForm() {
    var target = document.getElementById('oc-comments-form');
    if (!target) return;
    if (!config || !config.providers || !config.providers.microsoft) {
      target.innerHTML = '<p class="oc-comments-note">Comments are being configured.</p>';
      return;
    }
    if (!session.authenticated) {
      target.innerHTML = '<a class="oc-comments-signin" href="' + signInUrl() + '">Sign in with Microsoft to comment</a>';
      return;
    }
    target.innerHTML = [
      '<form id="oc-comment-submit">',
      '  <div class="oc-comments-user">Signed in as <strong>' + escapeHtml(session.user && session.user.name) + '</strong></div>',
      '  <label for="oc-comment-body">Comment</label>',
      '  <textarea id="oc-comment-body" maxlength="2000" rows="5" required placeholder="Add a helpful comment or question..."></textarea>',
      '  <div id="oc-turnstile"></div>',
      '  <button type="submit">Submit for approval</button>',
      '  <button type="button" class="oc-comments-signout" id="oc-comments-signout">Sign out</button>',
      '  <p class="oc-comments-status" id="oc-comments-status"></p>',
      '</form>'
    ].join('');
    ensureTurnstileScript();
    renderTurnstile();

    document.getElementById('oc-comments-signout').addEventListener('click', function () {
      localStorage.removeItem(TOKEN_KEY);
      session = { authenticated: false };
      renderForm();
    });

    document.getElementById('oc-comment-submit').addEventListener('submit', submitComment);
  }

  async function submitComment(event) {
    event.preventDefault();
    var status = document.getElementById('oc-comments-status');
    var body = document.getElementById('oc-comment-body').value.trim();
    if (!body) return;
    if (config.turnstileSiteKey && !turnstileToken) {
      status.textContent = 'Please complete the human verification.';
      return;
    }
    status.textContent = 'Submitting...';
    try {
      await api('/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug: slug(), body: body, turnstileToken: turnstileToken })
      });
      document.getElementById('oc-comment-body').value = '';
      resetTurnstile();
      status.textContent = 'Thanks. Your comment is pending approval.';
    } catch (error) {
      resetTurnstile();
      status.textContent = error.message || 'Could not submit comment.';
    }
  }

  async function init() {
    var wrap = document.querySelector('.article-wrap');
    if (!wrap) return;
    ensureStyles();
    tokenFromHash();
    var root = document.createElement('div');
    root.id = 'oc-comments-root';
    var related = wrap.querySelector('.related-section');
    wrap.insertBefore(root, related || null);
    renderShell(root);
    try {
      config = await api('/comments/config');
      var sessionData = await api('/comments/session');
      session = sessionData;
      var comments = await api('/comments?slug=' + encodeURIComponent(slug()));
      renderComments(comments.comments || []);
      renderForm();
    } catch (error) {
      document.getElementById('oc-comments-form').innerHTML = '<p class="oc-comments-note">Comments are temporarily unavailable.</p>';
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
