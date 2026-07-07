import os
import uuid
from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from app.extensions import db
from werkzeug.utils import secure_filename
from app.controllers.mural.forms import FormEditarFoto, FormFotos
from app.decorators.auth import professor_required
from app.models.mural_fotos import MuralFotos

mural_bp = Blueprint('mural', __name__, url_prefix='/mural', template_folder='templates/mural')

@mural_bp.route("/")
@login_required
def mural():
    fotos = (
        MuralFotos.query
        .order_by(MuralFotos.mft_created_at.desc())
        .all()
    )

    return render_template(
        "mural/listar.html",
        fotos=fotos
    )

@mural_bp.route("/adicionar_foto", methods=["GET", "POST"])
@professor_required
def adicionar_foto():
    form = FormFotos()

    if form.validate_on_submit():

        file = form.imagem.data

        filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{filename}"

        path = os.path.join(
            current_app.config["UPLOADED_IMAGES_DEST"],
            "mural",
            filename
        )

        os.makedirs(
            os.path.dirname(path),
            exist_ok=True
        )

        file.save(path)

        foto = MuralFotos(
            mft_img_id=f"uploads/images/mural/{filename}",
            mft_legenda=form.legenda.data,
            mft_usr_id=current_user.usr_id
        )

        db.session.add(foto)
        db.session.commit()

        flash("Foto adicionada ao mural com sucesso!", "success")
        return redirect(url_for("home.index"))

    return render_template("mural/adicionar.html", form=form)

@mural_bp.route("/editar/<int:foto_id>", methods=["GET", "POST"])
@professor_required
def editar_foto(foto_id):
    foto = MuralFotos.query.get_or_404(foto_id)

    form = FormEditarFoto(obj=foto)

    if form.validate_on_submit():
        foto.mft_legenda = form.legenda.data

        db.session.commit()

        flash("Legenda atualizada com sucesso!", "success")
        return redirect(url_for("mural.mural"))

    return render_template(
        "mural/editar.html",
        form=form,
        foto=foto
    )

@mural_bp.route("/excluir/<int:foto_id>", methods=["POST"])
@professor_required
def excluir_foto(foto_id):
    foto = MuralFotos.query.get_or_404(foto_id)

    caminho = os.path.join(
        current_app.static_folder,
        foto.mft_img_id
    )

    try:
        if os.path.exists(caminho):
            os.remove(caminho)
    except OSError:
        flash("Não foi possível remover o arquivo da imagem.", "warning")

    db.session.delete(foto)
    db.session.commit()

    flash("Foto removida do mural com sucesso!", "success")
    return redirect(url_for("mural.mural"))