/* ═══════════════════════════════════════════════════════════
   code.js — lightweight syntax highlighter + copy button
   Supports: PowerShell (default), HTML/XML, JSON
   ═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* ── PowerShell keywords ────────────────────────────────── */
  var PS_KW = new Set([
    'if','else','elseif','foreach','for','while','do','switch',
    'break','continue','return','function','filter','param',
    'begin','process','end','try','catch','finally','throw',
    'in','not','and','or','is','isnot','like','notlike',
    'match','notmatch','contains','notcontains',
    'gt','lt','ge','le','eq','ne','as',
    'true','false','null','void','using','class','enum',
    'import','module','requires','assembly','select','where',
    'sort','group','measure','format','out','write','read'
  ]);

  /* ── HTML escape ──────────────────────────────────────────── */
  function esc(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  /* ── Wrap in a coloured span ─────────────────────────────── */
  function tok(cls, text) {
    return '<span class="' + cls + '">' + text + '</span>';
  }

  /* ═══════════════════════════════════════════════════════════
     PowerShell / generic scripting highlighter
     Single-pass tokenizer — processes comment > here-string >
     quoted string > variable > parameter > word > number
     ═══════════════════════════════════════════════════════════ */
  function hlPS(raw) {
    var out = [];
    var n   = raw.length;
    var i   = 0;

    while (i < n) {
      var c = raw[i];

      /* Comment: # → end of line */
      if (c === '#') {
        var j = i;
        while (j < n && raw[j] !== '\n') j++;
        out.push(tok('tok-comment', esc(raw.slice(i, j))));
        i = j; continue;
      }

      /* Here-string: @"..."@ or @'...'@ */
      if (c === '@' && i + 1 < n && (raw[i+1] === '"' || raw[i+1] === "'")) {
        var hd  = raw[i+1];
        var end = raw.indexOf(hd + '@', i + 2);
        if (end !== -1) {
          out.push(tok('tok-string', esc(raw.slice(i, end + 2))));
          i = end + 2; continue;
        }
      }

      /* Double-quoted string: "..." (backtick escape) */
      if (c === '"') {
        var j = i + 1;
        while (j < n && raw[j] !== '"') { if (raw[j] === '`') j++; j++; }
        out.push(tok('tok-string', esc(raw.slice(i, j + 1))));
        i = j + 1; continue;
      }

      /* Single-quoted string: '...' */
      if (c === "'") {
        var j = i + 1;
        while (j < n && raw[j] !== "'") j++;
        out.push(tok('tok-string', esc(raw.slice(i, j + 1))));
        i = j + 1; continue;
      }

      /* Variable: $name  (skip bare $ with no alphanumeric) */
      if (c === '$') {
        var j = i + 1;
        while (j < n && /[\w:.[\]]/.test(raw[j])) j++;
        if (j > i + 1) {
          out.push(tok('tok-var', esc(raw.slice(i, j))));
          i = j; continue;
        }
      }

      /* Parameter: -Name  (dash followed by a letter) */
      if (c === '-' && i + 1 < n && /[A-Za-z]/.test(raw[i+1])) {
        var j = i + 1;
        while (j < n && /[A-Za-z0-9]/.test(raw[j])) j++;
        out.push(tok('tok-param', esc(raw.slice(i, j))));
        i = j; continue;
      }

      /* Word: cmdlet (Verb-Noun), keyword, or plain identifier */
      if (/[A-Za-z_]/.test(c)) {
        var j = i;
        while (j < n && /[A-Za-z0-9_-]/.test(raw[j])) j++;
        /* trim trailing dashes from word (they belong to next token) */
        while (j > i && raw[j-1] === '-') j--;
        var word = raw.slice(i, j);
        var low  = word.toLowerCase();
        if (PS_KW.has(low)) {
          out.push(tok('tok-kw', esc(word)));
        } else if (/^[A-Z][a-zA-Z0-9]+-[A-Z]/.test(word)) {
          out.push(tok('tok-cmdlet', esc(word)));
        } else {
          out.push(esc(word));
        }
        i = j; continue;
      }

      /* Number */
      if (/[0-9]/.test(c)) {
        var j = i;
        while (j < n && /[0-9.]/.test(raw[j])) j++;
        out.push(tok('tok-num', esc(raw.slice(i, j))));
        i = j; continue;
      }

      /* Anything else — pass through escaped */
      out.push(esc(c));
      i++;
    }

    return out.join('');
  }

  /* ═══════════════════════════════════════════════════════════
     HTML / XML highlighter (regex-based, post-escape)
     ═══════════════════════════════════════════════════════════ */
  function hlHTML(raw) {
    var s = esc(raw);

    /* Comments: <!-- ... --> */
    s = s.replace(/(&lt;!--[\s\S]*?--&gt;)/g, function(m) {
      return tok('tok-comment', m);
    });

    /* DOCTYPE */
    s = s.replace(/(&lt;!DOCTYPE[^&>]*&gt;)/gi, function(m) {
      return tok('tok-comment', m);
    });

    /* Closing tag: </name */
    s = s.replace(/(&lt;\/)([\w-]+)/g, function(_, slash, name) {
      return '<span style="color:#808080">' + slash + '</span>' + tok('tok-tag', name);
    });

    /* Opening tag: <name */
    s = s.replace(/(&lt;)([\w-]+)/g, function(_, lt, name) {
      return '<span style="color:#808080">' + lt + '</span>' + tok('tok-tag', name);
    });

    /* Attribute values: ="..."  (already &quot; after esc) */
    s = s.replace(/=(&quot;)(.*?)(&quot;)/g, function(_, q1, v, q2) {
      return '=' + tok('tok-aval', q1 + v + q2);
    });

    /* Attribute names: word= */
    s = s.replace(/\s([\w-]+)(=)/g, function(_, a, eq) {
      return ' ' + tok('tok-attr', a) + eq;
    });

    /* HTML entities: &amp;xxx; */
    s = s.replace(/(&amp;[a-zA-Z0-9#]+;)/g, function(m) {
      return tok('tok-entity', m);
    });

    return s;
  }

  /* ═══════════════════════════════════════════════════════════
     JSON highlighter
     ═══════════════════════════════════════════════════════════ */
  function hlJSON(raw) {
    var s = esc(raw);

    /* Keys: "key": */
    s = s.replace(/"([^"]*)"(?=\s*:)/g, function(_, k) {
      return tok('tok-jkey', '"' + k + '"');
    });

    /* String values: : "value" */
    s = s.replace(/(:\s*)"([^"]*)"/g, function(_, pre, v) {
      return pre + tok('tok-jstr', '"' + v + '"');
    });

    /* Numbers */
    s = s.replace(/(:\s*)(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/g, function(_, pre, n) {
      return pre + tok('tok-jnum', n);
    });

    /* Booleans + null */
    s = s.replace(/(:\s*)(true|false|null)/g, function(_, pre, b) {
      return pre + tok('tok-jbool', b);
    });

    /* Brackets and braces */
    s = s.replace(/([{}[\]])/g, function(m) {
      return tok('tok-jbrack', m);
    });

    return s;
  }

  /* ═══════════════════════════════════════════════════════════
     Language detection — reads the .code-label above the block
     ═══════════════════════════════════════════════════════════ */
  var LANG_NAMES = {
    ps:   'powershell',
    html: 'html',
    xml:  'xml',
    json: 'json',
    js:   'javascript'
  };

  function detectLang(block) {
    var prev = block.previousElementSibling;
    if (prev && prev.classList.contains('code-label')) {
      var t = prev.textContent.toLowerCase();
      if (t.includes('html'))                       return 'html';
      if (t.includes('xml') || t.includes('sitemap')) return 'xml';
      if (t.includes('json'))                       return 'json';
      if (t.includes('javascript') || /\bjs\b/.test(t)) return 'js';
    }
    return 'ps';
  }

  /* ═══════════════════════════════════════════════════════════
     SVG icons
     ═══════════════════════════════════════════════════════════ */
  var ICON_COPY = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
  var ICON_CHECK = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';

  /* ═══════════════════════════════════════════════════════════
     Copy to clipboard
     ═══════════════════════════════════════════════════════════ */
  function flashCopied(btn) {
    btn.innerHTML = ICON_CHECK + ' Copied!';
    btn.classList.add('copied');
    setTimeout(function () {
      btn.innerHTML = ICON_COPY + ' Copy';
      btn.classList.remove('copied');
    }, 2000);
  }

  function fallbackCopy(text, btn) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
    flashCopied(btn);
  }

  function copyCode(pre, btn) {
    var text = pre.textContent || pre.innerText || '';
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text)
        .then(function() { flashCopied(btn); })
        .catch(function() { fallbackCopy(text, btn); });
    } else {
      fallbackCopy(text, btn);
    }
  }

  /* ═══════════════════════════════════════════════════════════
     Main: wire up every .code-block on the page
     ═══════════════════════════════════════════════════════════ */
  function init() {
    document.querySelectorAll('.code-block').forEach(function(block) {
      var pre = block.querySelector('pre');
      if (!pre) return;

      /* Remove toolbar injected by main.js to avoid duplicate copy buttons */
      var existing = block.querySelector('.oc-code-toolbar');
      if (existing) existing.remove();

      var lang = detectLang(block);
      var raw  = pre.textContent || '';

      /* Apply syntax highlighting */
      if      (lang === 'html' || lang === 'xml') pre.innerHTML = hlHTML(raw);
      else if (lang === 'json')                   pre.innerHTML = hlJSON(raw);
      else                                         pre.innerHTML = hlPS(raw);

      /* Build copy button */
      var btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.setAttribute('aria-label', 'Copy code to clipboard');
      btn.innerHTML = ICON_COPY + ' Copy';
      btn.addEventListener('click', function() { copyCode(pre, btn); });

      /* Build header bar with lang badge + copy button */
      var header = document.createElement('div');
      header.className = 'code-header';

      var badge = document.createElement('span');
      badge.className = 'code-lang';
      badge.textContent = LANG_NAMES[lang] || lang;

      header.appendChild(badge);
      header.appendChild(btn);

      /* Insert header as first child of the code block */
      block.insertBefore(header, block.firstChild);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
