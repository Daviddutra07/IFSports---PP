from app.extensions import db
from app.models.notificacoes import Notificacao
from app.models.users import User
from app.models.frequencia import Frequencia


def criar_notificacao_usuario(
    usuario_id,
    tipo,
    titulo,
    descricao=None,
    link=None,
    publico="usuario",
    referencia_id=None,
    referencia_tipo=None,
    expira_em=None,
    commit=True
):
    notificacao = Notificacao(
        not_usr_id=usuario_id,
        not_tipo=tipo,
        not_titulo=titulo,
        not_descricao=descricao,
        not_link=link,
        not_lida=False,
        not_publico=publico,
        not_referencia_id=referencia_id,
        not_referencia_tipo=referencia_tipo,
        not_expira_em=expira_em
    )

    db.session.add(notificacao)

    if commit:
        db.session.commit()

    return notificacao


def criar_notificacoes_usuarios(
    usuarios_ids,
    tipo,
    titulo,
    descricao=None,
    link=None,
    publico="usuario",
    referencia_id=None,
    referencia_tipo=None,
    expira_em=None,
    commit=True
):
    notificacoes = []

    usuarios_unicos = set(usuarios_ids)

    for usuario_id in usuarios_unicos:
        notificacao = Notificacao(
            not_usr_id=usuario_id,
            not_tipo=tipo,
            not_titulo=titulo,
            not_descricao=descricao,
            not_link=link,
            not_lida=False,
            not_publico=publico,
            not_referencia_id=referencia_id,
            not_referencia_tipo=referencia_tipo,
            not_expira_em=expira_em
        )
        db.session.add(notificacao)
        notificacoes.append(notificacao)

    if commit:
        db.session.commit()

    return notificacoes


def buscar_usuarios_modalidade(modalidade_id):
    if not modalidade_id:
        return []

    usuarios = User.query.filter_by(usr_tipo="aluno",usr_mod_id=modalidade_id,usr_is_active=True).all()

    return [usuario.usr_id for usuario in usuarios]


def buscar_usuarios_ocorrencia(ocorrencia_id):
    if not ocorrencia_id:
        return []
    frequencias = Frequencia.query.filter_by(frq_ocorrencia_id=ocorrencia_id,frq_status="inscricao").all()

    return list({frequencia.frq_aluno_id for frequencia in frequencias})


def buscar_usuarios_global():
    usuarios = User.query.filter_by(
        usr_is_active=True
    ).all()

    return [usuario.usr_id for usuario in usuarios]

def criar_notificacao_por_publico(
    publico,
    tipo,
    titulo,
    descricao=None,
    link=None,
    usuario_id=None,
    modalidade_id=None,
    ocorrencia_id=None,
    referencia_id=None,
    referencia_tipo=None,
    expira_em=None,
    commit=True
):
    usuarios_ids = []

    if publico == "usuario":
        if usuario_id:
            usuarios_ids = [usuario_id]

    elif publico == "modalidade":
        usuarios_ids = buscar_usuarios_modalidade(modalidade_id)

    elif publico == "treino":
        usuarios_ids = buscar_usuarios_ocorrencia(ocorrencia_id)

    elif publico == "global":
        usuarios_ids = buscar_usuarios_global()

    if not usuarios_ids:
        return []

    return criar_notificacoes_usuarios(
        usuarios_ids=usuarios_ids,
        tipo=tipo,
        titulo=titulo,
        descricao=descricao,
        link=link,
        publico=publico,
        referencia_id=referencia_id,
        referencia_tipo=referencia_tipo,
        expira_em=expira_em,
        commit=commit
    )