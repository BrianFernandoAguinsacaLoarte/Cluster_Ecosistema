#!/usr/bin/env python3
"""
Nodo Maestro - Sierpinski Paralelo
Coordina workers con regiones fijas para visualizar tolerancia a fallos
"""
from flask import Flask, render_template, jsonify, request
import threading
import time
from datetime import datetime, timedelta
from collections import deque
import math

app = Flask(__name__)

# Estado global del sistema
system_state = {
    'workers': {},  # {worker_id: {status, last_heartbeat, tasks_completed, ...}}
    'active_tasks': {},  # {task_id: {worker_id, start_time, ...}}
    'completed_tasks': {},  # {task_id: {result, time, ...}}
    'regions': {  # Triángulos por región (fijo por worker)
        'worker1': [],  # Región superior
        'worker2': [],  # Región inferior derecha
        'worker3': []   # Región inferior izquierda
    },
    'depth': 6,
    'canvas': {'width': 600, 'height': 500},
    'generation_active': False,
    'start_time': None,
    'end_time': None,
    'stats': {
        'total_tasks': 3,  # 3 regiones fijas
        'completed': 0,
        'failed': 0,
        'reassigned': 0,
        'total_triangles': 0
    }
}

state_lock = threading.Lock()

# Configuración
HEARTBEAT_TIMEOUT = 10  # segundos
TASK_TIMEOUT = 30  # segundos
TASK_CHECK_INTERVAL = 2  # segundos


def subdivide_triangle(tri, depth):
    """Genera triángulos recursivamente hasta depth"""
    if depth == 0:
        return [tri]
    
    A, B, C = tri
    mid_AB = [(A[0] + B[0]) / 2, (A[1] + B[1]) / 2]
    mid_BC = [(B[0] + C[0]) / 2, (B[1] + C[1]) / 2]
    mid_CA = [(C[0] + A[0]) / 2, (C[1] + A[1]) / 2]
    
    # Recursión en los 3 subtriángulos
    result = []
    result.extend(subdivide_triangle([A, mid_AB, mid_CA], depth - 1))
    result.extend(subdivide_triangle([mid_AB, B, mid_BC], depth - 1))
    result.extend(subdivide_triangle([mid_CA, mid_BC, C], depth - 1))
    
    return result


def monitor_workers():
    """Monitorea workers y detecta nodos caídos"""
    while True:
        time.sleep(TASK_CHECK_INTERVAL)
        now = datetime.now()
        
        with state_lock:
            # Detectar workers muertos
            for worker_id, info in system_state['workers'].items():
                last_hb = datetime.fromisoformat(info['last_heartbeat'])
                seconds_since_heartbeat = (now - last_hb).total_seconds()
                
                if seconds_since_heartbeat > HEARTBEAT_TIMEOUT:
                    if info['status'] == 'active':
                        info['status'] = 'dead'
                        
                        # Limpiar COMPLETAMENTE los datos del worker muerto
                        if worker_id in system_state['completed_tasks']:
                            print(f"🧹 Eliminando tarea completada de {worker_id}")
                            del system_state['completed_tasks'][worker_id]
                        
                        if worker_id in system_state['active_tasks']:
                            print(f"🧹 Eliminando tarea activa de {worker_id}")
                            del system_state['active_tasks'][worker_id]
                        
                        # Limpiar región de triángulos
                        triangulos_eliminados = len(system_state['regions'].get(worker_id, []))
                        system_state['regions'][worker_id] = []
                        
                        print(f"\n⚠️  Worker {worker_id} MUERTO (sin heartbeat por {seconds_since_heartbeat:.1f}s)")
                        print(f"   🧹 Región limpiada ({triangulos_eliminados} triángulos eliminados)")
                        print(f"   📊 Regiones restantes:")
                        for wid in ['worker1', 'worker2', 'worker3']:
                            count = len(system_state['regions'].get(wid, []))
                            status = system_state['workers'].get(wid, {}).get('status', 'N/A')
                            print(f"      {wid}: {count} triángulos ({status})")


# Thread de monitoreo
monitor_thread = threading.Thread(target=monitor_workers, daemon=True)
monitor_thread.start()


@app.route('/')
def index():
    """Página principal"""
    with state_lock:
        print("\n🌐 PÁGINA SOLICITADA - Verificando estado inicial:")
        print(f"   Generation active: {system_state['generation_active']}")
        print(f"   Workers registrados: {len(system_state['workers'])}")
        print(f"   Tareas completadas: {len(system_state['completed_tasks'])}")
        print(f"   Triángulos por región:")
        for wid in ['worker1', 'worker2', 'worker3']:
            count = len(system_state['regions'].get(wid, []))
            print(f"      {wid}: {count} triángulos")
        total = sum(len(system_state['regions'].get(w, [])) for w in ['worker1', 'worker2', 'worker3'])
        print(f"   TOTAL: {total} triángulos en memoria\n")
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    """Maneja el favicon para evitar errores 404"""
    from flask import send_from_directory
    import os
    # Retorna 204 No Content si no hay favicon
    return '', 204


@app.route('/api/worker/register', methods=['POST'])
def register_worker():
    """Registra un nuevo worker"""
    print("\n🔔 Solicitud de registro recibida...")
    print(f"   Método: {request.method}")
    print(f"   Headers: {dict(request.headers)}")
    print(f"   Content-Type: {request.content_type}")
    
    data = request.get_json() or {}
    print(f"   JSON recibido: {data}")
    
    worker_id = data.get('worker_id')
    
    if not worker_id:
        print("   ❌ ERROR: worker_id no proporcionado")
        return jsonify({'error': 'worker_id required'}), 400
    
    with state_lock:
        if worker_id not in system_state['workers']:
            system_state['workers'][worker_id] = {
                'worker_id': worker_id,
                'status': 'active',
                'registered_at': datetime.now().isoformat(),
                'last_heartbeat': datetime.now().isoformat(),
                'tasks_completed': 0,
                'tasks_active': 0,
                'total_compute_time': 0.0
            }
            print(f"   ✅ Worker {worker_id} registrado exitosamente")
            print(f"   📊 Total workers activos: {len(system_state['workers'])}")
        else:
            # Reactivar worker
            system_state['workers'][worker_id]['status'] = 'active'
            system_state['workers'][worker_id]['last_heartbeat'] = datetime.now().isoformat()
            print(f"   🔄 Worker {worker_id} reactivado")
    
    return jsonify({'status': 'ok', 'worker_id': worker_id}), 200


@app.route('/api/worker/heartbeat', methods=['POST'])
def heartbeat():
    """Recibe heartbeat de worker"""
    data = request.get_json() or {}
    worker_id = data.get('worker_id')
    
    if not worker_id:
        return jsonify({'error': 'worker_id required'}), 400
    
    with state_lock:
        if worker_id in system_state['workers']:
            system_state['workers'][worker_id]['last_heartbeat'] = datetime.now().isoformat()
            return jsonify({'status': 'ok'}), 200
    
    return jsonify({'error': 'worker not registered'}), 404


@app.route('/api/task/request', methods=['GET'])
def request_task():
    """Worker solicita su región asignada (fija)"""
    worker_id = request.args.get('worker_id')
    
    if not worker_id:
        return jsonify({'error': 'worker_id required'}), 400
    
    with state_lock:
        # Verificar que el worker esté registrado
        if worker_id not in system_state['workers']:
            return jsonify({'error': 'worker not registered'}), 404
        
        # Actualizar heartbeat
        system_state['workers'][worker_id]['last_heartbeat'] = datetime.now().isoformat()
        
        # Verificar si hay generación activa
        if not system_state['generation_active']:
            return jsonify({'status': 'no_generation'}), 202
        
        # Verificar si ya procesó su tarea
        if worker_id in system_state['active_tasks']:
            return jsonify({'status': 'already_processing'}), 202
        
        if worker_id in system_state['completed_tasks']:
            return jsonify({'status': 'already_completed'}), 202
        
        # Asignar región fija según worker_id
        width = system_state['canvas']['width']
        height = system_state['canvas']['height']
        depth = system_state['depth']
        
        # Crear triángulo inicial
        padding = 50
        side = min(width - 2 * padding, (height - 2 * padding) * 1.15)
        h = side * math.sqrt(3) / 2
        x_center = width / 2
        y_top = padding
        
        A = [x_center, y_top]
        B = [x_center - side / 2, y_top + h]
        C = [x_center + side / 2, y_top + h]
        
        # Calcular puntos medios
        mid_AB = [(A[0] + B[0]) / 2, (A[1] + B[1]) / 2]
        mid_BC = [(B[0] + C[0]) / 2, (B[1] + C[1]) / 2]
        mid_CA = [(C[0] + A[0]) / 2, (C[1] + A[1]) / 2]
        
        # Asignar región según worker_id
        if worker_id == 'worker1':
            triangle = [A, mid_AB, mid_CA]  # Superior
            region_name = "Superior"
        elif worker_id == 'worker2':
            triangle = [mid_AB, B, mid_BC]  # Inferior Derecha
            region_name = "Inf. Derecha"
        elif worker_id == 'worker3':
            triangle = [mid_CA, mid_BC, C]  # Inferior Izquierda
            region_name = "Inf. Izquierda"
        else:
            return jsonify({'error': 'invalid worker_id'}), 400
        
        # Crear tarea para esta región
        task = {
            'task_id': worker_id,
            'triangle': triangle,
            'depth': depth,
            'region_name': region_name
        }
        
        # Registrar tarea activa
        system_state['active_tasks'][worker_id] = {
            'worker_id': worker_id,
            'start_time': datetime.now().isoformat(),
            'original_task': task
        }
        
        system_state['workers'][worker_id]['tasks_active'] += 1
        
        print(f"📤 Región {region_name} asignada a {worker_id}")
        
        return jsonify({
            'status': 'ok',
            'task': task
        }), 200


@app.route('/api/task/result', methods=['POST'])
def submit_result():
    """Worker envía resultado de su región"""
    data = request.get_json() or {}
    worker_id = data.get('worker_id')
    task_id = data.get('task_id')
    triangles = data.get('triangles', [])
    compute_time = data.get('compute_time', 0.0)
    
    if worker_id is None or task_id is None:
        return jsonify({'error': 'worker_id and task_id required'}), 400
    
    with state_lock:
        # Verificar que la tarea esté activa
        if task_id not in system_state['active_tasks']:
            return jsonify({'error': 'task not active or already completed'}), 409
        
        task_info = system_state['active_tasks'][task_id]
        
        # Verificar que el worker sea el correcto
        if task_info['worker_id'] != worker_id:
            return jsonify({'error': 'task assigned to different worker'}), 409
        
        # Registrar resultado
        system_state['completed_tasks'][task_id] = {
            'worker_id': worker_id,
            'triangles': triangles,
            'compute_time': compute_time,
            'completed_at': datetime.now().isoformat()
        }
        
        # Guardar triángulos en región específica del worker
        system_state['regions'][worker_id] = triangles
        system_state['stats']['completed'] += 1
        system_state['stats']['total_triangles'] += len(triangles)
        
        # Actualizar worker stats
        if worker_id in system_state['workers']:
            system_state['workers'][worker_id]['tasks_completed'] += 1
            system_state['workers'][worker_id]['tasks_active'] -= 1
            system_state['workers'][worker_id]['total_compute_time'] += compute_time
            system_state['workers'][worker_id]['last_heartbeat'] = datetime.now().isoformat()
        
        # Remover de tareas activas
        del system_state['active_tasks'][task_id]
        
        # Verificar si terminamos (todas las tareas de workers activos completadas)
        total_tasks_expected = system_state['stats']['total_tasks']
        if system_state['stats']['completed'] >= total_tasks_expected:
            system_state['end_time'] = datetime.now().isoformat()
            system_state['generation_active'] = False
            print(f"\n🎉 GENERACIÓN COMPLETADA!")
            print(f"   Total triángulos: {system_state['stats']['total_triangles']}")
        
        region_name = task_info['original_task'].get('region_name', '')
        print(f"✅ Región {region_name} completada por {worker_id} ({len(triangles)} triángulos, {compute_time:.3f}s)")
    
    return jsonify({'status': 'ok'}), 200


@app.route('/api/reset', methods=['POST'])
def reset_system():
    """Limpia completamente el estado del sistema"""
    with state_lock:
        system_state['active_tasks'].clear()
        system_state['completed_tasks'].clear()
        system_state['regions']['worker1'] = []
        system_state['regions']['worker2'] = []
        system_state['regions']['worker3'] = []
        system_state['generation_active'] = False
        system_state['start_time'] = None
        system_state['end_time'] = None
        system_state['stats'] = {
            'total_tasks': 3,
            'completed': 0,
            'failed': 0,
            'reassigned': 0,
            'total_triangles': 0
        }
        print("\n🧹 SISTEMA COMPLETAMENTE LIMPIADO")
        print("   Todas las regiones vaciadas")
        print("   Todos los estados reseteados\n")
    
    return jsonify({'status': 'ok', 'message': 'System reset complete'}), 200


@app.route('/api/generate', methods=['POST'])
def start_generation():
    """Inicia generación del fractal con regiones fijas"""
    data = request.get_json() or {}
    depth = data.get('depth', 6)
    
    with state_lock:
        if system_state['generation_active']:
            return jsonify({'error': 'generation already active'}), 409
        
        # Contar workers activos
        active_workers = sum(1 for w in system_state['workers'].values() if w['status'] == 'active')
        
        if active_workers == 0:
            return jsonify({'error': 'no active workers available'}), 400
        
        print("\n🧹 LIMPIANDO ESTADO ANTES DE GENERAR...")
        
        # Reset estado COMPLETO
        system_state['active_tasks'].clear()
        system_state['completed_tasks'].clear()
        
        # Limpiar TODAS las regiones EXPLÍCITAMENTE
        for worker_id in ['worker1', 'worker2', 'worker3']:
            old_count = len(system_state['regions'][worker_id])
            system_state['regions'][worker_id] = []
            if old_count > 0:
                print(f"   🗑️  {worker_id}: Eliminados {old_count} triángulos")
        
        system_state['depth'] = depth
        system_state['start_time'] = datetime.now().isoformat()
        system_state['end_time'] = None
        system_state['generation_active'] = True
        
        system_state['stats'] = {
            'total_tasks': active_workers,  # Solo contar workers activos
            'completed': 0,
            'failed': 0,
            'reassigned': 0,
            'total_triangles': 0
        }
        
        print(f"\n🚀 GENERACIÓN INICIADA (Regiones Fijas)")
        print(f"   Profundidad: {depth}")
        print(f"   Worker1 → Región Superior {'✅' if 'worker1' in system_state['workers'] and system_state['workers']['worker1']['status'] == 'active' else '❌'}")
        print(f"   Worker2 → Región Inferior Derecha {'✅' if 'worker2' in system_state['workers'] and system_state['workers']['worker2']['status'] == 'active' else '❌'}")
        print(f"   Worker3 → Región Inferior Izquierda {'✅' if 'worker3' in system_state['workers'] and system_state['workers']['worker3']['status'] == 'active' else '❌'}")
        print(f"   Workers activos: {active_workers}")
    
    return jsonify({
        'status': 'ok',
        'total_tasks': active_workers,
        'depth': depth
    }), 200


@app.route('/api/status', methods=['GET'])
def get_status():
    """Obtiene estado del sistema en tiempo real"""
    with state_lock:
        workers_list = []
        for worker_id, info in system_state['workers'].items():
            region_name = ""
            if worker_id == 'worker1':
                region_name = "Superior"
            elif worker_id == 'worker2':
                region_name = "Inf. Derecha"
            elif worker_id == 'worker3':
                region_name = "Inf. Izquierda"
            
            workers_list.append({
                'worker_id': worker_id,
                'status': info['status'],
                'region': region_name,
                'tasks_completed': info['tasks_completed'],
                'tasks_active': info['tasks_active'],
                'total_compute_time': info['total_compute_time'],
                'last_heartbeat': info['last_heartbeat']
            })
        
        elapsed = None
        if system_state['start_time']:
            start = datetime.fromisoformat(system_state['start_time'])
            if system_state['end_time']:
                end = datetime.fromisoformat(system_state['end_time'])
                elapsed = (end - start).total_seconds()
            else:
                elapsed = (datetime.now() - start).total_seconds()
        
        response = jsonify({
            'workers': workers_list,
            'tasks_pending': 0,
            'tasks_active': len(system_state['active_tasks']),
            'tasks_completed': system_state['stats']['completed'],
            'tasks_total': 3,  # 3 regiones fijas
            'tasks_reassigned': system_state['stats']['reassigned'],
            'triangles_total': system_state['stats']['total_triangles'],
            'generation_active': system_state['generation_active'],
            'elapsed_time': elapsed,
            'depth': system_state['depth']
        })
        
        # Evitar cache del navegador
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response, 200


@app.route('/api/data', methods=['GET'])
def get_data():
    """Retorna triángulos (solo regiones con workers activos)"""
    with state_lock:
        all_triangles = []
        regions_info = {}
        
        print("\n" + "="*60)
        print("🔍 DEBUG /api/data - DECISIÓN DE FILTRADO")
        print("="*60)
        
        # Solo incluir triángulos de workers activos que completaron su región
        for worker_id in ['worker1', 'worker2', 'worker3']:
            worker_exists = worker_id in system_state['workers']
            worker_active = worker_exists and system_state['workers'][worker_id]['status'] == 'active'
            task_completed = worker_id in system_state['completed_tasks']
            has_triangles = len(system_state['regions'].get(worker_id, [])) > 0
            
            print(f"\n📌 {worker_id.upper()}:")
            print(f"   ├─ Existe en workers: {worker_exists}")
            print(f"   ├─ Status activo: {worker_active}")
            print(f"   ├─ Tarea completada: {task_completed}")
            print(f"   ├─ Triángulos en región: {len(system_state['regions'].get(worker_id, []))}")
            
            # Condición: activo AND completado AND tiene triángulos
            incluir = worker_active and task_completed and has_triangles
            print(f"   └─ DECISIÓN: {'✅ INCLUIR' if incluir else '❌ EXCLUIR'}")
            
            if incluir:
                print(f"      └─ Razón: Worker activo + Tarea completa + Tiene triángulos")
            else:
                razones = []
                if not worker_active: razones.append("Worker no activo")
                if not task_completed: razones.append("Tarea no completada")
                if not has_triangles: razones.append("Sin triángulos")
                print(f"      └─ Razón: {', '.join(razones)}")
            
            regions_info[worker_id] = incluir
            
            # Solo agregar triángulos si el worker está activo y completó su tarea
            if incluir:
                triangulos_agregados = len(system_state['regions'][worker_id])
                all_triangles.extend(system_state['regions'][worker_id])
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"   └─ Total triángulos enviados al navegador: {len(all_triangles)}")
        print("="*60 + "\n")
        
        response = jsonify({
            'triangles': all_triangles,
            'count': len(all_triangles),
            'regions_active': regions_info
        })
        
        # Evitar cache del navegador
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response, 200


if __name__ == '__main__':
    print("=" * 60)
    print("🎯 NODO MAESTRO - SIERPINSKI PARALELO (Regiones Fijas)")
    print("=" * 60)
    
    # Verificar estado inicial limpio
    print("\n🔍 Verificando estado inicial:")
    with state_lock:
        total_triangles = sum(len(system_state['regions'].get(w, [])) for w in ['worker1', 'worker2', 'worker3'])
        print(f"   Triángulos en memoria: {total_triangles}")
        print(f"   Generation active: {system_state['generation_active']}")
        print(f"   Workers registrados: {len(system_state['workers'])}")
        for wid in ['worker1', 'worker2', 'worker3']:
            count = len(system_state['regions'].get(wid, []))
            if count > 0:
                print(f"      {wid}: {count} triángulos")
        if total_triangles > 0:
            print("   ⚠️  ADVERTENCIA: Hay triángulos en memoria al iniciar!")
        else:
            print("   ✅ Estado inicial limpio")
    
    print("\n📘 Instrucciones:")
    print("   1. Inicia workers en diferentes terminales:")
    print(f"      python worker.py --master http://127.0.0.1:5002 --id worker1")
    print(f"      python worker.py --master http://127.0.0.1:5002 --id worker2")
    print(f"      python worker.py --master http://127.0.0.1:5002 --id worker3")
    print(f"   2. Abre http://127.0.0.1:5002 en el navegador")
    print("   3. Genera un fractal y observa cómo cada worker procesa su región")
    print("   4. Desconecta un worker (Ctrl+C) y observa cómo su región desaparece")
    print("=" * 60)
    print()
    print("👂 Esperando conexiones de workers...")
    print()
    
    # Iniciar monitor de workers en background
    monitor_thread = threading.Thread(target=monitor_workers, daemon=True)
    monitor_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
