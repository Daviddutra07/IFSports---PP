from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, func

from app.models.treinos import Treino
from app.models.treino_ocorrencia import TreinoOcorrencia
from app.models.frequencia import Frequencia
from app.models.avisos import Aviso
from app.models.notificacoes import Notificacao
from app.models.users import User
from app.models.conquistas import Conquista, UsuarioConquista
from app.models.modalidades import Modalidade
from app.models.mural_fotos import MuralFotos
from app.services.gamification_service import  calcular_progresso_nivel, TIER_CONFIG
from app.extensions import db


home_bp = Blueprint("home",__name__,url_prefix="/",template_folder="templates/home")


@home_bp.route("/")
def index():

    if not current_user.is_authenticated:
        return render_template("home/home_guest.html")

    agora = datetime.now()

    notificacoes = (
        Notificacao.query
        .filter(
            Notificacao.not_usr_id == current_user.usr_id,
            or_(
                Notificacao.not_expira_em.is_(None),
                Notificacao.not_expira_em >= agora
            )
        )
        .order_by(Notificacao.not_lida.asc(), Notificacao.not_created_at.desc())
        .limit(5)
        .all()
    )

    total_notificacoes_nao_lidas = (
        Notificacao.query
        .filter_by(not_usr_id=current_user.usr_id, not_lida=False)
        .count()
    )

    fotos_mural = (MuralFotos.query.order_by(MuralFotos.mft_created_at.desc()).limit(6).all())

    modalidades_progresso = calcular_modalidades_progresso()

    if current_user.usr_tipo == "aluno":
        return _home_aluno(notificacoes,total_notificacoes_nao_lidas,fotos_mural, modalidades_progresso)

    return  _home_professor(notificacoes,total_notificacoes_nao_lidas,fotos_mural, modalidades_progresso)

def calcular_modalidades_progresso():

    total_alunos = (
        User.query
        .filter(User.usr_tipo == "aluno")
        .count()
    )


    modalidades = (
        Modalidade.query
        .order_by(Modalidade.mod_nome.asc())
        .all()
    )


    modalidades_progresso = []


    for modalidade in modalidades:

        quantidade = (
            User.query
            .filter(
                User.usr_tipo == "aluno",
                User.usr_mod_id == modalidade.mod_id
            )
            .count()
        )


        percentual = 0

        if total_alunos > 0:
            percentual = round(
                (quantidade / total_alunos) * 100
            )


        modalidades_progresso.append({
            "nome": modalidade.mod_nome,
            "quantidade": quantidade,
            "percentual": percentual
        })


    return modalidades_progresso

def _home_aluno(notificacoes, total_notificacoes_nao_lidas, fotos_mural, modalidades_progresso):
    agora = datetime.now()

    treinos_disponiveis = []
    if current_user.usr_mod_id:
        treinos_disponiveis = (
            Treino.query
            .join(TreinoOcorrencia, TreinoOcorrencia.tro_treino_id == Treino.trn_id)
            .filter(
                Treino.trn_ativo.is_(True),
                Treino.trn_deleted_at.is_(None),
                TreinoOcorrencia.tro_ativo.is_(True),
                TreinoOcorrencia.tro_validado_em.is_(None),
                TreinoOcorrencia.tro_data >= agora
            )
            .order_by(TreinoOcorrencia.tro_data.asc())
            .limit(3)
            .all()
        )

    conquistas_destaque = (
        UsuarioConquista.query
        .join(Conquista)
        .filter(
            UsuarioConquista.usc_usr_id == current_user.usr_id
        )
        .order_by(
            Conquista.cnq_tier_valor.desc(),
            Conquista.cnq_pontos_bonus.desc()
        )
        .limit(3)
        .all()
    )

    progresso_nivel = calcular_progresso_nivel(current_user.usr_pontos)

    total_treinos_modalidade = 0
    treinos_que_foi = 0
    frequencia_percentual = 0

    if current_user.usr_mod_id:
        data_inicio_frequencia = current_user.usr_created_At

        total_treinos_modalidade = (
            TreinoOcorrencia.query
            .join(Treino, TreinoOcorrencia.tro_treino_id == Treino.trn_id)
            .filter(
                Treino.trn_mod_id == current_user.usr_mod_id,
                Treino.trn_deleted_at.is_(None),
                TreinoOcorrencia.tro_validado_em.is_not(None),
                TreinoOcorrencia.tro_data >= data_inicio_frequencia
            )
            .count()
        )

        treinos_que_foi = (
            Frequencia.query
            .join(TreinoOcorrencia, Frequencia.frq_ocorrencia_id == TreinoOcorrencia.tro_id)
            .join(Treino, Frequencia.frq_treino_id == Treino.trn_id)
            .filter(
                Frequencia.frq_aluno_id == current_user.usr_id,
                Frequencia.frq_status == "presente",
                Frequencia.frq_validado_em.is_not(None),
                Treino.trn_mod_id == current_user.usr_mod_id,
                Treino.trn_deleted_at.is_(None),
                TreinoOcorrencia.tro_validado_em.is_not(None),
                TreinoOcorrencia.tro_data >= data_inicio_frequencia
            )
            .count()
        )

        if total_treinos_modalidade > 0:
            frequencia_percentual = round(
                (treinos_que_foi / total_treinos_modalidade) * 100
            )

    media_notas = (
        db.session.query(func.avg(Frequencia.frq_aluno_nota))
        .filter(
            Frequencia.frq_aluno_id == current_user.usr_id,
            Frequencia.frq_aluno_nota.is_not(None)
        )
        .scalar()
    )
    media_notas = round(float(media_notas), 1) if media_notas is not None else 0

    ranking = (
        User.query
        .filter(User.usr_tipo == "aluno")
        .order_by(User.usr_pontos.desc(), User.usr_nome.asc())
        .all()
    )

    posicao_ranking = None
    for posicao, usuario in enumerate(ranking, start=1):
        if usuario.usr_id == current_user.usr_id:
            posicao_ranking = posicao
            break

    return render_template(
        "home/home_logado.html",
        perfil="aluno",
        notificacoes=notificacoes,
        total_notificacoes_nao_lidas=total_notificacoes_nao_lidas,
        treinos_disponiveis=treinos_disponiveis,
        conquistas_destaque=conquistas_destaque,
        progresso_nivel=progresso_nivel,
        frequencia_percentual=frequencia_percentual,
        treinos_que_foi=treinos_que_foi,
        total_treinos_modalidade=total_treinos_modalidade,
        media_notas=media_notas,
        posicao_ranking=posicao_ranking,
        fotos_mural=fotos_mural,
        tier_config=TIER_CONFIG,
        modalidades_progresso=modalidades_progresso
    )


def _home_professor(notificacoes, total_notificacoes_nao_lidas, fotos_mural, modalidades_progresso):
    agora = datetime.now()

    proximas_ocorrencias = (
        TreinoOcorrencia.query
        .join(Treino, TreinoOcorrencia.tro_treino_id == Treino.trn_id)
        .filter(
            Treino.trn_pro_id == current_user.usr_id,
            Treino.trn_ativo.is_(True),
            Treino.trn_deleted_at.is_(None),
            TreinoOcorrencia.tro_ativo.is_(True),
            TreinoOcorrencia.tro_data >= agora
        )
        .order_by(TreinoOcorrencia.tro_data.asc())
        .limit(5)
        .all()
    )

    proximo_treino = None
    total_inscritos_proximo = 0

    if proximas_ocorrencias:
        proximo_treino = proximas_ocorrencias[0]

        total_inscritos_proximo = (
            Frequencia.query
            .filter(
                Frequencia.frq_ocorrencia_id == proximo_treino.tro_id,
                Frequencia.frq_status.in_(["inscricao", "presente"])
            )
            .count()
        )

    proximo_treino = proximas_ocorrencias[0] if proximas_ocorrencias else None

    treinos_pendentes = (
        TreinoOcorrencia.query
        .join(Treino)
        .filter(
            Treino.trn_pro_id == current_user.usr_id,
            Treino.trn_ativo.is_(True),
            Treino.trn_deleted_at.is_(None),
            TreinoOcorrencia.tro_ativo.is_(True),
            TreinoOcorrencia.tro_data < agora,
            TreinoOcorrencia.tro_validado_em.is_(None)
        )
        .order_by(TreinoOcorrencia.tro_data.asc())
        .all()
    )

    return render_template(
        "home/home_logado.html",
        perfil="professor",
        notificacoes=notificacoes,
        total_notificacoes_nao_lidas=total_notificacoes_nao_lidas,
        proximas_ocorrencias=proximas_ocorrencias,
        fotos_mural=fotos_mural,
        modalidades_progresso=modalidades_progresso,
        proximo_treino=proximo_treino,
        total_inscritos_proximo=total_inscritos_proximo,
        pendencias=treinos_pendentes
    )