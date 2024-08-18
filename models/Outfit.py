from db import db

class Outfit(db.Model):
    __tablename__ = 'outfits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_url = db.Column(db.String(255))
    clothes_in_outfits = db.Column(db.String(255))


def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_url': self.image_url,
            'clothes_in_outfits': [clothe.to_dict() for clothe in self.clothes_in_outfits]
        }