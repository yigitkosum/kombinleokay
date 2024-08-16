from flask_smorest import Blueprint
from db import db
from models import UserModel

from models.follow import FollowModel
from flask import request, jsonify
from models.post import PostModel
from models.Clothe import ClotheModel

blp = Blueprint("SocialMedia", __name__, description="Operations on social media")


@blp.route("/get_timeline", methods=["GET"])
def socialmedia():
    pass  #Buraya akış gelecek, ana sayfa

@blp.route("/addFriend", methods=["POST"])
def friendRequest():
    data = request.get_json()
    follower_id = data.get('follower_id')
    followed_id = data.get('followed_id')

    if not follower_id or not followed_id:
        return jsonify({'message': 'Both follower_id and followed_id are required'}), 400

    follower = UserModel.query.get(follower_id)
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


@blp.route("/unfollowFriend", methods=["DELETE"])
def remove_from_friens():
    data = request.get_json()
    follower_id = data.get('follower_id')
    followed_id = data.get('followed_id')

    if not follower_id or not followed_id:
        return jsonify({'message': 'Both follower_id and followed_id are required'}), 400

    follower = UserModel.query.get(follower_id)
    followed = UserModel.query.get(followed_id)

    if not follower or not followed:
        return jsonify({'message': 'User not found'}), 404

    #checking are they following
    follow = FollowModel.query.filter_by(follower_id=follower_id, followed_id=followed_id).first()

    if not follow:
        return jsonify({'message': 'Follow relationship not found'}), 404

    #delete follow relation
    db.session.delete(follow)
    db.session.commit()
    return jsonify({'message': 'Successfully unfollowed'}), 200


@blp.route("/sharePost", methods={"POST"})  #bu methodda clothes ve comments kısmı nasıl olacak. comments okey makeCommentten post id yapılır
def share_post():
    data = request.get_json()
    user_id = data.get('user_id')

    content = data.get('content')
    clothes = data.get('clothes', [])  #list olduğu için? bunsuz da olur mu acaba

    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    comments = data.get('comments', [])  #yine list oldugu icin yaprm da gerek var mı kontrol edilmeli

    post = PostModel(content=content, user_id=user_id,comments=comments,author=user)

    if clothes:
        for clothe_id in clothes:
            clothe = ClotheModel.query.get(clothe_id)
            if clothe:
                post.clothes.append(clothe)
            else:
                #eğer clothe yoksa sıkıntılı durum napıp nedip olmayan clothe girmemeli. şuan girmez gibi ama ilrede sıkıntı çıkarsa diye
                continue

    db.session.add(post)
    db.session.commit()

    return jsonify(post.to_dict()), 201
