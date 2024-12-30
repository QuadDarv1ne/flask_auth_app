import os
from flask import current_app, url_for
from flask_mail import Message
from app import mail

def send_reset_email(user):
    """
    Отправляет электронное письмо для сброса пароля пользователю.

    Эта функция генерирует токен для сброса пароля и отправляет пользователю электронное письмо
    с ссылкой для сброса пароля. Если отправка письма не удалась, в консоль выводится сообщение об ошибке.

    :param user: Объект User, которому необходимо отправить письмо для сброса пароля.
    :type user: User
    :return: None
    """
    token = user.get_reset_token()
    
    # Создание сообщения для отправки
    msg = Message('Сброс пароля',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Чтобы сбросить пароль, перейдите по следующей ссылке:
{url_for('auth.reset_token', token=token, _external=True)}

Если вы не запрашивали сброс пароля, просто проигнорируйте это сообщение.
'''

    try:
        # Отправка письма через Flask-Mail
        mail.send(msg)
        print(f"Email sent to {user.email}")
    except Exception as e:
        # Ошибка при отправке письма
        print(f"Failed to send email to {user.email}: {e}")
