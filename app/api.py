from flask import Blueprint, request, jsonify
from app.stats_manager import StatsManager
from utils.auth import require_auth

api_bp = Blueprint('api', __name__)

@api_bp.route('/submit', methods=['POST'])
@require_auth
def submit_data():
    if not request.is_json:
        return jsonify({'error': 'Bad Request: Expected JSON'}), 400

    data = request.json
    if "version" not in data:
        data["version"] = "-1"
    if "players" not in data:
        data["players"] = 0
    
    handler_name = data.get('handler')
    
    if not StatsManager.is_valid_handler(handler_name):
        return jsonify({'error': 'Invalid handler'}), 400

    success = StatsManager.add_stats(handler_name, data)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to add stats'}), 400

@api_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    stats = StatsManager.get_all_stats()
    return jsonify(stats)