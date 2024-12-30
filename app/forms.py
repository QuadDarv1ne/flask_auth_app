from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    """
    Форма регистрации нового пользователя.

    Поля:
        username (StringField): Имя пользователя, обязательное поле, длина от 2 до 20 символов.
        email (StringField): Email пользователя, обязательное поле, должен быть действующим email.
        password (PasswordField): Пароль пользователя, обязательное поле, длина не менее 6 символов.
        confirm_password (PasswordField): Подтверждение пароля, обязательное поле, должно совпадать с полем password.
        profile_picture (FileField): Фото профиля пользователя, необязательное поле.
        submit (SubmitField): Кнопка отправки формы.
    """
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    profile_picture = FileField('Фото профиля')  # Добавлено поле для загрузки фото
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    """
    Форма входа пользователя.

    Поля:
        email (StringField): Email пользователя, обязательное поле, должен быть действующим email.
        password (PasswordField): Пароль пользователя, обязательное поле.
        remember (BooleanField): Флажок "Запомнить меня", необязательное поле.
        submit (SubmitField): Кнопка отправки формы.
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')

class RequestResetForm(FlaskForm):
    """
    Форма запроса сброса пароля.

    Поля:
        email (StringField): Email пользователя, обязательное поле, должен быть действующим email.
        submit (SubmitField): Кнопка отправки формы.
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Запросить сброс пароля')

class ResetPasswordForm(FlaskForm):
    """
    Форма сброса пароля.

    Поля:
        password (PasswordField): Новый пароль пользователя, обязательное поле, длина не менее 6 символов.
        confirm_password (PasswordField): Подтверждение нового пароля, обязательное поле, должно совпадать с полем password.
        submit (SubmitField): Кнопка отправки формы.
    """
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Сбросить пароль')

class UpdateProfileForm(FlaskForm):
    """
    Форма обновления профиля пользователя.

    Поля:
        username (StringField): Новое имя пользователя, обязательное поле, длина от 2 до 20 символов.
        email (StringField): Новый email пользователя, обязательное поле, должен быть действующим email.
        profile_picture (FileField): Новое фото профиля пользователя, необязательное поле.
        submit (SubmitField): Кнопка отправки формы.
    """
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_picture = FileField('Новое фото профиля')  # Добавлено поле для загрузки нового фото
    submit = SubmitField('Сохранить изменения')
