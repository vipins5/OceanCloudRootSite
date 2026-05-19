/* ===== NAV SCROLL ===== */
const navbar = document.getElementById('navbar');
const backTop = document.getElementById('back-top');

window.addEventListener('scroll', () => {
  const y = window.scrollY;
  navbar.classList.toggle('scrolled', y > 60);
  if (backTop) backTop.classList.toggle('show', y > 400);
});

if (backTop) {
  backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* ===== MOBILE HAMBURGER ===== */
const ham   = document.getElementById('hamburger');
const links = document.getElementById('navLinks');

if (ham && links) {
  ham.addEventListener('click', () => {
    links.classList.toggle('open');
    ham.classList.toggle('active');
  });

  links.querySelectorAll('a').forEach(a =>
    a.addEventListener('click', () => {
      links.classList.remove('open');
      ham.classList.remove('active');
    })
  );
}

/* ===== SCROLL REVEAL ===== */
const revealEls = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver((entries) => {
  entries.forEach((e, i) => {
    if (e.isIntersecting) {
      setTimeout(() => e.target.classList.add('visible'), i * 80);
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0.12 });

revealEls.forEach(el => observer.observe(el));

/* ===== COUNTER ANIMATION ===== */
function animateCounter(el) {
  const target = parseFloat(el.dataset.target);
  const suffix = el.dataset.suffix || '';
  const prefix = el.dataset.prefix || '';
  const duration = 1800;
  const steps = 60;
  const step = target / steps;
  let current = 0;
  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    const display = Number.isInteger(target) ? Math.round(current) : current.toFixed(1);
    el.textContent = prefix + display + suffix;
    if (current >= target) clearInterval(timer);
  }, duration / steps);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      animateCounter(e.target);
      counterObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-target]').forEach(el => counterObserver.observe(el));

/* ===== CONTACT FORM ===== */
const form = document.getElementById('contactForm');
if (form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = form.querySelector('.btn-submit');
    btn.textContent = 'Sending…';
    btn.disabled = true;

    setTimeout(() => {
      form.style.display = 'none';
      const success = document.getElementById('formSuccess');
      if (success) success.style.display = 'block';
    }, 1400);
  });
}

/* ===== ACTIVE NAV LINK ===== */
const currentPage = window.location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav-links a').forEach(a => {
  const href = a.getAttribute('href');
  if (href === currentPage || (currentPage === '' && href === 'index.html')) {
    a.classList.add('active-link');
  }
});
