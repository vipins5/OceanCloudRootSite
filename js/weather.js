(function () {
  'use strict';

  // WMO weather code → [label, emoji]
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
      position: fixed;
      bottom: 24px;
      left: 24px;
      z-index: 9000;
      font-family: 'Inter', system-ui, sans-serif;
      opacity: 0;
      transform: translateY(12px);
      transition: opacity .4s ease, transform .4s ease;
      pointer-events: none;
    }
    #oc-weather.oc-w-ready {
      opacity: 1;
      transform: translateY(0);
      pointer-events: auto;
    }

    #oc-w-card {
      background: rgba(7, 26, 46, 0.94);
      border: 1px solid rgba(0, 180, 216, 0.28);
      border-radius: 16px;
      backdrop-filter: blur(14px);
      box-shadow: 0 8px 32px rgba(0,0,0,.5);
      padding: 12px 14px 10px;
      min-width: 200px;
      cursor: pointer;
      user-select: none;
      transition: border-color .2s;
    }
    #oc-w-card:hover { border-color: rgba(0,180,216,.55); }

    /* Current conditions */
    #oc-w-face {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    #oc-w-emoji {
      font-size: 30px;
      line-height: 1;
      flex-shrink: 0;
    }
    #oc-w-right { flex: 1; min-width: 0; }
    #oc-w-city {
      font-size: 11px;
      font-weight: 600;
      color: #00b4d8;
      letter-spacing: .4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    #oc-w-time {
      font-size: 11px;
      font-weight: 500;
      color: #5d8aa8;
      margin-top: 1px;
      letter-spacing: .2px;
    }
    #oc-w-time span {
      color: #8ba3bb;
      font-weight: 400;
    }
    #oc-w-temp {
      font-size: 18px;
      font-weight: 700;
      color: #f0f4f8;
      line-height: 1.2;
      margin-top: 2px;
    }
    #oc-w-detail {
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid rgba(255,255,255,.08);
      display: flex;
      justify-content: space-between;
      gap: 6px;
    }
    .oc-w-pill {
      font-size: 10.5px;
      color: #8ba3bb;
      white-space: nowrap;
    }

    /* Hint arrow */
    #oc-w-hint {
      text-align: center;
      font-size: 10px;
      color: #3d6080;
      margin-top: 7px;
      letter-spacing: .3px;
      transition: color .2s;
    }
    #oc-w-card:hover #oc-w-hint { color: #00b4d8; }

    /* Forecast panel */
    #oc-w-forecast {
      max-height: 0;
      overflow: hidden;
      transition: max-height .35s ease, opacity .3s ease, margin .3s ease;
      opacity: 0;
      margin-top: 0;
    }
    #oc-weather.oc-w-open #oc-w-forecast {
      max-height: 320px;
      opacity: 1;
      margin-top: 10px;
    }
    #oc-weather.oc-w-open #oc-w-hint { display: none; }

    #oc-w-fc-header {
      font-size: 10px;
      font-weight: 700;
      color: #4a6fa5;
      letter-spacing: .8px;
      text-transform: uppercase;
      margin-bottom: 6px;
      padding-top: 8px;
      border-top: 1px solid rgba(255,255,255,.08);
    }

    .oc-w-day {
      display: grid;
      grid-template-columns: 38px 26px 1fr auto;
      align-items: center;
      gap: 6px;
      padding: 5px 0;
      border-bottom: 1px solid rgba(255,255,255,.05);
    }
    .oc-w-day:last-child { border-bottom: none; }
    .oc-w-dn {
      font-size: 11px;
      font-weight: 600;
      color: #c8daea;
    }
    .oc-w-day:first-child .oc-w-dn { color: #00b4d8; }
    .oc-w-de { font-size: 16px; line-height: 1; }
    .oc-w-range {
      font-size: 11px;
      color: #8ba3bb;
      white-space: nowrap;
    }
    .oc-w-range strong { color: #e0eaf4; font-weight: 600; }
    .oc-w-rain {
      font-size: 10.5px;
      color: #4a8fa5;
      text-align: right;
      white-space: nowrap;
    }

    /* Close button */
    #oc-w-close {
      display: none;
      position: absolute;
      top: 7px;
      right: 9px;
      background: none;
      border: none;
      color: #4a6fa5;
      font-size: 15px;
      cursor: pointer;
      padding: 2px 5px;
      border-radius: 4px;
      line-height: 1;
      transition: color .2s;
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
  const hint     = document.getElementById('oc-w-hint');

  function openForecast(e) {
    if (e.target === closeBtn) return;
    widget.classList.add('oc-w-open');
  }
  function closeForecast(e) {
    e.stopPropagation();
    widget.classList.remove('oc-w-open');
  }

  card.addEventListener('click', openForecast);
  closeBtn.addEventListener('click', closeForecast);

  // Close on outside click
  document.addEventListener('click', e => {
    if (!widget.contains(e.target)) widget.classList.remove('oc-w-open');
  });

  // ── Data fetch ───────────────────────────────────────────────────────────────
  async function init() {
    try {
      // Step 1 — IP geolocation
      const geoRes = await fetch('https://ipapi.co/json/');
      if (!geoRes.ok) throw new Error('geo');
      const geo = await geoRes.json();
      if (!geo.latitude || !geo.longitude) throw new Error('no coords');

      // Step 2 — current + 7-day forecast from Open-Meteo (no API key)
      const wxUrl =
        `https://api.open-meteo.com/v1/forecast` +
        `?latitude=${geo.latitude}&longitude=${geo.longitude}` +
        `&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m` +
        `&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max` +
        `&wind_speed_unit=kmh&timezone=auto&forecast_days=7`;

      const wxRes = await fetch(wxUrl);
      if (!wxRes.ok) throw new Error('weather');
      const wx = await wxRes.json();

      // Current conditions
      const tempC  = Math.round(wx.current.temperature_2m);
      const feelsC = Math.round(wx.current.apparent_temperature);
      const wind   = Math.round(wx.current.wind_speed_10m);
      const [label, emoji] = cond(wx.current.weather_code);
      const city   = geo.city || geo.region || 'Your area';
      const region = geo.region_code ? `, ${geo.region_code}` : '';

      document.getElementById('oc-w-emoji').textContent = emoji;
      document.getElementById('oc-w-city').textContent  = city + region;
      document.getElementById('oc-w-temp').textContent  = `${tempC}°C / ${toF(tempC)}°F`;
      document.getElementById('oc-w-cond').textContent  = label;
      document.getElementById('oc-w-wind').textContent  = `Feels ${feelsC}°C · 💨 ${wind} km/h`;

      // Live local clock using visitor's timezone
      const tz       = geo.timezone;
      const timeFmt  = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit', hour12: true, timeZone: tz });
      const dateFmt  = new Intl.DateTimeFormat('en-US', { weekday: 'short', month: 'short', day: 'numeric', timeZone: tz });
      const timeEl   = document.getElementById('oc-w-time');

      function updateClock() {
        const now = new Date();
        timeEl.innerHTML = `${timeFmt.format(now)} <span>· ${dateFmt.format(now)}</span>`;
      }
      updateClock();
      setInterval(updateClock, 1000);

      // 7-day forecast rows
      const rows  = document.getElementById('oc-w-fc-rows');
      const daily = wx.daily;
      rows.innerHTML = daily.time.map((date, i) => {
        const hi   = Math.round(daily.temperature_2m_max[i]);
        const lo   = Math.round(daily.temperature_2m_min[i]);
        const rain = daily.precipitation_probability_max[i] ?? 0;
        const [, emo] = cond(daily.weather_code[i]);
        return `<div class="oc-w-day">
          <span class="oc-w-dn">${dayName(date, i)}</span>
          <span class="oc-w-de">${emo}</span>
          <span class="oc-w-range"><strong>${hi}°</strong> / ${lo}°</span>
          <span class="oc-w-rain">💧 ${rain}%</span>
        </div>`;
      }).join('');

      widget.classList.add('oc-w-ready');

    } catch (_) {
      widget.remove();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
