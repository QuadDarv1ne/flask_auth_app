import os
import logging
from app import create_app, db
from flask_migrate import Migrate

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем конфигурацию из переменных окружения
config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config_name)
migrate = Migrate(app, db)

def run_migrations():
    """Функция для выполнения миграций базы данных."""
    try:
        with app.app_context():
            if os.getenv('FLASK_ENV') == 'development':
                # Включаем миграции через Flask-Migrate
                logger.info("Выполнение миграций...")
                # Миграции с Alembic, предполагается, что команда миграции будет настроена
                from flask_migrate import upgrade
                upgrade()  # или команда flask db upgrade
            else:
                logger.info("Миграции не выполняются, так как окружение не development.")
    except Exception as e:
        logger.error(f"Ошибка при выполнении миграций: {e}")
        raise

if __name__ == '__main__':
    # Выполнение миграций при запуске
    run_migrations()
    
    # Запускаем приложение
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    logger.info(f"Запуск приложения в {'отладочном' if debug_mode else 'продакшн'} режиме...")
    app.run(debug=debug_mode)
