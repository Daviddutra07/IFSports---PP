from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from flask_mail import Message
from app.extensions import mail


def gerar_token(email, salt):
    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

    return serializer.dumps(
        email,
        salt=salt
    )


def validar_token(token, salt, expiration=900):
    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

    try:
        return serializer.loads(
            token,
            salt=salt,
            max_age=expiration
        )
    except Exception:
        return None


def enviar_email_confirmacao(user):
    token = gerar_token(
        user.usr_email,
        "email-confirm"
    )

    confirmar_url = url_for(
        "auth.confirmar_email",
        token=token,
        _external=True
    )

    msg = Message(
        subject="Confirme seu cadastro no IFSports",
        recipients=[user.usr_email]
    )

    msg.body = f"""
Olá, {user.usr_nome}!

Para confirmar seu cadastro no IFSports, clique no link abaixo:

{confirmar_url}

O link é válido por 15 minutos.

Caso você não tenha solicitado este cadastro, basta ignorar este e-mail.
"""

    mail.send(msg)


def enviar_email_reset(user):
    token = gerar_token(
        user.usr_email,
        "reset-password"
    )

    redefinir_url = url_for(
        "auth.redefinir_senha",
        token=token,
        _external=True
    )

    msg = Message(
        subject="Redefinição de senha - IFSports",
        recipients=[user.usr_email]
    )

    msg.body = f"""
Olá, {user.usr_nome}!

Recebemos uma solicitação para redefinir sua senha.

Clique no link abaixo para cadastrar uma nova senha:

{redefinir_url}

O link é válido por 15 minutos.

Se você não solicitou esta alteração, ignore este e-mail.
"""

    mail.send(msg)