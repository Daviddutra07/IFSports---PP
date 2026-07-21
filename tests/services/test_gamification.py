from app.services.gamification_service import (
    calcular_nivel,
    calcular_progresso_nivel
)


def test_nivel_amador():
    nivel, nome = calcular_nivel(0)

    assert nivel == 1
    assert nome == "Atleta Amador"


def test_nivel_dedicado():
    nivel, nome = calcular_nivel(250)

    assert nivel == 2
    assert nome == "Atleta Dedicado"


def test_nivel_competidor():
    nivel, nome = calcular_nivel(500)

    assert nivel == 3
    assert nome == "Atleta Competidor"


def test_nivel_alto_nivel():
    nivel, nome = calcular_nivel(900)

    assert nivel == 4
    assert nome == "Atleta de Alto Nível"


def test_nivel_profissional():
    nivel, nome = calcular_nivel(1500)

    assert nivel == 5
    assert nome == "Atleta Profissional"

def test_progresso_inicio():
    dados = calcular_progresso_nivel(0)

    assert dados["nivel"] == 1
    assert dados["percentual"] == 0


def test_progresso_metade_primeiro_nivel():
    dados = calcular_progresso_nivel(100)

    assert dados["nivel"] == 1
    assert dados["percentual"] == 50


def test_progresso_nivel_dois():
    dados = calcular_progresso_nivel(300)

    assert dados["nivel"] == 2
    assert dados["percentual"] == 40

def test_progresso_ultimo_nivel():
    dados = calcular_progresso_nivel(1500)

    assert dados["nivel"] == 5
    assert dados["percentual"] == 100

from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.users import User
from app.services.gamification_service import (
    adicionar_pontos,
    remover_pontos
)


def criar_usuario():

    usuario = User(
        usr_nome="Aluno",
        usr_email="aluno@escolar.ifrn.edu.br",
        usr_tipo="aluno",
        usr_senha_hash=generate_password_hash("123"),
        usr_pontos=0
    )

    db.session.add(usuario)
    db.session.commit()

    return usuario

def test_adicionar_pontos(app):

    with app.app_context():

        usuario = criar_usuario()

        adicionar_pontos(usuario.usr_id, 15)

        db.session.commit()

        usuario = User.query.get(usuario.usr_id)

        assert usuario.usr_pontos == 15

def test_remover_pontos(app):

    with app.app_context():

        usuario = criar_usuario()

        usuario.usr_pontos = 30

        db.session.commit()

        remover_pontos(usuario.usr_id, 10)

        db.session.commit()

        usuario = User.query.get(usuario.usr_id)

        assert usuario.usr_pontos == 20