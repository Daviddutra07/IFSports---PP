from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app.extensions import db

from app.models.treinos import Treino
from app.models.treino_ocorrencia import TreinoOcorrencia
from app.models.frequencia import Frequencia
from app.models.users import User
from app.models.conquistas import Conquista

def criar_treino(
    professor,
    modalidade,
    nome="Treino de Futsal",
    vagas=20,
    fixo=False
):

    treino = Treino(
        trn_nome=nome,
        trn_descricao="Treino criado automaticamente",
        trn_fixo=fixo,
        trn_quantidade=vagas,
        trn_pro_id=professor.usr_id,
        trn_mod_id=modalidade.mod_id,
        trn_ativo=True
    )

    db.session.add(treino)
    db.session.commit()

    return treino

def criar_ocorrencia(
    treino,
    dias=1
):

    ocorrencia = TreinoOcorrencia(

        tro_treino_id=treino.trn_id,

        tro_data=datetime.now() + timedelta(days=dias),

        tro_ativo=True,

        tro_vagas_ocupadas=0

    )

    db.session.add(ocorrencia)
    db.session.commit()

    return ocorrencia

def criar_frequencia(
    aluno,
    treino,
    ocorrencia,
    status="inscricao",
    nota=None
):

    frequencia = Frequencia(

        frq_aluno_id=aluno.usr_id,

        frq_treino_id=treino.trn_id,

        frq_ocorrencia_id=ocorrencia.tro_id,

        frq_data_ocorrencia=ocorrencia.tro_data,

        frq_status=status,

        frq_aluno_nota=nota

    )

    ocorrencia.tro_vagas_ocupadas += 1

    db.session.add(frequencia)

    db.session.commit()

    return frequencia


def criar_aluno(
    email,
    nome="Aluno",
    pontos=0,
    confirmed=True,
    ativo=True,
    senha="12345678"
):

    aluno = User(
        usr_nome=nome,
        usr_email=email,
        usr_senha_hash=generate_password_hash(senha),
        usr_tipo="aluno",
        usr_confirmed=confirmed,
        usr_is_active=ativo,
        usr_primeiro_login=False,
        usr_pontos=pontos,
        usr_img="images/default_profile.png"
    )

    db.session.add(aluno)
    db.session.commit()

    return aluno


def criar_conquista(
    tipo,
    meta=None,
    nome="Conquista Teste",
    bonus=10,
    tier="normal",
    tier_valor=1,
    descricao=None
):

    conquista = Conquista(
        cnq_nome=nome,
        cnq_descricao=descricao,
        cnq_tipo=tipo,
        cnq_meta=meta,
        cnq_pontos_bonus=bonus,
        cnq_tier=tier,
        cnq_tier_valor=tier_valor
    )

    db.session.add(conquista)
    db.session.commit()

    return conquista