from flask import render_template, redirect, url_for, flash, Blueprint, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import FavoriteCourse, User
from app.forms import UpdateProfileForm

profile_bp = Blueprint('profile', __name__)

@profile_bp.route("/profile", endpoint='user_profile')
@login_required
def profile():
    try:
        user_favorites = FavoriteCourse.query.filter_by(user_id=current_user.id).all()
        favorite_courses = [favorite.course for favorite in user_favorites]
        return render_template('profile.html', favorite_courses=favorite_courses)
    except Exception as e:
        flash('Ошибка при получении избранных курсов. Попробуйте снова.', 'danger')
        return redirect(url_for('main.home'))

@profile_bp.route("/profile/edit", methods=['GET', 'POST'])
@login_required
def profile_edit():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.profile_picture.data:
            try:
                # Удаление старого изображения профиля
                if current_user.image_file:
                    old_picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
                    if os.path.exists(old_picture_path):
                        os.remove(old_picture_path)

                # Сохранение нового изображения профиля
                profile_picture = form.profile_picture.data
                picture_filename = secure_filename(profile_picture.filename)
                picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)
                profile_picture.save(picture_path)
                current_user.image_file = picture_filename
            except Exception as e:
                flash('Ошибка при загрузке изображения профиля. Попробуйте снова.', 'danger')
                return redirect(url_for('profile.profile_edit'))

        try:
            db.session.commit()
            flash('Ваш профиль был обновлён', 'success')
            return redirect(url_for('profile.user_profile'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении профиля. Попробуйте снова.', 'danger')
            return redirect(url_for('profile.profile_edit'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('profile_edit.html', title='Редактировать профиль', form=form)

@profile_bp.route("/profile/remove_favorite/<int:course_id>", methods=['POST'])
@login_required
def remove_favorite(course_id):
    try:
        favorite = FavoriteCourse.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            flash('Курс удален из избранного.', 'success')
        else:
            flash('Курс не найден в избранных.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении курса из избранного. Попробуйте снова.', 'danger')
    return redirect(url_for('profile.user_profile'))