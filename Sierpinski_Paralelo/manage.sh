#!/bin/bash

# Script para gestionar el cluster de Sierpinski

case "$1" in
  build)
    echo "Construyendo imágenes Docker..."
    echo ""
    echo "📦 Construyendo imagen del master..."
    docker build -f Dockerfile.master -t sierpinski-master:latest .
    echo ""
    echo "📦 Construyendo imagen del worker..."
    docker build -f Dockerfile.worker -t sierpinski-worker:latest .
    echo ""
    echo "✓ Imágenes construidas exitosamente"
    echo ""
    docker images | grep sierpinski
    ;;
    
  deploy)
    echo "Desplegando el stack sierpinski..."
    docker stack deploy -c docker-compose.yml sierpinski
    echo "✓ Master desplegado en el nodo manager"
    echo "✓ Servicios worker creados (réplicas=0)"
    echo ""
    echo "Usa './manage.sh scale <worker> <replicas>' para escalar workers"
    ;;
    
  scale)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Uso: ./manage.sh scale <worker> <replicas>"
      echo "Workers disponibles: worker1, worker2, worker3"
      exit 1
    fi
    SERVICE="sierpinski_$2"
    REPLICAS=$3
    echo "Escalando $SERVICE a $REPLICAS réplicas..."
    docker service scale $SERVICE=$REPLICAS
    ;;
    
  status)
    echo "=== Estado del Cluster ==="
    docker node ls
    echo ""
    echo "=== Servicios ==="
    docker service ls
    echo ""
    echo "=== Distribución de tareas ==="
    docker stack ps sierpinski
    ;;
    
  logs)
    if [ -z "$2" ]; then
      echo "Uso: ./manage.sh logs <servicio>"
      echo "Servicios: master, worker1, worker2, worker3"
      exit 1
    fi
    SERVICE="sierpinski_$2"
    docker service logs $SERVICE -f
    ;;
    
  remove)
    echo "Eliminando el stack sierpinski..."
    docker stack rm sierpinski
    ;;
    
  *)
    echo "Gestor del Cluster Sierpinski"
    echo ""
    echo "Uso: ./manage.sh <comando> [opciones]"
    echo ""
    echo "Comandos:"
    echo "  build               - Construye las imágenes Docker (PRIMERO)"
    echo "  deploy              - Despliega el stack (solo master activo)"
    echo "  scale <worker> <n>  - Escala un worker (worker1|worker2|worker3)"
    echo "  status              - Muestra el estado del cluster"
    echo "  logs <servicio>     - Muestra logs (master|worker1|worker2|worker3)"
    echo "  remove              - Elimina el stack completo"
    echo ""
    echo "Ejemplos:"
    echo "  ./manage.sh build                # Construir imágenes (hacer primero)"
    echo "  ./manage.sh deploy               # Desplegar el stack"
    echo "  ./manage.sh scale worker1 1      # Escalar worker1"
    echo "  ./manage.sh scale worker2 1      # Escalar worker2"
    echo "  ./manage.sh logs master          # Ver logs del master"
    echo "  ./manage.sh status               # Ver estado del cluster"
    ;;
esac
