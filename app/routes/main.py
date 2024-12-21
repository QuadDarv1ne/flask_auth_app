from flask import render_template, Blueprint
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

# Главная страница
@main_bp.route("/")
@main_bp.route("/home")
def home():
    try:
        return render_template('home.html', title='Главная')
    except Exception as e:
        return render_template('errors/500.html'), 500

# Страница профиля пользователя
@main_bp.route("/profile")
@login_required  # Ограничивает доступ к маршруту только для аутентифицированных пользователей
def profile():
    try:
        return render_template('profile.html', title='Профиль', user=current_user)
    except Exception as e:
        return render_template('errors/500.html'), 500