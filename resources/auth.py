from flask_smorest import Blueprint
from db import db
import datetime
from models import UserModel, TokenBlacklist
from flask import request, jsonify
from passlib.hash import pbkdf2_sha256


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return "Sign Up Page"
    else:
        user_data = request.get_json()
        username = user_data.get('username')

        # Check if the username already exists
        
        user = UserModel.from_dict(user_data)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201  # Return the created user data

@auth_bp.route("/login", methods=["POST"])
def user_login():
    data = request.get_json()
    user = UserModel.query.filter_by(email=data["email"]).first()
    if user and pbkdf2_sha256.verify(data["password"], user.password):
       return {"message": "login succeed"}, 401
    return {"message": "Invalid credentials"}, 401

@auth_bp.route("/deleteUser/<int:user_id>", methods=["DELETE"])
def delete_user(user_id): 
    user = UserModel.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User successfully deleted"}), 200


@auth_bp.route("/logout", methods=['DELETE'])
def logout():
    return jsonify(msg="Successfully logged out"), 200
