from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Course, FavoriteCourse
import logging

courses_bp = Blueprint('courses', __name__)
logger = logging.getLogger(__name__)


# Роут для отображения всех курсов
@courses_bp.route('/courses')
def list_courses():
    try:
        courses = Course.query.all()
        logger.info(f"Fetched {len(courses)} courses.")  # Логирование количества курсов
        return render_template('courses.html', courses=courses)
    except Exception as e:
        logger.error(f"Error fetching courses: {e}")
        flash('Ошибка при получении списка курсов. Попробуйте снова.', 'danger')
        return redirect(url_for('main.home'))


# Роут для отображения деталей курса
@courses_bp.route('/courses/<int:course_id>')
def course_details(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        return render_template('course_details.html', course=course)
    except Exception as e:
        logger.error(f"Error fetching course details for course_id {course_id}: {e}")
        flash('Ошибка при получении деталей курса. Попробуйте снова.', 'danger')
        return redirect(url_for('courses.list_courses'))


# Роут для добавления курса в избранное
@courses_bp.route('/add_to_favorites/<int:course_id>', methods=['POST'])
@login_required
def add_to_favorites(course_id):
    try:
        # Проверка, есть ли курс уже в избранном
        favorite_exists = FavoriteCourse.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        
        if favorite_exists:
            flash('Курс уже в избранном.', 'info')
        else:
            favorite = FavoriteCourse(user_id=current_user.id, course_id=course_id)
            db.session.add(favorite)
            db.session.commit()
            flash('Курс добавлен в избранное.', 'success')
            logger.info(f"User {current_user.id} added course {course_id} to favorites.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding course {course_id} to favorites for user {current_user.id}: {e}")
        flash('Ошибка при добавлении в избранное. Попробуйте снова.', 'danger')
    return redirect(url_for('courses.list_courses'))


# Роут для отображения популярных курсов
@courses_bp.route('/popular_courses')
def popular_courses():
    try:
        # Примерный список популярных курсов, замените на реальную логику
        course_ids = [1, 2, 3]  # Это пример, замените на реальные популярные курсы
        courses = Course.query.filter(Course.id.in_(course_ids)).all()
        return render_template('courses.html', courses=courses)
    except Exception as e:
        logger.error(f"Error fetching popular courses: {e}")
        flash('Ошибка при получении популярных курсов. Попробуйте снова.', 'danger')
        return redirect(url_for('courses.list_courses'))
