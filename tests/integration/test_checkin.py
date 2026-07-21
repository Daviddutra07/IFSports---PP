from app.extensions import db
from app.models.frequencia import Frequencia
from tests.fixtures import * 

def test_checkin_sucesso(client, login_aluno, treino, ocorrencia):

    response = client.post(
        f"/treinos/{treino.trn_id}/checkin",
        follow_redirects=True
    )

    assert response.status_code == 200

    frequencia = Frequencia.query.filter_by(
        frq_aluno_id=login_aluno.usr_id,
        frq_treino_id=treino.trn_id
    ).first()

    assert frequencia is not None

    db.session.refresh(login_aluno)

    assert login_aluno.usr_pontos == 5

    db.session.refresh(ocorrencia)

    assert ocorrencia.tro_vagas_ocupadas == 1

from app.models.frequencia import Frequencia


def test_professor_nao_pode_checkin(
    client,
    login_professor,
    treino
):

    response = client.post(
        f"/treinos/{treino.trn_id}/checkin",
        follow_redirects=True
    )

    assert response.status_code == 200

    frequencia = Frequencia.query.first()

    assert frequencia is None

def test_checkin_repetido(
    client,
    login_aluno,
    treino,
    ocorrencia,
    frequencia
):

    response = client.post(
        f"/treinos/{treino.trn_id}/checkin",
        follow_redirects=True
    )

    assert response.status_code == 200

    from app.models.frequencia import Frequencia

    assert Frequencia.query.count() == 1

from app.extensions import db
from app.models.frequencia import Frequencia


def test_cancelar_checkin(
    client,
    login_aluno,
    treino,
    ocorrencia,
    frequencia
):

    ocorrencia.tro_vagas_ocupadas = 1
    login_aluno.usr_pontos = 5

    db.session.commit()

    response = client.post(
        f"/treinos/{treino.trn_id}/cancelar_checkin",
        follow_redirects=True
    )

    assert response.status_code == 200

    assert Frequencia.query.count() == 0

    db.session.refresh(login_aluno)

    assert login_aluno.usr_pontos == 0

    db.session.refresh(ocorrencia)

    assert ocorrencia.tro_vagas_ocupadas == 0

from app.extensions import db


def test_checkin_treino_lotado(
    client,
    login_aluno,
    treino,
    ocorrencia
):

    treino.trn_quantidade = 1
    ocorrencia.tro_vagas_ocupadas = 1

    db.session.commit()

    response = client.post(
        f"/treinos/{treino.trn_id}/checkin",
        follow_redirects=True
    )

    assert response.status_code == 200

    from app.models.frequencia import Frequencia

    assert Frequencia.query.count() == 0

from app.extensions import db


def test_checkin_treino_inativo(
    client,
    login_aluno,
    treino
):

    treino.trn_ativo = False

    db.session.commit()

    response = client.post(
        f"/treinos/{treino.trn_id}/checkin",
        follow_redirects=True
    )

    assert response.status_code == 200

    from app.models.frequencia import Frequencia

    assert Frequencia.query.count() == 0