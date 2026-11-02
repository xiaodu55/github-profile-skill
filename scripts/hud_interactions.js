
/* ---------- 启动序列 ---------- */
(function () {
  var overlay = document.getElementById('bootOverlay');
  if (!overlay) { return; }
  var lines = (window.SITE_CONTENT && window.SITE_CONTENT.boot_lines) || [
    '> loading operator profile ... ok',
    '> all subsystems nominal. welcome, operator.'
  ];
  var log = document.getElementById('bootLog');
  var bar = document.getElementById('bootProgress');
  var index = 0;
  var timer = setInterval(function () {
    if (log) { log.innerHTML = lines[Math.min(index, lines.length - 1)]; }
    if (bar) { bar.style.width = Math.min((index + 1) * (100 / lines.length), 100) + '%'; }
    index += 1;
    if (index > lines.length) {
      clearInterval(timer);
      overlay.classList.add('done');
      setTimeout(function () { if (overlay.parentNode) { overlay.parentNode.removeChild(overlay); } }, 600);
    }
  }, 320);
})();

/* ---------- 神经网络背景 ---------- */
(function () {
  var canvas = document.getElementById('neuralCanvas');
  if (!canvas) { return; }
  var ctx = canvas.getContext('2d');
  var nodes = [];
  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    var count = Math.min(70, Math.round(window.innerWidth / 26));
    nodes = [];
    for (var i = 0; i < count; i += 1) {
      nodes.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.28,
        vy: (Math.random() - 0.5) * 0.28,
        r: Math.random() * 1.6 + 0.6
      });
    }
  }
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (var i = 0; i < nodes.length; i += 1) {
      var a = nodes[i];
      a.x += a.vx; a.y += a.vy;
      if (a.x < 0 || a.x > canvas.width) { a.vx *= -1; }
      if (a.y < 0 || a.y > canvas.height) { a.vy *= -1; }
      ctx.beginPath();
      ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0, 240, 255, .32)';
      ctx.fill();
      for (var j = i + 1; j < nodes.length; j += 1) {
        var b = nodes[j];
        var dx = a.x - b.x, dy = a.y - b.y;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 140) {
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = 'rgba(0, 240, 255, ' + (0.13 * (1 - dist / 140)) + ')';
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  resize();
  window.addEventListener('resize', resize);
  draw();
})();

/* ---------- 雷达扫描 ---------- */
(function () {
  var canvas = document.getElementById('radarCanvas');
  if (!canvas) { return; }
  var ctx = canvas.getContext('2d');
  var azimuth = document.getElementById('radarAzimuth');
  var angle = 0;
  function resize() {
    var size = canvas.clientWidth || 280;
    canvas.width = size;
    canvas.height = size;
  }
  function draw() {
    var w = canvas.width, h = canvas.height;
    var cx = w / 2, cy = h / 2, r = Math.min(w, h) / 2 - 6;
    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = 'rgba(0, 240, 255, .26)';
    ctx.lineWidth = 1;
    for (var i = 1; i <= 3; i += 1) {
      ctx.beginPath();
      ctx.arc(cx, cy, (r / 3) * i, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.beginPath();
    ctx.moveTo(cx - r, cy); ctx.lineTo(cx + r, cy);
    ctx.moveTo(cx, cy - r); ctx.lineTo(cx, cy + r);
    ctx.stroke();
    var gradient = ctx.createLinearGradient(cx, cy, cx + Math.cos(angle) * r, cy + Math.sin(angle) * r);
    gradient.addColorStop(0, 'rgba(0, 240, 255, 0)');
    gradient.addColorStop(1, 'rgba(0, 240, 255, .3)');
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, r, angle - 0.5, angle);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();
    if (azimuth) {
      azimuth.textContent = (Math.round(angle * 180 / Math.PI) % 360).toString().padStart(3, '0') + '°';
    }
    angle += 0.012;
    requestAnimationFrame(draw);
  }
  resize();
  window.addEventListener('resize', resize);
  draw();
})();

/* ---------- 双语切换 ---------- */
(function () {
  var button = document.getElementById('langToggleBtn');
  var current = document.getElementById('langCurrent');
  var alt = document.getElementById('langAlt');
  if (!button || !window.SITE_I18N) { return; }
  var lang = 'zh';
  function apply() {
    var dict = window.SITE_I18N[lang] || {};
    document.querySelectorAll('[data-bind]').forEach(function (node) {
      var value = dict[node.getAttribute('data-bind')];
      if (typeof value === 'string') { node.textContent = value; }
    });
    if (current) { current.textContent = lang.toUpperCase(); }
    if (alt) { alt.textContent = lang === 'zh' ? 'EN' : 'ZH'; }
  }
  button.addEventListener('click', function () {
    lang = lang === 'zh' ? 'en' : 'zh';
    apply();
  });
  apply();
})();

/* ---------- 终端输入 ---------- */
(function () {
  var input = document.getElementById('termInput');
  var output = document.getElementById('termOutput');
  if (!input || !output) { return; }
  var commands = (window.SITE_CONTENT && window.SITE_CONTENT.terminal && window.SITE_CONTENT.terminal.commands) || {};
  function write(text, tone) {
    var line = document.createElement('div');
    line.className = 'term-line' + (tone ? ' ' + tone : '');
    line.textContent = text;
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
  }
  input.addEventListener('keydown', function (event) {
    if (event.key !== 'Enter') { return; }
    var raw = input.value.trim();
    if (!raw) { return; }
    input.value = '';
    write('duk@agent-ops ~ ' + raw, 'ok');
    var key = raw.toLowerCase();
    if (key === 'clear') { output.innerHTML = ''; return; }
    if (commands[key]) {
      write(commands[key], 'warn');
    } else {
      write("未知命令。输入 'help' 查看可用命令。", 'err');
    }
  });
})();
