import os
from flask import current_app
from flask_mail import Message
from app import mail

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Сброс пароля',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Чтобы сбросить пароль, перейдите по следующей ссылке:
{url_for('auth.reset_token', token=token, _external=True)}

Если вы не запрашивали сброс пароля, просто проигнорируйте это сообщение.
'''
    mail.send(msg)
