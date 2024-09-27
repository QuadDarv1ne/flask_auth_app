from flask import render_template, Blueprint
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
@main_bp.route("/home")
def home():
    return render_template('home.html', title='Главная')

@main_bp.route("/profile")
@login_required
def profile():
    return render_template('profile.html', title='Профиль', user=current_user)
