from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Course, FavoriteCourse

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/courses')
def list_courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)


@courses_bp.route('/courses/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_details.html', course=course)


@courses_bp.route('/add_to_favorites/<int:course_id>', methods=['POST'])
@login_required
def add_to_favorites(course_id):
    if not FavoriteCourse.query.filter_by(user_id=current_user.id, course_id=course_id).first():
        favorite = FavoriteCourse(user_id=current_user.id, course_id=course_id)
        db.session.add(favorite)
        try:
            db.session.commit()
            flash('Курс добавлен в избранное.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении в избранное. Попробуйте снова.', 'danger')
    else:
        flash('Курс уже в избранном.', 'info')
    return redirect(url_for('courses.list_courses'))
