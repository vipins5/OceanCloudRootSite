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
    var allowedPath =
      path === '/guides' || path === '/guides.html' ||
      path === '/news' || path === '/news.html' ||
      path === '/status' || path === '/status.html' ||
      path === '/message-center' || path === '/message-center.html' ||
      path.indexOf('/articles/guide-') === 0;

    if (!allowedPath) {
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

  function grantConsent() {
    if (!window.gtag) {
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { dataLayer.push(arguments); };
    }
    window.gtag('consent', 'update', {
      'analytics_storage': 'granted',
      'ad_storage': 'granted',
      'ad_user_data': 'granted',
      'ad_personalization': 'granted'
    });
  }

  function setConsent(value) {
    try { localStorage.setItem(CONSENT_KEY, value); } catch (e) {}
  }

  function init() {
    var consent = getConsent();

    // Initialize Google Consent Mode v2 with default 'denied' state
    // This ensures compliance with GDPR/CCPA before consent is obtained
    if (!window.dataLayer) {
      window.dataLayer = [];
    }
    if (!window.gtag) {
      window.gtag = function () { dataLayer.push(arguments); };
    }
    window.gtag('consent', 'default', {
      'analytics_storage': 'denied',
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied'
    });

    // AdSense is loaded independently of cookie consent on allowed pages so
    // that Google's review/verification crawler can detect the ad code.
    loadAdsense();

    if (consent === 'accepted') { 
      // Update consent to 'granted' after user acceptance
      grantConsent();
      loadGA(); 
      return; 
    }

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
        grantConsent();
        hideBanner();
        loadGA();
      });
    }

    if (btnDecline) {
      btnDecline.addEventListener('click', function () {
        setConsent('declined');
        hideBanner();
      });
    }
  }

  /* ── Web Vitals reporting via GA4 ──────────────────────────
     Sends CLS, INP, LCP, FCP, and TTFB as GA4 events once the
     user has accepted analytics. Uses the web-vitals library
     attribution build for diagnostic context.
     ─────────────────────────────────────────────────────── */
  function reportVital(metric) {
    if (!window.gtag) return;
    window.gtag('event', metric.name, {
      value:          Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
      metric_id:      metric.id,
      metric_value:   metric.value,
      metric_delta:   metric.delta,
      metric_rating:  metric.rating,
      non_interaction: true
    });
  }

  function loadWebVitals() {
    if (window.__vitalsLoaded) return;
    window.__vitalsLoaded = true;
    var s = document.createElement('script');
    s.type   = 'module';
    s.textContent = [
      "import{onCLS,onINP,onLCP,onFCP,onTTFB}from'https://unpkg.com/web-vitals@4/dist/web-vitals.attribution.js';",
      "var r=window.__reportVital;",
      "if(r){onCLS(r);onINP(r);onLCP(r);onFCP(r);onTTFB(r);}"
    ].join('');
    window.__reportVital = reportVital;
    document.head.appendChild(s);
  }

  /* Hook into GA load so vitals only fire after consent */
  var _origLoadGA = loadGA;
  loadGA = function () {
    _origLoadGA();
    loadWebVitals();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
