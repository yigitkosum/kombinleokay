from flask_smorest import Blueprint
from db import db
import datetime
from models import UserModel
from models import TokenBlacklist
from flask import request, jsonify
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jti, get_jwt
)

blp = Blueprint("SocialMedia", __name__, description="Operations on social media")


