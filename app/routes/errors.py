from flask import render_template, Blueprint, current_app

errors_bp = Blueprint('errors', __name__)

# Обработчик 404 ошибки (страница не найдена)
@errors_bp.app_errorhandler(404)
def error_404(error):
    current_app.logger.error(f'Page not found: {error}')  # Логирование ошибки
    return render_template('errors/404.html', error_message=str(error)), 404

# Обработчик 500 ошибки (внутренняя ошибка сервера)
@errors_bp.app_errorhandler(500)
def error_500(error):
    current_app.logger.error(f'Server error: {error}', exc_info=True)  # Логирование с трассировкой
    return render_template('errors/500.html', error_message="Что-то пошло не так. Мы уже работаем над этим!"), 500

# Обработчик 403 ошибки (доступ запрещён)
@errors_bp.app_errorhandler(403)
def error_403(error):
    current_app.logger.error(f'Forbidden: {error}')  # Логирование ошибки
    return render_template('errors/403.html', error_message="У вас нет прав для доступа к этой странице."), 403

# Обработчик 400 ошибки (неверный запрос)
@errors_bp.app_errorhandler(400)
def error_400(error):
    current_app.logger.error(f'Bad Request: {error}')  # Логирование ошибки
    return render_template('errors/400.html', error_message="Некорректный запрос. Проверьте введённые данные."), 400

# Регистрация ошибок
def register_error_handlers(app):
    app.register_blueprint(errors_bp)
