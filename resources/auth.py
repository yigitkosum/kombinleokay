from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from models import UserModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask import request, jsonify

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


        user = UserModel(**user_data)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201  # Return the created user data






