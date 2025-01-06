import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from app import db, bcrypt
from app.models import User
from app.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from app.utils import send_reset_email
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def save_profile_picture(form_picture):
    """Сохраняет загруженную фотографию профиля."""
    picture_filename = secure_filename(form_picture.filename)
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)
    form_picture.save(picture_path)
    return picture_filename

def redirect_if_authenticated(func):
    """Перенаправляет аутентифицированных пользователей."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('profile.user_profile'))
        return func(*args, **kwargs)
    return decorated_function

@auth_bp.route("/register", methods=['GET', 'POST'])
@redirect_if_authenticated
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Этот адрес электронной почты уже зарегистрирован. Пожалуйста, используйте другой.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        )

        if form.profile_picture.data:
            user.image_file = save_profile_picture(form.profile_picture.data)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Ваш аккаунт создан. Теперь вы можете войти.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при создании аккаунта. Попробуйте снова.', 'danger')
    
    return render_template('auth/register.html', title='Регистрация', form=form)

@auth_bp.route("/login", methods=['GET', 'POST'])
@redirect_if_authenticated
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('profile.user_profile'))
        flash('Вход не выполнен. Проверьте почту и пароль.', 'danger')
    return render_template('auth/login.html', title='Вход', form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth_bp.route("/reset_password", methods=['GET', 'POST'])
@redirect_if_authenticated
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('Письмо с инструкциями было отправлено на вашу почту.', 'info')
        else:
            flash('Пользователь с таким адресом электронной почты не найден.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Сброс пароля', form=form)

@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
@redirect_if_authenticated
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('Неверный или просроченный токен', 'warning')
        return redirect(url_for('auth.reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Ваш пароль был обновлен. Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_token.html', title='Сброс пароля', form=form)