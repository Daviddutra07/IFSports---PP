from flask_login import login_user, logout_user

from app.extensions import db
from tests.factories import criar_ocorrencia, criar_frequencia
from tests.fixtures import *


# ---------------------------------------------------------------------------
# ocorrencia_aberta
# ---------------------------------------------------------------------------

def test_ocorrencia_aberta_sem_ocorrencias(app, treino):
    assert treino.ocorrencia_aberta is None


def test_ocorrencia_aberta_com_ocorrencia_ativa(app, treino, ocorrencia):
    assert treino.ocorrencia_aberta.tro_id == ocorrencia.tro_id


def test_ocorrencia_aberta_ignora_validada(app, treino, ocorrencia):
    from datetime import datetime

    ocorrencia.tro_validado_em = datetime.now()
    db.session.commit()

    assert treino.ocorrencia_aberta is None


def test_ocorrencia_aberta_ignora_inativa(app, treino, ocorrencia):
    ocorrencia.tro_ativo = False
    db.session.commit()

    assert treino.ocorrencia_aberta is None


# ---------------------------------------------------------------------------
# vagas_ocupadas / vagas_restantes
# ---------------------------------------------------------------------------

def test_vagas_ocupadas_sem_ocorrencia_aberta(app, treino):
    assert treino.vagas_ocupadas == 0


def test_vagas_ocupadas_com_ocorrencia(app, treino, ocorrencia):
    ocorrencia.tro_vagas_ocupadas = 3
    db.session.commit()

    assert treino.vagas_ocupadas == 3


def test_vagas_restantes_sem_ocorrencia_aberta_usa_quantidade_total(app, treino):
    assert treino.vagas_restantes == treino.trn_quantidade


def test_vagas_restantes_desconta_ocupadas(app, treino, ocorrencia):
    treino.trn_quantidade = 20
    ocorrencia.tro_vagas_ocupadas = 5
    db.session.commit()

    assert treino.vagas_restantes == 15


# ---------------------------------------------------------------------------
# data_exibicao
# ---------------------------------------------------------------------------

def test_data_exibicao_sem_ocorrencia_aberta(app, treino):
    assert treino.data_exibicao is None


def test_data_exibicao_com_ocorrencia_aberta(app, treino, ocorrencia):
    assert treino.data_exibicao == ocorrencia.tro_data


# ---------------------------------------------------------------------------
# ja_fez_checkin
# ---------------------------------------------------------------------------

def test_ja_fez_checkin_false_para_professor(app, professor, treino, ocorrencia):
    with app.test_request_context():
        login_user(professor)

        assert treino.ja_fez_checkin is False

        logout_user()


def test_ja_fez_checkin_false_sem_ocorrencia_aberta(app, aluno, treino):
    with app.test_request_context():
        login_user(aluno)

        assert treino.ja_fez_checkin is False

        logout_user()


def test_ja_fez_checkin_false_sem_inscricao(app, aluno, treino, ocorrencia):
    with app.test_request_context():
        login_user(aluno)

        assert treino.ja_fez_checkin is False

        logout_user()


def test_ja_fez_checkin_true_com_inscricao(app, aluno, treino, ocorrencia):
    with app.test_request_context():
        criar_frequencia(aluno, treino, ocorrencia)

        login_user(aluno)

        assert treino.ja_fez_checkin is True

        logout_user()
