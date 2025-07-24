from flask import Blueprint, jsonify, request
from backend.services.sample_service import (
    create_sample, get_all_samples, get_sample_by_id, update_sample, delete_sample
)

sample_bp = Blueprint('sample', __name__, url_prefix='/samples')

@sample_bp.route('/', methods=['GET'])
def list_samples():
    samples = get_all_samples()
    return jsonify([s.to_dict() for s in samples])

@sample_bp.route('/<int:sample_id>', methods=['GET'])
def get_sample(sample_id):
    sample = get_sample_by_id(sample_id)
    if sample:
        return jsonify(sample.to_dict())
    return jsonify({'error': 'Not found'}), 404

@sample_bp.route('/', methods=['POST'])
def create_sample_api():
    data = request.get_json()
    sample = create_sample(data['name'], data.get('description'))
    return jsonify(sample.to_dict()), 201

@sample_bp.route('/<int:sample_id>', methods=['PUT'])
def update_sample_api(sample_id):
    data = request.get_json()
    sample = update_sample(sample_id, data['name'], data.get('description'))
    if sample:
        return jsonify(sample.to_dict())
    return jsonify({'error': 'Not found'}), 404

@sample_bp.route('/<int:sample_id>', methods=['DELETE'])
def delete_sample_api(sample_id):
    sample = delete_sample(sample_id)
    if sample:
        return jsonify({'result': 'success'})
    return jsonify({'error': 'Not found'}), 404 