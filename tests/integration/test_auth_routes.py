from werkzeug.security import check_password_hash

from app.extensions import db
from app.models.users import User
from app.services.email_service import gerar_token
from tests.factories import criar_aluno
from tests.fixtures import *


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------

def test_login_sucesso(client, aluno):
    response = client.post(
        "/auth/login",
        data={"email": aluno.usr_email, "senha": "12345678"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert "Login realizado com sucesso".encode("utf-8") in response.data

    # confirma que a sessão ficou autenticada de fato,
    # acessando uma rota que exige login
    pagina_protegida = client.get("/treinos/")
    assert pagina_protegida.status_code == 200


def test_login_senha_errada(client, aluno):
    response = client.post(
        "/auth/login",
        data={"email": aluno.usr_email, "senha": "senhaErrada"}
    )

    assert response.status_code == 200
    assert "Email ou senha inválidos".encode("utf-8") in response.data


def test_login_conta_nao_confirmada(client):
    criar_aluno(
        email="naoconfirmado@escolar.ifrn.edu.br",
        confirmed=False
    )

    response = client.post(
        "/auth/login",
        data={"email": "naoconfirmado@escolar.ifrn.edu.br", "senha": "12345678"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert "confirmar seu email".encode("utf-8") in response.data


def test_login_email_inexistente(client):
    response = client.post(
        "/auth/login",
        data={"email": "naoexiste@escolar.ifrn.edu.br", "senha": "12345678"}
    )

    assert response.status_code == 200
    assert "Email ou senha inválidos".encode("utf-8") in response.data


# ---------------------------------------------------------------------------
# confirmação de e-mail
# ---------------------------------------------------------------------------

def test_confirmar_email_token_valido(client):
    novo_aluno = criar_aluno(
        email="confirmar@escolar.ifrn.edu.br",
        confirmed=False
    )

    token = gerar_token(novo_aluno.usr_email, salt="email-confirm")

    response = client.get(
        f"/auth/confirmar/{token}",
        follow_redirects=True
    )

    assert response.status_code == 200

    usuario = User.query.filter_by(usr_email="confirmar@escolar.ifrn.edu.br").first()
    assert usuario.usr_confirmed is True


def test_confirmar_email_token_invalido(client):
    response = client.get(
        "/auth/confirmar/token-invalido",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert "Link inválido ou expirado".encode("utf-8") in response.data


# ---------------------------------------------------------------------------
# redefinição de senha
# ---------------------------------------------------------------------------

def test_redefinir_senha_token_valido(client):
    usuario = criar_aluno(
        email="resetar@escolar.ifrn.edu.br",
        confirmed=True
    )

    token = gerar_token(usuario.usr_email, salt="reset-password")

    response = client.post(
        f"/auth/redefinir-senha/{token}",
        data={"senha": "novaSenha123", "confirmar_senha": "novaSenha123"},
        follow_redirects=True
    )

    assert response.status_code == 200

    db.session.refresh(usuario)

    assert check_password_hash(usuario.usr_senha_hash, "novaSenha123")


def test_redefinir_senha_token_invalido(client):
    response = client.get(
        "/auth/redefinir-senha/token-invalido",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert "Link inválido ou expirado".encode("utf-8") in response.data


# ---------------------------------------------------------------------------
# professor_required (autorização)
# ---------------------------------------------------------------------------

def test_professor_required_bloqueia_aluno(client, login_aluno):
    response = client.get("/treinos/criar")

    assert response.status_code == 403


def test_professor_required_redireciona_anonimo(client):
    response = client.get("/treinos/criar")

    assert response.status_code in (301, 302)
    assert "/auth/login" in response.headers["Location"]
