from flask_smorest import Blueprint
from db import db
from models import UserModel

from models.follow import FollowModel
from flask import request, jsonify
from models.post import PostModel
from models.Clothe import ClotheModel
import boto3
import uuid
from models import UserModel, PostModel, ClotheModel
from flask_smorest import Blueprint

blp = Blueprint("SocialMedia", __name__, description="Operations on social media")

#s3 file upload



S3_BUCKET = 'kombinle'
s3 = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,
aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

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


@blp.route("/sharePost/<int:user_id>", methods=["POST"])
def share_post(user_id):
    content = request.form.get('content')

    # Retrieve the user
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Handling image upload to S3
    image_file = request.files.get('image')
    image_url = None
    if image_file:
        # Generate a unique filename
        filename = f"{uuid.uuid4().hex}-{image_file.filename}"
        
        try:
            # Upload the file to S3
            s3.upload_fileobj(image_file, S3_BUCKET, filename)

            # Construct the image URL
            image_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"
        except Exception as e:
            return jsonify({'message': 'Failed to upload image', 'error': str(e)}), 500

    # Create a new post with the image URL
    post = PostModel(content=content, user_id=user_id,image_url=image_url,author = user )

    # Save the post to the database
    db.session.add(post)
    db.session.commit()

    return jsonify(post.to_dict()), 201