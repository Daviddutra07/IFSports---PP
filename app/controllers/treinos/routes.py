from datetime import datetime, timezone
from flask import Blueprint, abort, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.treinos import Treino
from app.models.frequencia import Frequencia
from app.controllers.treinos.forms import TreinoCheckIn, TreinoExcluir, TreinoForm
from app.models.modalidades import Modalidade
from app.decorators.auth import professor_required

treinos_bp = Blueprint('treinos', __name__, url_prefix='/treinos', template_folder='templates/treinos')

@treinos_bp.route("/criar", methods=["GET", "POST"])
@professor_required
def criar():
    form = TreinoForm()

    modalidades = Modalidade.query.all()

    form.trn_mod_id.choices = [(m.mod_id, m.mod_nome) for m in modalidades]


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
        return redirect(url_for("treinos.listar"))

    return render_template("treinos/createupdate.html", form=form, url_action=url_for("treinos.criar"), acao="Criar")

@treinos_bp.route("/")
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    per_page = 6

    if current_user.usr_tipo == "professor":
        treinos = Treino.query.filter_by(trn_pro_id=current_user.usr_id)
        treinos_pag = treinos.paginate(page=page, per_page=per_page, error_out=False)
        excluir_form = TreinoExcluir()
        return render_template("treinos/listar.html", treinos=treinos, excluir_form=excluir_form, treinos_pag=treinos_pag)
    else:
        treinos = Treino.query
        checkin_form = TreinoCheckIn()
        treinos_pag = treinos.paginate(page=page, per_page=per_page, error_out=False)
        return render_template("treinos/listar.html", treinos=treinos, checkin_form=checkin_form, treinos_pag=treinos_pag)

@treinos_bp.route("/<int:id>/checkin", methods=["POST"])
@login_required
def checkin(id):
    if current_user.usr_tipo != "aluno":
        flash(" Apenas alunos podem realizar check-in.", "error")
        return redirect(url_for("treinos.listar"))

    treino = Treino.query.get_or_404(id)
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

@treinos_bp.route("/editar/<int:id>", methods = ["GET", "POST"])
@professor_required
def editar(id):
    treino = Treino.query.get_or_404(id)
    form = TreinoForm(obj=treino)

    modalidades = Modalidade.query.all()

    form.trn_mod_id.choices = [(m.mod_id, m.mod_nome) for m in modalidades]

    if not treino:
        flash("Item não encontrado!", "error")
        return redirect(url_for("item.itens"))

    if form.validate_on_submit():
        treino.trn_nome=form.trn_nome.data,
        treino.trn_descricao=form.trn_descricao.data,
        treino.trn_fixo = bool(form.trn_fixo.data)
        treino.trn_dia_semana=form.trn_dia_semana.data if form.trn_fixo.data else None,
        treino.trn_horario=form.trn_horario.data if form.trn_fixo.data else None,
        treino.trn_data=form.trn_data.data if not form.trn_fixo.data else None,
        treino.trn_pro_id=current_user.usr_id,
        treino.trn_quantidade=form.trn_quantidade.data,
        treino.trn_mod_id=form.trn_mod_id.data

        db.session.commit()

        flash("Treino editado com sucesso!", "success")
        return redirect(url_for("treinos.listar"))

    return render_template("treinos/createupdate.html", form=form, acao="Editar", url_action=url_for("treinos.editar", id=id))

@treinos_bp.route('/deletar/<int:id>', methods=["POST"])
@professor_required
def remover(id):
    treino = Treino.query.get_or_404(id)
    if treino.trn_pro_id != current_user.usr_id:
        abort(404)  
    try:
        db.session.delete(treino)
        db.session.commit()
        flash("Treino removido com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Não foi possível remover este treino: {str(e)}", "error")

    return redirect(url_for("treinos.listar"))