/* Оживление сайта: появление секций при прокрутке + интерактивная
   сеть-«молекула» в hero (отсылка к логотипу). Без библиотек.
   Уважает prefers-reduced-motion: вся анимация отключается. */
(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Появление при прокрутке ---------- */
  var toReveal = document.querySelectorAll('.lab-card, .panel, .launch-panel, .contacts dl');
  if (!reduced && 'IntersectionObserver' in window) {
    toReveal.forEach(function (el) { el.classList.add('reveal'); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    toReveal.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Сеть-«молекула» в hero ---------- */
  var canvas = document.getElementById('molecules');
  if (!canvas || reduced) return;
  var ctx = canvas.getContext('2d');
  var wrap = canvas.parentElement;
  var W, H, dots = [], mouse = { x: -9999, y: -9999 };
  var ORANGE = 'rgba(238, 114, 3, ';
  var GREEN = 'rgba(26, 86, 50, ';
  var N = 26, LINK = 120;

  function resize() {
    W = canvas.width = wrap.offsetWidth;
    H = canvas.height = wrap.offsetHeight;
  }
  function seed() {
    dots = [];
    for (var i = 0; i < N; i++) {
      dots.push({
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.35, vy: (Math.random() - 0.5) * 0.35,
        r: 2.2 + Math.random() * 2.4,
        green: Math.random() < 0.25
      });
    }
  }
  function step() {
    ctx.clearRect(0, 0, W, H);
    for (var i = 0; i < N; i++) {
      var d = dots[i];
      d.x += d.vx; d.y += d.vy;
      if (d.x < 0 || d.x > W) d.vx *= -1;
      if (d.y < 0 || d.y > H) d.vy *= -1;
      /* лёгкое отталкивание от курсора */
      var dx = d.x - mouse.x, dy = d.y - mouse.y, dist = Math.hypot(dx, dy);
      if (dist < 90 && dist > 0.01) { d.x += dx / dist * 1.1; d.y += dy / dist * 1.1; }
    }
    for (i = 0; i < N; i++) {
      for (var j = i + 1; j < N; j++) {
        var a = dots[i], b = dots[j];
        var L = Math.hypot(a.x - b.x, a.y - b.y);
        if (L < LINK) {
          ctx.strokeStyle = ORANGE + (0.16 * (1 - L / LINK)) + ')';
          ctx.lineWidth = 1.4;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        }
      }
    }
    for (i = 0; i < N; i++) {
      var p = dots[i];
      ctx.fillStyle = (p.green ? GREEN : ORANGE) + '0.55)';
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
    }
    requestAnimationFrame(step);
  }
  wrap.addEventListener('mousemove', function (e) {
    var r = canvas.getBoundingClientRect();
    mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
  });
  wrap.addEventListener('mouseleave', function () { mouse.x = mouse.y = -9999; });
  window.addEventListener('resize', function () { resize(); seed(); });
  resize(); seed(); step();
})();
