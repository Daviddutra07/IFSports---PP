from datetime import datetime
from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.notificacoes import Notificacao
from sqlalchemy import or_

notificacoes_bp = Blueprint("notificacoes",__name__,url_prefix="/notificacoes",template_folder="templates/notificacoes")

@notificacoes_bp.route("/")
@login_required
def listar():
    notificacoes = (
        Notificacao.query
        .filter(
            Notificacao.not_usr_id == current_user.usr_id,
            db.or_(
                Notificacao.not_expira_em.is_(None),
                Notificacao.not_expira_em >= datetime.now()
            )
        )
        .order_by(Notificacao.not_lida.asc(), Notificacao.not_created_at.desc())
        .all()
    )

    return render_template("notificacoes/listar.html", notificacoes=notificacoes)


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
    notificacoes = Notificacao.query.filter_by(
        not_usr_id=current_user.usr_id,
        not_lida=False
    ).all()

    for notificacao in notificacoes:
        notificacao.not_lida = True

    db.session.commit()
    flash("Todas as notificações foram marcadas como lidas.", "success")
    return redirect(url_for("notificacoes.listar"))