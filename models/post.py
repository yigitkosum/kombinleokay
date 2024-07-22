from db import db


class PostModel(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('UserModel', back_populates='posts', lazy=True, overlaps="user")
    clothes = db.relationship('ClotheModel', secondary="post_clothes", back_populates='posts', lazy='dynamic')
    comments = db.relationship('CommentModel', backref='post', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'clothes': [clothe.to_dict() for clothe in self.clothes],
            'comments': [comment.to_dict() for comment in self.comments.all()]
        }
