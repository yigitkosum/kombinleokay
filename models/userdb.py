from db import db



class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
<<<<<<< Updated upstream
    username = db.Column(db.String(80), unique=True, )
    password = db.Column(db.String(80) )
    name = db.Column(db.String(80) )
    surname = db.Column(db.String(80))
    email = db.Column(db.String(80) )
    clothes = db.relationship('ClotheModel', backref='owner', lazy='dynamic')
=======
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), )
    name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    email = db.Column(db.String(80))
    clothes = db.relationship('ClotheModel', backref='owner', lazy='dynamic', overlaps="user")

>>>>>>> Stashed changes



    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'clothes': [clothe.to_dict() for clothe in self.clothes.all()]

        }

    @classmethod
    def from_dict(cls, data):

        user = cls(
            id=data.get('id'),
            username=data.get('username'),
            name=data.get('name'),
            surname=data.get('surname'),
            email=data.get('email')
            # Add other fields as necessary
        )



        return user