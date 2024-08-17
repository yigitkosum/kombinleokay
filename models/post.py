from db import db


class PostModel(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_url = db.Column(db.String(255))
    author = db.relationship('UserModel', back_populates='posts', lazy=True, overlaps="user")
    comments = db.relationship('CommentModel', backref='post', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'image_url': self.image_url,  # Include the image URL in the dictionary
            'comments': [comment.to_dict() for comment in self.comments.all()],
        }
