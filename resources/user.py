from flask_smorest import Blueprint
from db import db
from models import UserModel
from models import CombinationModel
from models import ClotheModel
from models import Outfit
from constants import clotche_specifications as specs
from flask import request, jsonify



blp = Blueprint("Users", __name__, description="Operations on users")



@blp.route("/surveyRatingInsertion", methods=["POST"])
def surveyRatings():
    data = request.json

    # user_id'yi request body'den alıyoruz
    user_id = data.get("user_id")
    
    if not user_id:
        return {"message": "User ID is required"}, 400

    # Kullanıcıyı veritabanından bulalım
    user = UserModel.query.get(user_id)

    if user is None:
        return {"message": "User not found"}, 404

    # Survey verilerini data'dan alıyoruz
    survey = [data.get("0"), data.get("1"), data.get("2"), data.get("3"), data.get("4"), 
              data.get("5"), data.get("6"), data.get("7"), data.get("8"), data.get("9")]

    # Kullanıcının survey verilerini güncelleyelim
    user.survey = survey
    db.session.commit()

    return {"message": "Survey ratings inserted successfully"}

@blp.route("/getAllUsers")
def GetAllUsers():
    users = UserModel.query.all()
    users_dict = [user.to_dict() for user in users]
    return users_dict


@blp.route("/user/<int:user_id>/addItem", methods=["POST"])

def user_addItem(user_id):
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

    
    create_combinations(new_item)

    return new_item.to_dict()
    
def create_combinations(new_item):
    user = UserModel.query.get(new_item.user_id)

   
    if new_item.type in ['T-shirt', 'Shirt', 'Sweatshirt']:
        bottoms = user.clothes.filter_by(type='Pant').all() + user.clothes.filter_by(type='Short').all()
        shoes = user.clothes.filter_by(type='Shoe').all()
        jackets = user.clothes.filter_by(type='Jacket').all()

        for bottom in bottoms:
            for shoe in shoes:
                combination_data = {
                    'user_id': user.id,
                    'top_id': new_item.id,
                    'bottom_id': bottom.id,
                    'shoe_id': shoe.id,
                    'jacket_id': None,
                    'rating': None
                }
                combination = CombinationModel.from_dict(combination_data)
                db.session.add(combination)

                for jacket in jackets:
                    combination_with_jacket_data = {
                        'user_id': user.id,
                        'top_id': new_item.id,
                        'bottom_id': bottom.id,
                        'shoe_id': shoe.id,
                        'jacket_id': jacket.id,
                        'rating': None
                    }
                    combination_with_jacket = CombinationModel.from_dict(combination_with_jacket_data)
                    db.session.add(combination_with_jacket)

    elif new_item.type in ['Pant', 'Short']:
        tops = user.clothes.filter_by(type='T-shirt').all() + user.clothes.filter_by(type='Shirt').all() + user.clothes.filter_by(type='Sweatshirt').all()
        shoes = user.clothes.filter_by(type='Shoe').all()
        jackets = user.clothes.filter_by(type='Jacket').all()

        for top in tops:
            for shoe in shoes:
                combination_data = {
                    'user_id': user.id,
                    'top_id': top.id,
                    'bottom_id': new_item.id,
                    'shoe_id': shoe.id,
                    'jacket_id': None,
                    'rating': None
                }
                combination = CombinationModel.from_dict(combination_data)
                db.session.add(combination)

                for jacket in jackets:
                    combination_with_jacket_data = {
                        'user_id': user.id,
                        'top_id': top.id,
                        'bottom_id': new_item.id,
                        'shoe_id': shoe.id,
                        'jacket_id': jacket.id,
                        'rating': None
                    }
                    combination_with_jacket = CombinationModel.from_dict(combination_with_jacket_data)
                    db.session.add(combination_with_jacket)

    elif new_item.type == 'Shoe':
        tops = user.clothes.filter_by(type='T-shirt').all() + user.clothes.filter_by(type='Shirt').all() + user.clothes.filter_by(type='Sweatshirt').all()
        bottoms = user.clothes.filter_by(type='Pant').all() + user.clothes.filter_by(type='Short').all()
        jackets = user.clothes.filter_by(type='Jacket').all()

        for top in tops:
            for bottom in bottoms:
                combination_data = {
                    'user_id': user.id,
                    'top_id': top.id,
                    'bottom_id': bottom.id,
                    'shoe_id': new_item.id,
                    'jacket_id': None,
                    'rating': None
                }
                combination = CombinationModel.from_dict(combination_data)
                db.session.add(combination)

                for jacket in jackets:
                    combination_with_jacket_data = {
                        'user_id': user.id,
                        'top_id': top.id,
                        'bottom_id': bottom.id,
                        'shoe_id': new_item.id,
                        'jacket_id': jacket.id,
                        'rating': None
                    }
                    combination_with_jacket = CombinationModel.from_dict(combination_with_jacket_data)
                    db.session.add(combination_with_jacket)

    elif new_item.type == 'Jacket':
        tops = user.clothes.filter_by(type='T-shirt').all() + user.clothes.filter_by(type='Shirt').all() + user.clothes.filter_by(type='Sweatshirt').all()
        bottoms = user.clothes.filter_by(type='Pant').all() + user.clothes.filter_by(type='Short').all()
        shoes = user.clothes.filter_by(type='Shoe').all()

        for top in tops:
            for bottom in bottoms:
                for shoe in shoes:
                    combination_data = {
                        'user_id': user.id,
                        'top_id': top.id,
                        'bottom_id': bottom.id,
                        'shoe_id': shoe.id,
                        'jacket_id': new_item.id,
                        'rating': None
                    }
                    combination = CombinationModel.from_dict(combination_data)
                    db.session.add(combination)

    

    db.session.commit()


# DOKUNULMADI DURSUN BAKACAGIM 
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

@blp.route("/getAllItems/<user_id>",methods=["GET"])
def user_get_all_item(user_id):
    # Get the current user's identity from the JWT token
    
    # Fetch the user from the database
    user = UserModel.query.get(user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    # Retrieve the list of clothes associated with the user
    clothes = user.clothes  # Assuming 'clothes' is the relationship attribute in User model
    
    # Serialize the list of clothes to JSON format
    clothes_list = []
    for cloth in clothes:
        clothes_list.append({
           "id": cloth.id,
            "color": cloth.color,
            "size": cloth.size,
            "brand": cloth.brand,
            "type": cloth.type,
            "sex": cloth.sex,
            "image_url": cloth.image_url
        })
    
    # Return the serialized list as a response
    return jsonify(clothes_list), 200

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

@blp.route("/updateCombinationRating/<int:combination_id>", methods=["PUT"])
def update_combination_rating(combination_id):
    # Get the request data
    data = request.json
    
    # Validate that the 'rating' field is present in the request data
    rating = data.get('rating')
    if rating is None:
        return {"message": "'rating' is required"}, 400

    # Fetch the combination from the database
    combination = CombinationModel.query.get_or_404(combination_id)
    
    # Update the rating of the combination
    combination.rating = rating
    db.session.commit()
    
    return combination.to_dict(), 200


@blp.route("/getItem/<int:item_id>", methods=["GET"])
def user_getItem(item_id):
    item = ClotheModel.query.get_or_404(item_id)
    if item is None:
        return {"message": "Item not found"}, 404
    return item.to_dict(),200


######

@blp.route("/getCombination/<int:combination_id>", methods=["GET"])
def user_getCombination(combination_id):
    item = CombinationModel.query.get_or_404(combination_id)
    if item is None:
        return {"message": "Item not found"}, 404
    return item.to_dict(),200


@blp.route("/user/profile/<int:user_id>", methods = ["GET"])
def get_profile(user_id):
    user = UserModel.query.get(user_id)
    
    if user is None:
        return {"message": "user not found"}, 404
     
    return user.to_dict(),200



@blp.route("/updateVote/<int:item_id>", methods=["PUT"])
def user_updateVote(item_id):
    data = request.json
    vote = data.get('vote')
    if vote is None:
        return {"message": "'vote' is required"}, 400

    item = ClotheModel.query.get_or_404(item_id)
    if item is None:
        return {"message": "Item not found"}, 404
    if vote == 'true':
        item.vote = True
    else:
        item.vote = False

    db.session.commit()
    return item.to_dict(),200

@blp.route('/create_outfit', methods=['POST'])
def create_outfit():
    try:
        data = request.get_json()

        user_id = data.get('user_id')
        image_url = data.get('image_url')
        clothe_ids = data.get('clothe_ids')  # Giysi ID'leri listesi

        if not user_id or not image_url or not clothe_ids:
            return jsonify({'error': 'user_id, image_url, and clothe_ids are required'}), 400

        # Giysi ID'lerini virgülle ayrılmış bir stringe dönüştür
        clothe_ids_str = ','.join(map(str, clothe_ids))

        # Yeni bir Outfit oluştur
        new_outfit = Outfit
        new_outfit.user_id = user_id
        new_outfit.image_url = image_url
        new_outfit.clothe_ids = clothe_ids_str

        db.session.add(new_outfit)
        db.session.commit()

        return jsonify({'message': 'Outfit created successfully', 'outfit': new_outfit.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500