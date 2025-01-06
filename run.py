import os
import shutil
import logging
import ssl
from dotenv import load_dotenv
from app import create_app, db
from flask_migrate import Migrate, upgrade

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация приложения
config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config_name)
migrate = Migrate(app, db)

# Получаем переменные окружения и корректируем пути
ssl_cert_path = os.path.join(os.path.dirname(__file__), os.getenv('SSL_CERT_PATH', 'certificate/certificate.crt'))
ssl_key_path = os.path.join(os.path.dirname(__file__), os.getenv('SSL_KEY_PATH', 'certificate/private.key'))
ssl_password = os.getenv('SSL_KEY_PASSWORD')

logger.debug(f"Используемые пути для сертификата и ключа: {ssl_cert_path}, {ssl_key_path}")
logger.debug(f"Пароль для ключа: {ssl_password if ssl_password else 'не задан'}")

def is_env_flag_set(env_var, default=False):
    """
    Проверка флага окружения
    """
    value = os.getenv(env_var, str(default)).strip().lower()
    logger.debug(f"Проверка флага окружения {env_var}: {value}")
    return value in {'true', '1', 't', 'yes', 'y'}

def clean_temp_files():
    """
    Удаляет временные файлы, папки __pycache__ и файлы кэша Python.
    """
    try:
        temp_dir = 'tmp'
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Папка временных файлов '{temp_dir}' удалена.")
        
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.pyc', '.pyo')):
                    try:
                        os.remove(os.path.join(root, file))
                        logger.info(f"Удален файл: {file}")
                    except OSError as e:
                        logger.warning(f"Не удалось удалить файл {file}: {e}")

            if '__pycache__' in dirs:
                try:
                    shutil.rmtree(os.path.join(root, '__pycache__'))
                    logger.info(f"Удалена папка: {os.path.join(root, '__pycache__')}")
                except OSError as e:
                    logger.warning(f"Не удалось удалить папку __pycache__: {e}")
    except Exception as e:
        logger.error(f"Ошибка при удалении временных файлов: {e}")

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

def create_ssl_context():
    """
    Создаёт SSL-контекст для приложения, если сертификаты доступны.
    """
    if not os.path.exists(ssl_cert_path) or not os.access(ssl_cert_path, os.R_OK):
        logger.warning(f"SSL-сертификат недоступен: {ssl_cert_path}")
        return None
    if not os.path.exists(ssl_key_path) or not os.access(ssl_key_path, os.R_OK):
        logger.warning(f"Приватный ключ недоступен: {ssl_key_path}")
        return None

    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=ssl_cert_path, keyfile=ssl_key_path, password=ssl_password)
        logger.info(f"SSL-контекст успешно создан: {ssl_cert_path}, {ssl_key_path}")
        return context
    except ssl.SSLError as e:
        logger.error(f"Ошибка при создании SSL-контекста: {e}")
        try:
            with open(ssl_cert_path, 'r') as cert_file:
                logger.debug(f"Содержимое сертификата (первые 100 символов): {cert_file.read()[:100]}...")
            with open(ssl_key_path, 'r') as key_file:
                logger.debug(f"Содержимое ключа (первые 100 символов): {key_file.read()[:100]}...")
        except Exception as file_read_error:
            logger.warning(f"Не удалось прочитать файлы сертификата/ключа: {file_read_error}")
        return None

def get_ssl_config():
    """
    Возвращает конфигурацию для SSL-сертификатов, если они доступны.
    """
    ssl_context = create_ssl_context()
    if ssl_context:
        logger.info("Приложение будет работать с SSL.")
    else:
        logger.warning("SSL не будет использоваться. Соединение не защищено.")
    return ssl_context

if __name__ == '__main__':
    logger.debug("Запуск приложения...")

    clean_temp_files()

    # Миграции, если флаг установлен
    if is_env_flag_set('RUN_MIGRATIONS', False):
        run_migrations()

    # Включение режима отладки, если указано в переменных окружения
    debug_mode = is_env_flag_set('FLASK_DEBUG', False)
    port = int(os.getenv('PORT', 5000))
    logger.debug(f"Используем порт: {port}")
    
    ssl_context = get_ssl_config()
    
    logger.info(f"Запуск приложения в {'отладочном' if debug_mode else 'продакшн'} режиме на порту {port}...")
    try:
        app.run(debug=debug_mode, host='0.0.0.0', port=port, ssl_context=ssl_context)
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
