from flask import request, jsonify, send_file
import boto3
from flask_smorest import Blueprint
from io import BytesIO
from db import db
from models import Outfit
from models import ClotheModel



s3_bp = Blueprint('s3', __name__)


#S3 configuration
S3_BUCKET = 'kombinle'
s3 = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,
aws_secret_access_key=AWS_SECRET_ACCESS_KEY)



# Load the saved model
# def recognizer(image_path):
#     model_path = os.path.abspath('/app/s3file/clothes_recognizer.h5')
#     model = load_model(model_path)
    
#     # Load and preprocess the image you want to classify
#     img = load_img(image_path, target_size=(256, 256))
#     x = img_to_array(img)
#     x = np.expand_dims(x, axis=0)
#     x = x / 255.0  # Rescale the image
    
#     # Perform inference
#     predictions = model.predict(x)
#     predicted_class = np.argmax(predictions, axis=1)
    
#     # Print the predicted class
    
#     classes = ['black_dress',
#     'black_pants',
#     'black_shirt',
#     'black_shoes',
#     'black_shorts',
#     'black_suit',
#     'blue_dress',
#     'blue_pants',
#     'blue_shirt',
#     'blue_shoes',
#     'blue_shorts',
#     'brown_hoodie',
#     'brown_pants',
#     'brown_shoes',
#     'green_pants',
#     'green_shirt',
#     'green_shoes',
#     'green_shorts',
#     'green_suit',
#     'pink_hoodie',
#     'pink_pants',
#     'pink_skirt',
#     'red_dress',
#     'red_hoodie',
#     'red_pants',
#     'red_shirt',
#     'red_shoes',
#     'silver_shoes',
#     'silver_skirt',
#     'white_dress',
#     'white_pants',
#     'white_shoes',
#     'white_shorts',
#     'white_suit',
#     'yellow_dress',
#     'yellow_shorts',
#     'yellow_skirt']
#     clothes = classes[int(predicted_class)].split("_")
#     color = clothes[-2]
#     model = clothes[-1]
#     return color, model

#upload to S3
@s3_bp.route('/upload/<int:user_id>', methods=['POST'])
def upload_file(user_id):
    file = request.files['file']
    if not file:
            return jsonify({'error': 'No file part'}), 400
        
    if file.filename == ' ':
        return jsonify({'error':'No selected file'})
    
    print(user_id)
    
   # Extract data and handle None values
    color = request.form.get('color')
    size = request.form.get('size')
    brand = request.form.get('brand')
    type = request.form.get('type')
    sex = request.form.get('sex')

    # Ensure that variables that are not provided are set to None
    color = color if color is not None else None
    size = size if size is not None else None
    brand = brand if brand is not None else None
    type = type if type is not None else None
    sex = sex if sex is not None else None
  
    
    s3.upload_fileobj(file,S3_BUCKET,file.filename)
    
    object_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file.filename}"
    
    # Download the file from S3 to a temporary location
    # with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
    #     s3.download_fileobj(S3_BUCKET, file.filename, tmp_file)
    #     tmp_file_path = tmp_file.name
    
    # try:
    #     colorUp, modelUp = recognizer(tmp_file_path)
    # finally:
    #     # Clean up the temporary file
    #     os.remove(tmp_file_path)


     # Yeni ClotheModel nesnesi oluşturma
    new_clothe = ClotheModel(
        image_url=object_url,
        color=color,
        size=size,
        brand=brand,
        type=type,
        sex=sex,
        user_id=user_id
    )
    db.session.add(new_clothe)
    db.session.commit()
    return jsonify(new_clothe.to_dict()),200


@s3_bp.route('/image/<filename>',methods = ["GET"])
def get_image(filename):
    try:
        # Get the file from S3
        file_stream = BytesIO()
        s3.download_fileobj(S3_BUCKET, filename, file_stream)
        file_stream.seek(0)  # Move to the start of the stream
        return send_file(file_stream, mimetype='image/jpeg'),200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    

@s3_bp.route('/create_outfit/<int:user_id>', methods=['POST'])
def create_outfit(user_id):
    try:
        # Giysi ID'lerini ve dosyayı al
        clothe_ids = request.form.getlist('clothe_ids')  # Get a list of clothe IDs
        file = request.files.get('file')  # Use get to avoid KeyError

        if not file:
            return jsonify({'error': 'File is required'}), 400

        # Dosyayı S3'e yükle
        s3.upload_fileobj(file, S3_BUCKET, file.filename)
        object_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file.filename}"


        # Giysi ID'lerini virgülle ayrılmış bir stringe dönüştür
        #clothe_ids_str = ','.join(clothe_ids)

        new_outfit_dict = {
            "id": None,  # ID'siz oluşturulur, veritabanı tarafından atanır
            "user_id": user_id,
            "image_url": object_url,
            "clothes_in_outfits": clothe_ids
        }

        new_outfit = Outfit.from_dict(new_outfit_dict)
        db.session.add(new_outfit)
        db.session.commit()

        return jsonify({'message': 'Outfit created successfully', 'outfit': new_outfit.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    