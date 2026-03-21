# backend/routes/user_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from backend.auth.auth_service import AuthService

user_bp = Blueprint('users', __name__)


# GET /api/users
@user_bp.route('/api/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        users = AuthService.get_all_users()
        return jsonify(users), 200
    except Exception as e:
        print(f"❌ Get users error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# POST /api/users/create
@user_bp.route('/api/users/create', methods=['POST'])
@jwt_required()
def create_user():
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        data     = request.get_json()
        required = ['username', 'email', 'password', 'full_name', 'role']
        if not all(key in data for key in required):
            return jsonify({'error': 'Missing required fields'}), 400

        result = AuthService.create_user(
            username  = data['username'],
            email     = data['email'],
            password  = data['password'],
            full_name = data['full_name'],
            role      = data['role']
        )
        if 'error' in result:
            return jsonify(result), 400

        print(f"✅ User created: {result['email']}")
        return jsonify(result), 201

    except Exception as e:
        print(f"❌ Create user error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# DELETE /api/users/<user_id>
@user_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    try:
        from backend.database.db_config import SessionLocal
        from backend.database.models import User
        db   = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            db.close()
            return jsonify({'message': 'User not found'}), 404
        db.delete(user)
        db.commit()
        db.close()
        print(f"🗑️ User deleted: ID {user_id}")
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# PUT /api/users/<user_id>
@user_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user_status(user_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'message': 'Admin access required'}), 403
    data = request.get_json()
    try:
        from backend.database.db_config import SessionLocal
        from backend.database.models import User
        db   = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            db.close()
            return jsonify({'message': 'User not found'}), 404
        user.is_active = data.get('is_active', True)
        db.commit()
        db.close()
        print(f"✅ User {user_id} status updated to {user.is_active}")
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
