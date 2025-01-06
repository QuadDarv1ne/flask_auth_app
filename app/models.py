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
    Загружает пользователя по его ID из базы данных.

    :param user_id: Идентификатор пользователя.
    :return: Объект User, если он существует, иначе None.
    """
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    Модель пользователя системы.
    
    Атрибуты:
        id (int): Идентификатор пользователя.
        username (str): Имя пользователя.
        email (str): Электронная почта пользователя.
        image_file (str): Имя файла изображения пользователя.
        password (str): Хешированный пароль пользователя.
        
    Методы:
        get_reset_token(): Генерирует токен для сброса пароля.
        verify_reset_token(): Проверяет токен для сброса пароля.
        add_to_favorites(): Добавляет курс в избранное.
        remove_from_favorites(): Удаляет курс из избранного.
        get_favorite_courses(): Возвращает все избранные курсы.
        get_unique_favorite_courses(): Возвращает уникальные избранные курсы.
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
        Генерирует токен для сброса пароля с использованием секретного ключа.

        :param expires_sec: Время действия токена в секундах (по умолчанию 1800 секунд).
        :return: Токен для сброса пароля.
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token: str) -> 'User':
        """
        Проверяет токен для сброса пароля и возвращает пользователя, если токен валиден.

        :param token: Токен для сброса пароля.
        :return: Пользователь, если токен действителен, иначе None.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except (TypeError, ValueError):
            return None
        return User.query.get(user_id)

    def add_to_favorites(self, course_id: int) -> None:
        """
        Добавляет курс в избранное пользователя, если он еще не добавлен.

        :param course_id: Идентификатор курса для добавления в избранное.
        """
        if not FavoriteCourse.query.filter_by(user_id=self.id, course_id=course_id).first():
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

        :param course_id: Идентификатор курса для удаления из избранного.
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
        Возвращает список всех избранных курсов пользователя.

        :return: Список объектов курсов.
        """
        return [favorite.course for favorite in self.favorites]

    def get_unique_favorite_courses(self) -> list:
        """
        Возвращает уникальные избранные курсы пользователя, убирая дубликаты.

        :return: Список уникальных объектов курсов.
        """
        return list(set(self.get_favorite_courses()))

    def __repr__(self) -> str:
        """
        Строковое представление пользователя.

        :return: Строка с информацией о пользователе.
        """
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class FavoriteCourse(db.Model):
    """
    Модель для хранения информации об избранных курсах пользователя.

    Атрибуты:
        id (int): Идентификатор записи.
        user_id (int): Идентификатор пользователя.
        course_id (int): Идентификатор курса.
        created_at (datetime): Дата и время добавления курса в избранное.
    """
    __tablename__ = 'favorite_course'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='favorites')
    course = relationship('Course', backref='favorite_courses')

    def __repr__(self) -> str:
        """
        Строковое представление записи об избранном курсе.

        :return: Строка с информацией об избранном курсе.
        """
        return f"FavoriteCourse(user_id={self.user_id}, course_id={self.course_id}, created_at={self.created_at})"

class Course(db.Model):
    """
    Модель курса.

    Атрибуты:
        id (int): Идентификатор курса.
        title (str): Название курса.
        description (str): Описание курса.
        details (str): Подробная информация о курсе.
        image (str): Имя файла изображения курса.
        price (decimal): Цена курса.

    Методы:
        get_course_by_id(): Возвращает курс по его идентификатору.
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

        :param course_id: Идентификатор курса.
        :return: Курс, если он существует, иначе None.
        """
        return cls.query.get(course_id)

    def __repr__(self) -> str:
        """
        Строковое представление курса.

        :return: Строка с информацией о курсе.
        """
        return f'<Course(id={self.id}, title={self.title})>'

class Payment(db.Model):
    """
    Модель оплаты для курсов.

    Атрибуты:
        id (int): Идентификатор записи.
        course_id (int): Идентификатор курса.
        payment_status (str): Статус оплаты.
        created_at (datetime): Дата и время создания записи о платеже.
    """
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    payment_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=db.func.now())

    def __repr__(self) -> str:
        """
        Строковое представление записи о платеже.

        :return: Строка с информацией о платеже.
        """
        return f'<Payment(id={self.id}, course_id={self.course_id})>'
