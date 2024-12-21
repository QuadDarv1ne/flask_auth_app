import os
from flask import current_app, url_for
from flask_mail import Message
from app import mail

def send_reset_email(user):
    """
    Отправляет электронное письмо для сброса пароля пользователю.

    Параметры:
        user (User): Пользователь, которому необходимо отправить письмо для сброса пароля.

    Возвращает:
        None
    """
    token = user.get_reset_token()
    msg = Message('Сброс пароля',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Чтобы сбросить пароль, перейдите по следующей ссылке:
{url_for('auth.reset_token', token=token, _external=True)}

Если вы не запрашивали сброс пароля, просто проигнорируйте это сообщение.
'''
    try:
        mail.send(msg)
        print(f"Email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")