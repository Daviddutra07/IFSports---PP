from datetime import datetime
from flask import Blueprint, render_template, redirect, session, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.email_service import enviar_email_confirmacao, validar_token
from app.extensions import db
from app.models.users import User
from app.controllers.auth.forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data.lower()
        senha_hash = generate_password_hash(form.senha.data)
        role = form.user_role.data

        # Verifica se o email já existe
        if User.query.filter_by(usr_email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return render_template('auth/register.html', form=form)
        
        user = User(usr_email=email, usr_nome=nome, usr_tipo=role, usr_senha_hash=senha_hash)

        db.session.add(user)
        db.session.commit()

        try:
            enviar_email_confirmacao(user)
        except Exception:
            flash(' Erro ao enviar email de confirmação.', 'warning')
            

        flash('Cadastro realizado com sucesso! Verifique seu email para confirmar a conta.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/confirmar/<token>')
def confirmar_email(token):
    email = validar_token(token)

    if not email:
        flash(' Link inválido ou expirado.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(usr_email=email).first()

    if not user:
        flash(' Usuário não encontrado.', 'error')
        return redirect(url_for('auth.login'))

    if user.usr_confirmed:
        flash(' Conta já confirmada.', 'info')
    else:
        user.usr_confirmed = True
        user.usr_confirmed_at = datetime.now
        db.session.commit()
        flash('Conta confirmada com sucesso!', 'success')

    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.senha.data

        user = User.query.filter_by(usr_email=email).first()

        if not user or not check_password_hash(user.usr_senha_hash, password):
            flash(' Email ou senha inválidos.', 'error')
            return render_template('auth/login.html', form=form)

        if not user.usr_confirmed:
            flash(' Você precisa confirmar seu email antes de acessar o sistema.','warning')
            return redirect(url_for('auth.login'))

        if not user.usr_is_active:
            flash(' Sua conta está desativada.', 'error')
            return redirect(url_for('auth.login'))

        session.clear()
        logout_user()
        login_user(user)
        flash('Login realizado com sucesso!', 'success')

        if user.usr_primeiro_login:
            return redirect(url_for("usuarios.concluir") )

        return redirect(url_for('treinos.listar'))
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout', methods = ["POST"])
@login_required
def logout():
    logout_user()
    flash(' Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))