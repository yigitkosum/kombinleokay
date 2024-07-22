from db import db

class FollowModel(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=db.func.now())


def to_dict(self):
    return {
        'id': self.id,
        'follower_id': self.follower_id,
        'followed_id': self.followed_id,
    }