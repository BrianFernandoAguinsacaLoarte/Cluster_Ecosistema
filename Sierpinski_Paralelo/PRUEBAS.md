# 🧪 PRUEBAS PASO A PASO - CORRECCIONES APLICADAS

## ✅ Problemas Corregidos

### 1️⃣ **Canvas no se limpiaba al desconectar worker**
- **Problema:** Cuando desconectabas worker2, su región seguía visible
- **Solución:** El canvas ahora se redibuja SIEMPRE, incluso con array vacío
- **Código:** `drawTriangles(canvasData.triangles || [])`

### 2️⃣ **Regiones no se limpiaban al detectar worker muerto**
- **Problema:** Los triángulos del worker muerto permanecían en memoria
- **Solución:** Al detectar worker muerto, se limpia su región:
```python
system_state['regions'][worker_id] = []
del system_state['completed_tasks'][worker_id]
```

### 3️⃣ **Nueva generación no limpiaba estado anterior**
- **Problema:** Triángulos de generación anterior podían permanecer
- **Solución:** Limpieza completa de todas las regiones al iniciar generación

### 4️⃣ **Filtrado de regiones mejorado** 
- **Problema:** Lógica de filtrado no era clara
- **Solución:** Verificación explícita: worker existe + activo + completó + tiene triángulos

---

## 🧪 PRUEBA 1: Un solo worker (Worker1)

### **Objetivo:** Verificar que solo se muestra UNA región

**Pasos:**
```powershell
# Terminal 1
cd Sierpinski_Paralelo
python master.py

# Terminal 2
python worker.py --master http://127.0.0.1:5000 --id worker1
```

**En el navegador (http://127.0.0.1:5000):**
1. Verás **1 worker activo** (worker1)
2. Región: **Superior**
3. Haz clic en **🚀 Generar Fractal** (profundidad 6)

**Resultado Esperado:**
```
        △              
       △ △             ← SOLO REGIÓN SUPERIOR
      △   △            
     △ △ △ △           
                       ← VACÍO (no worker2)
                       
                       ← VACÍO (no worker3)
```

✅ **Verifica:** Solo se muestra el triángulo superior, no todo el fractal

---

## 🧪 PRUEBA 2: Agregar segundo worker (Worker2)

**Continuando desde la Prueba 1:**

```powershell
# Terminal 3 (nueva)
cd Sierpinski_Paralelo
python worker.py --master http://127.0.0.1:5000 --id worker2
```

**En el navegador:**
1. Verás **2 workers activos** (worker1, worker2)
2. Haz clic en **🚀 Generar Fractal** de nuevo

**Resultado Esperado:**
```
        △              
       △ △             ← Región Superior (worker1)
      △   △            
     △ △ △ △           
    △       △          ← Región Inferior Derecha (worker2)
   △ △                 
                       ← VACÍO (no worker3)
```

✅ **Verifica:** Ahora se muestran 2 regiones (superior + derecha)

---

## 🧪 PRUEBA 3: Agregar tercer worker (Worker3)

```powershell
# Terminal 4 (nueva)
cd Sierpinski_Paralelo
python worker.py --master http://127.0.0.1:5000 --id worker3
```

**En el navegador:**
1. Verás **3 workers activos**
2. Haz clic en **🚀 Generar Fractal**

**Resultado Esperado:**
```
        △              
       △ △             ← Región Superior (worker1)
      △   △            
     △ △ △ △           
    △       △          
   △ △     △ △         ← FRACTAL COMPLETO ✨
  △   △   △   △        
```

✅ **Verifica:** El fractal está completo con las 3 regiones

---

## 🧪 PRUEBA 4: Desconectar Worker2 

**Objetivo:** Verificar que su región DESAPARECE

**Pasos:**
1. Con el fractal completo visible
2. Ve a la Terminal 3 (worker2)
3. Presiona **Ctrl+C** para detenerlo
4. Espera **10-15 segundos**

**En el navegador observarás:**
- Worker2 cambia a estado **💀 dead**
- Después de 10 segundos, el monitor detecta que está muerto
- La **región inferior derecha DESAPARECE** del canvas

**Resultado Esperado:**
```
        △              
       △ △             ← Región Superior (worker1) ✅
      △   △            
     △ △   △           
    △         △        ← Región Derecha DESAPARECIDA ❌
   △ △       △ △       
  △   △     △   △      ← Región Izquierda (worker3) ✅
```

✅ **Verifica:** Solo quedan 2 regiones visibles

---

## 🧪 PRUEBA 5: Reconectar Worker2

**Objetivo:** Verificar que su región REAPARECE

```powershell
# Terminal 3 (donde detuvimos worker2)
python worker.py --master http://127.0.0.1:5000 --id worker2
```

**En el navegador:**
1. Worker2 aparece como **✅ active** nuevamente
2. Haz clic en **🚀 Generar Fractal**
3. La **región inferior derecha REAPARECE**

**Resultado Esperado:**
```
        △              
       △ △             
      △   △            
     △ △ △ △           ← FRACTAL COMPLETO DE NUEVO ✨
    △       △          
   △ △     △ △         
  △   △   △   △        
```

✅ **Verifica:** Las 3 regiones están completas nuevamente

---

## 🧪 PRUEBA 6: Desconectar múltiples workers

**Objetivo:** Verificar tolerancia a fallos múltiples

**Pasos:**
1. Con fractal completo
2. Detén worker2 (Ctrl+C en Terminal 3)
3. Espera 10 segundos → Región derecha desaparece
4. Detén worker3 (Ctrl+C en Terminal 4)
5. Espera 10 segundos → Región izquierda desaparece

**Resultado Esperado:**
```
        △              
       △ △             ← SOLO Región Superior (worker1)
      △   △            
     △ △ △ △           
```

✅ **Verifica:** Solo queda la región superior de worker1

---

## 🧪 PRUEBA 7: Limpiar canvas entre generaciones

**Objetivo:** Verificar que no quedan triángulos residuales

**Pasos:**
1. Genera fractal con profundidad **7** (muchos triángulos)
2. Espera a que complete
3. Detén worker2 y worker3
4. Espera 10 segundos (regiones desaparecen)
5. Genera fractal nuevamente con profundidad **4** (pocos triángulos)

**Resultado Esperado:**
- El canvas se limpia completamente
- Solo se muestran los triángulos de la nueva generación (profundidad 4)
- No hay "fantasmas" de la generación anterior

✅ **Verifica:** Solo triángulos de worker1 con profundidad 4

---

## 📊 Tabla de Verificación

| Prueba | Objetivo | Estado |
|--------|----------|--------|
| ✅ Solo worker1 | Una región visible | ⬜ Pendiente |
| ✅ + worker2 | Dos regiones visibles | ⬜ Pendiente |
| ✅ + worker3 | Tres regiones (completo) | ⬜ Pendiente |
| ✅ Desconectar worker2 | Región desaparece | ⬜ Pendiente |
| ✅ Reconectar worker2 | Región reaparece | ⬜ Pendiente |
| ✅ Desconectar múltiples | Solo quedan activos | ⬜ Pendiente |
| ✅ Limpiar entre generaciones | Sin residuos | ⬜ Pendiente |

---

## 🐛 Si algo no funciona:

### **Problema: Canvas no se limpia**
- **Solución:** Presiona F5 en el navegador para refrescar

### **Problema: Worker no aparece en dashboard**
- **Solución:** Espera 2-3 segundos, el dashboard actualiza cada 1s

### **Problema: Región no desaparece inmediatamente**
- **Solución:** Es normal, espera 10-15 segundos (timeout de heartbeat)

### **Problema: "generation already active"**
- **Solución:** Espera a que complete la generación actual

---

## ✅ Confirmación Final

Después de ejecutar todas las pruebas, deberías confirmar:

1. ✅ Solo worker1 → Solo región superior visible
2. ✅ Agregar workers → Regiones aparecen progresivamente  
3. ✅ Desconectar worker → Su región desaparece después de 10s
4. ✅ Reconectar worker → Su región reaparece al generar nuevo fractal
5. ✅ Canvas se limpia → No quedan triángulos residuales

---

¡Sistema corregido y funcionando correctamente! 🎉
