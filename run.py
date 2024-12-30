import os
import logging
from app import create_app, db
from flask_migrate import Migrate, upgrade

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Определяем конфигурацию из переменных окружения
config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config_name)
migrate = Migrate(app, db)

def run_migrations():
    """
    Выполняет миграции базы данных.
    """
    try:
        with app.app_context():
            logger.info("Выполнение миграций...")
            upgrade()
            logger.info("Миграции успешно выполнены.")
    except Exception as e:
        logger.error(f"Ошибка при выполнении миграций: {e}")
        raise

if __name__ == '__main__':
    # Выполняем миграции только в режиме разработки или если явно указано через переменные окружения
    if os.getenv('FLASK_ENV', 'production') == 'development' or os.getenv('RUN_MIGRATIONS', 'False').lower() in ['true', '1', 't']:
        run_migrations()
    
    # Определяем режим отладки
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    
    # Логируем режим работы приложения
    mode = 'отладочном' if debug_mode else 'продакшн'
    logger.info(f"Запуск приложения в {mode} режиме...")
    
    # Запуск приложения
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
