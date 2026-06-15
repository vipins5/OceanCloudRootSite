(function () {
  'use strict';

  var GA_ID       = 'G-2ZVXYXDHEZ';
  var ADSENSE_ID  = 'ca-pub-9926554564611983';
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

  function shouldLoadAdsense() {
    var path = (location.pathname || '').replace(/\/+$/, '').toLowerCase();
    if (path !== '/guides' && path !== '/guides.html' && path !== '/news' && path !== '/news.html') {
      return false;
    }
    var robots = document.querySelector('meta[name="robots"]');
    if (!robots) return true;
    var content = (robots.getAttribute('content') || '').toLowerCase();
    return content.indexOf('noindex') === -1;
  }

  function loadAdsense() {
    if (window.__adsenseLoaded) return;
    if (!shouldLoadAdsense()) return;
    window.__adsenseLoaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + ADSENSE_ID;
    s.crossOrigin = 'anonymous';
    document.head.appendChild(s);
  }

  function hideBanner() {
    var b = document.getElementById('oc-cookie-banner');
    if (!b) return;
    b.style.transition = 'opacity .3s ease, transform .3s ease';
    b.style.opacity   = '0';
    b.style.transform = 'translateY(20px)';
    setTimeout(function () { b.style.display = 'none'; }, 320);
  }

  function getConsent() {
    try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; }
  }

  function setConsent(value) {
    try { localStorage.setItem(CONSENT_KEY, value); } catch (e) {}
  }

  function init() {
    var consent = getConsent();

    if (consent === 'accepted') { loadGA(); loadAdsense(); return; }

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
        setConsent('accepted');
        hideBanner();
        loadGA();
        loadAdsense();
      });
    }

    if (btnDecline) {
      btnDecline.addEventListener('click', function () {
        setConsent('declined');
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
