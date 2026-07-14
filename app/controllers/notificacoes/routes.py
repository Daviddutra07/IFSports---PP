from datetime import datetime
from flask import Blueprint, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.notificacoes import Notificacao

notificacoes_bp = Blueprint("notificacoes",__name__,url_prefix="/notificacoes",template_folder="templates/notificacoes")

def buscar_notificacoes_ativas(usuario_id, limite=None):
    query = (
        Notificacao.query
        .filter(
            Notificacao.not_usr_id == usuario_id,
            db.or_(
                Notificacao.not_expira_em.is_(None),
                Notificacao.not_expira_em >= datetime.now()
            )
        )
        .order_by(Notificacao.not_lida.asc(), Notificacao.not_created_at.desc())
    )

    if limite:
        query = query.limit(limite)
    return query.all()

@notificacoes_bp.route("/")
@login_required
def listar():
    notificacoes = buscar_notificacoes_ativas(current_user.usr_id)

    return render_template("notificacoes/listar.html",notificacoes=notificacoes)

@notificacoes_bp.route("/dropdown")
@login_required
def dropdown():
    notificacoes = buscar_notificacoes_ativas(current_user.usr_id, limite=5)

    resultado = []
    for notificacao in notificacoes:
        resultado.append({
            "id": notificacao.not_id,
            "titulo": notificacao.not_titulo,
            "descricao": notificacao.not_descricao,
            "data": notificacao.not_created_at.strftime("%d/%m/%Y às %H:%M"),
            "lida": notificacao.not_lida,
            "link": notificacao.not_link
        })

    return jsonify({"notificacoes": resultado})


@notificacoes_bp.route("/<int:id>/ler", methods=["POST"])
@login_required
def marcar_como_lida(id):
    notificacao = Notificacao.query.get_or_404(id)

    if notificacao.not_usr_id != current_user.usr_id:
        return jsonify({"erro": "Acesso negado"}), 403

    notificacao.not_lida = True
    db.session.commit()

    return jsonify({"sucesso": True})


@notificacoes_bp.route("/ler_todas", methods=["POST"])
@login_required
def marcar_todas_como_lidas():
    notificacoes = (
        Notificacao.query
        .filter_by(
            not_usr_id=current_user.usr_id,
            not_lida=False
        )
        .all()
    )

    for notificacao in notificacoes:
        notificacao.not_lida = True

    db.session.commit()
    flash("Todas as notificações foram marcadas como lidas.", "success")
    return redirect(url_for("notificacoes.listar"))