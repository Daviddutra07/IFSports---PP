from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.treinos import Treino
from app.models.frequencia import Frequencia
from app.controllers.treinos.forms import TreinoForm
from app.models.modalidades import Modalidade
from app.decorators.auth import professor_required

treinos_bp = Blueprint('treinos', __name__, url_prefix='/treinos', template_folder='templates/treinos')

@treinos_bp.route("/criar", methods=["GET", "POST"])
@professor_required
def criar():
    form = TreinoForm()

    modalidades = Modalidade.query.all()

    for m in modalidades:
        form.trn_mod_id.choices = [(m.mod_id, m.mod_nome) ]

    if form.validate_on_submit():
        treino = Treino(
            trn_nome=form.trn_nome.data,
            trn_descricao=form.trn_descricao.data,
            trn_fixo=form.trn_fixo.data,
            trn_dia_semana=form.trn_dia_semana.data if form.trn_fixo.data else None,
            trn_horario=form.trn_horario.data if form.trn_fixo.data else None,
            trn_data=form.trn_data.data if not form.trn_fixo.data else None,
            trn_pro_id=current_user.usr_id,
            trn_quantidade=form.trn_quantidade.data,
            trn_mod_id=form.trn_mod_id.data
        )

        db.session.add(treino)
        db.session.commit()

        flash("Treino criado com sucesso!", "success")
        return redirect(url_for("treinos.criar"))

    return render_template("treinos/criar.html", form=form)

@treinos_bp.route("/")
@login_required
def listar():
    if current_user.usr_tipo == "professor":
        treinos = Treino.query.filter_by(trn_pro_id=current_user.usr_id).all()
    else:
        treinos = Treino.query.all()

    return render_template("treino/listar.html", treinos=treinos)

@treinos_bp.route("/<int:treino_id>/checkin", methods=["POST"])
@login_required
def checkin(treino_id):
    if current_user.usr_tipo != "aluno":
        flash(" Apenas alunos podem realizar check-in.", "error")
        return redirect(url_for("treinos.listar"))

    treino = Treino.query.get_or_404(treino_id)
    agora = datetime.now(timezone.utc)

    if treino.trn_fixo:
        data_ocorrencia = agora.date()
    else:
        data_ocorrencia = treino.trn_data

    existente = Frequencia.query.filter_by(
        frq_aluno_id=current_user.usr_id,
        frq_treino_id=treino.trn_id,
        frq_data_ocorrencia=data_ocorrencia
    ).first()

    if existente:
        flash(" Você já realizou check-in neste treino.", "warning")
        return redirect(url_for("treinos.listar"))

    frequencia = Frequencia(
        frq_aluno_id=current_user.usr_id,
        frq_treino_id=treino.trn_id,
        frq_data_ocorrencia=data_ocorrencia,
        frq_status="checkin"
    )

    db.session.add(frequencia)
    db.session.commit()

    flash("Check-in realizado com sucesso!", "success")
    return redirect(url_for("treinos.listar"))

@treinos_bp.route("/frequencia/<int:frequencia_id>/validar/<string:status>", methods=["POST"])
@professor_required
def validar_frequencia(frequencia_id, status):
    if status not in ["presente", "ausente"]:
        flash(" Status inválido.", "error")
        return redirect(url_for("treinos.listar"))

    frequencia = Frequencia.query.get_or_404(frequencia_id)

    if frequencia.treino.trn_pro_id != current_user.usr_id:
        flash(" Você não pode validar este treino.", "error")
        return redirect(url_for("treinos.listar"))

    frequencia.frq_status = status
    frequencia.frq_validado_em = datetime.now(timezone.utc)

    db.session.commit()

    flash("Frequência validada com sucesso!", "success")
    return redirect(url_for("treinos.listar"))