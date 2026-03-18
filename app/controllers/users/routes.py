from flask import Blueprint, abort, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from app.models.conquistas import UsuarioConquista, Conquista
from app.models.frequencia import Frequencia
from app.models.modalidades import Modalidade
from app.models.treinos import Treino
from app.models.users import User
from app.services.gamification_service import TIER_CONFIG, calcular_nivel, calcular_media
from app.controllers.users.forms import FormAluno, FormEditarAluno, FormEditarProfessor, FormProfessor
from app.extensions import db
from werkzeug.utils import secure_filename
import uuid
import os
from flask import current_app
from datetime import datetime
from sqlalchemy.orm import joinedload

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios', template_folder='templates/users')
@usuarios_bp.route("/<int:id>")
@login_required
def perfil(id):
    user = User.query.get_or_404(id)
    media = calcular_media(user.usr_id)
    if user.usr_tipo == "aluno":
        aluno = True
        nivel, nome = calcular_nivel(user.usr_pontos)
        conquistas = (UsuarioConquista.query.filter_by(usc_usr_id=id).order_by(UsuarioConquista.usc_registered_at.desc()).all())
        conquistas_exibicao = conquistas[:3] #Pegando só 3 para exibir
        total_conquistas = len(conquistas)

        agora = datetime.now()
        treinos = (
            Frequencia.query.options(
                joinedload(Frequencia.treino).joinedload(Treino.modalidade),
                joinedload(Frequencia.ocorrencia)
            )
            .filter(
                Frequencia.frq_aluno_id == id,
                Frequencia.frq_status == "presente",
                Frequencia.frq_data_ocorrencia < agora
            )
            .order_by(Frequencia.frq_data_ocorrencia.desc())
            .limit(3)
            .all()
        )        

        
        return render_template("users/perfil.html",user=user,conquistas=conquistas_exibicao, tier_config=TIER_CONFIG, nivel=nivel, total_conquistas=total_conquistas, aluno=aluno, treinos=treinos, media=media, nome=nome)
    return render_template("users/perfil.html",user=user)

@login_required
@usuarios_bp.route("/concluir", methods=["GET", "POST"])
def concluir():
    user = current_user

    if user.usr_primeiro_login == False:
        flash("Você já concluiu o seu perfil", "error")
        return redirect(url_for("treinos.listar"))

    if user.usr_tipo == "professor":
        form = FormProfessor()
    else:
        form = FormAluno()
        modalidades = Modalidade.query.all()
        form.modalidade.choices = [(m.mod_id, m.mod_nome) for m in modalidades]

    if form.validate_on_submit():
        if form.imagem.data:
            file = form.imagem.data
            filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}_{filename}"
            path = os.path.join(current_app.config["UPLOADED_IMAGES_DEST"], "perfis", filename)
            file.save(path)
            user.usr_img = f"uploads/images/perfis/{filename}"

        if user.usr_tipo == "aluno":
            user.usr_mod_id = form.modalidade.data
        user.usr_primeiro_login = False
        db.session.commit()
        flash("Perfil concluído com sucesso!", "success")
        return redirect(url_for("usuarios.perfil", id=user.usr_id))

    return render_template("users/confirmaruser.html", form=form, tipo=user.usr_tipo)

@usuarios_bp.route("/conquistas/<int:id>")
@login_required
def conquistas(id):
    user = User.query.get_or_404(id)
    total_cnq_usr = UsuarioConquista.query.filter_by(usc_usr_id=id).count()
    total_cnq = Conquista.query.count()
    conquistas_exibicao = (UsuarioConquista.query.join(Conquista, UsuarioConquista.usc_cnq_id == Conquista.cnq_id).filter(UsuarioConquista.usc_usr_id == id).order_by(Conquista.cnq_tier_valor.desc()).all())
    conquistas_disponiveis = (Conquista.query.outerjoin(UsuarioConquista, (UsuarioConquista.usc_cnq_id == Conquista.cnq_id) & (UsuarioConquista.usc_usr_id == id)).filter(UsuarioConquista.usc_id.is_(None)).all())
    return render_template("users/conquistas.html", user=user, total_cnq_usr=total_cnq_usr, total_cnq=total_cnq, conquistas=conquistas_exibicao, conquistas_disponiveis=conquistas_disponiveis, tier_config=TIER_CONFIG)

@usuarios_bp.route("/historico/<int:id>")
@login_required
def historico(id):
    user = User.query.get_or_404(id)

    page = request.args.get("page", 1, type=int)
    per_page = 6

    paginacao = (
        Frequencia.query
        .options(
            joinedload(Frequencia.treino).joinedload(Treino.modalidade),
            joinedload(Frequencia.ocorrencia)
        )
        .filter(
            Frequencia.frq_aluno_id == id,
            Frequencia.frq_status != "inscricao"
        )
        .order_by(Frequencia.frq_data_ocorrencia.desc())
        .paginate(page=page, per_page=per_page)
    )

    return render_template(
        "users/historico.html",
        user=user,
        treinos=paginacao.items,
        paginacao=paginacao
    )

@usuarios_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    user = User.query.get_or_404(id)

    if user.usr_id != current_user.usr_id:
        abort(403)

    if user.usr_tipo == "aluno":
        form = FormEditarAluno(obj=user)

        modalidades = Modalidade.query.all()
        form.modalidade.choices = [(m.mod_id, m.mod_nome) for m in modalidades]

        if request.method == "GET":
            form.nome.data = user.usr_nome
            form.modalidade.data = user.usr_mod_id
            form.imagem.data = user.usr_img

    else:
        form = FormEditarProfessor(obj=user)
        if request.method == "GET":
            form.nome.data = user.usr_nome
            form.imagem.data = user.usr_img

    if form.validate_on_submit():
        user.usr_nome = form.nome.data

        if user.usr_tipo == "aluno":
            user.usr_mod_id = form.modalidade.data

        if form.senha.data:
            user.usr_senha_hash = generate_password_hash(form.senha.data)

        if form.remover_imagem.data:
            if user.usr_img and "default_profile.png" not in user.usr_img:
                caminho_antigo = os.path.join(current_app.root_path, "static", user.usr_img)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)
            user.usr_img = "images/default_profile.png"

        if form.imagem.data:
            if user.usr_img and "default_profile.png" not in user.usr_img:
                caminho_antigo = os.path.join(current_app.root_path, "static", user.usr_img)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)

            file = form.imagem.data
            filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}_{filename}"
            path = os.path.join(current_app.config["UPLOADED_IMAGES_DEST"], "perfis", filename)
            file.save(path)
            user.usr_img = f"uploads/images/perfis/{filename}"

        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("usuarios.perfil", id=user.usr_id))

    return render_template("users/editarperfil.html", form=form, user=user)
