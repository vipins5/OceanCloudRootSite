/* ===== OceanCloud — main.js ===== */

/* ─── Custom cursor ─── */
(function () {
  const dot  = document.getElementById('c-dot');
  const ring = document.getElementById('c-ring');
  if (!dot || !ring) return;

  document.body.classList.add('has-mouse');

  let mx = -100, my = -100, rx = -100, ry = -100;

  document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });

  (function lerp() {
    rx += (mx - rx) * 0.1;
    ry += (my - ry) * 0.1;
    dot.style.left  = mx + 'px';
    dot.style.top   = my + 'px';
    ring.style.left = rx + 'px';
    ring.style.top  = ry + 'px';
    requestAnimationFrame(lerp);
  })();

  document.querySelectorAll('a, button, [data-cursor]').forEach(el => {
    el.addEventListener('mouseenter', () => document.body.classList.add('cursor-grow'));
    el.addEventListener('mouseleave', () => document.body.classList.remove('cursor-grow'));
  });
})();

/* ─── Hero word-reveal on load ─── */
document.addEventListener('DOMContentLoaded', () => {
  const words = document.querySelectorAll('.hero-h1 .word-inner');
  words.forEach((w, i) => {
    setTimeout(() => w.classList.add('in'), 200 + i * 120);
  });

  // hero image lazy-load zoom
  const heroImg = document.getElementById('heroImg');
  if (heroImg) {
    setTimeout(() => heroImg.classList.add('loaded'), 100);
  }
});

/* ─── Navbar scroll ─── */
const navbar  = document.getElementById('navbar');
const backTop = document.getElementById('back-top') || document.getElementById('back-to-top');

window.addEventListener('scroll', () => {
  const y = window.scrollY;
  if (navbar) navbar.classList.toggle('scrolled', y > 60);
  if (backTop) backTop.classList.toggle('show', y > 400);
}, { passive: true });

if (backTop && backTop.tagName === 'BUTTON') {
  backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* ─── Mobile hamburger ─── */
const ham   = document.getElementById('hamburger');
const links = document.getElementById('navLinks');

if (ham && links) {
  const toggleMenu = (open) => {
    links.classList.toggle('open', open);
    ham.classList.toggle('active', open);
    ham.setAttribute('aria-expanded', open);
    document.body.style.overflow = open ? 'hidden' : '';
  };
  ham.addEventListener('click', () => toggleMenu(!links.classList.contains('open')));
  links.querySelectorAll('a').forEach(a => a.addEventListener('click', () => toggleMenu(false)));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') toggleMenu(false); });
}

/* ─── Scroll reveal ─── */
const observer = new IntersectionObserver((entries) => {
  entries.forEach((e, i) => {
    if (e.isIntersecting) {
      setTimeout(() => e.target.classList.add('visible'), i * 70);
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0.10, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

/* ─── Stagger grid reveal ─── */
const staggerObs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      staggerObs.unobserve(e.target);
    }
  });
}, { threshold: 0.05, rootMargin: '0px 0px -20px 0px' });
document.querySelectorAll('.stagger-grid').forEach(el => staggerObs.observe(el));

/* ─── Counter animation ─── */
function animateCounter(el) {
  const target   = parseFloat(el.dataset.target);
  const suffix   = el.dataset.suffix || '';
  const prefix   = el.dataset.prefix || '';
  const duration = 1600;
  const steps    = 55;
  let   current  = 0;
  const step     = target / steps;

  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    const display = Number.isInteger(target)
      ? Math.round(current)
      : current.toFixed(1);
    el.textContent = prefix + display + suffix;
    if (current >= target) clearInterval(timer);
  }, duration / steps);
}

const counterObs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      animateCounter(e.target);
      counterObs.unobserve(e.target);
    }
  });
}, { threshold: 0.6 });

document.querySelectorAll('[data-target]').forEach(el => counterObs.observe(el));

/* ─── Parallax on image break ─── */
const parallaxEls = document.querySelectorAll('[data-parallax]');
if (parallaxEls.length) {
  window.addEventListener('scroll', () => {
    parallaxEls.forEach(el => {
      const rect  = el.getBoundingClientRect();
      const speed = parseFloat(el.dataset.parallax) || 0.3;
      const ofs   = (rect.top + rect.height / 2 - window.innerHeight / 2) * speed;
      el.style.transform = `translateY(${ofs}px)`;
    });
  }, { passive: true });
}

/* ─── Active nav link ─── */
const normalizePath = (value) => {
  try {
    const url = new URL(value, window.location.origin);
    let path = url.pathname.replace(/\/index\.html$/, '/').replace(/\.html$/, '').replace(/\/$/, '');
    return path || '/';
  } catch (_) {
    return value;
  }
};
const currentPage = normalizePath(window.location.pathname);
document.querySelectorAll('.nav-links a').forEach(a => {
  const href = normalizePath(a.getAttribute('href'));
  if (href === currentPage) {
    a.classList.add('active-link');
  }
});

/* ─── Lazy-load background images ─── */
const bgObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting && e.target.dataset.bg) {
      e.target.style.backgroundImage = `url('${e.target.dataset.bg}')`;
      bgObserver.unobserve(e.target);
    }
  });
}, { rootMargin: '200px' });
document.querySelectorAll('[data-bg]').forEach(el => bgObserver.observe(el));

/* ─── Contact form (basic fallback) ─── */
const form = document.getElementById('contactForm');
if (form) {
  form.addEventListener('submit', e => {
    e.preventDefault();
    const btn = form.querySelector('[type=submit]');
    if (btn) { btn.textContent = 'Sending…'; btn.disabled = true; }
    setTimeout(() => {
      form.style.display = 'none';
      const s = document.getElementById('formSuccess');
      if (s) s.style.display = 'block';
    }, 1400);
  });
}

/* --- Guide code blocks: copy button + lightweight syntax colors --- */
document.addEventListener('DOMContentLoaded', () => {
  const blocks = document.querySelectorAll('.code-block');
  if (!blocks.length) return;

  const escapeCode = value => value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  const restoreHeld = (line, held) => line.replace(/\uE000(A+)\uE001/g, (_, marker) => held[marker.length - 1] || '');

  const hold = (held, html) => {
    held.push(html);
    return `\uE000${'A'.repeat(held.length)}\uE001`;
  };

  const highlightLine = line => {
    const held = [];
    let output = escapeCode(line);

    output = output.replace(/(\/\/.*$|#.*$)/, match => hold(held, `<span class="token-comment">${match}</span>`));
    output = output.replace(/("[^"]*"|'[^']*')/g, match => hold(held, `<span class="token-string">${match}</span>`));
    output = output.replace(/(\$[A-Za-z_][\w.]*)/g, match => hold(held, `<span class="token-variable">${match}</span>`));
    output = output.replace(/(^|\s)(-[A-Za-z][\w-]*)/g, (match, lead, param) => `${lead}${hold(held, `<span class="token-param">${param}</span>`)}`);
    output = output.replace(/\b(\$true|\$false|\$null)\b/gi, match => hold(held, `<span class="token-bool">${match}</span>`));
    output = output.replace(/\b(\d+(?:\.\d+)?)\b/g, match => hold(held, `<span class="token-number">${match}</span>`));
    output = output.replace(/\b(GET|POST|PUT|PATCH|DELETE|MERGE|Method|URI|Headers|Body|Switch|Case|Default|Status|Amount|Created|DueDate|Department|Apply|Select|Where|Object|ForEach|Install|Import|Update|Connect|Export|Write|New|Set|Get)\b/g, match => hold(held, `<span class="token-keyword">${match}</span>`));
    output = output.replace(/\b([A-Za-z]+-[A-Za-z][\w-]*)\b/g, match => hold(held, `<span class="token-command">${match}</span>`));
    output = output.replace(/\b(https?:\/\/[^\s<]+|_[A-Za-z0-9/?$=.'&;%-]+)\b/g, match => hold(held, `<span class="token-path">${match}</span>`));
    output = output.replace(/(\||`|=>|=|\{|\}|\(|\)|\[|\]|,)/g, match => hold(held, `<span class="token-operator">${match}</span>`));

    return restoreHeld(output, held);
  };

  const highlightCode = value => value.split('\n').map(highlightLine).join('\n');

  const explicitCodeLabel = value => {
    const lang = (value || '').toLowerCase();
    if (['powershell', 'ps1', 'ps'].includes(lang)) return 'PowerShell';
    if (lang === 'json') return 'JSON';
    if (['api', 'http'].includes(lang)) return 'API';
    if (['logic-app', 'logicapp', 'logic-apps'].includes(lang)) return 'Logic App';
    if (['power-automate', 'powerautomate', 'flow'].includes(lang)) return 'Power Automate';
    if (['text', 'plain', 'prompt'].includes(lang)) return 'Text';
    return '';
  };

  const detectLabel = (code, block) => {
    const explicit = explicitCodeLabel(block?.dataset?.lang);
    if (explicit) return explicit;

    const previous = block?.previousElementSibling;
    if (previous?.classList?.contains('code-label')) {
      const labelText = previous.textContent.toLowerCase();
      if (labelText.includes('json')) return 'JSON';
      if (labelText.includes('graph') || labelText.includes('http get') || labelText.includes('api')) return 'API';
      if (labelText.includes('logic app')) return 'Logic App';
      if (labelText.includes('power automate')) return 'Power Automate';
    }

    if (/\$[A-Za-z_]|\b(Get|Set|New|Connect|Install|Import|Export|Update)-[A-Za-z]/.test(code)) return 'PowerShell';
    if (/^\s*[{[]/.test(code)) return 'JSON';
    if (/\b(GET|POST|PUT|PATCH|DELETE)\b|_api\/|graph\.microsoft\.com/i.test(code)) return 'API';
    return 'Script';
  };

  const copyText = text => {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise((resolve, reject) => {
      const area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      try {
        document.execCommand('copy') ? resolve() : reject(new Error('Copy failed'));
      } catch (error) {
        reject(error);
      } finally {
        area.remove();
      }
    });
  };

  blocks.forEach(block => {
    if (block.dataset.codeEnhanced === 'true') return;

    const source = block.querySelector('pre') || block;
    const originalText = source.textContent.replace(/^\n+|\s+$/g, '');
    const hasManualTokens = Boolean(block.querySelector('.kw, .str, .cm'));

    if (!hasManualTokens && source) source.innerHTML = highlightCode(originalText);

    const toolbar = document.createElement('div');
    toolbar.className = 'oc-code-toolbar';

    const label = document.createElement('span');
    label.className = 'oc-code-label';
    label.textContent = detectLabel(originalText, block);

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'oc-copy-btn';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code to clipboard');
    button.addEventListener('click', () => {
      copyText(originalText).then(() => {
        button.textContent = 'Copied';
        button.classList.add('copied');
        window.setTimeout(() => {
          button.textContent = 'Copy';
          button.classList.remove('copied');
        }, 1600);
      }).catch(() => {
        button.textContent = 'Press Ctrl+C';
        window.setTimeout(() => { button.textContent = 'Copy'; }, 1600);
      });
    });

    toolbar.append(label, button);
    block.prepend(toolbar);
    block.classList.add('oc-code-enhanced');
    block.dataset.codeEnhanced = 'true';
  });
});
