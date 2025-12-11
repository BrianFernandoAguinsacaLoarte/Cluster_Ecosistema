"""
In-memory storage for node data
Manages data received from distributed worker nodes
"""
import threading
from datetime import datetime

# In-memory storage for node data (module -> node_id -> data)
node_data = {
    'trees': {},
    'life': {},
    'food': {},
    'climate': {}
}

data_lock = threading.Lock()

def clean_stale_data():
    """Clean stale data older than 30 seconds"""
    with data_lock:
        now = datetime.now()
        for module in node_data:
            stale_nodes = [
                node_id for node_id, data in node_data[module].items()
                if (now - datetime.fromisoformat(data.get('timestamp', now.isoformat()))).total_seconds() > 30
            ]
            for node_id in stale_nodes:
                del node_data[module][node_id]
    threading.Timer(10, clean_stale_data).start()
