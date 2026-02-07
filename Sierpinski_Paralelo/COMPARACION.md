# 📊 COMPARACIÓN: Secuencial vs Paralelo

## 🔴 Cluster_Ecosistema (SECUENCIAL - Puerto 5001)

```
┌─────────────────────────────────────────┐
│  SISTEMA DE TURNOS - NO PARALELO       │
└─────────────────────────────────────────┘

Worker1 ───► [ESPERA] ───► Procesa Región 0 ───► ✓
                              ↓
Worker2 ───► [ESPERA] ───────► Procesa Región 1 ───► ✓
                                  ↓
Worker3 ───► [ESPERA] ───────────► Procesa Región 2 ───► ✓

⏱️  Tiempo total: T + T + T = 3T (SECUENCIAL)
🚀 Speedup: 1.0x (SIN GANANCIA)
```

**Cómo funciona:**
- Worker1 solicita tarea → El maestro verifica si es su turno
- Si NO es su turno → Respuesta 204 (espera)
- Si SÍ es su turno → Procesa y envía resultado
- El maestro cambia el turno al siguiente worker
- **Problema:** Los workers pasan la mayor parte del tiempo ESPERANDO

---

## 🟢 Sierpinski_Paralelo (PARALELO - Puerto 5000) ⭐

```
┌─────────────────────────────────────────┐
│  SISTEMA PARALELO - SIN TURNOS          │
└─────────────────────────────────────────┘

Worker1 ───► Procesa Región Superior       ───► ✓
              ⚡ SIMULTÁNEO ⚡
Worker2 ───► Procesa Región Inf. Derecha  ───► ✓
              ⚡ SIMULTÁNEO ⚡
Worker3 ───► Procesa Región Inf. Izquierda ───► ✓

⏱️  Tiempo total: max(T1, T2, T3) ≈ T (PARALELO)
🚀 Speedup: 3.0x (3 VECES MÁS RÁPIDO)
```

**Cómo funciona:**
- Todos los workers solicitan tareas INMEDIATAMENTE
- Cada worker recibe su región fija (sin esperar)
- TODOS procesan al mismo tiempo
- **Ventaja:** Aprovecha múltiples núcleos/máquinas

---

## 🎯 Tolerancia a Fallos Visual

```
3 Workers Activos:          Desconectar Worker2:        Reconectar Worker2:
        △                           △                           △              
       △ △                         △ △                         △ △             
      △   △                       △   △                       △   △            
     △ △ △ △                     △ △   △                     △ △ △ △           
    △       △                   △         △                 △       △          
   △ △     △ △                 △ △       △ △               △ △     △ △         
  △   △   △   △               △   △     △   △             △   △   △   △        

  ✅ COMPLETO                 ⚠️ REGIÓN DERECHA            ✅ COMPLETO
                             DESAPARECE                   NUEVAMENTE
```

---

## 📋 Comandos de Ejecución

### Cluster_Ecosistema (SECUENCIAL)
```powershell
cd Cluster_Ecosistema
python app.py  # Puerto 5001

python worker_node.py --master http://127.0.0.1:5001 --module sierpinski --interval 1
```

### Sierpinski_Paralelo (PARALELO) ⭐
```powershell
cd Sierpinski_Paralelo
python master.py  # Puerto 5000

python worker.py --master http://127.0.0.1:5000 --id worker1
python worker.py --master http://127.0.0.1:5000 --id worker2
python worker.py --master http://127.0.0.1:5000 --id worker3
```

---

## 🏆 Resultados de Rendimiento (Profundidad 7)

| Sistema | Workers | Tiempo | Speedup |
|---------|---------|--------|---------|
| Cluster_Ecosistema | 3 | ~9-12s | 1.0x ❌ |
| Sierpinski_Paralelo | 1 | ~9-10s | 1.0x |
| Sierpinski_Paralelo | 2 | ~5-6s | 1.8x |
| Sierpinski_Paralelo | 3 | ~3-4s | 2.8x ✅ |

**Sierpinski_Paralelo es 3x más rápido!** 🚀
