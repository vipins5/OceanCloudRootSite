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
    link.href = '../css/comments.css?v=4';
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

  function signInUrl(provider) {
    return API_BASE + '/comments/auth/' + provider + '/start?return_to=' + encodeURIComponent(window.location.href.split('#')[0]);
  }

  function providerLabel(provider) {
    return { microsoft: 'Microsoft', google: 'Google', github: 'GitHub' }[provider] || provider;
  }

  function providerIcon(provider) {
    if (provider === 'microsoft') {
      return '<span class="oc-provider-icon oc-ms-icon" aria-hidden="true"><span></span><span></span><span></span><span></span></span>';
    }
    if (provider === 'google') {
      return '<span class="oc-provider-icon oc-google-icon" aria-hidden="true"><svg viewBox="0 0 18 18" focusable="false"><path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.92c1.7-1.57 2.68-3.88 2.68-6.62z"/><path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.8.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 0 0 9 18z"/><path fill="#FBBC05" d="M3.97 10.72A5.41 5.41 0 0 1 3.68 9c0-.6.1-1.18.29-1.72V4.95H.96A9 9 0 0 0 0 9c0 1.45.35 2.82.96 4.05l3.01-2.33z"/><path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.58C13.46.9 11.43 0 9 0A9 9 0 0 0 .96 4.95l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z"/></svg></span>';
    }
    if (provider === 'github') {
      return '<span class="oc-provider-icon oc-github-icon" aria-hidden="true">GH</span>';
    }
    return '';
  }

  function enabledProviders() {
    var providers = config && config.providers ? config.providers : {};
    return ['microsoft', 'google', 'github'].filter(function (provider) {
      return providers[provider];
    });
  }

  function providerText() {
    var labels = enabledProviders().map(providerLabel);
    if (!labels.length) return 'Sign in with a verified account to comment.';
    if (labels.length === 1) return 'Sign in with your verified ' + labels[0] + ' account to comment.';
    if (labels.length === 2) return 'Sign in with a verified ' + labels[0] + ' or ' + labels[1] + ' account to comment.';
    return 'Sign in with a verified ' + labels.slice(0, -1).join(', ') + ', or ' + labels[labels.length - 1] + ' account to comment.';
  }

  function signInButtons() {
    return enabledProviders().map(function (provider) {
      return '<a class="oc-comments-signin oc-comments-signin-' + provider + '" href="' + signInUrl(provider) + '">' + providerIcon(provider) + '<span>Sign in with ' + providerLabel(provider) + '</span></a>';
    }).join('');
  }

  function renderShell(root) {
    root.innerHTML = [
      '<section class="oc-comments" aria-labelledby="oc-comments-title">',
      '  <div class="oc-comments-head">',
      '    <p class="oc-comments-label">Discussion</p>',
      '    <h2 id="oc-comments-title">Comments</h2>',
      '    <p id="oc-comments-provider-copy">Sign in with a verified account to comment. Comments appear only after approval.</p>',
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
    if (!config || !config.providers || !signInButtons()) {
      target.innerHTML = '<p class="oc-comments-note">Comments are being configured.</p>';
      return;
    }
    var providerCopy = document.getElementById('oc-comments-provider-copy');
    if (providerCopy) providerCopy.textContent = providerText() + ' Comments appear only after approval.';
    if (!session.authenticated) {
      target.innerHTML = '<div class="oc-comments-signins">' + signInButtons() + '</div>';
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
