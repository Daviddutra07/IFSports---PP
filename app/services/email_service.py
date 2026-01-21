from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from flask_mail import Message
from app.extensions import mail

def gerar_token_confirmacao(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm')


def validar_token(token, expiration=900):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token,salt='email-confirm',max_age=expiration)
    except Exception:
        return None
    return email


def enviar_email_confirmacao(user):
    token = gerar_token_confirmacao(user.usr_email)

    confirmar_url = url_for('auth.confirmar_email',token=token,_external=True)

    msg = Message(subject='Confirme seu cadastro no IF Sports', recipients=[user.usr_email])

    msg.body = f"""
Olá!

Para confirmar seu cadastro no IF Sports, clique no link abaixo:

{confirmar_url}

Se você não solicitou este cadastro, ignore este email.
"""

    mail.send(msg)
