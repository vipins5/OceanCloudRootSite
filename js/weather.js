(function () {
  'use strict';

  const WMO = {
    0:  ['Clear sky',          '☀️'],
    1:  ['Mainly clear',       '🌤️'],
    2:  ['Partly cloudy',      '⛅'],
    3:  ['Overcast',           '☁️'],
    45: ['Foggy',              '🌫️'],
    48: ['Icy fog',            '🌫️'],
    51: ['Light drizzle',      '🌦️'],
    53: ['Drizzle',            '🌦️'],
    55: ['Heavy drizzle',      '🌧️'],
    61: ['Light rain',         '🌧️'],
    63: ['Rain',               '🌧️'],
    65: ['Heavy rain',         '🌧️'],
    71: ['Light snow',         '🌨️'],
    73: ['Snow',               '🌨️'],
    75: ['Heavy snow',         '❄️'],
    77: ['Snow grains',        '❄️'],
    80: ['Rain showers',       '🌦️'],
    81: ['Rain showers',       '🌧️'],
    82: ['Heavy showers',      '⛈️'],
    85: ['Snow showers',       '🌨️'],
    86: ['Heavy snow showers', '🌨️'],
    95: ['Thunderstorm',       '⛈️'],
    96: ['Thunderstorm',       '⛈️'],
    99: ['Thunderstorm',       '⛈️']
  };

  const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  function toF(c) { return Math.round(c * 9 / 5 + 32); }
  function cond(code) { return WMO[code] || ['—', '🌡️']; }
  function dayName(dateStr, i) {
    return i === 0 ? 'Today' : DAYS[new Date(dateStr + 'T12:00:00').getDay()];
  }

  // ── Styles ───────────────────────────────────────────────────────────────────
  const styleEl = document.createElement('style');
  styleEl.textContent = `
    #oc-weather {
      position: fixed; bottom: 24px; left: 24px; z-index: 9000;
      font-family: 'Inter', system-ui, sans-serif;
      opacity: 0; transform: translateY(12px);
      transition: opacity .4s ease, transform .4s ease;
      pointer-events: none;
    }
    #oc-weather.oc-w-ready { opacity: 1; transform: translateY(0); pointer-events: auto; }

    #oc-w-card {
      background: rgba(7,26,46,0.94);
      border: 1px solid rgba(0,180,216,0.28);
      border-radius: 16px; backdrop-filter: blur(14px);
      box-shadow: 0 8px 32px rgba(0,0,0,.5);
      padding: 12px 14px 10px; min-width: 200px;
      cursor: pointer; user-select: none; transition: border-color .2s;
      position: relative;
    }
    #oc-w-card:hover { border-color: rgba(0,180,216,.55); }

    #oc-w-face { display: flex; align-items: center; gap: 10px; }
    #oc-w-emoji { font-size: 30px; line-height: 1; flex-shrink: 0; }
    #oc-w-right { flex: 1; min-width: 0; }
    #oc-w-city {
      font-size: 11px; font-weight: 600; color: #00b4d8; letter-spacing: .4px;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    #oc-w-time { font-size: 11px; font-weight: 500; color: #5d8aa8; margin-top: 1px; letter-spacing: .2px; }
    #oc-w-time span { color: #8ba3bb; font-weight: 400; }
    #oc-w-temp { font-size: 18px; font-weight: 700; color: #f0f4f8; line-height: 1.2; margin-top: 2px; }

    #oc-w-detail {
      margin-top: 8px; padding-top: 8px;
      border-top: 1px solid rgba(255,255,255,.08);
      display: flex; justify-content: space-between; gap: 6px;
    }
    .oc-w-pill { font-size: 10.5px; color: #8ba3bb; white-space: nowrap; }

    #oc-w-hint {
      text-align: center; font-size: 10px; color: #3d6080;
      margin-top: 7px; letter-spacing: .3px; transition: color .2s;
    }
    #oc-w-card:hover #oc-w-hint { color: #00b4d8; }

    #oc-w-forecast {
      max-height: 0; overflow: hidden;
      transition: max-height .35s ease, opacity .3s ease, margin .3s ease;
      opacity: 0; margin-top: 0;
    }
    #oc-weather.oc-w-open #oc-w-forecast { max-height: 320px; opacity: 1; margin-top: 10px; }
    #oc-weather.oc-w-open #oc-w-hint { display: none; }

    #oc-w-fc-header {
      font-size: 10px; font-weight: 700; color: #4a6fa5;
      letter-spacing: .8px; text-transform: uppercase;
      margin-bottom: 6px; padding-top: 8px;
      border-top: 1px solid rgba(255,255,255,.08);
    }
    .oc-w-day {
      display: grid; grid-template-columns: 38px 26px 1fr auto;
      align-items: center; gap: 6px; padding: 5px 0;
      border-bottom: 1px solid rgba(255,255,255,.05);
    }
    .oc-w-day:last-child { border-bottom: none; }
    .oc-w-dn { font-size: 11px; font-weight: 600; color: #c8daea; }
    .oc-w-day:first-child .oc-w-dn { color: #00b4d8; }
    .oc-w-de { font-size: 16px; line-height: 1; }
    .oc-w-range { font-size: 11px; color: #8ba3bb; white-space: nowrap; }
    .oc-w-range strong { color: #e0eaf4; font-weight: 600; }
    .oc-w-rain { font-size: 10.5px; color: #4a8fa5; text-align: right; white-space: nowrap; }

    #oc-w-close {
      display: none; position: absolute; top: 7px; right: 9px;
      background: none; border: none; color: #4a6fa5;
      font-size: 15px; cursor: pointer; padding: 2px 5px;
      border-radius: 4px; line-height: 1; transition: color .2s;
    }
    #oc-w-close:hover { color: #00b4d8; }
    #oc-weather.oc-w-open #oc-w-close { display: block; }

    @media (max-width: 480px) {
      #oc-weather { bottom: 14px; left: 10px; }
      #oc-w-card  { min-width: 180px; }
    }
  `;
  document.head.appendChild(styleEl);

  // ── Markup ───────────────────────────────────────────────────────────────────
  const widget = document.createElement('div');
  widget.id = 'oc-weather';
  widget.setAttribute('role', 'complementary');
  widget.setAttribute('aria-label', 'Local weather');
  widget.innerHTML = `
    <div id="oc-w-card">
      <button id="oc-w-close" aria-label="Close forecast">✕</button>
      <div id="oc-w-face">
        <div id="oc-w-emoji">⋯</div>
        <div id="oc-w-right">
          <div id="oc-w-city">Locating…</div>
          <div id="oc-w-time">—</div>
          <div id="oc-w-temp">—</div>
        </div>
      </div>
      <div id="oc-w-detail">
        <span class="oc-w-pill" id="oc-w-cond">—</span>
        <span class="oc-w-pill" id="oc-w-wind">—</span>
      </div>
      <div id="oc-w-hint">▲ tap for 7-day forecast</div>
      <div id="oc-w-forecast">
        <div id="oc-w-fc-header">7-Day Forecast</div>
        <div id="oc-w-fc-rows"></div>
      </div>
    </div>`;
  document.body.appendChild(widget);

  // ── Toggle forecast ───────────────────────────────────────────────────────────
  const card     = document.getElementById('oc-w-card');
  const closeBtn = document.getElementById('oc-w-close');

  card.addEventListener('click', function (e) {
    if (e.target === closeBtn) return;
    widget.classList.add('oc-w-open');
  });
  closeBtn.addEventListener('click', function (e) {
    e.stopPropagation();
    widget.classList.remove('oc-w-open');
  });
  document.addEventListener('click', function (e) {
    if (!widget.contains(e.target)) widget.classList.remove('oc-w-open');
  });

  // ── Fetch with timeout ────────────────────────────────────────────────────────
  function fetchJSON(url) {
    return new Promise(function (resolve, reject) {
      var done = false;
      var timer = setTimeout(function () {
        if (!done) { done = true; reject(new Error('timeout')); }
      }, 7000);
      fetch(url)
        .then(function (r) {
          clearTimeout(timer);
          if (!r.ok) { done = true; reject(new Error('HTTP ' + r.status)); return; }
          return r.json();
        })
        .then(function (d) { if (!done) { done = true; resolve(d); } })
        .catch(function (e) { clearTimeout(timer); if (!done) { done = true; reject(e); } });
    });
  }

  // ── Geo APIs (3 independent fallbacks, ipapi.co removed — requires paid plan) ─
  function getGeo() {
    // 1) ipwho.is — free 10k/month, CORS-safe, returns IANA timezone
    return fetchJSON('https://ipwho.is/')
      .then(function (d) {
        if (!d.success || d.latitude == null) throw new Error('bad data');
        return {
          latitude:    d.latitude,
          longitude:   d.longitude,
          city:        d.city || d.region || 'Your area',
          region_code: d.region_code || '',
          timezone:    (d.timezone && d.timezone.id) ? d.timezone.id : 'UTC'
        };
      })
      .catch(function () {
        // 2) ipinfo.io — free 50k/month, very reliable
        return fetchJSON('https://ipinfo.io/json')
          .then(function (d) {
            if (!d.loc) throw new Error('no loc');
            var parts = d.loc.split(',');
            var lat = parseFloat(parts[0]);
            var lon = parseFloat(parts[1]);
            if (isNaN(lat) || isNaN(lon)) throw new Error('bad coords');
            return {
              latitude:    lat,
              longitude:   lon,
              city:        d.city || 'Your area',
              region_code: '',
              timezone:    d.timezone || 'UTC'
            };
          })
          .catch(function () {
            // 3) geojs.io — free, unlimited, no key
            return fetchJSON('https://get.geojs.io/v1/ip/geo.json')
              .then(function (d) {
                var lat = parseFloat(d.latitude);
                var lon = parseFloat(d.longitude);
                if (isNaN(lat) || isNaN(lon)) throw new Error('bad coords');
                return {
                  latitude:    lat,
                  longitude:   lon,
                  city:        d.city || 'Your area',
                  region_code: '',
                  timezone:    d.timezone || 'UTC'
                };
              });
          });
      });
  }

  // ── Main init ─────────────────────────────────────────────────────────────────
  function init() {
    getGeo()
      .then(function (geo) {
        var wxUrl =
          'https://api.open-meteo.com/v1/forecast' +
          '?latitude='  + geo.latitude +
          '&longitude=' + geo.longitude +
          '&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m' +
          '&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max' +
          '&wind_speed_unit=kmh&timezone=auto&forecast_days=7';

        return fetchJSON(wxUrl).then(function (wx) {
          var tempC  = Math.round(wx.current.temperature_2m);
          var feelsC = Math.round(wx.current.apparent_temperature);
          var wind   = Math.round(wx.current.wind_speed_10m);
          var wc     = cond(wx.current.weather_code);
          var label  = wc[0], emoji = wc[1];
          var cityLine = geo.city + (geo.region_code ? ', ' + geo.region_code : '');

          document.getElementById('oc-w-emoji').textContent = emoji;
          document.getElementById('oc-w-city').textContent  = cityLine;
          document.getElementById('oc-w-temp').textContent  = tempC + '°C / ' + toF(tempC) + '°F';
          document.getElementById('oc-w-cond').textContent  = label;
          document.getElementById('oc-w-wind').textContent  = 'Feels ' + feelsC + '°C · 💨 ' + wind + ' km/h';

          // Validate timezone before using it
          var tz = 'UTC';
          try {
            new Intl.DateTimeFormat('en-US', { timeZone: geo.timezone }).format(new Date());
            tz = geo.timezone;
          } catch (_) {}

          var timeFmt = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit', hour12: true, timeZone: tz });
          var dateFmt = new Intl.DateTimeFormat('en-US', { weekday: 'short', month: 'short', day: 'numeric', timeZone: tz });
          var timeEl  = document.getElementById('oc-w-time');

          function updateClock() {
            var now = new Date();
            timeEl.innerHTML = timeFmt.format(now) + ' <span>· ' + dateFmt.format(now) + '</span>';
          }
          updateClock();
          setInterval(updateClock, 1000);

          // 7-day forecast
          var rows  = document.getElementById('oc-w-fc-rows');
          var daily = wx.daily;
          rows.innerHTML = daily.time.map(function (date, i) {
            var hi   = Math.round(daily.temperature_2m_max[i]);
            var lo   = Math.round(daily.temperature_2m_min[i]);
            var rain = daily.precipitation_probability_max[i] != null ? daily.precipitation_probability_max[i] : 0;
            var emo  = cond(daily.weather_code[i])[1];
            return '<div class="oc-w-day">' +
              '<span class="oc-w-dn">' + dayName(date, i) + '</span>' +
              '<span class="oc-w-de">' + emo + '</span>' +
              '<span class="oc-w-range"><strong>' + hi + '°</strong> / ' + lo + '°</span>' +
              '<span class="oc-w-rain">💧 ' + rain + '%</span>' +
              '</div>';
          }).join('');

          widget.classList.add('oc-w-ready');
        });
      })
      .catch(function (err) {
        console.warn('OceanCloud weather:', err.message);
        widget.remove();
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
