(function () {
  'use strict';

  var DEFAULT_CONFIG = {
    count:   80,
    color:   '0,180,216',
    maxDist: 130,
    speed:   0.25,
    dotSize: 2,
    opacity: 0.40
  };

  function parseConfig(el) {
    var raw = el.getAttribute('data-particles');
    if (!raw) return Object.assign({}, DEFAULT_CONFIG);
    try {
      return Object.assign({}, DEFAULT_CONFIG, JSON.parse(raw));
    } catch (e) {
      return Object.assign({}, DEFAULT_CONFIG);
    }
  }

  function initCanvas(canvas) {
    var cfg  = parseConfig(canvas);
    var ctx  = canvas.getContext('2d');
    var dots = [];
    var raf  = null;

    function resize() {
      canvas.width  = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    }

    function createDots() {
      dots = [];
      for (var i = 0; i < cfg.count; i++) {
        dots.push({
          x:  Math.random() * canvas.width,
          y:  Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * cfg.speed * 2,
          vy: (Math.random() - 0.5) * cfg.speed * 2,
          r:  cfg.dotSize > 0 ? cfg.dotSize : 2
        });
      }
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // move dots
      dots.forEach(function (d) {
        d.x += d.vx;
        d.y += d.vy;
        if (d.x < 0 || d.x > canvas.width)  d.vx *= -1;
        if (d.y < 0 || d.y > canvas.height) d.vy *= -1;
      });

      // draw connections
      var maxDist2 = cfg.maxDist * cfg.maxDist;
      for (var i = 0; i < dots.length; i++) {
        for (var j = i + 1; j < dots.length; j++) {
          var dx = dots[i].x - dots[j].x;
          var dy = dots[i].y - dots[j].y;
          var dist2 = dx * dx + dy * dy;
          if (dist2 < maxDist2) {
            var ratio = 1 - Math.sqrt(dist2) / cfg.maxDist;
            ctx.beginPath();
            ctx.strokeStyle = 'rgba(' + cfg.color + ',' + (cfg.opacity * ratio * 0.6) + ')';
            ctx.lineWidth = 0.8;
            ctx.moveTo(dots[i].x, dots[i].y);
            ctx.lineTo(dots[j].x, dots[j].y);
            ctx.stroke();
          }
        }
      }

      // draw dots
      dots.forEach(function (d) {
        ctx.beginPath();
        ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + cfg.color + ',' + cfg.opacity + ')';
        ctx.fill();
      });

      raf = requestAnimationFrame(draw);
    }

    function start() {
      if (raf) cancelAnimationFrame(raf);
      resize();
      createDots();
      draw();
    }

    // Handle resize: debounce
    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(start, 150);
    });

    start();
  }

  function initAll() {
    var canvases = document.querySelectorAll('canvas[data-particles]');
    canvases.forEach(function (canvas) {
      initCanvas(canvas);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }
}());
