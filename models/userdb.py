from db import db

class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, )
    password = db.Column(db.String(80) )
    name = db.Column(db.String(80) )
    surname = db.Column(db.String(80))
    email = db.Column(db.String(80) )
    clothes = db.relationship('ClotheModel', backref='owner', lazy='dynamic')



    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'clothes': [clothe.to_dict() for clothe in self.clothes.all()]
            # Add other fields as necessary
        }