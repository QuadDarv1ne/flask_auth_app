from flask import render_template, Blueprint, current_app

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def error_404(error):
    current_app.logger.error(f'Page not found: {error}')  # Логирование ошибки
    return render_template('errors/404.html'), 404

@errors_bp.app_errorhandler(500)
def error_500(error):
    current_app.logger.error(f'Server error: {error}', exc_info=True)  # Логирование ошибки с информацией об исключении
    return render_template('errors/500.html'), 500

@errors_bp.app_errorhandler(403)
def error_403(error):
    current_app.logger.error(f'Forbidden: {error}')  # Логирование ошибки
    return render_template('errors/403.html'), 403