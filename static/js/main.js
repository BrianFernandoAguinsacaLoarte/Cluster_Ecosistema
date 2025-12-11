// Main controller for ecosystem simulations using Web Workers
// Each module has its own worker and canvas

const modules = {
  trees: { canvasId: 'trees-canvas', statsId: 'trees-stats', workerPath: '/static/js/workers/trees.js' },
  life: { canvasId: 'life-canvas', statsId: 'life-stats', workerPath: '/static/js/workers/life.js' },
  food: { canvasId: 'food-canvas', statsId: 'food-stats', workerPath: '/static/js/workers/food.js' },
  climate: { canvasId: 'climate-canvas', statsId: 'climate-stats', workerPath: '/static/js/workers/climate.js' },
};

const workers = {}; // hold active workers
const imageCache = {}; // cache loaded images

// Preload images with promises
function preloadImages() {
  const images = [
    '/static/img/arbol.png',
    '/static/img/leon.png',
    '/static/img/manzana.jpg',
    '/static/img/nube.png'
  ];
  
  const promises = images.map(src => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        imageCache[src] = img;
        console.log('Loaded:', src);
        resolve(img);
      };
      img.onerror = () => {
        console.error('Failed to load:', src);
        reject(new Error(`Failed to load ${src}`));
      };
      img.src = src;
    });
  });
  
  return Promise.all(promises);
}

function startModule(name) {
  const mod = modules[name];
  if (!mod) return;
  // Stop existing worker if any before starting
  stopModule(name);

  const canvas = document.getElementById(mod.canvasId);
  const statsEl = document.getElementById(mod.statsId);

  // Don't use OffscreenCanvas for now because images can't be loaded in workers
  const worker = new Worker(mod.workerPath, { type: 'module' });
  workers[name] = worker;

  // Initialize worker without canvas transfer
  const initMsg = { type: 'init', payload: { width: canvas.width, height: canvas.height } };
  worker.postMessage(initMsg);

  // Listen for updates
  worker.onmessage = (ev) => {
    const { type, payload } = ev.data || {};
    if (type === 'stats') {
      statsEl.textContent = payload.text;
    } else if (type === 'draw') {
      // Draw on main thread
      const ctx = canvas.getContext('2d');
      const { ops } = payload;
      ops.forEach((op) => {
        const { cmd, args } = op;
        if (cmd === 'clear') {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
        } else if (cmd === 'image') {
          const [src, x, y, w, h] = args;
          const img = imageCache[src];
          if (img && img.complete) {
            ctx.drawImage(img, x, y, w, h);
          } else {
            console.warn('Image not loaded:', src);
          }
        } else if (cmd === 'circle') {
          const [x, y, r, color] = args;
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(x, y, r, 0, Math.PI * 2);
          ctx.fill();
        } else if (cmd === 'rect') {
          const [x, y, w, h, color] = args;
          ctx.fillStyle = color;
          ctx.fillRect(x, y, w, h);
        }
      });
    }
  };
}

function stopModule(name) {
  const worker = workers[name];
  if (worker) {
    worker.postMessage({ type: 'stop' });
    worker.terminate();
    delete workers[name];
  }
}

// Wire buttons
function wireControls() {
  document.querySelectorAll('button[data-action][data-module]').forEach((btn) => {
    const action = btn.getAttribute('data-action');
    const mod = btn.getAttribute('data-module');
    btn.addEventListener('click', () => {
      if (action === 'start') startModule(mod);
      else if (action === 'stop') stopModule(mod);
    });
  });
}

// Auto start all on load
window.addEventListener('DOMContentLoaded', () => {
  wireControls();
  console.log('Preloading images...');
  preloadImages()
    .then(() => {
      console.log('All images loaded, starting modules...');
      Object.keys(modules).forEach(startModule);
    })
    .catch(err => {
      console.error('Error loading images:', err);
      // Start anyway with fallback
      Object.keys(modules).forEach(startModule);
    });
});
