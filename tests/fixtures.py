from werkzeug.security import generate_password_hash

import pytest

from app.extensions import db

from app.models.users import User
from app.models.modalidades import Modalidade

from werkzeug.datastructures import MultiDict

@pytest.fixture
def form_data():
    return MultiDict

from tests.factories import (
    criar_treino,
    criar_ocorrencia,
    criar_frequencia
)

@pytest.fixture
def modalidade():

    modalidade = Modalidade(
        mod_nome="Futsal"
    )

    db.session.add(modalidade)
    db.session.commit()

    return modalidade

@pytest.fixture
def professor():

    professor = User(
        usr_nome="Professor",
        usr_email="prof@ifrn.edu.br",
        usr_senha_hash=generate_password_hash("12345678"),
        usr_tipo="professor",
        usr_confirmed=True,
        usr_is_active=True,
        usr_primeiro_login=False,
        usr_pontos=0,
        usr_img="images/default_profile.png"
    )

    db.session.add(professor)
    db.session.commit()

    return professor

@pytest.fixture
def aluno(modalidade):

    aluno = User(
        usr_nome="Aluno",
        usr_email="aluno@escolar.ifrn.edu.br",
        usr_senha_hash=generate_password_hash("12345678"),
        usr_tipo="aluno",
        usr_confirmed=True,
        usr_is_active=True,
        usr_primeiro_login=False,
        usr_mod_id=modalidade.mod_id,
        usr_pontos=0,
        usr_img="images/default_profile.png"
    )

    db.session.add(aluno)
    db.session.commit()

    return aluno

@pytest.fixture
def login_professor(client, professor):

    with client.session_transaction() as sess:

        sess["_user_id"] = str(professor.usr_id)

        sess["_fresh"] = True

    return professor

@pytest.fixture
def login_aluno(client, aluno):

    with client.session_transaction() as sess:

        sess["_user_id"] = str(aluno.usr_id)

        sess["_fresh"] = True

    return aluno

@pytest.fixture
def treino(professor, modalidade):

    return criar_treino(
        professor,
        modalidade
    )

@pytest.fixture
def ocorrencia(treino):

    return criar_ocorrencia(
        treino
    )

@pytest.fixture
def frequencia(aluno, treino, ocorrencia):

    return criar_frequencia(
        aluno,
        treino,
        ocorrencia
    )