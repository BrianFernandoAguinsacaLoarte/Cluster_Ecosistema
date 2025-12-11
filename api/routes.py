"""
API routes for distributed node communication
Endpoints to receive and aggregate data from worker nodes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from .storage import node_data, data_lock

api_bp = Blueprint('api', __name__, url_prefix='/api')

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
