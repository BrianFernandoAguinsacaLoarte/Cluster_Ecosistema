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

def run_worker(master_url, module, object_count, interval):
    """Main worker loop"""
    node_id = get_node_id()
    generators = {
        'trees': generate_trees_data,
        'life': generate_life_data,
        'food': generate_food_data,
        'climate': generate_climate_data
    }
    
    if module not in generators:
        print(f"Error: Invalid module '{module}'. Must be: trees, life, food, or climate")
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ecosystem simulation worker node')
    parser.add_argument('--master', required=True, help='Master API URL (e.g., http://192.168.1.10:5000)')
    parser.add_argument('--module', required=True, choices=['trees', 'life', 'food', 'climate'],
                        help='Ecosystem module to simulate')
    parser.add_argument('--count', type=int, default=20, help='Number of objects to generate (default: 20)')
    parser.add_argument('--interval', type=int, default=2, help='Update interval in seconds (default: 2)')
    
    args = parser.parse_args()
    
    run_worker(args.master, args.module, args.count, args.interval)
