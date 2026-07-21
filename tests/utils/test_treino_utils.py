from datetime import datetime, time, timedelta

from app.controllers.treinos.utils import (
    calcular_primeira_data,
    calcular_proxima_data,
    obter_ocorrencia_aberta,
)
from tests.factories import criar_ocorrencia
from tests.fixtures import *


class FakeDatetime(datetime):
    """
    Subclasse usada para congelar o valor de datetime.now() nos testes,
    permitindo assertar resultados de forma determinística.
    """
    fixed_now = None

    @classmethod
    def now(cls, tz=None):
        return cls.fixed_now


def _freeze(monkeypatch, fixed_now):
    FakeDatetime.fixed_now = fixed_now
    monkeypatch.setattr(
        "app.controllers.treinos.utils.datetime",
        FakeDatetime
    )


# ---------------------------------------------------------------------------
# calcular_primeira_data
# ---------------------------------------------------------------------------

def test_primeira_data_dia_diferente_na_mesma_semana(monkeypatch):
    # "Agora" é segunda-feira (weekday=0), às 10h
    agora = datetime(2026, 7, 20, 10, 0)
    _freeze(monkeypatch, agora)

    # Pede quarta-feira (weekday=2) às 19h
    resultado = calcular_primeira_data(2, time(19, 0))

    assert resultado == datetime(2026, 7, 22, 19, 0)


def test_primeira_data_mesmo_dia_horario_ainda_nao_passou(monkeypatch):
    # "Agora" é segunda-feira, às 8h
    agora = datetime(2026, 7, 20, 8, 0)
    _freeze(monkeypatch, agora)

    # Pede segunda-feira às 10h (ainda não passou hoje)
    resultado = calcular_primeira_data(0, time(10, 0))

    assert resultado == datetime(2026, 7, 20, 10, 0)


def test_primeira_data_mesmo_dia_horario_ja_passou(monkeypatch):
    # "Agora" é segunda-feira, às 20h
    agora = datetime(2026, 7, 20, 20, 0)
    _freeze(monkeypatch, agora)

    # Pede segunda-feira às 10h (já passou hoje) -> deve ir pra próxima semana
    resultado = calcular_primeira_data(0, time(10, 0))

    assert resultado == datetime(2026, 7, 27, 10, 0)


def test_primeira_data_dia_anterior_na_semana_pula_para_proxima(monkeypatch):
    # "Agora" é quinta-feira (weekday=3)
    agora = datetime(2026, 7, 23, 12, 0)
    _freeze(monkeypatch, agora)

    # Pede terça-feira (weekday=1), que já passou nesta semana
    resultado = calcular_primeira_data(1, time(9, 0))

    assert resultado == datetime(2026, 7, 28, 9, 0)


# ---------------------------------------------------------------------------
# calcular_proxima_data
# ---------------------------------------------------------------------------

def test_proxima_data_soma_sete_dias():
    data_atual = datetime(2026, 7, 20, 19, 0)

    resultado = calcular_proxima_data(data_atual)

    assert resultado == data_atual + timedelta(days=7)
    assert resultado == datetime(2026, 7, 27, 19, 0)


# ---------------------------------------------------------------------------
# obter_ocorrencia_aberta
# ---------------------------------------------------------------------------

def test_obter_ocorrencia_aberta_retorna_none_sem_ocorrencias(app, treino):
    assert obter_ocorrencia_aberta(treino.trn_id) is None


def test_obter_ocorrencia_aberta_ignora_inativas_e_validadas(app, treino, ocorrencia):
    from app.extensions import db

    # ocorrencia (fixture) está ativa e não validada -> é a aberta
    inativa = criar_ocorrencia(treino, dias=2)
    inativa.tro_ativo = False

    validada = criar_ocorrencia(treino, dias=3)
    validada.tro_validado_em = datetime.now()

    db.session.commit()

    resultado = obter_ocorrencia_aberta(treino.trn_id)

    assert resultado.tro_id == ocorrencia.tro_id


def test_obter_ocorrencia_aberta_retorna_mais_antiga(app, treino, ocorrencia):
    # ocorrencia (fixture) foi criada com dias=1; criamos uma mais distante
    mais_distante = criar_ocorrencia(treino, dias=5)

    resultado = obter_ocorrencia_aberta(treino.trn_id)

    assert resultado.tro_id == ocorrencia.tro_id
    assert resultado.tro_data < mais_distante.tro_data
