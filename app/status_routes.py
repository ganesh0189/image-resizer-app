from flask import Blueprint, jsonify, request
from app.system_monitor import system_monitor
from app.queue_manager import queue_manager
import uuid

status_bp = Blueprint('status', __name__)

@status_bp.route('/api/status', methods=['GET'])
def get_status():
    """Get the current system status"""
    status = system_monitor.get_system_status()
    return jsonify(status)

@status_bp.route('/api/queue/position', methods=['GET'])
def get_queue_position():
    """Get the position of a request in the queue"""
    request_id = request.args.get('request_id')
    if not request_id:
        return jsonify({"error": "Missing request_id parameter"}), 400
    
    position = queue_manager.get_queue_position(request_id)
    return jsonify({"position": position})

@status_bp.route('/api/queue/join', methods=['POST'])
def join_queue():
    """Join the processing queue"""
    ip_address = request.remote_addr
    request_id = str(uuid.uuid4())
    
    position, error = queue_manager.add_to_queue(request_id, ip_address)
    
    if error:
        return jsonify({"error": error}), 429  # Too Many Requests
    
    return jsonify({
        "request_id": request_id,
        "position": position,
        "estimated_wait": position * 5  # Rough estimate: 5 seconds per request
    }) 