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
const backTop = document.getElementById('back-top');

window.addEventListener('scroll', () => {
  const y = window.scrollY;
  if (navbar) navbar.classList.toggle('scrolled', y > 60);
  if (backTop) backTop.classList.toggle('show', y > 400);
}, { passive: true });

// back-to-top is now <a href="#"> — browser handles scroll natively

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
const currentPage = window.location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav-links a').forEach(a => {
  const href = a.getAttribute('href');
  if (href === currentPage || (currentPage === '' && href === 'index.html')) {
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
