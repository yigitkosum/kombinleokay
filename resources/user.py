from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from models import UserModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask import request, jsonify

blp = Blueprint("Users", __name__, description="Operations on users")


@blp.route("/user/<int:user_id>")
class User(MethodView):
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return jsonify(user)

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}


@blp.route("/user")
class UserList(MethodView):
    def get(self):
        users = UserModel.query.all()
        users_dict = [user.to_dict() for user in users]
        return users_dict


    def post(self):
        user_data = request.json  # Get the JSON data from the request body
        username = user_data.get("username")
        password = user_data.get("password")
        if not username or not password:
            abort(400, message="Username and password are required")

        new_user = UserModel(username=username, password=password)
        
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User created successfully"}
        