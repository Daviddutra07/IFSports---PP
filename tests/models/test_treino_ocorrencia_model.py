from datetime import datetime

from app.extensions import db
from tests.fixtures import *


# ---------------------------------------------------------------------------
# vagas_restantes
# ---------------------------------------------------------------------------

def test_vagas_restantes_sem_ocupacao(app, treino, ocorrencia):
    assert ocorrencia.vagas_restantes == treino.trn_quantidade


def test_vagas_restantes_com_ocupacao(app, treino, ocorrencia):
    treino.trn_quantidade = 10
    ocorrencia.tro_vagas_ocupadas = 4
    db.session.commit()

    assert ocorrencia.vagas_restantes == 6


def test_vagas_restantes_lotado(app, treino, ocorrencia):
    treino.trn_quantidade = 5
    ocorrencia.tro_vagas_ocupadas = 5
    db.session.commit()

    assert ocorrencia.vagas_restantes == 0


# ---------------------------------------------------------------------------
# ja_validado
# ---------------------------------------------------------------------------

def test_ja_validado_false_por_padrao(app, ocorrencia):
    assert ocorrencia.ja_validado is False


def test_ja_validado_true_apos_validacao(app, ocorrencia):
    ocorrencia.tro_validado_em = datetime.now()
    db.session.commit()

    assert ocorrencia.ja_validado is True
