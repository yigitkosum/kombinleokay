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
            'clothes_in_outfits': self.clothes_in_outfits.split(',')  # Convert string back to list
        }

    @classmethod
    def from_dict(cls, data):
        clothes_list = data.get('clothes_in_outfits', [])
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            image_url=data.get('image_url'),
            clothes_in_outfits=','.join(clothes_list)  # Convert list back to string
        )
