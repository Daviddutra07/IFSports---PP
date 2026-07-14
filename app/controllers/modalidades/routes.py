from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from sqlalchemy import func
from app.controllers.modalidades.forms import ModalidadeForm
from app.decorators.auth import professor_required
from app.models.modalidades import Modalidade
from app.models.users import User
from app.models.treinos import Treino
from app.extensions import db

modalidades_bp = Blueprint(
    "modalidades",
    __name__,
    url_prefix="/modalidades",
    template_folder="templates/modalidades",
)


@modalidades_bp.route("/")
@login_required
def listar():

    modalidades = (
        db.session.query(
            Modalidade,
            func.count(User.usr_id).label("total_alunos")
        )
        .outerjoin(User,(User.usr_mod_id == Modalidade.mod_id)& (User.usr_tipo == "aluno"))
        .group_by(Modalidade.mod_id)
        .order_by(Modalidade.mod_nome)
        .all()
    )

    modalidades_bloqueadas = set()

    for modalidade, _ in modalidades:

        possui_usuario = User.query.filter_by(
            usr_mod_id=modalidade.mod_id
        ).first()

        possui_treino = Treino.query.filter_by(
            trn_mod_id=modalidade.mod_id
        ).first()

        if possui_usuario or possui_treino:
            modalidades_bloqueadas.add(modalidade.mod_id)

    return render_template(
        "modalidades/listar.html",
        modalidades=modalidades,
        modalidades_bloqueadas=modalidades_bloqueadas
    )


@modalidades_bp.route("/criar", methods=["GET", "POST"])
@professor_required
def criar():
    form = ModalidadeForm()

    if form.validate_on_submit():
        modalidade = Modalidade(
            mod_nome=form.mod_nome.data.strip()
        )

        db.session.add(modalidade)
        db.session.commit()

        flash("Modalidade criada com sucesso!", "success")
        return redirect(url_for("modalidades.listar"))

    return render_template(
        "modalidades/modalidades.html",
        form=form,
        titulo="Inserir Modalidade"
    )


@modalidades_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@professor_required
def editar(id):
    modalidade = Modalidade.query.get_or_404(id)

    form = ModalidadeForm(obj=modalidade)

    if form.validate_on_submit():
        modalidade.mod_nome = form.mod_nome.data.strip()

        db.session.commit()

        flash("Modalidade atualizada com sucesso!", "success")
        return redirect(url_for("modalidades.listar"))

    return render_template(
        "modalidades/modalidades.html",
        form=form,
        modalidade=modalidade,
        titulo="Editar Modalidade"
    )


@modalidades_bp.route("/excluir/<int:id>", methods=["POST"])
@professor_required
def excluir(id):
    modalidade = Modalidade.query.get_or_404(id)

    possui_usuarios = User.query.filter_by(
        usr_mod_id=id
    ).first()

    possui_treinos = Treino.query.filter_by(
        trn_mod_id=id
    ).first()

    if possui_usuarios or possui_treinos:
        flash(
            "Não é possível excluir esta modalidade, pois existem usuários ou treinos vinculados a ela.",
            "danger",
        )
        return redirect(url_for("modalidades.listar"))

    db.session.delete(modalidade)
    db.session.commit()

    flash("Modalidade excluída com sucesso!", "success")
    return redirect(url_for("modalidades.listar"))