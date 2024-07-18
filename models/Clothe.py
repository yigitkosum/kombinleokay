from db import db


class ClotheModel(db.Model):
    __tablename__ = 'clothes'
    id = db.Column(db.Integer, primary_key=True)  # Bize özel
    color = db.Column(db.String(100))
    size = db.Column(db.String(50))  # Oversize, Slim, Regular
    brand = db.Column(db.String(50), default="Default")
    type = db.Column(db.String(50))  # Tişört, pantolon, vs vs
    sex = db.Column(db.String(50), default="Unisex")  # Male, Female , Unisex
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel', back_populates='clothes', lazy=True, overlaps="owner")

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'id': self.id,
            'color': self.color,
            'size': self.size,
            'brand': self.brand,
            'type': self.type,
            'sex': self.sex,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get('user_id'),
            id=data.get('id'),
            color=data.get('color'),
            size=data.get('size'),
            brand=data.get('brand'),
            type=data.get('type'),
            sex=data.get('sex')
        )
