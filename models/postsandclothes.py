from db import db

post_clothes = db.Table('post_clothes',
                        db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
                        db.Column('clothe_id', db.Integer, db.ForeignKey('clothes.id'), primary_key=True)
                        )
