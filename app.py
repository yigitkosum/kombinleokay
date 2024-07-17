from flask import Flask
from flask_smorest import Api

from resources.user import blp as UserBlueprint

from db import db
import models
from flask_migrate import Migrate

app = Flask(__name__)

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Stores REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:06mrtnsrn@db/kombinledb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)



with app.app_context():
    db.create_all()


api = Api(app)

@app.route("/")
def index():
    return "Hello World!"

api.register_blueprint(UserBlueprint)

if __name__ == "__main__":
    app.run(debug=True)
   


