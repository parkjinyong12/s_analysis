# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from backend.services.user_service import create_user, get_all_users
from backend.utils.transaction import safe_transaction, read_only_transaction

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/', methods=['GET'])
@read_only_transaction
def get_users():
    users = get_all_users()
    return jsonify([
        {'id': u.id, 'username': u.username, 'email': u.email}
        for u in users
    ])

@user_bp.route('/', methods=['POST'])
@safe_transaction
def create_user_api():
    data = request.get_json()
    user = create_user(data['username'], data['email'])
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email}), 201 