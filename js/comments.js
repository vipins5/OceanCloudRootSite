(function () {
  'use strict';

  var API_BASE = 'https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev';
  var TOKEN_KEY = 'ocCommentToken';
  var config = null;
  var session = { authenticated: false };
  var turnstileToken = '';
  var turnstileWidgetId = null;
  var replyTarget = null;
  var THREAD_VISIBLE_REPLIES = 3;
  var EMOJIS = ['👍','👏','✅','💡','🚀','😊','🙏','🔒','🎉','🔥','⭐','🙌','💯','🤝','👀','📝','⚡','🛠️','📌','📣','❤️','😄','🤔','👌','☕','🌊','📚','🧠','🔎','🏆'];

  function slug() {
    var part = window.location.pathname.split('/').pop() || '';
    return part.replace(/\.html$/, '');
  }

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"]/g, function (char) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char];
    });
  }

  function safeUrl(value) {
    try {
      var raw = String(value || '').replace(/&amp;/g, '&').trim();
      var url = new URL(raw);
      if (url.protocol !== 'https:' && url.protocol !== 'http:') return '';
      return url.toString();
    } catch (error) {
      return '';
    }
  }

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
      return false;
    }
  }

  function removeStoredToken() {
    try { localStorage.removeItem(TOKEN_KEY); } catch (error) {}
  }

  function renderRichText(value) {
    var html = escapeHtml(value).replace(/\r\n/g, '\n');

    html = html.replace(/!\[([^\]]{0,100})\]\((https?:\/\/[^\s)]+)\)/g, function (match, alt, url) {
      var cleanUrl = safeUrl(url);
      if (!cleanUrl) return match;
      return '<a class="oc-comment-image-link" href="' + escapeHtml(cleanUrl) + '" target="_blank" rel="noopener noreferrer"><img class="oc-comment-image" src="' + escapeHtml(cleanUrl) + '" alt="' + escapeHtml(alt || 'Comment image') + '" loading="lazy" /></a>';
    });
    html = html.replace(/\[([^\]]{1,140})\]\((https?:\/\/[^\s)]+)\)/g, function (match, label, url) {
      var cleanUrl = safeUrl(url);
      if (!cleanUrl) return match;
      return '<a href="' + escapeHtml(cleanUrl) + '" target="_blank" rel="noopener noreferrer">' + label + '</a>';
    });
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    return html.replace(/\n/g, '<br>');
  }

  function tokenFromHash() {
    var match = window.location.hash.match(/oc_comment_token=([^&]+)/);
    if (!match) return;
    setStoredToken(decodeURIComponent(match[1]));
    history.replaceState(null, '', window.location.pathname + window.location.search);
  }

  function authHeaders() {
    var token = getStoredToken();
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
    link.href = '/css/comments.css?v=7';
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
    try {
      turnstileWidgetId = window.turnstile.render(target, {
        sitekey: config.turnstileSiteKey,
        callback: function (token) { turnstileToken = token; },
        'expired-callback': function () { turnstileToken = ''; },
        'error-callback': function () { turnstileToken = ''; turnstileWidgetId = null; },
      });
    } catch (error) {
      turnstileWidgetId = null;
      turnstileToken = '';
    }
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

    var topLevel = [];
    var repliesByParent = {};
    items.forEach(function (item) {
      if (item.parent_id) {
        var key = String(item.parent_id);
        repliesByParent[key] = repliesByParent[key] || [];
        repliesByParent[key].push(item);
      } else {
        topLevel.push(item);
      }
    });

    list.innerHTML = topLevel.map(function (item) {
      var replies = repliesByParent[String(item.id)] || [];
      var hiddenCount = Math.max(0, replies.length - THREAD_VISIBLE_REPLIES);
      return '<article class="oc-comment-thread" data-comment-id="' + item.id + '">' +
        renderComment(item, false, replies.length) +
        (replies.length ? '<div class="oc-comment-replies">' + replies.map(function (reply, index) {
          return '<div class="oc-comment-reply-wrap' + (index >= THREAD_VISIBLE_REPLIES ? ' oc-reply-hidden' : '') + '">' + renderComment(reply, true, 0) + '</div>';
        }).join('') + '</div>' : '') +
        (hiddenCount ? '<button type="button" class="oc-comments-show-replies" data-parent-id="' + item.id + '">Show ' + hiddenCount + ' more repl' + (hiddenCount === 1 ? 'y' : 'ies') + '</button>' : '') +
        '</article>';
    }).join('');
  }

  function renderComment(item, isReply, replyCount) {
    var actions = [];
    if (!isReply && !item.is_deleted) {
      actions.push('<button type="button" class="oc-comment-reply-btn" data-reply-id="' + item.id + '" data-reply-name="' + escapeHtml(item.display_name) + '">Reply</button>');
    }
    if (item.can_delete) {
      actions.push('<button type="button" class="oc-comment-delete-btn" data-delete-id="' + item.id + '">Delete</button>');
    }
    if (!isReply && replyCount) {
      actions.push('<span>' + replyCount + ' repl' + (replyCount === 1 ? 'y' : 'ies') + '</span>');
    }

    return '<article class="oc-comment' + (isReply ? ' oc-comment-reply' : '') + '" data-comment-id="' + item.id + '">' +
      '<div class="oc-comment-meta"><strong>' + escapeHtml(item.display_name) + '</strong><span>' + escapeHtml(new Date(item.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })) + '</span></div>' +
      '<div class="oc-comment-body' + (item.is_deleted ? ' oc-comment-deleted' : '') + '">' + (item.is_deleted ? 'This comment was deleted.' : renderRichText(item.body)) + '</div>' +
      (actions.length ? '<div class="oc-comment-actions">' + actions.join('') + '</div>' : '') +
      '</article>';
  }

  function emojiButtons() {
    return EMOJIS.map(function (emoji) {
      return '<button type="button" data-emoji="' + emoji + '">' + emoji + '</button>';
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
      '  <div id="oc-reply-context" class="oc-reply-context" hidden></div>',
      '  <label for="oc-comment-body">Comment</label>',
      '  <div class="oc-comment-toolbar" aria-label="Comment formatting tools">',
      '    <button type="button" data-format="bold">B</button>',
      '    <button type="button" data-format="italic"><em>I</em></button>',
      '    <button type="button" data-format="code">Code</button>',
      '    <button type="button" data-format="link">Link</button>',
      '    <button type="button" data-format="image">Image</button>',
      '    <button type="button" data-format="emoji">Emoji</button>',
      '  </div>',
      '  <div id="oc-emoji-panel" class="oc-emoji-panel" hidden>',
      '    ' + emojiButtons(),
      '  </div>',
      '  <textarea id="oc-comment-body" maxlength="2000" rows="5" required placeholder="Add a helpful comment or question..."></textarea>',
      '  <p class="oc-format-note">Supports **bold**, *italic*, `code`, [links](https://...), image URLs, and emoji. All comments are moderated.</p>',
      '  <div id="oc-turnstile"></div>',
      '  <button type="submit">Submit for approval</button>',
      '  <button type="button" class="oc-comments-signout" id="oc-comments-signout">Sign out</button>',
      '  <p class="oc-comments-status" id="oc-comments-status"></p>',
      '</form>'
    ].join('');
    ensureTurnstileScript();
    renderTurnstile();

    document.getElementById('oc-comments-signout').addEventListener('click', function () {
      removeStoredToken();
      session = { authenticated: false };
      replyTarget = null;
      renderForm();
    });

    document.getElementById('oc-comment-submit').addEventListener('submit', submitComment);
    bindFormattingTools();
  }

  function textarea() {
    return document.getElementById('oc-comment-body');
  }

  function insertText(text) {
    var field = textarea();
    if (!field) return;
    var start = field.selectionStart || 0;
    var end = field.selectionEnd || 0;
    field.value = field.value.slice(0, start) + text + field.value.slice(end);
    field.focus();
    field.selectionStart = field.selectionEnd = start + text.length;
    field.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function wrapSelection(prefix, suffix, fallback) {
    var field = textarea();
    if (!field) return;
    var start = field.selectionStart || 0;
    var end = field.selectionEnd || 0;
    var selected = field.value.slice(start, end) || fallback;
    var next = prefix + selected + suffix;
    field.value = field.value.slice(0, start) + next + field.value.slice(end);
    field.focus();
    field.selectionStart = start + prefix.length;
    field.selectionEnd = start + prefix.length + selected.length;
    field.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function bindFormattingTools() {
    var toolbar = document.querySelector('.oc-comment-toolbar');
    var panel = document.getElementById('oc-emoji-panel');
    if (!toolbar) return;

    toolbar.addEventListener('click', function (event) {
      var button = event.target.closest('button[data-format]');
      if (!button) return;
      var format = button.dataset.format;
      if (format === 'bold') wrapSelection('**', '**', 'bold text');
      if (format === 'italic') wrapSelection('*', '*', 'italic text');
      if (format === 'code') wrapSelection('`', '`', 'code');
      if (format === 'link') {
        var linkUrl = prompt('Paste a link URL');
        if (safeUrl(linkUrl)) wrapSelection('[', '](' + safeUrl(linkUrl) + ')', 'link text');
      }
      if (format === 'image') {
        var imageUrl = prompt('Paste an image URL');
        if (safeUrl(imageUrl)) insertText('![image](' + safeUrl(imageUrl) + ')');
      }
      if (format === 'emoji' && panel) panel.hidden = !panel.hidden;
    });

    if (panel) {
      panel.addEventListener('click', function (event) {
        var button = event.target.closest('button[data-emoji]');
        if (!button) return;
        insertText(button.dataset.emoji || '');
      });
    }
  }

  function setReplyTarget(id, name) {
    replyTarget = { id: Number(id), name: name || 'comment' };
    var context = document.getElementById('oc-reply-context');
    var body = document.getElementById('oc-comment-body');
    if (context) {
      context.hidden = false;
      context.innerHTML = 'Replying to <strong>' + escapeHtml(replyTarget.name) + '</strong> <button type="button" id="oc-reply-cancel">Cancel</button>';
      document.getElementById('oc-reply-cancel').addEventListener('click', clearReplyTarget);
    }
    if (body) {
      body.placeholder = 'Write a reply...';
      body.focus();
    }
  }

  function clearReplyTarget() {
    replyTarget = null;
    var context = document.getElementById('oc-reply-context');
    var body = document.getElementById('oc-comment-body');
    if (context) {
      context.hidden = true;
      context.innerHTML = '';
    }
    if (body) body.placeholder = 'Add a helpful comment or question...';
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
      var wasReply = Boolean(replyTarget);
      await api('/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug: slug(), body: body, parentId: replyTarget ? replyTarget.id : null, turnstileToken: turnstileToken })
      });
      document.getElementById('oc-comment-body').value = '';
      clearReplyTarget();
      resetTurnstile();
      status.textContent = 'Thanks. Your ' + (wasReply ? 'reply' : 'comment') + ' is pending approval.';
    } catch (error) {
      resetTurnstile();
      status.textContent = error.message || 'Could not submit comment.';
    }
  }

  async function deleteComment(id) {
    if (!id) return;
    if (!confirm('Delete this comment?')) return;
    try {
      await api('/comments/' + encodeURIComponent(id), { method: 'DELETE' });
      var comments = await api('/comments?slug=' + encodeURIComponent(slug()));
      renderComments(comments.comments || []);
    } catch (error) {
      alert(error.message || 'Could not delete comment.');
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

  document.addEventListener('click', function (event) {
    var replyButton = event.target.closest('.oc-comment-reply-btn');
    if (replyButton) {
      if (!session.authenticated) {
        document.getElementById('oc-comments-form')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
      setReplyTarget(replyButton.dataset.replyId, replyButton.dataset.replyName);
      document.getElementById('oc-comments-form')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    var showButton = event.target.closest('.oc-comments-show-replies');
    if (showButton) {
      var thread = showButton.closest('.oc-comment-thread');
      if (!thread) return;
      thread.querySelectorAll('.oc-reply-hidden').forEach(function (reply) {
        reply.classList.remove('oc-reply-hidden');
      });
      showButton.remove();
      return;
    }

    var deleteButton = event.target.closest('.oc-comment-delete-btn');
    if (deleteButton) {
      deleteComment(Number(deleteButton.dataset.deleteId || 0));
    }
  });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
