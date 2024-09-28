from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from . import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    
    favorites = relationship('FavoriteCourse', back_populates='user', cascade='all, delete-orphan')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return User.query.get(user_id)

    def add_to_favorites(self, course_id):
        if not any(favorite.course_id == course_id for favorite in self.favorites):
            new_favorite = FavoriteCourse(user_id=self.id, course_id=course_id)
            db.session.add(new_favorite)
            db.session.commit()

    def remove_from_favorites(self, course_id):
        favorite = FavoriteCourse.query.filter_by(user_id=self.id, course_id=course_id).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()

    def get_favorite_courses(self):
        return [favorite.course for favorite in self.favorites]

    def get_unique_favorite_courses(self):
        return list(set(favorite.course for favorite in self.favorites))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class FavoriteCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='favorites')
    course = relationship('Course', backref='favorite_courses')

    def __repr__(self):
        return f"FavoriteCourse(user_id={self.user_id}, course_id={self.course_id}, created_at={self.created_at})"

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(150), nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)

    @classmethod
    def get_course_by_id(cls, course_id):
        return cls.query.get(course_id)

    def __repr__(self):
        return f'<Course(id={self.id}, title={self.title})>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, ForeignKey('course.id'), nullable=False)
    payment_status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Payment(id={self.id}, course_id={self.course_id})>'
