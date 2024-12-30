from flask import render_template, Blueprint
from flask_login import login_required, current_user
import logging

# Инициализация Blueprint
main_bp = Blueprint('main', __name__)

# Настройка логирования
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Главная страница
@main_bp.route("/")
@main_bp.route("/home")
def home():
    try:
        return render_template('home.html', title='Главная')
    except Exception as e:
        logger.error(f"Ошибка при загрузке главной страницы: {e}")
        return render_template('errors/500.html', error_message=str(e)), 500

# Страница профиля пользователя
@main_bp.route("/profile")
@login_required  # Ограничивает доступ к маршруту только для аутентифицированных пользователей
def profile():
    try:
        return render_template('profile.html', title='Профиль', user=current_user)
    except Exception as e:
        logger.error(f"Ошибка при загрузке страницы профиля: {e}")
        return render_template('errors/500.html', error_message=str(e)), 500

@main_bp.route('/vk_video')
def video():
    try:
        return render_template('vk_video.html')  # Рендерим страницу с видео
    except Exception as e:
        logger.error(f"Ошибка при загрузке страницы с видео: {e}")
        return render_template('errors/500.html', error_message=str(e)), 500
