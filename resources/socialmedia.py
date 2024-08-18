from flask_smorest import Blueprint
from db import db
from models.follow import FollowModel
from flask import request, jsonify
import boto3
import uuid
from models import UserModel, PostModel, CommentModel
from datetime import datetime, timedelta

blp = Blueprint("SocialMedia", __name__, description="Operations on social media")


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


@blp.route("/exploreUser", methods=["POST"])
def explore():
    data = request.get_json()

    query = data.get('q', '') if data else ''

    if not query:
        return jsonify({'message': 'Query parameter is required'}), 400

    # Search for users whose names, surnames, or usernames contain the query string
    results = UserModel.query.filter(
        (UserModel.name.ilike(f"%{query}%")) |
        (UserModel.surname.ilike(f"%{query}%")) |
        (UserModel.username.ilike(f"%{query}%"))
    ).all()

    if not results:
        return jsonify({'message': 'No users found'}), 404

    return jsonify([user.to_dict() for user in results]), 200



@blp.route("/exploreFollowingPosts/<int:user_id>", methods=["GET"])
def exploreFollowingPosts(user_id):
    # Retrieve the user
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get the list of user IDs that the current user is following
    followed_user_ids = [followed.followed_id for followed in user.following]
    
    # Calculate the date 4 days ago
    four_days_ago = datetime.now() - timedelta(days=4)
    
    # Query for posts from followed users in the last 4 days
    posts = PostModel.query.filter(
        PostModel.user_id.in_(followed_user_ids),
        PostModel.timestamp >= four_days_ago
    ).all()
    
    # Return the list of posts
    return jsonify([post.to_dict() for post in posts]), 200



@blp.route('/savePost', methods=['POST'])
def save_post():
    data = request.get_json()

    user_id = data.get('user_id')
    post_id = data.get('post_id')

    user = UserModel.query.get(user_id)
    post = PostModel.query.get(post_id)

    if not user or not post:
        return jsonify({'message': 'User or Post not found'}), 404

    if post in user.saved_posts:
        return jsonify({'message': 'Post already saved by this user'}), 400

    user.saved_posts.append(post)
    db.session.commit()

    return jsonify({'message': 'Post saved successfully'}), 200


@blp.route('/getAllSavePosts/<int:user_id>', methods=['GET'])
def get_all_saved_posts(user_id):
    user = UserModel.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    saved_posts = [post.to_dict() for post in user.saved_posts]

    return jsonify(saved_posts), 200

@blp.route('/unsavePost', methods=['POST'])
def unsave_post():
    data = request.get_json()

    user_id = data.get('user_id')
    post_id = data.get('post_id')

    user = UserModel.query.get(user_id)
    post = PostModel.query.get(post_id)

    if not user or not post:
        return jsonify({'message': 'User or Post not found'}), 404

    if post not in user.saved_posts:
        return jsonify({'message': 'Post not saved by this user'}), 400

    user.saved_posts.remove(post)
    db.session.commit()

    return jsonify({'message': 'Post unsaved successfully'}), 200



@blp.route('/makeComment/<int:user_id>/<int:post_id>', methods=["POST"])
def make_comment(user_id, post_id):
    data = request.get_json()

    content = data.get('content')

    if not content:
        return jsonify({'message': 'Content is required'}), 400

    # Retrieve the user and post
    user = UserModel.query.get(user_id)
    post = PostModel.query.get(post_id)

    if not user or not post:
        return jsonify({'message': 'User or Post not found'}), 404

    # Create a new comment
    comment = CommentModel(content=content, user_id=user_id, post_id=post_id)

    # Save the comment to the database
    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_dict()), 201
    