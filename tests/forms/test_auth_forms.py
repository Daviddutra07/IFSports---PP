from werkzeug.datastructures import MultiDict

from app.controllers.auth.forms import RegisterForm


def test_register_email_aluno(app):
    with app.test_request_context():

        form = RegisterForm(formdata=MultiDict({
            "nome": "Aluno Teste",
            "email": "aluno@escolar.ifrn.edu.br",
            "senha": "12345678",
            "confirmar_senha": "12345678",
            "role_provisorio": "aluno"
        }))

        assert form.validate()
        assert form.user_role == "aluno"


def test_register_email_professor(app):
    with app.test_request_context():

        form = RegisterForm(formdata=MultiDict({
            "nome": "Professor",
            "email": "prof@ifrn.edu.br",
            "senha": "12345678",
            "confirmar_senha": "12345678",
            "role_provisorio": "professor"
        }))

        assert form.validate()
        assert form.user_role == "professor"


def test_register_email_invalido(app):
    with app.test_request_context():

        form = RegisterForm(formdata=MultiDict({
            "nome": "Teste",
            "email": "gmail@gmail.com",
            "senha": "12345678",
            "confirmar_senha": "12345678",
            "role_provisorio": "aluno"
        }))

        assert not form.validate()
        assert "email" in form.errors


def test_register_senhas_diferentes(app):
    with app.test_request_context():

        form = RegisterForm(formdata=MultiDict({
            "nome": "Teste",
            "email": "aluno@escolar.ifrn.edu.br",
            "senha": "12345678",
            "confirmar_senha": "87654321",
            "role_provisorio": "aluno"
        }))

        assert not form.validate()
        assert "senha" in form.errors
        assert "As senhas devem ser iguais" in form.senha.errors[0]