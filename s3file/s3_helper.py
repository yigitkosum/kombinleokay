from flask import request, jsonify, render_template, redirect, url_for, send_file
import boto3
from flask_smorest import Blueprint
from io import BytesIO
from db import db
from models import ClotheModel
from flask_jwt_extended import jwt_required, get_jwt_identity

s3_bp = Blueprint('s3', __name__)


#S3 configuration
S3_BUCKET = 'kombinle'
s3 = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,
aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


#upload to S3
@s3_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    file = request.files['file']
    
    if not file:
            return jsonify({'error': 'No file part'}), 400
        
    if file.filename == ' ':
        return jsonify({'error':'No selected file'})
    
    
    user_id = get_jwt_identity()
    
    print(user_id)
    
    s3.upload_fileobj(file,S3_BUCKET,file.filename)
    
    object_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file.filename}"

     # Yeni ClotheModel nesnesi oluşturma
    new_clothe = ClotheModel(
        image_url=object_url,
        color="",
        size="",
        brand="",
        type="",
        sex="",
        user_id=user_id
    )
    db.session.add(new_clothe)
    db.session.commit()
    return redirect(url_for('index', image_url = object_url))


@s3_bp.route('/uploadImage')
def index():
    image_url = request.args.get('image_url')
    # Extract filename from URL if needed
    image_filename = image_url.split('/')[-1] if image_url else None
    return render_template('index.html', image_url=image_url, image_filename=image_filename)


@s3_bp.route('/image/<filename>')
def get_image(filename):
    try:
        # Get the file from S3
        file_stream = BytesIO()
        s3.download_fileobj(S3_BUCKET, filename, file_stream)
        file_stream.seek(0)  # Move to the start of the stream
        return send_file(file_stream, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({'error': str(e)}), 404