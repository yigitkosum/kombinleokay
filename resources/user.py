from flask_smorest import Blueprint
from db import db
from models import UserModel
from models import ClotheModel
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required
from constants import clotche_specifications as specs
from flask import request

blp = Blueprint("Users", __name__, description="Operations on users")


@blp.route("/getAllUsers")
def GetAllUsers():
    users = UserModel.query.all()
    users_dict = [user.to_dict() for user in users]
    return users_dict



@blp.route("/user/addItem", methods=["POST"])
def user_addItem():
    item_data = request.json
    required_fields = ["color", "type", "user_id"]
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


@blp.route("/updateItem/<int:item_id>", methods=["PUT"])
def user_updateItem(item_id):
    data = request.json
    clothe = ClotheModel.query.get_or_404(item_id)

    color = data.get('color', clothe.color)
    size = data.get('size', clothe.size)
    brand = data.get('brand', clothe.brand)
    type = data.get('type', clothe.type)
    sex = data.get('sex', clothe.sex)

    clothe.update(color=color, size=size, brand=brand, type=type, sex=sex)
    db.session.commit()
    return clothe.to_dict(),200


@blp.route("/getItem/<int:item_id>", methods=["GET"])
def user_getItem(item_id):
    item = ClotheModel.query.get_or_404(item_id)
    if item is None:
        return {"message": "Item not found"}, 404
    return item.to_dict(),200

