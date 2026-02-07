# ⚡ Guía Rápida de Inicio

## 🎯 Inicio en 3 Pasos

### 1️⃣ Instalar Dependencias

```bash
cd Sierpinski_Paralelo
pip install -r requirements.txt
```

### 2️⃣ Opción A: Ejecución Manual

**Terminal 1 - Maestro**:
```bash
python master.py
```

**Terminal 2 - Worker 1**:
```bash
python worker.py --master http://127.0.0.1:5000 --id worker1
```

**Terminal 3 - Worker 2**:
```bash
python worker.py --master http://127.0.0.1:5000 --id worker2
```

**Terminal 4 - Worker 3**:
```bash
python worker.py --master http://127.0.0.1:5000 --id worker3
```

### 2️⃣ Opción B: Demo Automático (Windows)

```bash
demo.bat
```

Este script:
- ✅ Inicia el maestro
- ✅ Inicia 3 workers
- ✅ Abre el navegador automáticamente

### 3️⃣ Usar el Dashboard

1. Abre **http://127.0.0.1:5000**
2. Verás los workers conectados (✅)
3. Configura:
   - Profundidad: `6`
   - Cutoff: `3`
4. Haz clic en **"🚀 Generar Fractal"**
5. **Observa cómo trabajan en paralelo**

---

## 🧪 Experimentos Rápidos

### Experimento 1: Ver Paralelización (2 min)

```bash
# Con 1 worker
python master.py        # Terminal 1
python worker.py --master http://127.0.0.1:5000 --id w1  # Terminal 2

# Dashboard: Genera fractal → nota el tiempo
# Tiempo esperado: ~5 segundos

# Agrega 2 workers más (sin cerrar nada)
python worker.py --master http://127.0.0.1:5000 --id w2  # Terminal 3
python worker.py --master http://127.0.0.1:5000 --id w3  # Terminal 4

# Dashboard: Genera de nuevo
# Tiempo esperado: ~1.8 segundos
# Speedup: ~2.8x 🚀
```

### Experimento 2: Tolerancia a Fallos (3 min)

```bash
# Inicia sistema completo (maestro + 3 workers)
demo.bat

# Dashboard: Genera fractal con cutoff=4 (81 tareas)
# Mientras procesa, ve a Terminal de Worker 2
# Presiona Ctrl+C para matarlo

# Observa en Dashboard:
# ✅ Worker 2 marcado como 💀
# ✅ Sus tareas se reasignan
# ✅ Generación continúa
```

### Experimento 3: Agregar Workers Dinámicamente (2 min)

```bash
# Inicia solo 1 worker
python master.py                                   # Terminal 1
python worker.py --master http://127.0.0.1:5000 --id w1  # Terminal 2

# Dashboard: Genera con cutoff=4 (81 tareas)
# Mientras procesa (tomará ~10-15s con 1 worker)

# DURANTE la ejecución, agrega más workers:
python worker.py --master http://127.0.0.1:5000 --id w2  # Terminal 3
python worker.py --master http://127.0.0.1:5000 --id w3  # Terminal 4

# Observa cómo inmediatamente toman tareas
# La velocidad aumenta al instante! ⚡
```

---

## 📊 Configuraciones Recomendadas

### Para Demo Rápida (30 seg)
```
Profundidad: 5
Cutoff: 2
Workers: 2
Tareas: 9
```

### Para Ver Paralelización (1 min)
```
Profundidad: 6
Cutoff: 3
Workers: 3
Tareas: 27
```

### Para Probar Fallos (2 min)
```
Profundidad: 7
Cutoff: 4
Workers: 4
Tareas: 81
```

---

## 🎮 Controles del Dashboard

| Acción | Efecto |
|--------|--------|
| Generar Fractal | Inicia la generación distribuida |
| Aumentar Depth | Más recursión, más triángulos |
| Aumentar Cutoff | Más tareas, mejor distribución |

---

## 🛑 Detener el Sistema

1. **Workers**: `Ctrl+C` en cada terminal
2. **Maestro**: `Ctrl+C` en su terminal

---

## ❓ Problemas Comunes

### "No hay workers"
- ✅ Verifica que ejecutaste `python worker.py ...`
- ✅ Espera 2-3 segundos (actualización automática)

### "ModuleNotFoundError"
- ✅ Ejecuta `pip install -r requirements.txt`

### Workers no se conectan
- ✅ Verifica que el maestro está corriendo
- ✅ Usa la URL correcta: `http://127.0.0.1:5000`

---

## 💡 Tips

- **Ver logs**: Observa las terminales para ver la actividad
- **Refresh**: El dashboard se actualiza automáticamente cada 1s
- **Multiple PCs**: Cambia `127.0.0.1` por la IP del maestro

---

**¡Listo para experimentar! 🚀**
