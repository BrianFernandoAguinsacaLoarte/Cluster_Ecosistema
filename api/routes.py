"""
API routes for distributed node communication
Endpoints to receive and aggregate data from worker nodes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from .storage import node_data, data_lock, sierpinski_state

api_bp = Blueprint('api', __name__, url_prefix='/api')


def find_slot_index(node_id):
    slots = sierpinski_state['slots']
    for idx, slot in enumerate(slots):
        if slot and slot.get('node_id') == node_id:
            return idx
    return None


def cleanup_sierpinski_stale():
    now = datetime.now()
    timeout_seconds = sierpinski_state['timeout_seconds']
    slots = sierpinski_state['slots']
    latest = sierpinski_state['latest']
    current = sierpinski_state['current_task']

    for idx, slot in enumerate(slots):
        if not slot:
            continue
        last_seen = slot.get('last_seen')
        if not last_seen:
            continue
        age = (now - datetime.fromisoformat(last_seen)).total_seconds()
        if age <= timeout_seconds:
            continue

        slots[idx] = None
        latest[idx] = None

        if current and current.get('slot_index') == idx:
            current_created = current.get('created_at')
            if current_created:
                task_age = (now - datetime.fromisoformat(current_created)).total_seconds()
                if task_age > timeout_seconds:
                    sierpinski_state['current_task'] = None
                    sierpinski_state['task_counter'] += 1
                    sierpinski_state['turn_index'] = (sierpinski_state['turn_index'] + 1) % 3

@api_bp.route('/data/<module>', methods=['POST'])
def receive_data(module):
    """Receive data from worker nodes"""
    if module not in node_data:
        return jsonify({'error': 'Invalid module'}), 400
    
    data = request.get_json()
    node_id = data.get('node_id', 'unknown')
    
    with data_lock:
        node_data[module][node_id] = {
            'timestamp': datetime.now().isoformat(),
            'data': data.get('data', []),
            'stats': data.get('stats', {})
        }
    
    return jsonify({'status': 'ok', 'module': module, 'node_id': node_id}), 200

@api_bp.route('/data/<module>', methods=['GET'])
def get_data(module):
    """Get aggregated data for a module"""
    if module not in node_data:
        return jsonify({'error': 'Invalid module'}), 400
    
    with data_lock:
        aggregated = {
            'module': module,
            'nodes': list(node_data[module].keys()),
            'count': len(node_data[module]),
            'data': [],
            'total_objects': 0
        }
        
        for node_id, node_info in node_data[module].items():
            aggregated['data'].extend(node_info.get('data', []))
            aggregated['total_objects'] += len(node_info.get('data', []))
    
    return jsonify(aggregated), 200

@api_bp.route('/status', methods=['GET'])
def status():
    """Get system status"""
    with data_lock:
        return jsonify({
            'trees_nodes': len(node_data['trees']),
            'life_nodes': len(node_data['life']),
            'food_nodes': len(node_data['food']),
            'climate_nodes': len(node_data['climate']),
            'total_nodes': sum(len(node_data[m]) for m in node_data)
        }), 200


@api_bp.route('/sierpinski/register', methods=['POST'])
def register_sierpinski_node():
    """Register a Sierpinski worker node"""
    data = request.get_json() or {}
    node_id = data.get('node_id')
    if not node_id:
        return jsonify({'error': 'node_id required'}), 400

    with data_lock:
        cleanup_sierpinski_stale()
        slot_index = find_slot_index(node_id)
        if slot_index is None:
            slots = sierpinski_state['slots']
            try:
                slot_index = slots.index(None)
            except ValueError:
                return jsonify({'error': 'max 3 nodes allowed'}), 400
            slots[slot_index] = {'node_id': node_id, 'last_seen': datetime.now().isoformat()}
        else:
            sierpinski_state['slots'][slot_index]['last_seen'] = datetime.now().isoformat()

    return jsonify({'status': 'ok', 'node_id': node_id, 'slot': slot_index}), 200


@api_bp.route('/sierpinski/task', methods=['GET'])
def get_sierpinski_task():
    """Assign the next Sierpinski task in strict round-robin order"""
    node_id = request.args.get('node_id')
    if not node_id:
        return jsonify({'error': 'node_id required'}), 400

    with data_lock:
        cleanup_sierpinski_stale()
        slot_index = find_slot_index(node_id)
        if slot_index is None:
            return jsonify({'error': 'node not registered'}), 404

        slots = sierpinski_state['slots']
        if all(slot is None for slot in slots):
            return jsonify({'status': 'waiting'}), 202

        current = sierpinski_state['current_task']
        if current:
            if current['node_id'] == node_id:
                return jsonify(current), 200
            return ('', 204)

        for _ in range(3):
            if slots[sierpinski_state['turn_index']] is not None:
                break
            sierpinski_state['turn_index'] = (sierpinski_state['turn_index'] + 1) % 3

        turn_slot = slots[sierpinski_state['turn_index']]
        if not turn_slot or turn_slot.get('node_id') != node_id:
            return ('', 204)

        task_id = sierpinski_state['task_counter']
        task = {
            'task_id': task_id,
            'node_id': node_id,
            'slot_index': slot_index,
            'region_id': slot_index,
            'depth': sierpinski_state['depth'],
            'canvas': sierpinski_state['canvas'],
            'created_at': datetime.now().isoformat()
        }
        sierpinski_state['current_task'] = task

    return jsonify(task), 200


@api_bp.route('/sierpinski/result', methods=['POST'])
def post_sierpinski_result():
    """Receive Sierpinski result from a worker and advance turn"""
    data = request.get_json() or {}
    node_id = data.get('node_id')
    task_id = data.get('task_id')
    region_id = data.get('region_id')
    triangles = data.get('triangles', [])
    stats = data.get('stats', {})

    if node_id is None or task_id is None or region_id is None:
        return jsonify({'error': 'node_id, task_id, region_id required'}), 400

    with data_lock:
        cleanup_sierpinski_stale()
        current = sierpinski_state['current_task']
        if not current or current.get('node_id') != node_id or current.get('task_id') != task_id:
            return jsonify({'error': 'task mismatch'}), 409

        slot_index = find_slot_index(node_id)
        if slot_index is None:
            return jsonify({'error': 'node not registered'}), 404

        sierpinski_state['slots'][slot_index]['last_seen'] = datetime.now().isoformat()

        sierpinski_state['latest'][region_id] = {
            'timestamp': datetime.now().isoformat(),
            'node_id': node_id,
            'task_id': task_id,
            'triangles': triangles,
            'stats': stats
        }

        sierpinski_state['current_task'] = None
        sierpinski_state['task_counter'] += 1
        sierpinski_state['turn_index'] = (sierpinski_state['turn_index'] + 1) % 3

    return jsonify({'status': 'ok'}), 200


@api_bp.route('/sierpinski/data', methods=['GET'])
def get_sierpinski_data():
    """Get aggregated Sierpinski triangles for rendering"""
    with data_lock:
        cleanup_sierpinski_stale()
        triangles = []
        latest = sierpinski_state['latest']
        last_update = None
        last_task_id = None

        for region_info in latest.values():
            if not region_info:
                continue
            triangles.extend(region_info.get('triangles', []))
            last_update = region_info.get('timestamp')
            last_task_id = region_info.get('task_id')

        slots = sierpinski_state['slots']
        active_nodes = [slot for slot in slots if slot is not None]
        turn_slot = slots[sierpinski_state['turn_index']]
        turn_node = turn_slot.get('node_id') if turn_slot else None

    return jsonify({
        'triangles': triangles,
        'stats': {
            'nodes': len(active_nodes),
            'turn_node': turn_node,
            'total_triangles': len(triangles),
            'last_task_id': last_task_id,
            'last_update': last_update
        }
    }), 200
