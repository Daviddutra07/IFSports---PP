from datetime import datetime

from app.extensions import db
from app.models.frequencia import Frequencia
from tests.fixtures import *


def test_treino_ja_validado_false_sem_frequencias(app, ocorrencia):
    assert Frequencia.treino_ja_validado(ocorrencia.tro_id) is False


def test_treino_ja_validado_false_com_frequencia_nao_validada(app, ocorrencia, frequencia):
    assert Frequencia.treino_ja_validado(ocorrencia.tro_id) is False


def test_treino_ja_validado_true_com_frequencia_validada(app, ocorrencia, frequencia):
    frequencia.frq_validado_em = datetime.now()
    db.session.commit()

    assert Frequencia.treino_ja_validado(ocorrencia.tro_id) is True


def test_treino_ja_validado_nao_afeta_outras_ocorrencias(app, treino, ocorrencia, frequencia):
    from tests.factories import criar_ocorrencia

    outra_ocorrencia = criar_ocorrencia(treino, dias=2)

    frequencia.frq_validado_em = datetime.now()
    db.session.commit()

    assert Frequencia.treino_ja_validado(outra_ocorrencia.tro_id) is False
