#!/usr/bin/env python3
"""
Nodo Worker - Sierpinski Paralelo
Procesa tareas en paralelo con otros workers (no espera turnos)
"""
import requests
import time
import argparse
import sys
import socket
import random
import threading


def midpoint(p1, p2):
    """Calcula punto medio"""
    return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]


def sierpinski_subdivide(tri, depth, out):
    """Genera triángulos de Sierpinski recursivamente"""
    if depth == 0:
        # Aplanar triángulo para envío
        out.append([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]])
        return
    
    A, B, C = tri
    mid_AB = midpoint(A, B)
    mid_BC = midpoint(B, C)
    mid_CA = midpoint(C, A)
    
    # Recursión en 3 subtriángulos (omitir el central)
    sierpinski_subdivide([A, mid_AB, mid_CA], depth - 1, out)
    sierpinski_subdivide([mid_AB, B, mid_BC], depth - 1, out)
    sierpinski_subdivide([mid_CA, mid_BC, C], depth - 1, out)


def process_task(task):
    """Procesa una tarea de Sierpinski"""
    triangle = task['triangle']
    depth = task['depth']
    
    triangles = []
    start_time = time.time()
    
    # Generar triángulos recursivamente
    sierpinski_subdivide(triangle, depth, triangles)
    
    compute_time = time.time() - start_time
    
    return {
        'triangles': triangles,
        'compute_time': compute_time,
        'count': len(triangles)
    }


class Worker:
    def __init__(self, master_url, worker_id):
        self.master_url = master_url.rstrip('/')
        self.worker_id = worker_id
        self.running = True
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_compute_time': 0.0,
            'triangles_generated': 0
        }
        
    def register(self):
        """Registra el worker con el maestro"""
        url = f"{self.master_url}/api/worker/register"
        print(f"\n📡 Intentando registrar como {self.worker_id}...")
        print(f"   URL: {url}")
        try:
            print(f"   Enviando POST request...")
            response = requests.post(url, json={'worker_id': self.worker_id}, timeout=5)
            print(f"   Respuesta recibida: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Registrado exitosamente como {self.worker_id}")
                return True
            else:
                print(f"❌ Error en registro: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Error de conexión: No se puede conectar al maestro")
            print(f"   Verifica que el master esté ejecutándose en {self.master_url}")
            print(f"   Detalle: {e}")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ Timeout: El maestro no respondió en 5 segundos")
            return False
        except Exception as e:
            print(f"❌ Error inesperado conectando al maestro: {e}")
            return False
    
    def heartbeat_loop(self):
        """Envía heartbeat periódico al maestro"""
        url = f"{self.master_url}/api/worker/heartbeat"
        while self.running:
            try:
                response = requests.post(url, json={'worker_id': self.worker_id}, timeout=5)
                if response.status_code != 200:
                    print(f"⚠️  Heartbeat falló: {response.status_code}")
            except Exception as e:
                print(f"⚠️  Error en heartbeat: {e}")
            
            time.sleep(3)  # Heartbeat cada 3 segundos
    
    def request_task(self):
        """Solicita tarea al maestro (sin esperar turno)"""
        url = f"{self.master_url}/api/task/request"
        try:
            response = requests.get(url, params={'worker_id': self.worker_id}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    return data.get('task')
            elif response.status_code == 202:
                # No hay tareas disponibles aún
                return None
            else:
                print(f"⚠️  Error solicitando tarea: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error solicitando tarea: {e}")
            return None
    
    def submit_result(self, task_id, result):
        """Envía resultado de tarea al maestro"""
        url = f"{self.master_url}/api/task/result"
        payload = {
            'worker_id': self.worker_id,
            'task_id': task_id,
            'triangles': result['triangles'],
            'compute_time': result['compute_time']
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                print(f"⚠️  Error enviando resultado: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error enviando resultado: {e}")
            return False
    
    def work_loop(self):
        """Loop principal: solicita y procesa tareas continuamente"""
        print(f"🔄 Iniciando loop de trabajo...")
        print(f"   Solicitando tareas continuamente (sin esperar turno)")
        print("=" * 60)
        
        idle_count = 0
        
        while self.running:
            try:
                # Solicitar tarea (INMEDIATO, sin esperar turno)
                task = self.request_task()
                
                if task is None:
                    # No hay tareas disponibles
                    idle_count += 1
                    if idle_count % 10 == 1:
                        print(f"⏳ Esperando tareas... (intentos: {idle_count})")
                    time.sleep(1)
                    continue
                
                idle_count = 0
                task_id = task['task_id']
                
                print(f"\n📥 Tarea {task_id} recibida")
                print(f"   Profundidad: {task['depth']}")
                
                # Procesar tarea
                print(f"⚙️  Procesando tarea {task_id}...")
                result = process_task(task)
                
                print(f"✅ Tarea {task_id} completada:")
                print(f"   - Triángulos: {result['count']}")
                print(f"   - Tiempo: {result['compute_time']:.4f}s")
                
                # Enviar resultado
                if self.submit_result(task_id, result):
                    self.stats['tasks_completed'] += 1
                    self.stats['total_compute_time'] += result['compute_time']
                    self.stats['triangles_generated'] += result['count']
                    print(f"📤 Resultado enviado exitosamente")
                else:
                    self.stats['tasks_failed'] += 1
                    print(f"❌ Falló envío de resultado")
                
                print(f"\n📊 Stats Locales:")
                print(f"   - Tareas completadas: {self.stats['tasks_completed']}")
                print(f"   - Tiempo total cómputo: {self.stats['total_compute_time']:.2f}s")
                print(f"   - Triángulos generados: {self.stats['triangles_generated']}")
                print("=" * 60)
                
            except KeyboardInterrupt:
                print(f"\n\n🛑 Worker {self.worker_id} detenido por usuario")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Error en work loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(2)
    
    def run(self):
        """Inicia el worker"""
        print("\n" + "=" * 60)
        print(f"🚀 WORKER NODE: {self.worker_id}")
        print("=" * 60)
        print(f"Maestro: {self.master_url}")
        print("=" * 60)
        
        # Registrarse con el maestro
        if not self.register():
            print("❌ No se pudo registrar con el maestro. Abortando.")
            return
        
        # Iniciar thread de heartbeat
        heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        print(f"💓 Heartbeat iniciado (cada 3s)")
        
        # Iniciar loop de trabajo
        try:
            self.work_loop()
        finally:
            self.running = False
            print(f"\n📊 RESUMEN FINAL - {self.worker_id}:")
            print(f"   Tareas completadas: {self.stats['tasks_completed']}")
            print(f"   Tareas fallidas: {self.stats['tasks_failed']}")
            print(f"   Tiempo total: {self.stats['total_compute_time']:.2f}s")
            print(f"   Triángulos generados: {self.stats['triangles_generated']}")
            print("=" * 60)


def get_hostname_id():
    """Genera ID basado en hostname"""
    hostname = socket.gethostname()
    return f"{hostname}-{random.randint(1000, 9999)}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Worker Node - Sierpinski Paralelo')
    parser.add_argument('--master', required=True, help='URL del maestro (ej: http://127.0.0.1:5000)')
    parser.add_argument('--id', dest='worker_id', help='ID del worker (opcional, se genera automático)')
    
    args = parser.parse_args()
    
    worker_id = args.worker_id or get_hostname_id()
    
    worker = Worker(args.master, worker_id)
    worker.run()
