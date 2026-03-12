from datetime import datetime
from flask import Blueprint, abort, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from app.controllers.treinos.utils import calcular_primeira_data, calcular_proxima_data
from app.extensions import db, socketio
from app.models.treinos import Treino
from app.models.frequencia import Frequencia
from app.controllers.treinos.forms import TreinoCheckIn, TreinoExcluir, TreinoForm
from app.models.modalidades import Modalidade
from app.decorators.auth import professor_required

treinos_bp = Blueprint('treinos', __name__, url_prefix='/treinos', template_folder='templates/treinos')

def render_card_treino(treino):
    return render_template(
        "components/_card_treino.html",
        treino=treino,
        checkin_form=TreinoCheckIn(),
        excluir_form=TreinoExcluir(),
        user_tipo=current_user.usr_tipo
    )

@treinos_bp.route("/")
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    per_page = 6

    if current_user.usr_tipo == "professor":
        treinos_query = Treino.query.filter(Treino.trn_pro_id == current_user.usr_id,Treino.trn_ativo == True,Treino.trn_deleted_at.is_(None)).order_by(Treino.trn_data.desc())
        treinos_pag = treinos_query.paginate(page=page, per_page=per_page, error_out=False)
        excluir_form = TreinoExcluir()
        return render_template("treinos/listar.html", treinos=treinos_query,treinos_pag=treinos_pag,excluir_form=excluir_form)
    
    treinos_query = Treino.query.filter(Treino.trn_ativo == True,Treino.trn_deleted_at.is_(None)).order_by(Treino.trn_data.desc())
    treinos_pag = treinos_query.paginate(page=page, per_page=per_page, error_out=False)
    checkin_form = TreinoCheckIn()


    return render_template("treinos/listar.html",treinos=treinos_query,treinos_pag=treinos_pag,checkin_form=checkin_form)

@treinos_bp.route("/criar", methods=["GET", "POST"])
@professor_required
def criar():
    form = TreinoForm()

    modalidades = Modalidade.query.all()

    form.trn_mod_id.choices = [(m.mod_id, m.mod_nome) for m in modalidades]

    if form.validate_on_submit():
        if form.trn_fixo.data == True:
            primeira_data = calcular_primeira_data(form.trn_dia_semana.data, form.trn_horario.data)
            proxima_data = calcular_proxima_data(primeira_data)
            treino = Treino(trn_nome=form.trn_nome.data, trn_descricao=form.trn_descricao.data, trn_fixo=form.trn_fixo.data, trn_dia_semana=form.trn_dia_semana.data, trn_horario=form.trn_horario.data, trn_data=primeira_data, trn_proxima_data = proxima_data, trn_pro_id=current_user.usr_id, trn_quantidade=form.trn_quantidade.data, trn_mod_id=form.trn_mod_id.data)
        else: 
            data_avulsa = form.trn_data.data

            treino = Treino(trn_nome=form.trn_nome.data, trn_descricao=form.trn_descricao.data, trn_fixo=form.trn_fixo.data, trn_data=data_avulsa, trn_pro_id=current_user.usr_id, trn_quantidade=form.trn_quantidade.data, trn_mod_id=form.trn_mod_id.data)

        db.session.add(treino)
        db.session.commit()

        socketio.emit("atualizar_treinos", room="alunos")

        flash("Treino criado com sucesso!", "success")
        return redirect(url_for("treinos.listar"))

    return render_template("treinos/createupdate.html", form=form, url_action=url_for("treinos.criar"), acao="Criar")    

@treinos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@professor_required
def editar(id):
    treino = Treino.query.get_or_404(id)
    form = TreinoForm(obj=treino)

    modalidades = Modalidade.query.all()
    form.trn_mod_id.choices = [(m.mod_id, m.mod_nome) for m in modalidades]

    total_checkins = treino.trn_vagas_ocupadas

    data_antiga = treino.trn_data

    if form.validate_on_submit():
        form.populate_obj(treino)

        if treino.trn_fixo:
            primeira_data = calcular_primeira_data(
                form.trn_dia_semana.data,
                form.trn_horario.data
            )
            treino.trn_data = primeira_data
            treino.trn_proxima_data = calcular_proxima_data(primeira_data)
        else:
            treino.trn_data = form.trn_data.data
            treino.trn_proxima_data = None
            treino.trn_dia_semana = None
            treino.trn_horario = None

        nova_data = treino.trn_data


        if form.trn_quantidade.data < total_checkins:
            flash("Ops! O número de check-ins já registrados é maior que a quantidade de vagas, impossível editar. Se necessário, apague o treino", "warning")
            db.session.rollback()
            return redirect(url_for("treinos.editar", id=id))
        
        if data_antiga.date() == nova_data.date() and data_antiga.time() != nova_data.time():
            # mudou só o horário ele atualiza
            Frequencia.query.filter_by(frq_treino_id=treino.trn_id, frq_data_ocorrencia=data_antiga).update({"frq_data_ocorrencia": nova_data})

        elif data_antiga.date() != nova_data.date():
            Frequencia.query.filter_by(frq_treino_id=treino.trn_id, frq_data_ocorrencia=data_antiga).delete()
            treino.trn_vagas_ocupadas = 0
            flash("A data do treino foi alterada. Todos os check-ins foram removidos.", "warning")

        db.session.commit()
        flash("Treino editado com sucesso!", "success")

        # Emite o card atualizado para todos os alunos
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
        flash(f"Não foi possível remover este treino: {str(e)}", "error")
        db.session.rollback()

    return redirect(url_for("treinos.listar"))


@treinos_bp.route("/<int:id>/checkin", methods=["POST"])
@login_required
def checkin(id):
    treino =  (Treino.query.filter_by(trn_id=id).with_for_update().first_or_404())
    agora = datetime.now()

    data_ocorrencia = treino.trn_data

    if current_user.usr_tipo != "aluno":
        flash(" Apenas alunos podem realizar check-in.", "error")
        return redirect(url_for("treinos.listar"))
    
    if agora > treino.trn_data:
        flash("Não é possível fazer check-in em um treino depois de passar a data e horário", "error")
        return redirect(url_for("treinos.listar")) 

    if treino.trn_vagas_ocupadas >= treino.trn_quantidade: 
        flash("Treino lotado.", "error") 
        return redirect(url_for("treinos.listar")) 
    
    existente = Frequencia.query.filter_by(
        frq_aluno_id=current_user.usr_id,
        frq_treino_id=treino.trn_id,
        frq_data_ocorrencia=data_ocorrencia
    ).first()

    if existente:
        flash(" Você já realizou check-in neste treino.", "warning")
        return redirect(url_for("treinos.listar"))
    
    if not treino.trn_ativo:
        flash("Este treino não está mais ativo.", "error")
        return redirect(url_for("treinos.listar"))

    frequencia = Frequencia(frq_aluno_id=current_user.usr_id, frq_treino_id=treino.trn_id, frq_data_ocorrencia=data_ocorrencia,frq_status="checkin")

    db.session.add(frequencia)
    treino.trn_vagas_ocupadas += 1
    db.session.commit()

    flash("Check-in realizado com sucesso!", "success")
    #Atualiza a página principal de treinos quando algúém faz check-in
    socketio.emit("atualizar_treinos", room="alunos")
    #Atualiza a tabela de alunos participantes do treino quando você estiver na página de detalhes dele
    room = f"treino_{treino.trn_id}"
    socketio.emit("novo_checkin",{"treino_id": treino.trn_id, "aluno_id": current_user.usr_id, "aluno": current_user.usr_nome, "horario": frequencia.frq_checkin_em.strftime("%H:%M"), "status": frequencia.frq_status},room=room)

    return redirect(url_for("treinos.listar"))

@treinos_bp.route("/<int:id>/cancelar_checkin", methods=["POST"])
@login_required
def cancelar_checkin(id):
    treino = Treino.query.get_or_404(id)
    data_ocorrencia = treino.trn_data

    frequencia = Frequencia.query.filter_by(
        frq_aluno_id=current_user.usr_id,
        frq_treino_id=treino.trn_id,
        frq_data_ocorrencia=data_ocorrencia
    ).first()

    if not frequencia:
        flash("Você não possui check-in neste treino.", "info")
        return redirect(url_for("treinos.listar"))
    
    if datetime.now() > treino.trn_data:
        flash("Você não pode retirar o check-in em um treino que já ocorreu ou está ocorrendo.", "warning")
        return redirect(url_for("treinos.listar"))

    db.session.delete(frequencia)
    treino.trn_vagas_ocupadas -= 1
    db.session.commit()

    flash("Check-in cancelado com sucesso!", "success")
    socketio.emit("atualizar_treinos", room="alunos")

    room = f"treino_{treino.trn_id}"
    socketio.emit("checkin_cancelado", {"treino_id": treino.trn_id, "aluno_id": current_user.usr_id},room=room)

    return redirect(url_for("treinos.listar"))

@treinos_bp.route('/detalhes/<int:treino_id>/validar', methods=["POST"])
@professor_required
def validar_frequencias(treino_id):
    agora = datetime.now()

    treino = Treino.query.get_or_404(treino_id)

    ja_validado = Frequencia.treino_ja_validado(treino_id, treino.trn_data)

    if ja_validado:
        flash("Este treino já foi validado.", "warning")
        return redirect(url_for("treinos.detalhes", id=treino_id))

    if treino.trn_pro_id != current_user.usr_id:
        flash("Você não pode validar este treino.", "error")
        return redirect(url_for("treinos.detalhes", id=treino_id))
    
    if agora < treino.trn_data:
        flash("Você só poder validar um treino após chegar o horário e data dele.", "info")
        return redirect(url_for("treinos.detalhes", id=treino_id))

    alunos = Frequencia.query.filter_by(frq_treino_id=treino_id, frq_data_ocorrencia=treino.trn_data).all()

    if not alunos:
        flash("Não há participantes para validar.", "warning")
        return redirect(url_for("treinos.detalhes", id=treino_id))

    for frequencia in alunos:
        status = "presente" if f"status_{frequencia.frq_id}" in request.form else "ausente"
        frequencia.frq_status = status
        frequencia.frq_validado_em = datetime.now()
        db.session.add(frequencia)

    if treino.trn_fixo:
        treino.trn_data = treino.trn_proxima_data
        treino.trn_proxima_data = calcular_proxima_data(treino.trn_data)
        treino.trn_vagas_ocupadas = 0

    else: 
        treino.trn_ativo = 0

    db.session.commit()
    flash("Frequências validadas com sucesso!", "success")

    socketio.emit("atualizar_treinos", room="alunos")

    return redirect(url_for("treinos.detalhes", id=treino_id))


@treinos_bp.route('/detalhes/<int:id>', methods=["GET"])
@login_required
def detalhes(id):
    treino = Treino.query.get_or_404(id)

    alunos = Frequencia.query.filter_by(frq_treino_id=id, frq_data_ocorrencia=treino.trn_data).all()

    ja_validado = Frequencia.treino_ja_validado(id, treino.trn_data)

    return render_template("treinos/detalhes.html", treino=treino, alunos=alunos, ja_validado=ja_validado)

