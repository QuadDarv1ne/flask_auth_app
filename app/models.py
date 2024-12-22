from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from . import db, login_manager

@login_manager.user_loader
def load_user(user_id: int) -> 'User':
    """
    Загружает пользователя по ID.
    """
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    Модель пользователя.
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    image_file = Column(String(20), nullable=False, default='default.jpg')
    password = Column(String(60), nullable=False)
    
    favorites = relationship('FavoriteCourse', back_populates='user', cascade='all, delete-orphan')

    def get_reset_token(self, expires_sec: int = 1800) -> str:
        """
        Генерирует токен для сброса пароля.
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token: str) -> 'User':
        """
        Проверяет токен для сброса пароля.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except (TypeError, ValueError):
            return None
        return User.query.get(user_id)

    def add_to_favorites(self, course_id: int) -> None:
        """
        Добавляет курс в избранное пользователя.
        """
        if not any(favorite.course_id == course_id for favorite in self.favorites):
            try:
                new_favorite = FavoriteCourse(user_id=self.id, course_id=course_id)
                db.session.add(new_favorite)
                db.session.commit()
            except db.exc.SQLAlchemyError as e:
                db.session.rollback()
                raise e

    def remove_from_favorites(self, course_id: int) -> None:
        """
        Удаляет курс из избранного пользователя.
        """
        favorite = FavoriteCourse.query.filter_by(user_id=self.id, course_id=course_id).first()
        if favorite:
            try:
                db.session.delete(favorite)
                db.session.commit()
            except db.exc.SQLAlchemyError as e:
                db.session.rollback()
                raise e

    def get_favorite_courses(self) -> list:
        """
        Возвращает список избранных курсов пользователя.
        """
        return [favorite.course for favorite in self.favorites]

    def get_unique_favorite_courses(self) -> list:
        """
        Возвращает список уникальных избранных курсов пользователя.
        """
        return list(set(favorite.course for favorite in self.favorites))

    def __repr__(self) -> str:
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class FavoriteCourse(db.Model):
    """
    Модель избранного курса.
    """
    __tablename__ = 'favorite_course'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='favorites')
    course = relationship('Course', backref='favorite_courses')

    def __repr__(self) -> str:
        return f"FavoriteCourse(user_id={self.user_id}, course_id={self.course_id}, created_at={self.created_at})"

class Course(db.Model):
    """
    Модель курса.
    """
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    description = Column(String(255), nullable=False)
    details = Column(db.Text, nullable=False)
    image = Column(String(150), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    @classmethod
    def get_course_by_id(cls, course_id: int) -> 'Course':
        """
        Возвращает курс по его идентификатору.
        """
        return cls.query.get(course_id)

    def __repr__(self) -> str:
        return f'<Course(id={self.id}, title={self.title})>'

class Payment(db.Model):
    """
    Модель оплаты.
    """
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    payment_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=db.func.now())

    def __repr__(self) -> str:
        return f'<Payment(id={self.id}, course_id={self.course_id})>'
