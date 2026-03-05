from flask import Blueprint, flash, redirect, render_template, url_for
from app.controllers.modalidades.forms import ModalidadeForm
from app.decorators.auth import professor_required
from app.models.modalidades import Modalidade
from app.extensions import db

modalidades_bp = Blueprint('modalidades', __name__, url_prefix='/modalidades', template_folder='templates/modalidades')

@modalidades_bp.route("/criar", methods=["GET", "POST"])
@professor_required
def criar():
    form = ModalidadeForm()

    if form.validate_on_submit():
        modalidade = Modalidade(
            mod_nome=form.mod_nome.data,
        )

        db.session.add(modalidade)
        db.session.commit()

        flash("Modalidade criada com sucesso!", "success")
        return redirect(url_for("treinos.listar"))

    return render_template("modalidades/modalidades.html", form=form)