from flask.views import MethodView
from flask_smorest import Blueprint, abort
from constants import clotche_specifications
from db import db
from models import UserModel
from models import ClotheModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from constants import clotche_specifications as specs
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


@blp.route("/user/addItem",methods=["POST"])
def user_addItem():
    item_data = request.json
    user_id = item_data.get("user_id")
    required_fields = ["color", "type","user_id"]
    for field in required_fields:
        if field not in item_data:
            return {"message": f"{field} is required"}, 400



    if item_data.get("size") not in specs.valid_sizes:
        return {"message": "Invalid size value"}, 400
    if item_data.get("type") not in specs.valid_types:
        return {"message": "Invalid type value"}, 400
    if item_data.get("sex", "Unisex") not in specs.valid_sexes:
        return {"message": "Invalid sex value"}, 400

    new_item = ClotheModel.from_dict(item_data)
    db.session.add(new_item)
    db.session.commit()
    return new_item.to_dict()


@blp.route("/user/deleteItem/<int:item_id>", methods=["DELETE"])
def user_deleteItem(item_id):
    # Find the item by its ID
    item = ClotheModel.query.get(item_id)

    if item is None:
        # Return a 404 error if the item was not found
        return {"message": "Item not found"}, 404

    # Delete the item from the database
    db.session.delete(item)
    db.session.commit()

    return {"message": "Item deleted successfully"}

