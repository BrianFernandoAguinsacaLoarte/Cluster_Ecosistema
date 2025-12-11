// Climate system simulation worker - Fetches data from API
let running = false;
let ctx = null;
let width = 400, height = 300;
let apiUrl = '/api/data/climate';

function initCanvas(offscreen) {
  if (offscreen) ctx = offscreen.getContext('2d');
}

let clouds = [];
let temperature = 20;
let humidity = 0.5;

function reset() {
  clouds = [];
}

function drawFallback() {
  const ops = [{ cmd: 'clear', args: [] }];
  clouds.forEach(c => {
    ops.push({ cmd: 'image', args: ['/static/img/nube.png', c.x - c.size/2, c.y - c.size/2, c.size, c.size] });
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
    clouds = data.data.map(c => ({ x: c.x, y: c.y, vx: c.vx, size: c.size }));
    if (clouds.length > 0) {
      temperature = clouds.reduce((s,c)=>s+(c.temperature||20),0)/clouds.length;
      humidity = clouds.reduce((s,c)=>s+(c.humidity||0.5),0)/clouds.length;
    }
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
      postMessage({ type: 'stats', payload: { text: `Temp: ${temperature.toFixed(1)}°C | Humedad: ${(humidity*100).toFixed(0)}% | Nodos: ${apiData.count}` } });
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