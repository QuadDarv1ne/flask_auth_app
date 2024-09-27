from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User
from app.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from app.utils import send_reset_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ваш аккаунт был создан! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Регистрация', form=form)


@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile.user_profile'))  # Перенаправляем на профиль, если пользователь уже аутентифицирован
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # Измените здесь, чтобы перенаправлять на страницу профиля
            return redirect(next_page) if next_page else redirect(url_for('profile.user_profile'))  # Перенаправляем на профиль
        else:
            flash('Вход не выполнен. Проверьте почту и пароль.', 'danger')
    return render_template('auth/login.html', title='Вход', form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
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
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Неверный или просроченный токен', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Ваш пароль был обновлен! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title='Сброс пароля', form=form)
