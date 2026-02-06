#!/usr/bin/env python3
"""
Worker node script that generates simulation data and sends to master API.
Each node generates objects for one ecosystem module (trees, life, food, or climate).
"""
import requests
import time
import random
import argparse
import sys
import socket

def get_node_id():
    """Generate unique node ID from hostname and random suffix"""
    hostname = socket.gethostname()
    return f"{hostname}-{random.randint(1000, 9999)}"

def generate_trees_data(count):
    """Generate tree objects"""
    return [
        {
            'x': random.random() * 400,
            'y': random.random() * 300,
            'height': 20 + random.random() * 40,
            'growth': 0.1 + random.random() * 0.3
        }
        for _ in range(count)
    ]

def generate_life_data(count):
    """Generate animal objects"""
    return [
        {
            'x': random.random() * 400,
            'y': random.random() * 300,
            'vx': -1 + random.random() * 2,
            'vy': -1 + random.random() * 2,
            'energy': 50 + random.random() * 50
        }
        for _ in range(count)
    ]

def generate_food_data(count):
    """Generate food resource objects"""
    return [
        {
            'x': random.random() * 400,
            'y': random.random() * 300,
            'amount': 50 + random.random() * 50,
            'regen': 0.3 + random.random() * 0.7
        }
        for _ in range(count)
    ]

def generate_climate_data(count):
    """Generate climate objects (clouds)"""
    return [
        {
            'x': random.random() * 400,
            'y': 20 + random.random() * 100,
            'vx': 0.3 + random.random() * 0.8,
            'size': 20 + random.random() * 40,
            'temperature': 15 + random.random() * 15,
            'humidity': 0.3 + random.random() * 0.5
        }
        for _ in range(count)
    ]


def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)


def sierpinski_subdivide(tri, depth, out):
    if depth == 0:
        out.append([tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]])
        return
    a, b, c = tri
    ab = midpoint(a, b)
    bc = midpoint(b, c)
    ca = midpoint(c, a)
    sierpinski_subdivide((a, ab, ca), depth - 1, out)
    sierpinski_subdivide((ab, b, bc), depth - 1, out)
    sierpinski_subdivide((ca, bc, c), depth - 1, out)


def generate_sierpinski_triangles(region_id, depth, width, height, padding=10):
    a = (width / 2.0, padding)
    b = (padding, height - padding)
    c = (width - padding, height - padding)
    ab = midpoint(a, b)
    bc = midpoint(b, c)
    ca = midpoint(c, a)

    if region_id == 0:
        base = (a, ab, ca)
    elif region_id == 1:
        base = (ab, b, bc)
    else:
        base = (ca, bc, c)

    triangles = []
    sierpinski_subdivide(base, depth, triangles)
    return triangles

def run_worker(master_url, module, object_count, interval):
    """Main worker loop"""
    node_id = get_node_id()
    generators = {
        'trees': generate_trees_data,
        'life': generate_life_data,
        'food': generate_food_data,
        'climate': generate_climate_data
    }
    
    if module == 'sierpinski':
        run_sierpinski_worker(master_url, node_id, interval)
        return
    if module not in generators:
        print(f"Error: Invalid module '{module}'. Must be: trees, life, food, climate, or sierpinski")
        sys.exit(1)
    
    generate = generators[module]
    endpoint = f"{master_url}/api/data/{module}"
    
    print(f"Worker Node: {node_id}")
    print(f"Module: {module}")
    print(f"Objects: {object_count}")
    print(f"Interval: {interval}s")
    print(f"Master API: {endpoint}")
    print("=" * 50)
    
    iteration = 0
    while True:
        try:
            # Generate data
            data = generate(object_count)
            
            # Prepare payload
            payload = {
                'node_id': node_id,
                'data': data,
                'stats': {
                    'count': len(data),
                    'iteration': iteration
                }
            }
            
            # Send to master
            response = requests.post(endpoint, json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"[{iteration}] ✓ Sent {len(data)} {module} objects to master")
            else:
                print(f"[{iteration}] ✗ Error: {response.status_code} - {response.text}")
            
            iteration += 1
            time.sleep(interval)
            
        except requests.exceptions.ConnectionError:
            print(f"[{iteration}] ✗ Cannot connect to master at {master_url}")
            time.sleep(interval * 2)
        except KeyboardInterrupt:
            print("\nShutting down worker node...")
            break
        except Exception as e:
            print(f"[{iteration}] ✗ Error: {e}")
            time.sleep(interval)


def run_sierpinski_worker(master_url, node_id, interval):
    register_url = f"{master_url}/api/sierpinski/register"
    task_url = f"{master_url}/api/sierpinski/task"
    result_url = f"{master_url}/api/sierpinski/result"

    def register():
        try:
            reg = requests.post(register_url, json={'node_id': node_id}, timeout=5)
            if reg.status_code != 200:
                print(f"Registration failed: {reg.status_code} - {reg.text}")
                return False
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            return False

    if not register():
        return

    print(f"Sierpinski Worker Node: {node_id}")
    print(f"Master API: {master_url}")
    print("Waiting for tasks...")
    print("=" * 50)

    while True:
        try:
            resp = requests.get(task_url, params={'node_id': node_id}, timeout=10)
            if resp.status_code == 404:
                if not register():
                    time.sleep(interval)
                continue
            if resp.status_code == 204:
                time.sleep(interval)
                continue
            if resp.status_code == 202:
                time.sleep(interval)
                continue
            if resp.status_code != 200:
                print(f"Task error: {resp.status_code} - {resp.text}")
                time.sleep(interval)
                continue

            task = resp.json()
            region_id = task.get('region_id')
            depth = task.get('depth')
            canvas = task.get('canvas') or {}
            width = canvas.get('width', 400)
            height = canvas.get('height', 300)

            triangles = generate_sierpinski_triangles(region_id, depth, width, height)
            payload = {
                'node_id': node_id,
                'task_id': task.get('task_id'),
                'region_id': region_id,
                'triangles': triangles,
                'stats': {
                    'triangles': len(triangles),
                    'depth': depth
                }
            }

            send = requests.post(result_url, json=payload, timeout=10)
            if send.status_code == 200:
                print(f"✓ Sent region {region_id} ({len(triangles)} triangles)")
            elif send.status_code in (404, 409):
                print("Result rejected, re-registering...")
                register()
            else:
                print(f"Result error: {send.status_code} - {send.text}")

            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nShutting down Sierpinski worker...")
            break
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(interval)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ecosystem simulation worker node')
    parser.add_argument('--master', required=True, help='Master API URL (e.g., http://192.168.1.10:5000)')
    parser.add_argument('--module', required=True, choices=['trees', 'life', 'food', 'climate', 'sierpinski'],
                        help='Ecosystem module to simulate')
    parser.add_argument('--count', type=int, default=20, help='Number of objects to generate (default: 20)')
    parser.add_argument('--interval', type=int, default=2, help='Update interval in seconds (default: 2)')
    
    args = parser.parse_args()
    
    run_worker(args.master, args.module, args.count, args.interval)
