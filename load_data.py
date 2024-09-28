import json
import logging
from app import create_app, db
from app.models import Course

# Настройка логирования
logging.basicConfig(level=logging.INFO)

app = create_app()

def load_courses_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Файл {file_path} не найден.")
        return []
    except json.JSONDecodeError:
        logging.error(f"Ошибка декодирования JSON в файле {file_path}.")
        return []

def populate_courses():
    with app.app_context():  # Создаем контекст приложения
        courses_data = load_courses_from_json('courses.json')

        # Очистить таблицу перед загрузкой новых данных
        db.session.query(Course).delete()
        db.session.commit()

        if not courses_data:
            logging.warning("Нет данных для загрузки курсов.")
            return

        courses = []
        for course_data in courses_data:
            course = Course(
                id=course_data['id'],
                title=course_data['title'],
                description=course_data['description'],
                details=course_data['details'],
                image=course_data['image'],
                price=course_data.get('price', 0)
            )
            courses.append(course)

        db.session.bulk_save_objects(courses)
        db.session.commit()
        logging.info(f"{len(courses)} курсов успешно загружено.")

if __name__ == '__main__':
    populate_courses()
