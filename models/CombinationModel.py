from db import db

class CombinationModel(db.Model):
    __tablename__ = "combinations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    top_id = db.Column(db.Integer, db.ForeignKey("clothes.id"), nullable=False)
    bottom_id = db.Column(db.Integer, db.ForeignKey("clothes.id"), nullable=False)
    shoe_id = db.Column(db.Integer, db.ForeignKey("clothes.id"), nullable=False)
    jacket_id = db.Column(db.Integer, db.ForeignKey("clothes.id"), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(255))

    user = db.relationship("UserModel", back_populates="combinations")
    top = db.relationship("ClotheModel", foreign_keys=[top_id])
    bottom = db.relationship("ClotheModel", foreign_keys=[bottom_id])
    shoe = db.relationship("ClotheModel", foreign_keys=[shoe_id])
    jacket = db.relationship("ClotheModel", foreign_keys=[jacket_id])


    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get('user_id'),
            top_id=data.get('top_id'),
            bottom_id=data.get('bottom_id'),
            shoe_id=data.get('shoe_id'),
            jacket_id=data.get('jacket_id'),
            rating=data.get('rating', None)  
        )

    def to_dict(self):
        if(self.jacket is None):

            return {
            'id': self.id,
            'user_id': self.user_id,
            'top_id': self.top.to_dict(),
            'bottom_id': self.bottom.to_dict(),
            'shoe_id': self.shoe.to_dict(),
            'jacket_id': None ,
            'rating': self.rating
            }
        else : 
            return{
                
            'id': self.id,
            'user_id': self.user_id,
            'top_id': self.top.to_dict(),
            'bottom_id': self.bottom.to_dict(),
            'shoe_id': self.shoe.to_dict(),
            'jacket_id': self.jacket.to_dict(),
            'rating': self.rating
            }