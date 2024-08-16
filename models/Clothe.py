from db import db

class ClotheModel(db.Model):
    __tablename__ = 'clothes'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(100))
    size = db.Column(db.String(50))
    brand = db.Column(db.String(50), default="Default")
    type = db.Column(db.String(50))
    sex = db.Column(db.String(50), default="Unisex")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel', back_populates='clothes', lazy=True, overlaps="owner")
    image_url = db.Column(db.String(255))
    posts = db.relationship('PostModel', secondary="post_clothes", back_populates='clothes', lazy='dynamic')
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'id': self.id,
            'color': self.color,
            'size': self.size,
            'brand': self.brand,
            'type': self.type,
            'sex': self.sex,
            'image_url': self.image_url,
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
            sex=data.get('sex'),
            image_url=data.get('image_url')
        )

    def update(self, color=None, size=None, brand=None, type=None, sex=None):
        if color is not None:
            self.color = color
        if size is not None:
            self.size = size
        if brand is not None:
            self.brand = brand
        if type is not None:
            self.type = type
        if sex is not None:
            self.sex = sex