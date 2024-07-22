from flask import Flask,jsonify
from flask_smorest import Api

from models import TokenBlacklist
from resources.user import blp as UserBlueprint
from resources.auth import auth_bp as AuthBlueprint
<<<<<<< Updated upstream
from s3file.s3_helper import s3_bp as S3Blueprint

=======
>>>>>>> Stashed changes
from db import db
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jti, get_jwt
)
from flask_migrate import Migrate
from sqlalchemy import create_engine


app = Flask(__name__)

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Stores REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:12345@db/databasekom"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "bicakci"
app.config["JWT_SECRET_KEY"] = "bicakci"
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

#sql alchemy engine:
engine = create_engine(
    app.config["SQLALCHEMY_DATABASE_URI"],
    pool_size=5,
    max_overflow=0,
)

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

api = Api(app)


@app.route("/")
def index():
    return "İlk Sayfa"


api.register_blueprint(UserBlueprint)
api.register_blueprint(AuthBlueprint)
api.register_blueprint(S3Blueprint)



@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    return token is not None

if __name__ == "__main__":
    app.run(debug=True)
