// Main controller for ecosystem simulations
// Handles tab switching, data detection, and rendering

const modules = {
  trees: { canvasId: 'trees-canvas', statsId: 'trees-stats', statusId: 'trees-status', overlayId: 'trees-overlay', workerPath: '/static/js/workers/trees.js', color: '#10b981', icon: '🌳' },
  life: { canvasId: 'life-canvas', statsId: 'life-stats', statusId: 'life-status', overlayId: 'life-overlay', workerPath: '/static/js/workers/life.js', color: '#ef4444', icon: '🦁' },
  food: { canvasId: 'food-canvas', statsId: 'food-stats', statusId: 'food-status', overlayId: 'food-overlay', workerPath: '/static/js/workers/food.js', color: '#f59e0b', icon: '🍎' },
  climate: { canvasId: 'climate-canvas', statsId: 'climate-stats', statusId: 'climate-status', overlayId: 'climate-overlay', workerPath: '/static/js/workers/climate.js', color: '#3b82f6', icon: '☁️' },
};

const workers = {};
const imageCache = {};
const moduleData = {}; // Store latest data for each module
const moduleLastUpdate = {}; // Track last update time
const DATA_TIMEOUT = 5000; // 5 seconds without data = inactive

// Preload images
function preloadImages() {
  const images = [
    '/static/img/arbol.png',
    '/static/img/leon.png',
    '/static/img/comida.png',
    '/static/img/nube.png'
  ];

  const promises = images.map(src => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        imageCache[src] = img;
        console.log('✓ Loaded:', src);
        resolve(img);
      };
      img.onerror = () => {
        console.error('✗ Failed to load:', src);
        reject(new Error(`Failed to load ${src}`));
      };
      img.src = src;
    });
  });

  return Promise.all(promises);
}

// Tab switching
function setupTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');

      // Update buttons
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Update content
      tabContents.forEach(content => {
        if (content.id === `${targetTab}-view`) {
          content.classList.add('active');
        } else {
          content.classList.remove('active');
        }
      });
    });
  });
}

// Check if module has recent data
function isModuleActive(moduleName) {
  const lastUpdate = moduleLastUpdate[moduleName];
  if (!lastUpdate) return false;
  return (Date.now() - lastUpdate) < DATA_TIMEOUT;
}

// Update module status UI
function updateModuleStatus(moduleName, hasData) {
  const mod = modules[moduleName];
  const statusBadge = document.getElementById(mod.statusId);
  const overlay = document.getElementById(mod.overlayId);
  const moduleIndicator = document.querySelector(`.module-indicator[data-module="${moduleName}"]`);

  if (hasData) {
    statusBadge.textContent = 'Activo';
    statusBadge.classList.add('active');
    overlay.classList.remove('show');
    if (moduleIndicator) moduleIndicator.classList.add('active');
  } else {
    statusBadge.textContent = 'Sin datos';
    statusBadge.classList.remove('active');
    overlay.classList.add('show');
    if (moduleIndicator) moduleIndicator.classList.remove('active');
  }
}

// Update combined stats
function updateCombinedStats() {
  Object.keys(modules).forEach(moduleName => {
    const data = moduleData[moduleName];
    const statCard = document.getElementById(`stat-${moduleName}`);
    const statValue = statCard.querySelector('.stat-value');

    if (data && isModuleActive(moduleName)) {
      statValue.textContent = data.length || 0;
    } else {
      statValue.textContent = '-';
    }
  });

  // Update combined overlay
  const activeModules = Object.keys(modules).filter(isModuleActive);
  const combinedOverlay = document.getElementById('combined-overlay');

  if (activeModules.length === 0) {
    combinedOverlay.classList.add('show');
  } else {
    combinedOverlay.classList.remove('show');
  }
}

// Draw combined canvas
function drawCombinedCanvas() {
  const canvas = document.getElementById('combined-canvas');
  const ctx = canvas.getContext('2d');

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Only draw active modules
  Object.keys(modules).forEach(moduleName => {
    if (!isModuleActive(moduleName)) return;

    const data = moduleData[moduleName];
    if (!data || data.length === 0) return;

    const mod = modules[moduleName];

    data.forEach(item => {
      // Scale coordinates to combined canvas
      const scaleX = canvas.width / 400;
      const scaleY = canvas.height / 300;
      const x = item.x * scaleX;
      const y = item.y * scaleY;

      // Draw based on module type
      if (moduleName === 'trees') {
        const img = imageCache['/static/img/arbol.png'];
        if (img && img.complete) {
          const h = (item.height || 30) * scaleY;
          ctx.drawImage(img, x - 10 * scaleX, y - h, 20 * scaleX, h);
        }
      } else if (moduleName === 'life') {
        const img = imageCache['/static/img/leon.png'];
        if (img && img.complete) {
          ctx.drawImage(img, x - 15 * scaleX, y - 15 * scaleY, 30 * scaleX, 30 * scaleY);
        }
      } else if (moduleName === 'food') {
        const img = imageCache['/static/img/comida.png'];
        if (img && img.complete) {
          const size = ((item.amount || 50) / 100 * 20 + 10) * scaleX;
          ctx.drawImage(img, x - size / 2, y - size / 2, size, size);
        }
      } else if (moduleName === 'climate') {
        const img = imageCache['/static/img/nube.png'];
        if (img && img.complete) {
          const size = (item.size || 30) * scaleX;
          ctx.drawImage(img, x - size / 2, y - size / 2, size, size);
        }
      }
    });
  });
}

// Start a module worker
function startModule(name) {
  const mod = modules[name];
  if (!mod) return;

  stopModule(name);

  const canvas = document.getElementById(mod.canvasId);
  const statsEl = document.getElementById(mod.statsId);

  const worker = new Worker(mod.workerPath, { type: 'module' });
  workers[name] = worker;

  worker.postMessage({ type: 'init', payload: { width: canvas.width, height: canvas.height } });

  worker.onmessage = (ev) => {
    const { type, payload } = ev.data || {};

    if (type === 'stats') {
      statsEl.textContent = payload.text;
    } else if (type === 'draw') {
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
    } else if (type === 'data') {
      // Store data for combined view
      moduleData[name] = payload.data || [];
      moduleLastUpdate[name] = Date.now();
      updateModuleStatus(name, true);
      updateCombinedStats();
      drawCombinedCanvas();
    }
  };
}

// Stop a module worker
function stopModule(name) {
  const worker = workers[name];
  if (worker) {
    worker.postMessage({ type: 'stop' });
    worker.terminate();
    delete workers[name];
  }
}

// Periodically check for inactive modules
function startInactivityChecker() {
  setInterval(() => {
    Object.keys(modules).forEach(moduleName => {
      const isActive = isModuleActive(moduleName);
      updateModuleStatus(moduleName, isActive);
    });
    updateCombinedStats();
    drawCombinedCanvas();
  }, 1000);
}

// Initialize
window.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 Initializing Ecosystem Simulation...');

  setupTabs();
  startInactivityChecker();

  preloadImages()
    .then(() => {
      console.log('✓ All images loaded');
      Object.keys(modules).forEach(startModule);
    })
    .catch(err => {
      console.error('✗ Error loading images:', err);
      Object.keys(modules).forEach(startModule);
    });
});
