from db import db

class UserModel(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    demo = db.Column(db.String(80))


    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'demo': self.demo,
            # Add other fields as necessary
        }