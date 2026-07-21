from app.controllers.auth.forms import RegisterForm
from tests.fixtures import *

class TestRegisterForm:

    def test_email_aluno_valido(self, app, form_data):

        with app.test_request_context():

            form = RegisterForm(formdata=form_data({
                "nome": "David",
                "email": "david@escolar.ifrn.edu.br",
                "senha": "12345678",
                "confirmar_senha": "12345678",
                "role_provisorio": "aluno"
            }))

            assert form.validate()
            assert form.user_role == "aluno"

    def test_email_professor_valido(self, app, form_data):

        with app.test_request_context():

            form = RegisterForm(formdata=form_data({
                "nome": "Professor",
                "email": "prof@ifrn.edu.br",
                "senha": "12345678",
                "confirmar_senha": "12345678",
                "role_provisorio": "professor"
            }))

            assert form.validate()
            assert form.user_role == "professor"

    def test_email_institucional_invalido(self, app, form_data):

        with app.test_request_context():

            form = RegisterForm(formdata=form_data({
                "nome": "David",
                "email": "gmail@gmail.com",
                "senha": "12345678",
                "confirmar_senha": "12345678",
                "role_provisorio": "aluno"
            }))

            assert not form.validate()
            assert "Use seu email institucional do IFRN." in form.email.errors

    def test_senhas_diferentes(self, app, form_data):

        with app.test_request_context():

            form = RegisterForm(formdata=form_data({
                "nome": "David",
                "email": "david@escolar.ifrn.edu.br",
                "senha": "12345678",
                "confirmar_senha": "87654321",
                "role_provisorio": "aluno"
            }))

            assert not form.validate()

    def test_senha_curta(self, app, form_data):

        with app.test_request_context():

            form = RegisterForm(formdata=form_data({
                "nome": "David",
                "email": "david@escolar.ifrn.edu.br",
                "senha": "123",
                "confirmar_senha": "123",
                "role_provisorio": "aluno"
            }))

            assert not form.validate()