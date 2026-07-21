from datetime import datetime, timedelta

import pytest

from app.extensions import db
from app.models.treino_ocorrencia import TreinoOcorrencia
from tests.fixtures import *


@pytest.fixture(autouse=True)
def mock_dependencias(mocker):
    mocker.patch("app.controllers.treinos.routes.criar_notificacao_usuario")
    mocker.patch("app.controllers.treinos.routes.verificar_conquistas")
    mocker.patch("app.controllers.treinos.routes.socketio.emit")


def test_validar_presenca(
    client,
    login_professor,
    ocorrencia,
    frequencia
):
    # Arrange
    ocorrencia.tro_data = datetime.now() - timedelta(hours=2)

    pontos_antes = frequencia.aluno.usr_pontos

    db.session.commit()

    # Act
    response = client.post(
        f"/treinos/detalhes/{ocorrencia.tro_id}/validar",
        data={
            f"status_{frequencia.frq_id}": "on",
            f"estrelas_{frequencia.frq_id}": "5"
        },
        follow_redirects=False
    )

    # Assert
    assert response.status_code == 302

    db.session.refresh(frequencia)
    db.session.refresh(ocorrencia)
    db.session.refresh(frequencia.aluno)

    assert frequencia.frq_status == "presente"
    assert frequencia.frq_aluno_nota == 5
    assert frequencia.frq_validado_em is not None
    assert ocorrencia.tro_validado_em is not None
    assert frequencia.aluno.usr_pontos == pontos_antes + 15


def test_validar_ausencia(
    client,
    login_professor,
    ocorrencia,
    frequencia
):
    # Arrange
    ocorrencia.tro_data = datetime.now() - timedelta(hours=1)

    pontos_antes = frequencia.aluno.usr_pontos

    db.session.commit()

    # Act
    response = client.post(
        f"/treinos/detalhes/{ocorrencia.tro_id}/validar",
        data={},
        follow_redirects=False
    )

    # Assert
    assert response.status_code == 302

    db.session.refresh(frequencia)
    db.session.refresh(frequencia.aluno)

    assert frequencia.frq_status == "ausente"
    assert frequencia.frq_validado_em is not None
    assert frequencia.aluno.usr_pontos == pontos_antes


def test_impedir_validar_antes_do_treino(
    client,
    login_professor,
    ocorrencia
):
    ocorrencia.tro_data = datetime.now() + timedelta(hours=2)

    db.session.commit()

    response = client.post(
        f"/treinos/detalhes/{ocorrencia.tro_id}/validar",
        follow_redirects=True
    )

    assert b"Voc\xc3\xaa s\xc3\xb3 pode validar" in response.data


def test_nao_validar_duas_vezes(
    client,
    login_professor,
    ocorrencia,
    frequencia
):
    ocorrencia.tro_data = datetime.now() - timedelta(hours=2)
    ocorrencia.tro_validado_em = datetime.now()

    frequencia.frq_status = "presente"
    frequencia.frq_validado_em = datetime.now()

    db.session.commit()

    response = client.post(
        f"/treinos/detalhes/{ocorrencia.tro_id}/validar",
        follow_redirects=True
    )

    db.session.refresh(frequencia)

    assert b"j\xc3\xa1 foi validado" in response.data
    assert frequencia.frq_status == "presente"


def test_validar_sem_participantes(
    client,
    login_professor,
    treino,
    ocorrencia
):
    ocorrencia.tro_data = datetime.now() - timedelta(hours=2)

    db.session.commit()

    response = client.post(
        f"/treinos/detalhes/{ocorrencia.tro_id}/validar",
        follow_redirects=False
    )

    assert response.status_code == 302

    db.session.refresh(ocorrencia)

    assert ocorrencia.tro_ativo is False


def test_treino_fixo_cria_nova_ocorrencia(
    client,
    login_professor,
    treino,
    ocorrencia,
    frequencia
):
    treino.trn_fixo = True

    ocorrencia.tro_data = datetime.now() - timedelta(hours=1)

    db.session.commit()

    response = client.post(
        f"/treinos/detalhes/{ocorrencia.tro_id}/validar",
        data={
            f"status_{frequencia.frq_id}": "on"
        },
        follow_redirects=False
    )

    assert response.status_code == 302

    quantidade = TreinoOcorrencia.query.filter_by(
        tro_treino_id=treino.trn_id
    ).count()

    assert quantidade == 2

    nova_ocorrencia = (
        TreinoOcorrencia.query
        .filter_by(tro_treino_id=treino.trn_id)
        .order_by(TreinoOcorrencia.tro_data.desc())
        .first()
    )

    assert nova_ocorrencia.tro_id != ocorrencia.tro_id
    assert nova_ocorrencia.tro_data > ocorrencia.tro_data
    assert nova_ocorrencia.tro_ativo is True


def test_treino_unico_encerrado(
    client,
    login_professor,
    treino,
    ocorrencia,
    frequencia
):
    treino.trn_fixo = False

    ocorrencia.tro_data = datetime.now() - timedelta(hours=1)

    db.session.commit()

    response = client.post(
        f"/treinos/detalhes/{ocorrencia.tro_id}/validar",
        data={
            f"status_{frequencia.frq_id}": "on"
        },
        follow_redirects=False
    )

    assert response.status_code == 302

    db.session.refresh(treino)
    db.session.refresh(ocorrencia)

    assert treino.trn_ativo is False
    assert ocorrencia.tro_ativo is False