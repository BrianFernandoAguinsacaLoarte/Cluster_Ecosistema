#!/bin/bash

# Script para configurar un nodo worker

echo "🔧 Configurando nodo worker..."
echo ""

# 1. Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "📦 Instalando Docker..."
    sudo apt update
    sudo apt install docker.io -y
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "✅ Docker instalado"
else
    echo "✅ Docker ya está instalado"
fi

# 2. Construir imágenes
echo ""
echo "🏗️  Construyendo imágenes Docker..."
docker build -f Dockerfile -t ecosystem-master:latest .
docker build -f Dockerfile.worker -t ecosystem-worker:latest .

# Para Sierpinski (si existe)
if [ -d "Sierpinski_Paralelo" ]; then
    cd Sierpinski_Paralelo
    docker build -f Dockerfile.master -t sierpinski-master:latest .
    docker build -f Dockerfile.worker -t sierpinski-worker:latest .
    cd ..
fi

echo ""
echo "✅ Imágenes construidas exitosamente"
echo ""
docker images | grep -E "ecosystem|sierpinski"

echo ""
echo "📝 Próximo paso:"
echo "   Ejecuta el comando 'docker swarm join' que te dio el manager"
echo "   Ejemplo: docker swarm join --token SWMTKN-1-xxx... IP_MANAGER:2377"
