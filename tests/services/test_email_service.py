from app.services.email_service import gerar_token, validar_token
from tests.fixtures import *


def test_gerar_token_e_validar_com_sucesso(app):
    token = gerar_token("aluno@escolar.ifrn.edu.br", salt="email-confirm")

    email = validar_token(token, salt="email-confirm")

    assert email == "aluno@escolar.ifrn.edu.br"


def test_validar_token_expirado_retorna_none(app):
    token = gerar_token("aluno@escolar.ifrn.edu.br", salt="email-confirm")

    # expiration negativo garante que o token já esteja expirado
    # no instante da validação, sem precisar esperar tempo real
    # transcorrer (evita teste lento/instável baseado em sleep()).
    email = validar_token(token, salt="email-confirm", expiration=-1)

    assert email is None


def test_validar_token_adulterado_retorna_none(app):
    token = gerar_token("aluno@escolar.ifrn.edu.br", salt="email-confirm")

    ultimo_char = token[-1]
    token_adulterado = token[:-1] + ("a" if ultimo_char != "a" else "b")

    email = validar_token(token_adulterado, salt="email-confirm")

    assert email is None
