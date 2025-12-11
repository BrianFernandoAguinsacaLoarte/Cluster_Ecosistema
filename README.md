# Simulación de Ecosistema Distribuido

Sistema de simulación de ecosistema con arquitectura distribuida usando Flask, Web Workers y Docker Swarm.

## Arquitectura

### Nodo Maestro (Master)
- **Flask API** en puerto 5000
- Recibe datos de nodos workers distribuidos
- Sirve interfaz web con 4 paneles: Árboles, Vida, Comida y Clima
- Agrega datos de múltiples nodos en tiempo real

### Nodos Workers
- Scripts Python (`worker_node.py`) que generan datos de simulación
- Envían datos al master vía API REST cada 2 segundos
- Cada worker simula uno de los 4 módulos del ecosistema

## Endpoints API

```
POST /api/data/<module>  - Recibe datos de workers
GET  /api/data/<module>  - Obtiene datos agregados
GET  /api/status         - Estado del sistema
```

Módulos: `trees`, `life`, `food`, `climate`

## Configuración Local (Desarrollo)

### 1. Instalar dependencias
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Ejecutar master
```powershell
python app.py
```
Abre `http://localhost:5000`

### 3. Ejecutar workers (en terminales separadas)
```powershell
# Worker de árboles
python worker_node.py --master http://localhost:5000 --module trees --count 30

# Worker de vida
python worker_node.py --master http://localhost:5000 --module life --count 25

# Worker de comida
python worker_node.py --master http://localhost:5000 --module food --count 40

# Worker de clima
python worker_node.py --master http://localhost:5000 --module climate --count 15
```

## Configuración Docker Swarm (Producción)

### Prerrequisitos en Debian 13
```bash
# Instalar Docker
sudo apt update
sudo apt install -y docker.io docker-compose

# Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 1. Inicializar Swarm en Nodo Manager
```bash
# En la primera máquina (manager)
docker swarm init --advertise-addr <IP_MANAGER>
```

Guarda el comando `docker swarm join --token ...` que aparece.

### 2. Unir Nodos Workers
```bash
# En las otras máquinas (workers)
docker swarm join --token <TOKEN> <IP_MANAGER>:2377
```

### 3. Verificar Nodos
```bash
docker node ls
```

### 4. Construir Imágenes (en manager)
```bash
cd /ruta/proyecto
docker build -t ecosystem-master:latest .
docker build -t ecosystem-worker:latest -f Dockerfile.worker .
```

### 5. Desplegar Stack
```bash
docker stack deploy -c docker-compose.yml ecosystem
```

### 6. Verificar Servicios
```bash
docker stack services ecosystem
docker service logs ecosystem_master
docker service logs ecosystem_worker-trees
```

### 7. Escalar Workers
```bash
# Aumentar workers de árboles a 5 réplicas
docker service scale ecosystem_worker-trees=5

# Aumentar workers de vida a 3 réplicas
docker service scale ecosystem_worker-life=3
```

### 8. Acceder a la Interfaz
Abre `http://<IP_MANAGER>:5000` en el navegador.

## Configuración Multi-Máquina

### Opción A: Red Overlay Automática (Docker Swarm)
Ya configurado en `docker-compose.yml` con red `ecosystem-net`.

### Opción B: Workers Manuales en Otras IPs
Si prefieres ejecutar workers fuera de Docker:

**En Máquina 1 (Master en 192.168.1.10)**
```bash
python app.py
```

**En Máquina 2 (Workers en 192.168.1.20)**
```bash
python worker_node.py --master http://192.168.1.10:5000 --module trees --count 30 &
python worker_node.py --master http://192.168.1.10:5000 --module life --count 25 &
```

**En Máquina 3 (Workers en 192.168.1.30)**
```bash
python worker_node.py --master http://192.168.1.10:5000 --module food --count 40 &
python worker_node.py --master http://192.168.1.10:5000 --module climate --count 15 &
```

## Estructura del Proyecto

```
Pagina Diseño/
├── app.py                  # Flask app principal
├── worker_node.py          # Script para nodos workers
├── requirements.txt        # Dependencias Python
├── Dockerfile              # Imagen master
├── Dockerfile.worker       # Imagen worker
├── docker-compose.yml      # Configuración Swarm
├── api/
│   ├── __init__.py
│   ├── routes.py          # Endpoints API
│   └── storage.py         # Almacenamiento en memoria
├── templates/
│   └── index.html         # Interfaz web
└── static/
    ├── css/
    │   └── styles.css
    └── js/
        ├── main.js        # Controlador principal
        └── workers/       # Web Workers (frontend)
            ├── trees.js
            ├── life.js
            ├── food.js
            └── climate.js
```

## Comandos Útiles Docker Swarm

```bash
# Ver logs en tiempo real
docker service logs -f ecosystem_master

# Inspeccionar servicio
docker service inspect ecosystem_worker-trees

# Eliminar stack
docker stack rm ecosystem

# Verificar estado del swarm
docker info | grep Swarm

# Dejar el swarm (en worker node)
docker swarm leave

# Forzar salida (en manager)
docker swarm leave --force
```

## Firewall (Debian)

Abrir puertos necesarios:
```bash
# En manager
sudo ufw allow 2377/tcp   # Swarm management
sudo ufw allow 7946/tcp   # Container network discovery
sudo ufw allow 7946/udp
sudo ufw allow 4789/udp   # Overlay network
sudo ufw allow 5000/tcp   # Flask API

sudo ufw enable
```

## Variables de Entorno

Para personalizar workers:
- `MASTER_URL`: URL del master (default: http://master:5000)
- `MODULE`: trees, life, food o climate
- `COUNT`: Número de objetos a generar
- `INTERVAL`: Intervalo en segundos entre envíos

## Troubleshooting

### Workers no conectan
- Verificar IP del master: `docker inspect ecosystem_master`
- Verificar red overlay: `docker network ls`
- Ping desde worker: `docker exec <container> ping master`

### Interfaz no muestra datos
- Verificar `/api/status` en navegador
- Revisar consola del navegador (F12)
- Verificar logs del master

### Nodos no se ven en Swarm
- Verificar conectividad de red entre máquinas
- Verificar puertos de firewall
- Reiniciar Docker: `sudo systemctl restart docker`

## Mejoras Futuras

- Persistencia con Redis/PostgreSQL
- Autenticación de nodos con JWT
- Dashboard de métricas con Grafana
- WebSockets para actualizaciones en tiempo real
- Load balancer con Nginx
