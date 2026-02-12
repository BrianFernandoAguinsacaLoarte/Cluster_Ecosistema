# Cluster Sierpinski - Guía de Despliegue Docker Swarm

## 🎯 Arquitectura

- **Nodo Manager**: Ejecuta solo el servicio `master` (Flask API en puerto 5000)
- **Nodos Worker**: Ejecutan los workers que tú elijas (worker1, worker2, worker3)

Cada worker procesa una región fija del triángulo de Sierpinski:
- **worker1**: Región superior
- **worker2**: Región inferior derecha
- **worker3**: Región inferior izquierda

## 📋 Requisitos Previos

1. Docker instalado en todas las máquinas
2. Docker Swarm inicializado
3. Puertos abiertos: 5000 (master), 2377, 7946, 4789 (swarm)

## 🚀 Configuración Inicial

### 1. En el Nodo Manager (VM principal)

```bash
# Inicializar Docker Swarm (si no lo has hecho)
docker swarm init

# Obtener el token para unir workers
docker swarm join-token worker
```

### 2. En cada Nodo Worker

```bash
# Unirse al swarm (usa el token del paso anterior)
docker swarm join --token SWMTKN-1-xxxxx IP_MANAGER:2377
```

### 3. Verificar el cluster

```bash
# En el manager
docker node ls
```

## 📦 Despliegue

### Paso 1: Copiar archivos a tu VM Debian

Asegúrate de tener estos archivos en la carpeta `Sierpinski_Paralelo`:
- `docker-compose.yml`
- `Dockerfile.master`
- `Dockerfile.worker`
- `master.py`
- `worker.py`
- `requirements.txt`
- `templates/` (carpeta con index.html)
- `manage.sh`

### Paso 2: Dar permisos al script

```bash
chmod +x manage.sh
```

### Paso 3: Desplegar el stack

```bash
# Desplegar (solo master se ejecuta inicialmente)
./manage.sh deploy
```

### Paso 4: Verificar que el master está corriendo

```bash
# Ver el estado
./manage.sh status

# Ver logs del master
./manage.sh logs master
```

### Paso 5: Acceder a la aplicación

Desde tu navegador en Windows:
```
http://IP_DEL_MANAGER:5000
```

Para obtener la IP del manager:
```bash
hostname -I
```

### Paso 6: Escalar workers en cada nodo

**Desde el nodo manager**, escala los workers:

```bash
# Escalar worker1 (se ejecutará en un nodo worker)
./manage.sh scale worker1 1

# Escalar worker2 (se ejecutará en un nodo worker)
./manage.sh scale worker2 1

# Escalar worker3 (se ejecutará en un nodo worker)
./manage.sh scale worker3 1
```

### Paso 7: Ver la distribución

```bash
./manage.sh status
```

## 🎮 Uso de la Aplicación

1. Abre el navegador en `http://IP_MANAGER:5000`
2. Verás el dashboard con los workers conectados
3. Configura la profundidad (depth) del fractal
4. Haz clic en "🚀 Generar Fractal"
5. Observa cómo cada worker procesa su región en paralelo

## 🧪 Demostraciones

### Demo 1: Tolerancia a Fallos

1. Inicia los 3 workers
2. Genera un fractal (depth=6)
3. **Durante la ejecución, escala worker2 a 0**:
   ```bash
   ./manage.sh scale worker2 0
   ```
4. Observa en el dashboard:
   - Worker2 desaparece
   - Su región se limpia automáticamente
   - Los otros workers continúan

### Demo 2: Agregar Workers Dinámicamente

1. Inicia solo worker1:
   ```bash
   ./manage.sh scale worker1 1
   ```
2. Genera un fractal
3. **Mientras está procesando**, agrega worker2:
   ```bash
   ./manage.sh scale worker2 1
   ```
4. Worker2 inmediatamente toma su región

## 📊 Comandos Útiles

```bash
# Ver todos los servicios
docker service ls

# Ver dónde está corriendo cada worker
docker stack ps sierpinski

# Ver logs de un worker específico
./manage.sh logs worker1

# Ver logs del master
./manage.sh logs master

# Escalar un worker
./manage.sh scale worker1 2  # 2 réplicas

# Ver el estado completo
./manage.sh status

# Eliminar todo el stack
./manage.sh remove
```

## 🔧 Distribución de Workers

Docker Swarm distribuirá automáticamente los workers entre los nodos disponibles:

- Si tienes 1 nodo worker: Todos los workers correrán ahí
- Si tienes 2 nodos worker: Se distribuirán entre ambos
- Si tienes 3+ nodos worker: Cada worker puede correr en un nodo diferente

### Ver dónde está corriendo cada worker:

```bash
docker stack ps sierpinski

# Salida ejemplo:
# NAME                IMAGE                    NODE         DESIRED STATE
# sierpinski_master.1 sierpinski-master:latest debian-vm1   Running
# sierpinski_worker1.1 sierpinski-worker:latest debian-vm2   Running
# sierpinski_worker2.1 sierpinski-worker:latest debian-vm3   Running
```

## 🐛 Troubleshooting

### Los workers no se conectan al master

```bash
# Ver logs del worker
./manage.sh logs worker1

# Verificar que el master está corriendo
./manage.sh logs master

# Verificar la red
docker network ls
docker network inspect sierpinski_sierpinski-net
```

### No puedo acceder al puerto 5000

```bash
# En la VM manager, abrir el puerto
sudo ufw allow 5000/tcp
sudo ufw reload

# Verificar que el servicio está escuchando
sudo netstat -tulpn | grep 5000
```

### Los workers no aparecen en el dashboard

1. Espera 1-2 segundos (actualización automática)
2. Verifica que los workers estén corriendo:
   ```bash
   docker service ls
   ```
3. Verifica los logs:
   ```bash
   ./manage.sh logs worker1
   ```

### Error: "network not manually attachable"

Ya está solucionado en el `docker-compose.yml` con `attachable: true`

## 🔄 Actualizar el Código

Si modificas el código de master.py o worker.py:

```bash
# 1. Eliminar el stack actual
./manage.sh remove

# 2. Reconstruir las imágenes (en el nodo manager)
docker build -f Dockerfile.master -t sierpinski-master:latest .
docker build -f Dockerfile.worker -t sierpinski-worker:latest .

# 3. Desplegar de nuevo
./manage.sh deploy

# 4. Escalar workers
./manage.sh scale worker1 1
./manage.sh scale worker2 1
./manage.sh scale worker3 1
```

## 🧹 Limpieza

```bash
# Eliminar el stack
./manage.sh remove

# Salir del swarm (en un worker)
docker swarm leave

# Eliminar un nodo del swarm (en el manager)
docker node rm NOMBRE_NODO

# Limpiar imágenes no usadas
docker system prune -a
```

## 📝 Notas Importantes

1. **El master SIEMPRE corre en el nodo manager**
2. **Los workers SOLO corren en nodos worker** (no en el manager)
3. **Cada worker tiene un ID fijo** (worker1, worker2, worker3)
4. **Cada worker procesa una región específica** del triángulo
5. **Si un worker se cae, su región desaparece** (tolerancia a fallos visual)

## 🎯 Flujo Completo de Ejemplo

```bash
# 1. Desplegar el stack
./manage.sh deploy

# 2. Verificar que el master está corriendo
./manage.sh status

# 3. Acceder al dashboard
# http://192.168.0.104:5000

# 4. Escalar worker1 en el nodo worker 1
./manage.sh scale worker1 1

# 5. Escalar worker2 en el nodo worker 2
./manage.sh scale worker2 1

# 6. Ver distribución
./manage.sh status

# 7. Generar fractal desde el dashboard

# 8. Ver logs en tiempo real
./manage.sh logs master

# 9. Cuando termines, limpiar
./manage.sh remove
```

---

**¡Disfruta de la computación distribuida con Sierpinski! 🔺🚀**
