# Cluster Ecosistema - Guía de Despliegue

## Arquitectura

- **Nodo Manager**: Ejecuta solo el servicio `master` (API Flask en puerto 5000)
- **Nodos Worker**: Ejecutan los servicios worker que tú elijas (trees, life, food, climate)

## Configuración Inicial

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

## Despliegue

### Opción 1: Usando el script de gestión (RECOMENDADO)

```bash
# Dar permisos de ejecución
chmod +x manage.sh

# Desplegar el stack (solo master activo inicialmente)
./manage.sh deploy

# Ver el estado
./manage.sh status

# Escalar workers según necesites
./manage.sh scale trees 2    # 2 réplicas de worker-trees
./manage.sh scale life 1     # 1 réplica de worker-life
./manage.sh scale food 1     # 1 réplica de worker-food
./manage.sh scale climate 1  # 1 réplica de worker-climate

# Ver logs
./manage.sh logs master
./manage.sh logs trees

# Eliminar todo
./manage.sh remove
```

### Opción 2: Comandos manuales

```bash
# Desplegar el stack
docker stack deploy -c docker-compose.yml cluster_ecosistema

# Ver servicios
docker service ls

# Escalar workers manualmente
docker service scale cluster_ecosistema_worker-trees=2
docker service scale cluster_ecosistema_worker-life=1
docker service scale cluster_ecosistema_worker-food=1
docker service scale cluster_ecosistema_worker-climate=1

# Ver distribución de tareas
docker stack ps cluster_ecosistema

# Ver logs
docker service logs cluster_ecosistema_master -f
docker service logs cluster_ecosistema_worker-trees -f

# Eliminar el stack
docker stack rm cluster_ecosistema
```

## Distribución de Servicios

Con la configuración actual:

- ✅ **master**: Solo corre en el nodo manager (1 réplica)
- ✅ **worker-trees**: Solo corre en nodos worker (0 réplicas inicialmente)
- ✅ **worker-life**: Solo corre en nodos worker (0 réplicas inicialmente)
- ✅ **worker-food**: Solo corre en nodos worker (0 réplicas inicialmente)
- ✅ **worker-climate**: Solo corre en nodos worker (0 réplicas inicialmente)

**Importante**: Los workers tienen `replicas: 0` por defecto. Debes escalarlos manualmente en cada nodo según necesites.

## Ejemplo de Flujo Completo

```bash
# 1. Desplegar (solo master activo)
./manage.sh deploy

# 2. Verificar que el master está corriendo
./manage.sh status

# 3. Acceder a la aplicación
# http://IP_MANAGER:5000

# 4. En el nodo worker 1, escalar trees
./manage.sh scale trees 1

# 5. En el nodo worker 2, escalar life
./manage.sh scale life 1

# 6. Ver distribución
./manage.sh status

# 7. Ver logs de un worker
./manage.sh logs trees
```

## Comandos Útiles

```bash
# Ver todos los nodos del cluster
docker node ls

# Ver qué está corriendo en cada nodo
docker node ps NOMBRE_NODO

# Ver detalles de un servicio
docker service inspect cluster_ecosistema_master

# Actualizar un servicio
docker service update cluster_ecosistema_master

# Forzar redistribución de tareas
docker service update --force cluster_ecosistema_worker-trees
```

## Acceso a la Aplicación

Una vez desplegado el master:

```
http://IP_DEL_MANAGER:5000
```

Para obtener la IP del manager:
```bash
hostname -I
```

## Troubleshooting

### Los workers no se distribuyen en los nodos worker

Verifica que los nodos estén correctamente etiquetados:
```bash
docker node ls
# Debe mostrar "worker" en la columna MANAGER STATUS para los workers
```

### No puedo acceder al puerto 5000

```bash
# Abrir el puerto en el firewall
sudo ufw allow 5000/tcp
```

### Ver por qué un servicio no inicia

```bash
docker service ps cluster_ecosistema_worker-trees --no-trunc
```

## Limpieza

```bash
# Eliminar el stack
./manage.sh remove

# o manualmente
docker stack rm cluster_ecosistema

# Salir del swarm (en un worker)
docker swarm leave

# Eliminar un nodo del swarm (en el manager)
docker node rm NOMBRE_NODO
```
