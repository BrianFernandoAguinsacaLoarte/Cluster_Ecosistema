#!/bin/bash

# Script para gestionar el cluster del ecosistema

case "$1" in
  deploy)
    echo "Desplegando el stack cluster_ecosistema..."
    docker stack deploy -c docker-compose.yml cluster_ecosistema
    echo "✓ Master desplegado en el nodo manager"
    echo "✓ Servicios worker creados (réplicas=0)"
    echo ""
    echo "Usa './manage.sh scale <servicio> <replicas>' para escalar workers"
    ;;
    
  scale)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Uso: ./manage.sh scale <servicio> <replicas>"
      echo "Servicios disponibles: trees, life, food, climate"
      exit 1
    fi
    SERVICE="cluster_ecosistema_worker-$2"
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
    docker stack ps cluster_ecosistema
    ;;
    
  logs)
    if [ -z "$2" ]; then
      echo "Uso: ./manage.sh logs <servicio>"
      echo "Servicios: master, trees, life, food, climate"
      exit 1
    fi
    if [ "$2" == "master" ]; then
      SERVICE="cluster_ecosistema_master"
    else
      SERVICE="cluster_ecosistema_worker-$2"
    fi
    docker service logs $SERVICE -f
    ;;
    
  remove)
    echo "Eliminando el stack cluster_ecosistema..."
    docker stack rm cluster_ecosistema
    ;;
    
  *)
    echo "Gestor del Cluster Ecosistema"
    echo ""
    echo "Uso: ./manage.sh <comando> [opciones]"
    echo ""
    echo "Comandos:"
    echo "  deploy              - Despliega el stack (solo master activo)"
    echo "  scale <tipo> <n>    - Escala un worker (trees|life|food|climate)"
    echo "  status              - Muestra el estado del cluster"
    echo "  logs <servicio>     - Muestra logs (master|trees|life|food|climate)"
    echo "  remove              - Elimina el stack completo"
    echo ""
    echo "Ejemplos:"
    echo "  ./manage.sh deploy"
    echo "  ./manage.sh scale trees 2"
    echo "  ./manage.sh scale life 1"
    echo "  ./manage.sh logs master"
    echo "  ./manage.sh status"
    ;;
esac
