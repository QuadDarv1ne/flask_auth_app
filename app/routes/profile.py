from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from flask import current_app
from app import db
from app.models import User
from app.forms import UpdateProfileForm

profile_bp = Blueprint('profile', __name__)

@profile_bp.route("/profile", endpoint='user_profile')
@login_required
def profile():
    return render_template('profile.html', title='Профиль', user=current_user)

@profile_bp.route("/profile/edit", methods=['GET', 'POST'])
@login_required
def profile_edit():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        # Обработка загрузки нового фото профиля
        if form.profile_picture.data:
            profile_picture = form.profile_picture.data
            picture_filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(current_app.root_path, 'static/profile_pics', picture_filename))
            current_user.image_file = picture_filename

        db.session.commit()
        flash('Ваш профиль был обновлён', 'success')
        return redirect(url_for('profile.user_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('profile_edit.html', title='Редактировать профиль', form=form)
