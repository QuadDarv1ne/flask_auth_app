import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Базовая конфигурация для всех окружений.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', f'sqlite:///{os.path.join(BASE_DIR, "instance", "site.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Конфигурация для email (опционально)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', None)  # по умолчанию None
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', None)  # по умолчанию None

    # Проверка наличия обязательных переменных
    @classmethod
    def validate_config(cls):
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY отсутствует. Убедитесь, что она настроена.")
        # Почтовые настройки необязательные, поэтому проверка не требуется

class DevelopmentConfig(Config):
    """
    Конфигурация для разработки.
    """
    DEBUG = True

class TestingConfig(Config):
    """
    Конфигурация для тестирования.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_TEST_DATABASE_URI', f'sqlite:///{os.path.join(BASE_DIR, "instance", "test.db")}')

class ProductionConfig(Config):
    """
    Конфигурация для продакшена.
    """
    DEBUG = False

# Словарь с вариантами конфигураций
config_options = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}

# Валидация конфигурации при загрузке
current_config = config_options[os.environ.get('FLASK_ENV', 'default')]
current_config.validate_config()
