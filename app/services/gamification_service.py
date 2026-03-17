from app.models.users import User
from app.models.frequencia import Frequencia
from app.extensions import db
from sqlalchemy import func
from app.models.conquistas import Conquista, UsuarioConquista
from app.extensions import db

TIER_CONFIG = {
    "normal": {
        "icone": "🔹", 
        "cor": "#b9e3f1",
        "borda": "#51c0e8",
        "tier_cor": "#424242"
    },
    "ativo": {
        "icone": "🔥", 
        "cor": "#e4b372",  
        "borda": "#f88d00",
        "tier_cor": "#424242"
    },

    "bronze": {
        "icone": "🥉",
        "cor": "#cd8032d4",
        "borda": "#8b5014ff",
        "texto": "#fff",
        "tier_cor": "#e8e8e8"
    },
    "prata": {
        "icone": "🥈",
        "cor": "#cdcdcd",
        "borda": "#a3a3a3",
        "tier_cor": "#424242"
    },
    "ouro": {
        "icone": "🥇",
        "cor": "#f5d017f1",
        "borda": "#daa520",
        "tier_cor": "#424242"
    },
    "lendária": {
        "icone": "🏆",
        "cor": "#4800c4d0",
        "borda": "#2c0079ff",
        "texto": "#fff",
        "tier_cor": "#e8e8e8"
    }
}

def adicionar_pontos(usuario_id, pontos):
    usuario = User.query.get(usuario_id)
    usuario.usr_pontos += pontos

def remover_pontos(usuario_id, pontos):
    usuario = User.query.get(usuario_id)
    usuario.usr_pontos -= pontos

def calcular_nivel(pontos):
    if pontos >= 1100:
        return 5, "Atleta Profissional"

    elif pontos >= 750:
        return 4, "Atleta de Alto Nível"

    elif pontos >= 450:
        return 3, "Atleta Competidor"

    elif pontos >= 200:
        return 2, "Atleta Dedicado"

    else:
        return 1, "Atleta Amador"

def calcular_media(usuario_id):
    media = db.session.query(func.avg(Frequencia.frq_aluno_nota))\
        .filter(Frequencia.frq_aluno_id == usuario_id)\
        .filter(Frequencia.frq_status == "presente")\
        .filter(Frequencia.frq_aluno_nota != None)\
        .scalar()

    return round(media, 2) if media else None

def verificar_conquistas(user_id):

    conquistas = Conquista.query.all()

    # presenças
    presencas = db.session.query(func.count(Frequencia.frq_id)).filter(
        Frequencia.frq_aluno_id == user_id,
        Frequencia.frq_status == "presente"
    ).scalar() or 0

    # inscrições
    inscricoes = db.session.query(func.count(Frequencia.frq_id)).filter(
        Frequencia.frq_aluno_id == user_id
    ).scalar() or 0

    # avaliações
    avaliacoes = db.session.query(
        func.count(Frequencia.frq_aluno_nota),
        func.avg(Frequencia.frq_aluno_nota)
    ).filter(
        Frequencia.frq_aluno_id == user_id,
        Frequencia.frq_aluno_nota != None
    ).first()

    total_avaliacoes = avaliacoes[0] or 0
    media_notas = float(avaliacoes[1] or 0)

    # nota perfeita (calculada uma vez)
    nota_perfeita = db.session.query(Frequencia.frq_id).filter(
        Frequencia.frq_aluno_id == user_id,
        Frequencia.frq_aluno_nota == 5
    ).first() is not None

    # pontos
    usuario = User.query.get(user_id)
    pontos = usuario.usr_pontos

    # ranking
    ranking = db.session.query(User.usr_id).order_by(User.usr_pontos.desc()).all()

    posicao = None
    for i, u in enumerate(ranking, start=1):
        if u.usr_id == user_id:
            posicao = i
            break

    for conquista in conquistas:

        desbloquear = False
        if conquista.cnq_tipo == "inscricao":
            if inscricoes >= conquista.cnq_meta:
                desbloquear = True

        elif conquista.cnq_tipo == "presenca":
            if presencas >= conquista.cnq_meta:
                desbloquear = True


        elif conquista.cnq_tipo == "primeira_avaliacao":
            if total_avaliacoes >= 1:
                desbloquear = True

        elif conquista.cnq_tipo == "nota_perfeita":
            if nota_perfeita:
                desbloquear = True

        elif conquista.cnq_tipo == "media":
            if total_avaliacoes >= 3 and media_notas >= conquista.cnq_meta:
                desbloquear = True

        elif conquista.cnq_tipo == "pontos":
            if pontos >= conquista.cnq_meta:
                desbloquear = True

        elif conquista.cnq_tipo == "ranking":
            if posicao and posicao <= conquista.cnq_meta:
                desbloquear = True

        if desbloquear:
            conceder_conquista(user_id, conquista)

def conceder_conquista(user_id, conquista):

    existe = UsuarioConquista.query.filter_by(
        usc_usr_id=user_id,
        usc_cnq_id=conquista.cnq_id
    ).first()

    if existe:
        return False

    nova = UsuarioConquista(
        usc_usr_id=user_id,
        usc_cnq_id=conquista.cnq_id
    )

    db.session.add(nova)

    # bônus da conquista
    usuario = User.query.get(user_id)
    usuario.usr_pontos += conquista.cnq_pontos_bonus

    return True