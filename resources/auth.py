from flask_smorest import Blueprint
from db import db
import datetime
from models import UserModel, TokenBlacklist
from flask import request, jsonify
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import (
    create_access_token,jwt_required, current_user, get_jwt
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return "Sign Up Page"
    else:
        user_data = request.get_json()
        username = user_data.get('username')

        # Check if the username already exists
        existing_user = UserModel.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Username already taken'}), 400

        user = UserModel.from_dict(user_data)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201  # Return the created user data

@auth_bp.route("/login", methods=["POST"])
def user_login():
    data = request.get_json()
    user = UserModel.query.filter_by(email=data["email"]).first()
    if user and pbkdf2_sha256.verify(data["password"], user.password):
        access_token = create_access_token(identity=user.id, fresh=True)
        return {"access_token": access_token}, 200
    return {"message": "Invalid credentials"}, 401

@auth_bp.route("/logout", methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    now = datetime.datetime.utcnow()
    blacklisted_token = TokenBlacklist(jti=jti, created_at=now)
    db.session.add(blacklisted_token)
    db.session.commit()
    return jsonify(msg="Successfully logged out"), 200


