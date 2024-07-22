from db import db
from passlib.hash import pbkdf2_sha256


class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, )
    password = db.Column(db.String(200))
    name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    email = db.Column(db.String(80))
    clothes = db.relationship('ClotheModel', backref='owner', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'clothes': [clothe.to_dict() for clothe in self.clothes.all()],

        }

    @classmethod
    def from_dict(cls, data):
        user = cls(
            id=data.get('id'),
            username=data.get('username'),
            name=data.get('name'),
            surname=data.get('surname'),
            email=data.get('email'),
            password=pbkdf2_sha256.hash(data.get('password'))
        )

        return user
