// Trees simulation worker - Fetches data from API
let running = false;
let ctx = null;
let width = 400, height = 300;
let apiUrl = '/api/data/trees';

function initCanvas(offscreen) {
  if (offscreen) {
    ctx = offscreen.getContext('2d');
  }
}

let trees = [];
function reset() {
  trees = [];
}

function drawFallback() {
  // Prepare draw ops with image for main thread
  const ops = [{ cmd: 'clear', args: [] }];
  trees.forEach(t => {
    ops.push({ cmd: 'image', args: ['/static/img/arbol.png', t.x - 15, t.y - 30, 30, 30] });
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
    trees = data.data.map(t => ({ x: t.x, y: t.y, h: t.height || 30, growth: t.growth || 0.2 }));
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
      const avgH = trees.length > 0 ? Math.round(trees.reduce((a,b)=>a+b.h,0)/trees.length) : 0;
      postMessage({ type: 'stats', payload: { text: `Árboles: ${trees.length} | Nodos: ${apiData.count} | Altura media: ${avgH}` } });
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