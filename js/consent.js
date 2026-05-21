(function () {
  'use strict';

  var GA_ID       = 'G-2ZVXYXDHEZ';
  var CONSENT_KEY = 'oc_cookie_consent';

  function loadGA() {
    if (window.__gaLoaded) return;
    window.__gaLoaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID, { anonymize_ip: true });
  }

  function hideBanner() {
    var b = document.getElementById('oc-cookie-banner');
    if (!b) return;
    b.style.transition = 'opacity .3s ease, transform .3s ease';
    b.style.opacity   = '0';
    b.style.transform = 'translateY(20px)';
    setTimeout(function () { b.style.display = 'none'; }, 320);
  }

  function init() {
    var consent = localStorage.getItem(CONSENT_KEY);

    if (consent === 'accepted') { loadGA(); return; }

    var banner = document.getElementById('oc-cookie-banner');
    if (!banner) return;

    if (!consent) {
      banner.style.display = 'flex';
      setTimeout(function () {
        banner.style.opacity   = '1';
        banner.style.transform = 'translateY(0)';
      }, 300);
    }

    var btnAccept  = document.getElementById('ccb-accept');
    var btnDecline = document.getElementById('ccb-decline');

    if (btnAccept) {
      btnAccept.addEventListener('click', function () {
        localStorage.setItem(CONSENT_KEY, 'accepted');
        hideBanner();
        loadGA();
      });
    }

    if (btnDecline) {
      btnDecline.addEventListener('click', function () {
        localStorage.setItem(CONSENT_KEY, 'declined');
        hideBanner();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
