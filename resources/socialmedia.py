from flask_smorest import Blueprint
from db import db
import datetime
from models import UserModel
from models import TokenBlacklist
from models.follow import FollowModel
from flask import request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jti, get_jwt
)

blp = Blueprint("SocialMedia", __name__, description="Operations on social media")


@blp.route("/get_timeline", methods=["GET"])
def socialmedia():
    pass #Buraya akış gelecek, ana sayfa

@blp.route("/addFriend", methods=["POST"])
@jwt_required()
def friendRequest():
    data = request.get_json()
    follower_id = get_jwt_identity()
    followed_id = data.get('followed_id')

    if not follower_id or not followed_id:
        return jsonify({'message': 'Both follower_id and followed_id are required'}), 400

    follower = get_jwt_identity()
    followed = UserModel.query.get(followed_id)

    if not follower or not followed:
        return jsonify({'message': 'User not found'}), 404

    # Check if the follow relationship already exists
    follow = FollowModel.query.filter_by(follower_id=follower_id, followed_id=followed_id).first()
    if follow:
        return jsonify({'message': 'Already following'}), 400

    # Create a new follow relationship
    follow = FollowModel(follower_id=follower_id, followed_id=followed_id)
    db.session.add(follow)
    db.session.commit()

    return jsonify({'message': 'Successfully followed'}), 200

@blp.route("/unfollowFriend", methods = ["DELETE"])
@jwt_required()
def remove_from_friens():
    data = request.get_json()
    follower_id = get_jwt_identity()
    followed_id = data.get('followed_id')
    
    if not follower_id or not followed_id:
        return jsonify({'message': 'Both follower_id and followed_id are required'}), 400

    follower = UserModel.query.get(follower_id)
    followed = UserModel.query.get(followed_id)
    
    
    if not follower or not followed:
        return jsonify({'message': 'User not found'}), 404
    
    #checking are they following
    follow = FollowModel.query.filter_by(follower_id = follower_id, followed_id = followed_id).first()
    
    if not follow:
        return jsonify({'message': 'Follow relationship not found'}), 404
    
    #delete follow relation
    db.session.delete(follow)
    db.session.commit()
    return jsonify({'message': 'Successfully unfollowed'}), 200
    







