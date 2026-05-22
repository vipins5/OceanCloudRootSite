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

  function toF(c) { return Math.round(c * 9 / 5 + 32); }
  function condition(code) { return WMO[code] || ['—', '🌡️']; }

  // ── Styles ──────────────────────────────────────────────────────────────────
  const css = `
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
    #oc-weather.oc-w-mini #oc-w-detail { display: none; }
    #oc-weather.oc-w-mini #oc-w-face { gap: 6px; }

    #oc-w-card {
      background: rgba(7, 26, 46, 0.92);
      border: 1px solid rgba(0, 180, 216, 0.25);
      border-radius: 14px;
      backdrop-filter: blur(12px);
      box-shadow: 0 8px 32px rgba(0,0,0,.45);
      padding: 12px 14px 10px;
      min-width: 170px;
      cursor: default;
      user-select: none;
    }

    #oc-w-face {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    #oc-w-emoji {
      font-size: 28px;
      line-height: 1;
      flex-shrink: 0;
    }
    #oc-w-right {
      flex: 1;
      min-width: 0;
    }
    #oc-w-city {
      font-size: 11px;
      font-weight: 600;
      color: #00b4d8;
      letter-spacing: .4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    #oc-w-temp {
      font-size: 17px;
      font-weight: 700;
      color: #f0f4f8;
      line-height: 1.2;
      margin-top: 1px;
    }

    #oc-w-detail {
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid rgba(255,255,255,.08);
      display: flex;
      justify-content: space-between;
      gap: 8px;
    }
    .oc-w-pill {
      font-size: 10.5px;
      color: #8ba3bb;
      white-space: nowrap;
    }

    #oc-w-toggle {
      position: absolute;
      top: 6px;
      right: 8px;
      background: none;
      border: none;
      color: #4a6fa5;
      font-size: 13px;
      line-height: 1;
      cursor: pointer;
      padding: 2px 4px;
      border-radius: 4px;
      transition: color .2s;
    }
    #oc-w-toggle:hover { color: #00b4d8; }

    @media (max-width: 480px) {
      #oc-weather { bottom: 16px; left: 12px; }
    }
  `;

  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // ── Markup ───────────────────────────────────────────────────────────────────
  const widget = document.createElement('div');
  widget.id = 'oc-weather';
  widget.setAttribute('role', 'complementary');
  widget.setAttribute('aria-label', 'Local weather');
  widget.innerHTML = `
    <div id="oc-w-card">
      <button id="oc-w-toggle" aria-label="Toggle weather detail" title="Minimise">−</button>
      <div id="oc-w-face">
        <div id="oc-w-emoji">⋯</div>
        <div id="oc-w-right">
          <div id="oc-w-city">Locating…</div>
          <div id="oc-w-temp">—</div>
        </div>
      </div>
      <div id="oc-w-detail">
        <span class="oc-w-pill" id="oc-w-cond">—</span>
        <span class="oc-w-pill" id="oc-w-wind">—</span>
      </div>
    </div>`;
  document.body.appendChild(widget);

  // ── Toggle minimise ──────────────────────────────────────────────────────────
  const toggleBtn = document.getElementById('oc-w-toggle');
  toggleBtn.addEventListener('click', () => {
    const mini = widget.classList.toggle('oc-w-mini');
    toggleBtn.textContent = mini ? '+' : '−';
    toggleBtn.title = mini ? 'Expand' : 'Minimise';
  });

  // ── Data fetch ───────────────────────────────────────────────────────────────
  async function init() {
    try {
      // Step 1 — get location from IP
      const geoRes = await fetch('https://ipapi.co/json/');
      if (!geoRes.ok) throw new Error('geo');
      const geo = await geoRes.json();
      if (!geo.latitude || !geo.longitude) throw new Error('no coords');

      // Step 2 — get weather from Open-Meteo (no API key needed)
      const wxUrl =
        `https://api.open-meteo.com/v1/forecast` +
        `?latitude=${geo.latitude}&longitude=${geo.longitude}` +
        `&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m` +
        `&wind_speed_unit=kmh&timezone=auto`;
      const wxRes = await fetch(wxUrl);
      if (!wxRes.ok) throw new Error('weather');
      const wx = await wxRes.json();

      const tempC   = Math.round(wx.current.temperature_2m);
      const feelsC  = Math.round(wx.current.apparent_temperature);
      const windKmh = Math.round(wx.current.wind_speed_10m);
      const [label, emoji] = condition(wx.current.weather_code);

      const city   = geo.city || geo.region || 'Your area';
      const region = geo.region_code ? `, ${geo.region_code}` : '';

      document.getElementById('oc-w-emoji').textContent = emoji;
      document.getElementById('oc-w-city').textContent  = city + region;
      document.getElementById('oc-w-temp').textContent  = `${tempC}°C / ${toF(tempC)}°F`;
      document.getElementById('oc-w-cond').textContent  = label;
      document.getElementById('oc-w-wind').textContent  = `Feels ${feelsC}°C · 💨 ${windKmh} km/h`;

      widget.classList.add('oc-w-ready');

    } catch (_) {
      widget.remove();
    }
  }

  // Defer so it doesn't block page render
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
