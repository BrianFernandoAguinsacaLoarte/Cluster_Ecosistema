// Food resources simulation worker - Fetches data from API
let running = false;
let ctx = null;
let width = 400, height = 300;
let apiUrl = '/api/data/food';

function initCanvas(offscreen) {
  if (offscreen) ctx = offscreen.getContext('2d');
}

let resources = [];
function reset() {
  resources = [];
}

function drawFallback() {
  const ops = [{ cmd: 'clear', args: [] }];
  resources.forEach(r => {
    const size = Math.max(15, r.amount * 0.2);
    ops.push({ cmd: 'image', args: ['/static/img/comida.png', r.x - size / 2, r.y - size / 2, size, size] });
  });
  postMessage({ type: 'draw', payload: { ops } });
}

function draw() {
  // Always use fallback because images must be drawn on main thread
  drawFallback();
}

async function fetchData() {
  try {
    const response = await fetch(apiUrl);
    const data = await response.json();
    resources = data.data.map(r => ({ x: r.x, y: r.y, amount: r.amount, regen: r.regen }));
    return data;
  } catch (e) {
    return null;
  }
}

function tick() {
  if (!running) return;
  fetchData().then(apiData => {
    if (apiData) {
      draw();
      const avg = resources.length > 0 ? Math.round(resources.reduce((s, r) => s + r.amount, 0) / resources.length) : 0;
      postMessage({ type: 'stats', payload: { text: `Recursos: ${resources.length} | Nodos: ${apiData.count} | Promedio: ${avg}` } });
    }
    setTimeout(tick, 1000);
  });
}

onmessage = (ev) => {
  const { type, payload, canvas } = ev.data || {};
  if (type === 'init') {
    width = payload.width; height = payload.height;
    if (canvas) initCanvas(canvas);
    reset(); running = true; tick();
  } else if (type === 'stop') {
    running = false;
  }
};