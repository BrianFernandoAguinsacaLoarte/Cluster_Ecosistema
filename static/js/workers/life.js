// Life simulation worker - Fetches data from API
let running = false;
let ctx = null;
let width = 400, height = 300;
let apiUrl = '/api/data/life';

function initCanvas(offscreen) {
  if (offscreen) ctx = offscreen.getContext('2d');
}

let animals = [];
function reset() {
  animals = [];
}

function drawFallback() {
  const ops = [{ cmd: 'clear', args: [] }];
  animals.forEach(a => {
    ops.push({ cmd: 'image', args: ['/static/img/leon.png', a.x - 12, a.y - 12, 24, 24] });
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
    animals = data.data.map(a => ({ x: a.x, y: a.y, vx: a.vx, vy: a.vy, energy: a.energy }));
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
      const avgEnergy = animals.length > 0 ? Math.round(animals.reduce((s,a)=>s+a.energy,0)/animals.length) : 0;
      postMessage({ type: 'stats', payload: { text: `Animales: ${animals.length} | Nodos: ${apiData.count} | Energía: ${avgEnergy}` } });
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