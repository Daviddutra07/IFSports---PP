from datetime import datetime
from flask import Blueprint, abort, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from app.controllers.treinos.utils import calcular_primeira_data, calcular_proxima_data, obter_ocorrencia_aberta
from app.extensions import db, socketio
from app.models.treinos import Treino
from app.models.frequencia import Frequencia
from app.models.treino_ocorrencia import TreinoOcorrencia
from app.controllers.treinos.forms import TreinoCheckIn, TreinoExcluir, TreinoForm
from app.models.modalidades import Modalidade
from app.decorators.auth import professor_required
from app.services.gamification_service import adicionar_pontos, remover_pontos, verificar_conquistas

treinos_bp = Blueprint('treinos', __name__, url_prefix='/treinos', template_folder='templates/treinos')

@treinos_bp.route("/")
@login_required
def listar():
    page = request.args.get("page", 1, type=int)
    per_page = 6

    query_base = (Treino.query.join(TreinoOcorrencia, TreinoOcorrencia.tro_treino_id == Treino.trn_id).filter(Treino.trn_ativo.is_(True),Treino.trn_deleted_at.is_(None),TreinoOcorrencia.tro_ativo.is_(True),TreinoOcorrencia.tro_validado_em.is_(None)).order_by(TreinoOcorrencia.tro_data.desc()).distinct())

    if current_user.usr_tipo == "professor":
        query_base = query_base.filter(Treino.trn_pro_id == current_user.usr_id)
        treinos_pag = query_base.paginate(page=page, per_page=per_page, error_out=False)
        excluir_form = TreinoExcluir()

        return render_template("treinos/listar.html",treinos_pag=treinos_pag,excluir_form=excluir_form)

    treinos_pag = query_base.paginate(page=page, per_page=per_page, error_out=False)
    checkin_form = TreinoCheckIn()

    return render_template("treinos/listar.html",treinos_pag=treinos_pag,checkin_form=checkin_form)

@treinos_bp.route("/criar", methods=["GET", "POST"])
@professor_required
def criar():
    form = TreinoForm()
    modalidades = Modalidade.query.all()
    form.trn_mod_id.choices = [(m.mod_id, m.mod_nome) for m in modalidades]

    if form.validate_on_submit():
        if form.trn_fixo.data:
            data_ocorrencia = calcular_primeira_data(form.trn_dia_semana.data,form.trn_horario.data)

            treino = Treino(trn_nome=form.trn_nome.data,trn_descricao=form.trn_descricao.data,trn_fixo=True,trn_dia_semana=form.trn_dia_semana.data,trn_horario=form.trn_horario.data,trn_pro_id=current_user.usr_id,trn_quantidade=form.trn_quantidade.data,trn_mod_id=form.trn_mod_id.data)
        else:
            data_ocorrencia = form.trn_data.data
            treino = Treino(trn_nome=form.trn_nome.data,trn_descricao=form.trn_descricao.data,trn_fixo=False,trn_dia_semana=None,trn_horario=None,trn_pro_id=current_user.usr_id,trn_quantidade=form.trn_quantidade.data,trn_mod_id=form.trn_mod_id.data)

        db.session.add(treino)
        db.session.flush()
        ocorrencia = TreinoOcorrencia(tro_treino_id=treino.trn_id,tro_data=data_ocorrencia)

        db.session.add(ocorrencia)
        db.session.commit()

        socketio.emit("atualizar_treinos", room="alunos")
        flash("Treino criado com sucesso!", "success")
        return redirect(url_for("treinos.listar"))

    return render_template("treinos/createupdate.html",form=form,url_action=url_for("treinos.criar"),acao="Criar") 

@treinos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@professor_required
def editar(id):
    treino = Treino.query.get_or_404(id)
    form = TreinoForm(obj=treino)

    modalidades = Modalidade.query.all()
    form.trn_mod_id.choices = [(m.mod_id, m.mod_nome) for m in modalidades]

    ocorrencia = obter_ocorrencia_aberta(treino.trn_id)

    if request.method == "GET":
        if not treino.trn_fixo and ocorrencia:
            form.trn_data.data = ocorrencia.tro_data

    if form.validate_on_submit():
        total_checkins = ocorrencia.tro_vagas_ocupadas if ocorrencia else 0

        if form.trn_quantidade.data < total_checkins:
            flash("Ops! O número de check-ins já registrados é maior que a quantidade de vagas, impossível editar.","warning")
            return redirect(url_for("treinos.editar", id=id))

        treino.trn_nome = form.trn_nome.data
        treino.trn_descricao = form.trn_descricao.data
        treino.trn_fixo = form.trn_fixo.data
        treino.trn_quantidade = form.trn_quantidade.data
        treino.trn_mod_id = form.trn_mod_id.data

        if treino.trn_fixo:
            treino.trn_dia_semana = form.trn_dia_semana.data
            treino.trn_horario = form.trn_horario.data
            nova_data = calcular_primeira_data(form.trn_dia_semana.data,form.trn_horario.data)
        else:
            treino.trn_dia_semana = None
            treino.trn_horario = None
            nova_data = form.trn_data.data

        if ocorrencia:
            data_antiga = ocorrencia.tro_data
            ocorrencia.tro_data = nova_data

            Frequencia.query.filter_by(frq_ocorrencia_id=ocorrencia.tro_id).update({"frq_data_ocorrencia": nova_data},synchronize_session=False)

            if data_antiga != nova_data:
                flash("A data da ocorrência aberta foi atualizada.", "info")

        db.session.commit()

        flash("Treino editado com sucesso!", "success")
        socketio.emit("atualizar_treinos", room="alunos")

        return redirect(url_for("treinos.listar"))

    return render_template("treinos/createupdate.html",form=form,acao="Editar",url_action=url_for("treinos.editar", id=id))

@treinos_bp.route('/deletar/<int:id>', methods=["POST"])
@professor_required
def remover(id):
    treino = Treino.query.get_or_404(id)
    if treino.trn_pro_id != current_user.usr_id:
        abort(404)  
    try:
        treino.trn_deleted_at = datetime.now()
        treino.trn_ativo = False
        db.session.commit()
        flash("Treino removido com sucesso!", "success")
        socketio.emit("atualizar_treinos", room="alunos")
    except Exception as e:
        flash(f"Não foi possível remover este treino", "error")
        db.session.rollback()

    return redirect(url_for("treinos.listar"))

@treinos_bp.route("/<int:id>/checkin", methods=["POST"])
@login_required
def checkin(id):
    treino = Treino.query.filter_by(trn_id=id).with_for_update().first_or_404()
    agora = datetime.now()

    if current_user.usr_tipo != "aluno":
        flash("Apenas alunos podem realizar inscrição.", "error")
        return redirect(url_for("treinos.listar"))

    if not treino.trn_ativo:
        flash("Este treino não está mais ativo.", "error")
        return redirect(url_for("treinos.listar"))

    ocorrencia = obter_ocorrencia_aberta(treino.trn_id)

    if not ocorrencia:
        flash("Não há ocorrência aberta para este treino.", "error")
        return redirect(url_for("treinos.listar"))

    if agora > ocorrencia.tro_data:
        flash("Não é possível fazer inscrição em um treino depois de passar a data e horário.", "error")
        return redirect(url_for("treinos.listar"))

    if ocorrencia.tro_vagas_ocupadas >= treino.trn_quantidade:
        flash("Treino lotado.", "error")
        return redirect(url_for("treinos.listar"))

    existente = Frequencia.query.filter_by(frq_aluno_id=current_user.usr_id,frq_treino_id=treino.trn_id,frq_ocorrencia_id=ocorrencia.tro_id).first()

    if existente:
        flash("Você já realizou sua inscrição neste treino.", "warning")
        return redirect(url_for("treinos.listar"))

    if treino.trn_fixo:
        frequencia = Frequencia(frq_aluno_id=current_user.usr_id,frq_treino_id=treino.trn_id,frq_ocorrencia_id=ocorrencia.tro_id,frq_data_ocorrencia=ocorrencia.tro_data,frq_status="inscricao",frq_trn_nome=treino.trn_nome,frq_mod_nome=treino.modalidade.mod_nome)
    else:
        frequencia = Frequencia(frq_aluno_id=current_user.usr_id,frq_treino_id=treino.trn_id,frq_ocorrencia_id=ocorrencia.tro_id,frq_data_ocorrencia=ocorrencia.tro_data,frq_status="inscricao")

    ocorrencia.tro_vagas_ocupadas += 1

    adicionar_pontos(current_user.usr_id, 5)

    db.session.add(frequencia)
    db.session.flush()      

    verificar_conquistas(current_user.usr_id)  

    db.session.commit()

    flash("Check-in realizado com sucesso!", "success")
    socketio.emit("atualizar_treinos", room="alunos")

    room = f"ocorrencia_{ocorrencia.tro_id}"
    socketio.emit("novo_checkin",{"ocorrencia_id": ocorrencia.tro_id, "treino_id": treino.trn_id, "aluno_id": current_user.usr_id, "aluno": current_user.usr_nome, "horario": frequencia.frq_reserva_em.strftime("%H:%M"), "status": frequencia.frq_status},room=room)

    return redirect(url_for("treinos.listar"))

@treinos_bp.route("/<int:id>/cancelar_checkin", methods=["POST"])
@login_required
def cancelar_checkin(id):
    treino = Treino.query.get_or_404(id)
    ocorrencia = obter_ocorrencia_aberta(treino.trn_id)

    if not ocorrencia:
        flash("Não há ocorrência aberta para este treino.", "warning")
        return redirect(url_for("treinos.listar"))

    frequencia = Frequencia.query.filter_by(
        frq_aluno_id=current_user.usr_id,
        frq_treino_id=treino.trn_id,
        frq_ocorrencia_id=ocorrencia.tro_id
    ).first()

    if not frequencia:
        flash("Você não possui inscrição neste treino.", "info")
        return redirect(url_for("treinos.listar"))

    if datetime.now() > ocorrencia.tro_data:
        flash("Você não pode retirar a inscrição em um treino que já ocorreu ou está ocorrendo.", "warning")
        return redirect(url_for("treinos.listar"))

    db.session.delete(frequencia)
    ocorrencia.tro_vagas_ocupadas -= 1
    remover_pontos(current_user.usr_id, 5)
    db.session.commit()

    flash("Inscrição cancelada com sucesso!", "success")
    socketio.emit("atualizar_treinos", room="alunos")

    room = f"ocorrencia_{ocorrencia.tro_id}"
    socketio.emit("checkin_cancelado",{"ocorrencia_id": ocorrencia.tro_id, "treino_id": treino.trn_id, "aluno_id": current_user.usr_id},room=room)

    return redirect(url_for("treinos.listar"))

@treinos_bp.route('/detalhes/<int:ocorrencia_id>/validar', methods=["GET", "POST"])
@professor_required
def validar_frequencias(ocorrencia_id):
    agora = datetime.now()

    ocorrencia = TreinoOcorrencia.query.get_or_404(ocorrencia_id)
    treino = ocorrencia.treino

    ja_validado = Frequencia.treino_ja_validado(ocorrencia.tro_id)

    alunos = Frequencia.query.filter_by(frq_ocorrencia_id=ocorrencia.tro_id).all()

    if treino.trn_pro_id != current_user.usr_id:
        flash("Você não pode validar este treino.", "error")
        return redirect(url_for("treinos.detalhes", ocorrencia_id=ocorrencia.tro_id))

    if request.method == "POST":
        if ja_validado:
            flash("Este treino já foi validado.", "warning")
            return redirect(url_for("treinos.detalhes", ocorrencia_id=ocorrencia.tro_id))

        if agora < ocorrencia.tro_data:
            flash("Você só pode validar após o treino.", "info")
            return redirect(url_for("treinos.detalhes", ocorrencia_id=ocorrencia.tro_id))

        if not alunos:
            ocorrencia.tro_ativo = False

            if treino.trn_fixo:
                nova_ocorrencia = TreinoOcorrencia(tro_treino_id=treino.trn_id,tro_data=calcular_proxima_data(ocorrencia.tro_data))
                db.session.add(nova_ocorrencia)
            else:
                treino.trn_ativo = False

            db.session.commit()
            flash("Não há participantes para validar.", "warning")
            return redirect(url_for("treinos.listar", ocorrencia_id=ocorrencia.tro_id))

        for frequencia in alunos:
            status = "presente" if f"status_{frequencia.frq_id}" in request.form else "ausente"
            frequencia.frq_status = status
            frequencia.frq_validado_em = datetime.now()

            nota = request.form.get(f"estrelas_{frequencia.frq_id}")
            if nota:
                frequencia.frq_aluno_nota = int(nota)

            if status == "presente":
                adicionar_pontos(frequencia.aluno.usr_id, 10 + (int(nota) if nota else 0))

            verificar_conquistas(frequencia.aluno.usr_id)

        ocorrencia.tro_validado_em = datetime.now()
        ocorrencia.tro_ativo = False

        if treino.trn_fixo:
            nova_ocorrencia = TreinoOcorrencia(tro_treino_id=treino.trn_id,tro_data=calcular_proxima_data(ocorrencia.tro_data))
            db.session.add(nova_ocorrencia)
        else:
            treino.trn_ativo = False

        db.session.commit()

        flash("Frequências validadas com sucesso!", "success")
        socketio.emit("atualizar_treinos", room="alunos")
        return redirect(url_for("treinos.detalhes", ocorrencia_id=ocorrencia.tro_id))

    return render_template("treinos/validar_frequencias.html",treino=treino,ocorrencia=ocorrencia,alunos=alunos,ja_validado=ja_validado)

@treinos_bp.route('/detalhes/<int:ocorrencia_id>', methods=["GET"])
@login_required
def detalhes(ocorrencia_id):
    ocorrencia = TreinoOcorrencia.query.get_or_404(ocorrencia_id)
    treino = ocorrencia.treino

    alunos = Frequencia.query.filter_by(frq_ocorrencia_id=ocorrencia.tro_id).all()

    ja_validado = Frequencia.treino_ja_validado(ocorrencia.tro_id)

    return render_template("treinos/detalhes.html",treino=treino,ocorrencia=ocorrencia,alunos=alunos,ja_validado=ja_validado)

