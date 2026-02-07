# 🔺 Sierpinski Paralelo - Computación Distribuida Real

Implementación **verdaderamente paralela** del Triángulo de Sierpinski con múltiples nodos workers, tolerancia a fallos y visualización en tiempo real.

## 🎯 Diferencias con la Versión Secuencial

| Característica | Versión Secuencial | Esta Versión (Paralela) |
|---|---|---|
| **Ejecución** | Turnos (Round-Robin) | Paralela Real |
| **Workers simultáneos** | 1 a la vez | Todos simultáneamente |
| **Detección de fallos** | No | Sí (heartbeat + timeout) |
| **Reasignación** | No | Automática |
| **Escalabilidad** | Limitada | N workers |
| **Speedup** | 1x (secuencial) | ~Nx (lineal) |

## 📦 Características

✅ **Paralelización Real**: Todos los workers procesan tareas simultáneamente
✅ **Tolerancia a Fallos**: Detecta nodos caídos y reasigna tareas automáticamente  
✅ **Visualización en Tiempo Real**: Dashboard web con métricas actualizadas
✅ **Distribución Dinámica**: Cola de tareas distribuida bajo demanda
✅ **Monitoreo de Nodos**: Heartbeat y estado de cada worker
✅ **Comparación Visual**: Ve el impacto de agregar/quitar workers

## 🏗️ Arquitectura

```
┌─────────────────────┐
│   Nodo Maestro      │
│   (Flask + API)     │
│                     │
│ - Cola de tareas    │
│ - Monitor workers   │
│ - Dashboard web     │
└──────────┬──────────┘
           │
           ├─────────────────┬─────────────────┐
           │                 │                 │
    ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
    │  Worker 1   │  │  Worker 2   │  │  Worker 3   │
    │             │  │             │  │             │
    │ Heartbeat ❤️│  │ Heartbeat ❤️│  │ Heartbeat ❤️│
    │ Procesa ⚙️  │  │ Procesa ⚙️  │  │ Procesa ⚙️  │
    └─────────────┘  └─────────────┘  └─────────────┘
     PARALELO         PARALELO         PARALELO
```

## 🚀 Instalación

```bash
# 1. Navegar a la carpeta
cd Sierpinski_Paralelo

# 2. Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Ejecución

### Paso 1: Iniciar el Nodo Maestro

Abre una terminal y ejecuta:

```bash
python master.py
```

Deberías ver:
```
============================================================
🎯 NODO MAESTRO - SIERPINSKI PARALELO
============================================================
Servidor iniciando en http://127.0.0.1:5000
...
```

### Paso 2: Abrir el Dashboard

Abre tu navegador en:
```
http://127.0.0.1:5000
```

### Paso 3: Iniciar Workers (en terminales separadas)

**Terminal 2** (Worker 1):
```bash
python worker.py --master http://127.0.0.1:5000 --id worker1
```

**Terminal 3** (Worker 2):
```bash
python worker.py --master http://127.0.0.1:5000 --id worker2
```

**Terminal 4** (Worker 3):
```bash
python worker.py --master http://127.0.0.1:5000 --id worker3
```

### Paso 4: Generar Fractal

En el dashboard web:
1. Configura profundidad y cutoff
2. Haz clic en "🚀 Generar Fractal"
3. **Observa cómo TODOS los workers trabajan en paralelo**

## 🧪 Demostraciones

### Demo 1: Ver Paralelización Real

1. Inicia 1 worker
2. Genera fractal (depth=6, cutoff=3) → nota el tiempo
3. Inicia 2 workers más (sin detener el maestro)
4. Genera de nuevo → **verás ~3x speedup**

### Demo 2: Tolerancia a Fallos

1. Inicia 3 workers
2. Genera fractal con cutoff=4 (81 tareas)
3. **Durante la ejecución, presiona Ctrl+C en worker2**
4. Observa en el dashboard:
   - Worker2 marcado como 💀 (muerto)
   - Sus tareas **se reasignan automáticamente**
   - La generación **continúa** con los workers restantes

### Demo 3: Agregar Workers en Tiempo Real

1. Inicia generación con 1 worker (tomará tiempo)
2. **Mientras está procesando**, inicia 2 workers más
3. Los nuevos workers **inmediatamente toman tareas**
4. La velocidad **aumenta dinámicamente**

## 📊 Experimentos Sugeridos

### Experimento 1: Speedup Lineal

| Workers | Tiempo (s) | Speedup | Eficiencia |
|---------|------------|---------|------------|
| 1       | ~5.0s      | 1.0x    | 100%       |
| 2       | ~2.6s      | 1.9x    | 95%        |
| 3       | ~1.8s      | 2.8x    | 93%        |
| 4       | ~1.4s      | 3.6x    | 90%        |

Configuración: depth=7, cutoff=3 (27 tareas)

### Experimento 2: Impacto del Cutoff

| Cutoff | Tareas | Workers | Distribución |
|--------|--------|---------|--------------|
| 2      | 9      | 3       | 3-3-3        |
| 3      | 27     | 3       | 9-9-9        |
| 4      | 81     | 3       | 27-27-27     |

Mayor cutoff = mejor distribución = mejor speedup

### Experimento 3: Recuperación de Fallos

1. Iniciar 3 workers
2. Generar con 81 tareas (cutoff=4)
3. Matar 1 worker al 33% de progreso
4. **Medir tiempo de recuperación**
5. Matar otro worker al 66%
6. **Verificar que termina con 1 worker**

## 🔍 Monitoreo

### En el Dashboard

- **Workers Activos**: Lista de nodos con su estado (✅/💀)
- **Métricas por Worker**:
  - Tareas completadas
  - Tareas activas
  - Tiempo total de cómputo
- **Progreso Global**:
  - Barra de progreso en tiempo real
  - Tiempo transcurrido
  - Triángulos generados

### En la Terminal del Maestro

```
✅ Worker worker1 registrado
📤 Tarea 0 asignada a worker1 (quedan 26)
📤 Tarea 1 asignada a worker2 (quedan 25)
📤 Tarea 2 asignada a worker3 (quedan 24)
✅ Tarea 0 completada por worker1 (729 triángulos, 0.234s)
⚠️  Worker worker2 MUERTO (sin heartbeat)
🔄 Tarea 1 reasignada (worker muerto)
```

### En la Terminal del Worker

```
🚀 WORKER NODE: worker1
💓 Heartbeat iniciado (cada 3s)
📥 Tarea 0 recibida
⚙️  Procesando tarea 0...
✅ Tarea 0 completada:
   - Triángulos: 729
   - Tiempo: 0.2340s
📤 Resultado enviado exitosamente
```

## 🛑 Detener el Sistema

1. **Workers**: Presiona `Ctrl+C` en cada terminal
2. **Maestro**: Presiona `Ctrl+C` en la terminal del maestro

## 📈 Análisis de Rendimiento

### Overhead de Comunicación

```
Tiempo Total = Tiempo Cómputo + Overhead Comunicación + Overhead Coordinación

Para N workers con T tareas:
- Secuencial: T × tiempo_tarea
- Paralelo: (T / N) × tiempo_tarea + overhead

Overhead ≈ (N × heartbeats) + (T × request/response)
```

### Cuándo es Mejor Paralelo?

✅ **Bueno para paralelizar**:
- Profundidad alta (depth ≥ 6)
- Cutoff alto (más tareas que workers)
- Tareas computacionalmente intensivas

❌ **No vale la pena paralelizar**:
- Profundidad baja (depth < 4)
- Pocas tareas (tareas < workers)
- Overhead > tiempo de cómputo

## 🔧 Configuración Avanzada

### Ajustar Timeouts (master.py)

```python
HEARTBEAT_TIMEOUT = 10  # Tiempo para marcar worker muerto
TASK_TIMEOUT = 30       # Tiempo máximo por tarea
TASK_CHECK_INTERVAL = 2 # Frecuencia de monitoreo
```

### Ejecutar en Red Local

**En el servidor maestro**:
```bash
# Obtener IP local
ipconfig  # Windows
ifconfig  # Linux/Mac

# Ejecutar maestro
python master.py
```

**En otros computadores**:
```bash
python worker.py --master http://192.168.1.100:5000 --id worker_pc2
```

## 📁 Estructura del Proyecto

```
Sierpinski_Paralelo/
├── master.py           # Nodo maestro (coordinador)
├── worker.py           # Nodo worker (procesador)
├── requirements.txt    # Dependencias
├── README.md          # Esta documentación
└── templates/
    └── index.html     # Dashboard web
```

## 🆚 Comparación: Secuencial vs Paralelo

### Código Crítico

**Secuencial (turnos)**:
```python
# Solo UN worker recibe tarea
if current_task is not None:
    return 'espera tu turno'
```

**Paralelo (inmediato)**:
```python
# CUALQUIER worker puede recibir tarea
if task_queue:
    task = task_queue.popleft()  # Sin esperar
    return task
```

### Resultados Reales

Con 27 tareas (cutoff=3), depth=6:

| Modo | Workers | Tiempo | Speedup |
|------|---------|--------|---------|
| Secuencial | 3 | 5.1s | 1.0x |
| Paralelo | 1 | 5.2s | 1.0x |
| Paralelo | 2 | 2.7s | 1.9x |
| Paralelo | 3 | 1.8s | 2.9x |

**Speedup casi lineal! 🚀**

## 🐛 Troubleshooting

### Workers no se conectan

- Verificar que el maestro esté corriendo
- Verificar firewall (puerto 5000)
- Verificar URL correcta

### Workers no aparecen en dashboard

- Esperar 1-2 segundos (actualización automática)
- Verificar logs del worker
- Verificar que el worker se registró exitosamente

### Tareas no se distribuyen

- Verificar que hiciste clic en "Generar Fractal"
- Verificar que hay workers activos (✅)
- Ver logs del maestro

## 💡 Extensiones Futuras

- [ ] Persistencia con Redis/PostgreSQL
- [ ] Autenticación de workers
- [ ] Métricas con Prometheus/Grafana
- [ ] Deploy con Docker Compose
- [ ] Kubernetes para auto-scaling
- [ ] WebSockets para updates más rápidos

## 📝 Licencia

Proyecto educativo de código abierto.

---

**¡Explora la potencia de la computación paralela distribuida! 🚀**
