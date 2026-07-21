from app.extensions import db
from app.models.conquistas import UsuarioConquista
from app.services.gamification_service import (
    conceder_conquista,
    verificar_conquistas,
)
from tests.factories import criar_aluno, criar_conquista, criar_frequencia
from tests.fixtures import *


def _concedida(usuario, conquista):
    return UsuarioConquista.query.filter_by(
        usc_usr_id=usuario.usr_id,
        usc_cnq_id=conquista.cnq_id
    ).first() is not None


# ---------------------------------------------------------------------------
# conceder_conquista
# ---------------------------------------------------------------------------

def test_conceder_conquista_primeira_vez(app, aluno):
    conquista = criar_conquista(tipo="pontos", meta=100, bonus=20)

    resultado = conceder_conquista(aluno.usr_id, conquista)
    db.session.commit()

    assert resultado is True
    assert _concedida(aluno, conquista)
    assert aluno.usr_pontos == 20


def test_conceder_conquista_ja_concedida_nao_duplica_nem_soma_pontos_de_novo(app, aluno):
    conquista = criar_conquista(tipo="pontos", meta=100, bonus=20)

    conceder_conquista(aluno.usr_id, conquista)
    db.session.commit()

    resultado = conceder_conquista(aluno.usr_id, conquista)
    db.session.commit()

    assert resultado is False
    assert aluno.usr_pontos == 20
    assert UsuarioConquista.query.filter_by(
        usc_usr_id=aluno.usr_id,
        usc_cnq_id=conquista.cnq_id
    ).count() == 1


# ---------------------------------------------------------------------------
# verificar_conquistas - tipo "pontos"
# ---------------------------------------------------------------------------

def test_verifica_conquista_pontos_atinge_meta(app, aluno):
    conquista = criar_conquista(tipo="pontos", meta=100, bonus=20)
    aluno.usr_pontos = 150
    db.session.commit()

    verificar_conquistas(aluno.usr_id)

    assert _concedida(aluno, conquista)
    assert aluno.usr_pontos == 170


def test_verifica_conquista_pontos_nao_atinge_meta(app, aluno):
    conquista = criar_conquista(tipo="pontos", meta=100, bonus=20)
    aluno.usr_pontos = 50
    db.session.commit()

    verificar_conquistas(aluno.usr_id)

    assert not _concedida(aluno, conquista)
    assert aluno.usr_pontos == 50


# ---------------------------------------------------------------------------
# verificar_conquistas - tipo "inscricao" / "presenca"
# ---------------------------------------------------------------------------

def test_verifica_conquista_inscricao_conta_qualquer_status(app, aluno, treino):
    conquista = criar_conquista(tipo="inscricao", meta=2, bonus=5)

    for i in range(2):
        ocorrencia = criar_ocorrencia(treino, dias=i + 1)
        criar_frequencia(aluno, treino, ocorrencia, status="inscricao")

    verificar_conquistas(aluno.usr_id)

    assert _concedida(aluno, conquista)


def test_verifica_conquista_presenca_ignora_inscricoes_nao_presentes(app, aluno, treino):
    conquista = criar_conquista(tipo="presenca", meta=1, bonus=5)

    ocorrencia = criar_ocorrencia(treino, dias=1)
    criar_frequencia(aluno, treino, ocorrencia, status="inscricao")

    verificar_conquistas(aluno.usr_id)

    assert not _concedida(aluno, conquista)


def test_verifica_conquista_presenca_conta_apenas_status_presente(app, aluno, treino):
    conquista = criar_conquista(tipo="presenca", meta=1, bonus=5)

    ocorrencia = criar_ocorrencia(treino, dias=1)
    criar_frequencia(aluno, treino, ocorrencia, status="presente")

    verificar_conquistas(aluno.usr_id)

    assert _concedida(aluno, conquista)


# ---------------------------------------------------------------------------
# verificar_conquistas - tipo "primeira_avaliacao" / "nota_perfeita"
# ---------------------------------------------------------------------------

def test_verifica_conquista_primeira_avaliacao(app, aluno, treino, ocorrencia):
    conquista = criar_conquista(tipo="primeira_avaliacao", bonus=5)

    criar_frequencia(aluno, treino, ocorrencia, status="presente", nota=3)

    verificar_conquistas(aluno.usr_id)

    assert _concedida(aluno, conquista)


def test_verifica_conquista_nota_perfeita_exige_nota_cinco(app, aluno, treino, ocorrencia):
    conquista = criar_conquista(tipo="nota_perfeita", bonus=5)

    criar_frequencia(aluno, treino, ocorrencia, status="presente", nota=4)

    verificar_conquistas(aluno.usr_id)

    assert not _concedida(aluno, conquista)


def test_verifica_conquista_nota_perfeita_concede_com_nota_cinco(app, aluno, treino, ocorrencia):
    conquista = criar_conquista(tipo="nota_perfeita", bonus=5)

    criar_frequencia(aluno, treino, ocorrencia, status="presente", nota=5)

    verificar_conquistas(aluno.usr_id)

    assert _concedida(aluno, conquista)


# ---------------------------------------------------------------------------
# verificar_conquistas - tipo "media"
# ---------------------------------------------------------------------------

def test_verifica_conquista_media_exige_minimo_tres_avaliacoes(app, aluno, treino):
    conquista = criar_conquista(tipo="media", meta=4.0, bonus=5, nome="Boa média")

    for i, nota in enumerate([5, 5]):
        ocorrencia = criar_ocorrencia(treino, dias=i + 1)
        criar_frequencia(aluno, treino, ocorrencia, status="presente", nota=nota)

    verificar_conquistas(aluno.usr_id)

    assert not _concedida(aluno, conquista)


def test_verifica_conquista_media_concede_com_tres_avaliacoes_e_meta_atingida(app, aluno, treino):
    conquista = criar_conquista(tipo="media", meta=4.0, bonus=5, nome="Boa média")

    for i, nota in enumerate([4, 4, 5]):
        ocorrencia = criar_ocorrencia(treino, dias=i + 1)
        criar_frequencia(aluno, treino, ocorrencia, status="presente", nota=nota)

    verificar_conquistas(aluno.usr_id)

    assert _concedida(aluno, conquista)


def test_verifica_conquista_elite_esportiva_exige_dez_avaliacoes(app, aluno, treino):
    # regra especial: "Elite esportiva!" exige 10 avaliações, não 3
    conquista = criar_conquista(
        tipo="media", meta=4.0, bonus=5, nome="Elite esportiva!"
    )

    for i, nota in enumerate([5, 5, 5, 5, 5, 5, 5, 5, 5]):  # 9 avaliações
        ocorrencia = criar_ocorrencia(treino, dias=i + 1)
        criar_frequencia(aluno, treino, ocorrencia, status="presente", nota=nota)

    verificar_conquistas(aluno.usr_id)

    assert not _concedida(aluno, conquista)

    # a décima avaliação completa o mínimo exigido
    ocorrencia = criar_ocorrencia(treino, dias=10)
    criar_frequencia(aluno, treino, ocorrencia, status="presente", nota=5)

    verificar_conquistas(aluno.usr_id)

    assert _concedida(aluno, conquista)


# ---------------------------------------------------------------------------
# verificar_conquistas - tipo "ranking"
# ---------------------------------------------------------------------------

def test_verifica_conquista_ranking_exige_minimo_dez_participantes(app, aluno):
    conquista = criar_conquista(tipo="ranking", meta=1, bonus=5)

    aluno.usr_pontos = 1000
    db.session.commit()

    # apenas o aluno da fixture existe -> menos de 10 participantes no ranking
    verificar_conquistas(aluno.usr_id)

    assert not _concedida(aluno, conquista)


def test_verifica_conquista_ranking_concede_quando_top_e_ha_dez_participantes(app, aluno):
    conquista = criar_conquista(tipo="ranking", meta=1, bonus=5)

    aluno.usr_pontos = 1000
    db.session.commit()

    for i in range(9):
        criar_aluno(email=f"aluno{i}@escolar.ifrn.edu.br", pontos=10)

    verificar_conquistas(aluno.usr_id)

    assert _concedida(aluno, conquista)


def test_verifica_conquista_ranking_nao_concede_fora_da_meta(app, aluno):
    conquista = criar_conquista(tipo="ranking", meta=1, bonus=5)

    aluno.usr_pontos = 5  # vai ficar em última posição
    db.session.commit()

    for i in range(9):
        criar_aluno(email=f"aluno{i}@escolar.ifrn.edu.br", pontos=1000)

    verificar_conquistas(aluno.usr_id)

    assert not _concedida(aluno, conquista)


# ---------------------------------------------------------------------------
# verificar_conquistas - recursão em cascata
# ---------------------------------------------------------------------------

def test_verifica_conquista_cascata_pontos_bonus_desbloqueia_outra(app, aluno):
    """
    Ganhar pontos por uma conquista pode ser suficiente pra desbloquear
    outra na mesma chamada (a função se chama recursivamente quando
    houve_nova é True).
    """
    conquista_a = criar_conquista(
        tipo="pontos", meta=50, bonus=60, nome="A", tier_valor=1
    )
    conquista_b = criar_conquista(
        tipo="pontos", meta=100, bonus=10, nome="B", tier_valor=2
    )

    aluno.usr_pontos = 50  # atinge só a meta de A (50 + 60 = 110 >= meta de B)
    db.session.commit()

    verificar_conquistas(aluno.usr_id)

    assert _concedida(aluno, conquista_a)
    assert _concedida(aluno, conquista_b)
    assert aluno.usr_pontos == 120
