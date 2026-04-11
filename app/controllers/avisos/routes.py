from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app.extensions import db
from app.decorators.auth import professor_required
from app.models.avisos import Aviso
from app.models.modalidades import Modalidade
from app.models.treino_ocorrencia import TreinoOcorrencia
from app.models.treinos import Treino
from app.models.frequencia import Frequencia
from app.controllers.avisos.forms import AvisoForm
from app.services.notificacao_service import criar_notificacao_por_publico

avisos_bp = Blueprint("avisos",__name__,url_prefix="/avisos",template_folder="templates")

def encher_select(form):
    modalidades = Modalidade.query.order_by(Modalidade.mod_nome.asc()).all()
    treinos = Treino.query.filter(Treino.trn_ativo.is_(True), Treino.trn_deleted_at.is_(None)).order_by(Treino.trn_created_at.desc()).all()

    form.avs_modalidade_id.choices = [(0, "Todas / Global")] + [(m.mod_id, m.mod_nome) for m in modalidades]

    form.avs_treino_id.choices = [(0, "Nenhum treino específico")] + [
    (
        t.trn_id,
        f"{t.trn_nome} - {t.data_exibicao.strftime('%d/%m/%Y %H:%M')}"
        if t.data_exibicao else t.trn_nome
    ) for t in treinos]
    
@avisos_bp.route("/")
@login_required
def listar():
    agora = datetime.now()

    if current_user.usr_tipo == "professor":
        avisos = (Aviso.query.filter(Aviso.avs_ativo == True).order_by(Aviso.avs_fixado.desc(), Aviso.avs_created_at.desc()).all())
    else:
        filtros_visibilidade = [
            and_(
                Aviso.avs_modalidade_id.is_(None),
                Aviso.avs_treino_id.is_(None)
            )
        ]

        if current_user.usr_mod_id:
            filtros_visibilidade.append(Aviso.avs_modalidade_id == current_user.usr_mod_id)

        treinos_ids = []

        frequencias = Frequencia.query.filter_by(frq_aluno_id=current_user.usr_id).all()

        for freq in frequencias:
            treino = freq.treino

            if not treino:
                continue
            
            if not treino.trn_fixo:
                treinos_ids.append(treino.trn_id)
                continue
            
            ocorrencia_atual = treino.ocorrencia_aberta

            if (
                ocorrencia_atual
                and freq.frq_ocorrencia_id == ocorrencia_atual.tro_id
            ):
                treinos_ids.append(treino.trn_id)

        treinos_ids = list(set(treinos_ids))

        if treinos_ids:
            filtros_visibilidade.append(Aviso.avs_treino_id.in_(treinos_ids))

        avisos = (Aviso.query.filter(Aviso.avs_ativo == True,
                or_(Aviso.avs_expira_em.is_(None),Aviso.avs_expira_em >= agora),
                or_(*filtros_visibilidade)
            ).order_by(Aviso.avs_fixado.desc(), Aviso.avs_created_at.desc()).all())

    return render_template("avisos/listar.html", avisos=avisos)

@avisos_bp.route("/criar", methods=["GET", "POST"])
@professor_required
def criar():
    form = AvisoForm()
    encher_select(form)

    if form.validate_on_submit():
        modalidade_id = form.avs_modalidade_id.data if form.avs_modalidade_id.data != 0 else None
        treino_id = form.avs_treino_id.data if form.avs_treino_id.data != 0 else None

        aviso = Aviso(
            avs_titulo=form.avs_titulo.data,
            avs_mensagem=form.avs_mensagem.data,
            avs_modalidade_id=modalidade_id,
            avs_treino_id=treino_id,
            avs_fixado=form.avs_fixado.data,
            avs_expira_em=form.avs_expira_em.data,
            avs_autor_id=current_user.usr_id
        )

        db.session.add(aviso)
        db.session.commit()

        if aviso.avs_treino_id:
            criar_notificacao_por_publico(
                publico="treino",
                tipo="aviso",
                titulo=f"Novo Aviso - {aviso.avs_titulo}",
                descricao=aviso.avs_mensagem,
                link=url_for("avisos.listar"),
                ocorrencia_id=aviso.treino.ocorrencia_aberta.tro_id if aviso.treino and aviso.treino.ocorrencia_aberta else None,
                referencia_id=aviso.avs_id,
                referencia_tipo="aviso",
                expira_em=aviso.avs_expira_em + time
            )

        elif aviso.avs_modalidade_id:
            criar_notificacao_por_publico(
                publico="modalidade",
                tipo="aviso",
                titulo=aviso.avs_titulo,
                descricao=aviso.avs_mensagem,
                link=url_for("avisos.listar"),
                modalidade_id=aviso.avs_modalidade_id,
                referencia_id=aviso.avs_id,
                referencia_tipo="aviso",
                expira_em=aviso.avs_expira_em
            )

        else:
            criar_notificacao_por_publico(
                publico="global",
                tipo="aviso",
                titulo=aviso.avs_titulo,
                descricao=aviso.avs_mensagem,
                link=url_for("avisos.listar"),
                referencia_id=aviso.avs_id,
                referencia_tipo="aviso",
                expira_em=aviso.avs_expira_em
            )

        flash("Aviso criado com sucesso.", "success")
        return redirect(url_for("avisos.listar"))

    return render_template("avisos/form.html", form=form, titulo="Criar Aviso")

@avisos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@professor_required
def editar(id):
    aviso = Aviso.query.get_or_404(id)
    form = AvisoForm(obj=aviso)
    encher_select(form)

    if request.method == "GET":
        form.avs_modalidade_id.data = aviso.avs_modalidade_id or 0
        form.avs_treino_id.data = aviso.avs_treino_id or 0

    if form.validate_on_submit():
        aviso.avs_titulo = form.avs_titulo.data
        aviso.avs_mensagem = form.avs_mensagem.data
        aviso.avs_modalidade_id = form.avs_modalidade_id.data if form.avs_modalidade_id.data != 0 else None
        aviso.avs_treino_id = form.avs_treino_id.data if form.avs_treino_id.data != 0 else None
        aviso.avs_fixado = form.avs_fixado.data
        aviso.avs_expira_em = form.avs_expira_em.data

        db.session.commit()

        flash("Aviso atualizado com sucesso.", "success")
        return redirect(url_for("avisos.listar"))

    return render_template("avisos/form.html", form=form, titulo="Editar Aviso")

@avisos_bp.route("/excluir/<int:id>", methods=["POST"])
@professor_required
def excluir(id):
    aviso = Aviso.query.get_or_404(id)
    aviso.avs_ativo = False

    db.session.commit()

    flash("Aviso removido com sucesso.", "success")
    return redirect(url_for("avisos.listar"))