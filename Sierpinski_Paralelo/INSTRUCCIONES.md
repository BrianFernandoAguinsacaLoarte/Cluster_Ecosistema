# 🚀 Sierpinski Paralelo - Instrucciones de Ejecución

## ✨ Características

Este proyecto demuestra **computación distribuida PARALELA** donde:
- ✅ Cada worker procesa su región **simultáneamente** (no por turnos)
- ✅ Cuando un worker se conecta, su región aparece
- ✅ Cuando un worker se desconecta, su región **desaparece** del fractal
- ✅ Visualización en tiempo real del estado de cada nodo

---

## 📋 Pasos de Ejecución

### **PASO 1: Iniciar el Servidor Maestro**

**Terminal 1 (PowerShell):**
```powershell
cd C:\Users\ACER\Desktop\ProyectoPFinal\Sierpinski_Paralelo
python master.py
```

✅ **Verás:**
```
============================================================
🎯 NODO MAESTRO - SIERPINSKI PARALELO (Regiones Fijas)
============================================================

📘 Instrucciones:
   1. Inicia 3 workers en diferentes terminales...
```

El servidor estará listo en: **http://127.0.0.1:5000**

---

### **PASO 2: Abrir el Dashboard**

Abre tu navegador y ve a:
```
http://127.0.0.1:5000
```

✅ Verás el dashboard esperando workers

---

### **PASO 3: Iniciar Worker 1 (Región Superior)**

**Terminal 2 (PowerShell):**
```powershell
cd C:\Users\ACER\Desktop\ProyectoPFinal\Sierpinski_Paralelo
python worker.py --master http://127.0.0.1:5000 --id worker1
```

✅ **Verás:**
```
============================================================
🚀 WORKER NODE: worker1
============================================================
✅ Registrado exitosamente como worker1
💓 Heartbeat iniciado (cada 3s)
🔄 Iniciando loop de trabajo...
```

🎯 **En el dashboard:** Aparecerá worker1 con estado "✅ active" y región "Superior"

---

### **PASO 4: Iniciar Worker 2 (Región Inferior Derecha)**

**Terminal 3 (PowerShell):**
```powershell
cd C:\Users\ACER\Desktop\ProyectoPFinal\Sierpinski_Paralelo
python worker.py --master http://127.0.0.1:5000 --id worker2
```

🎯 **En el dashboard:** Aparecerá worker2 con región "Inf. Derecha"

---

### **PASO 5: Iniciar Worker 3 (Región Inferior Izquierda)**

**Terminal 4 (PowerShell):**
```powershell
cd C:\Users\ACER\Desktop\ProyectoPFinal\Sierpinski_Paralelo
python worker.py --master http://127.0.0.1:5000 --id worker3
```

🎯 **En el dashboard:** Aparecerá worker3 con región "Inf. Izquierda"

---

### **PASO 6: Generar el Fractal**

En el dashboard web:
1. Ajusta la **Profundidad** (recomendado: 6 o 7)
2. Haz clic en **🚀 Generar Fractal**

✅ **Observarás:**
- Los 3 workers procesan **SIMULTÁNEAMENTE** (no por turnos)
- Cada worker genera su región del triángulo
- El fractal se construye en tiempo real
- Verás el progreso: "Tareas Completadas: 1, 2, 3"

---

### **PASO 7: Probar Tolerancia a Fallos**

**Desconectar un worker:**
1. Ve a la terminal de worker2 (por ejemplo)
2. Presiona **Ctrl+C** para detenerlo

✅ **Observarás en el dashboard:**
- El worker2 cambia a estado "💀 dead"
- La **región inferior derecha desaparece** del fractal
- Solo se muestran las regiones de worker1 y worker3

**Reconectar el worker:**
```powershell
python worker.py --master http://127.0.0.1:5000 --id worker2
```

- El worker2 vuelve a estado "✅ active"
- Haz clic en **🚀 Generar Fractal** nuevamente
- La región inferior derecha **reaparece** en el fractal

---

## 🔍 Diferencias con Cluster_Ecosistema

| Característica | Cluster_Ecosistema | Sierpinski_Paralelo |
|----------------|-------------------|---------------------|
| **Ejecución** | Secuencial (turnos) | **Paralela** |
| **Workers esperan turno** | ✅ Sí | ❌ No |
| **Todos trabajan a la vez** | ❌ No | ✅ Sí |
| **Speedup real** | ~1.0x (sin ganancia) | ~3.0x (con 3 workers) |
| **Tolerancia a fallos** | Limitada | **Visual en tiempo real** |

---

## 📊 Qué Esperar

### **Con 3 workers activos (Profundidad 7):**
- **Triángulos totales:** ~6,561 (3^7)
- **Por región:** ~2,187 triángulos/worker
- **Tiempo:** ~2-5 segundos total
- **Speedup:** ~3.0x vs 1 worker

### **Con 2 workers activos:**
- Solo 2 regiones visibles
- Tiempo mayor (~4-7 segundos)
- Speedup: ~2.0x

### **Con 1 worker activo:**
- Solo 1 región visible
- Tiempo mayor (~7-10 segundos)
- Sin speedup (1.0x)

---

## 🛑 Detener el Sistema

1. **Detener workers:** Presiona **Ctrl+C** en cada terminal de worker
2. **Detener maestro:** Presiona **Ctrl+C** en la terminal del maestro

---

## ⚡ Pruebas Recomendadas

### **Prueba 1: Conexión Progresiva**
1. Inicia solo worker1
2. Genera fractal → verás solo región superior
3. Inicia worker2 
4. Genera fractal → verás 2 regiones
5. Inicia worker3
6. Genera fractal → verás las 3 regiones completas

### **Prueba 2: Desconexión Progresiva**
1. Genera fractal completo (3 regiones)
2. Detén worker3 → región izquierda desaparece
3. Detén worker2 → región derecha desaparece
4. Solo queda región superior (worker1)

### **Prueba 3: Reconexión en Caliente**
1. Genera fractal completo
2. Detén worker2
3. Espera 10 segundos (timeout de heartbeat)
4. Observa cómo desaparece su región
5. Reinicia worker2
6. Genera nuevamente → reaparece su región

---

## 🐛 Solución de Problemas

### **Error: Cannot connect to master**
- Verifica que master.py esté ejecutándose
- Confirma que la URL sea `http://127.0.0.1:5000`

### **Worker no aparece en dashboard**
- Espera 1-2 segundos para actualización
- Verifica que el worker esté registrado (mensaje "✅ Registrado...")

### **Región no desaparece al desconectar**
- Espera 10 segundos (timeout de heartbeat)
- Actualiza el navegador

### **Import flask could not be resolved**
- Este error es solo de Pylance (análisis estático)
- Los paquetes ya están instalados, el código funciona correctamente

---

## 📚 Recursos Adicionales

- **Cluster_Ecosistema:** Sistema secuencial (turnos) en puerto 5001
- **FractalTriangulo:** Sistema MPI (true parallel) con mpiexec
- **Sierpinski_Paralelo:** Sistema HTTP paralelo en puerto 5000

---

¡Disfruta explorando la computación distribuida paralela! 🎉
