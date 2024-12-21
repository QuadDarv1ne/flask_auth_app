import os
from app import create_app, db
from flask_migrate import Migrate

# Создаём приложение с конфигурацией из переменных окружения
config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config_name)
migrate = Migrate(app, db)

try:
    with app.app_context():
        # Выполняем миграции базы данных, если они есть
        if os.getenv('FLASK_ENV') == 'development':
            db.create_all()
except Exception as e:
    print(f"Error: {e}")

if __name__ == '__main__':
    # Запускаем приложение
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't'])