from flask import Flask
from flask_smorest import Api
from resources.user import blp as UserBlueprint
from resources.auth import auth_bp as AuthBlueprint
from s3file.s3_helper import s3_bp as S3Blueprint
from resources.socialmedia import blp as SocialMediaBlueprint
from dotenv import load_dotenv

from db import db
from flask_migrate import Migrate
from sqlalchemy import create_engine
from models.userdb import user_lookup_callback

app = Flask(__name__)
load_dotenv()

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Stores REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:12345@db/databasekom"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#sql alchemy engine:
engine = create_engine(
    app.config["SQLALCHEMY_DATABASE_URI"],
    pool_size=5,
    max_overflow=0,
)

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

api = Api(app)


@app.route("/")
def index():
    return "İlk Sayfa"


api.register_blueprint(SocialMediaBlueprint)
api.register_blueprint(UserBlueprint)
api.register_blueprint(AuthBlueprint)
api.register_blueprint(S3Blueprint)




if __name__ == "__main__":
    app.run(debug=True)



if __name__ == "__main__":
    app.run(debug=True)
