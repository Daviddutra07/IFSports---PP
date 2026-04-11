import os

from flask import Flask
from dotenv import load_dotenv
from flask_login import current_user
from flask_socketio import join_room,leave_room

from app.config import Config
from app.extensions import db, login_manager, mail, socketio
from app.models.notificacoes import Notificacao
from app.seed.conquistas import inserir_conquistas

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    os.makedirs(app.config['UPLOADED_IMAGES_DEST'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOADED_IMAGES_DEST'], 'perfis'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOADED_IMAGES_DEST'], 'mural'), exist_ok=True)

    db.init_app(app)
    socketio.init_app(app)

    @socketio.on("connect")
    def handle_connect():
        if current_user.is_authenticated:
            if current_user.usr_tipo == "aluno":
                join_room("alunos")
            elif current_user.usr_tipo == "professor":
                join_room("professores")

    @socketio.on("entrar_pagina_treinos")
    def entrar_pagina_treinos():
        if current_user.is_authenticated:
            join_room("pagina_treinos")
    
    @socketio.on("sair_pagina_treinos")
    def sair_pagina_treinos():
        if current_user.is_authenticated:
            leave_room("pagina_treinos")

    @socketio.on("entrar_ocorrencia")
    def entrar_ocorrencia(data):
        ocorrencia_id = data["ocorrencia_id"]
        room = f"ocorrencia_{ocorrencia_id}"
        join_room(room)
    

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    mail.init_app(app)
    login_manager.login_message = "Você precisa estar logado para acessar esta página."
    login_manager.login_message_category = "warning"

    from app.models.users import User
    from app.models.treinos import Treino
    from app.models.frequencia import Frequencia
    from app.models.modalidades import Modalidade
    from app.models.conquistas import Conquista
    from app.models.treino_ocorrencia import TreinoOcorrencia
    from app.models.avisos import Aviso
    

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_logout_form():
        from app.controllers.auth.forms import LogoutForm
        return dict(logout_form=LogoutForm())
    
    @app.context_processor
    def inject_notificacoes():
        tem_notificacoes_nao_lidas = False

        if current_user.is_authenticated:
            tem_notificacoes_nao_lidas = Notificacao.query.filter_by(
                not_usr_id=current_user.usr_id,
                not_lida=False
            ).first() is not None

        return dict(tem_notificacoes_nao_lidas=tem_notificacoes_nao_lidas)

    # Registrar controllers (blueprints)
    from app.controllers.auth.routes import auth_bp
    from app.controllers.treinos.routes import treinos_bp
    from app.controllers.modalidades.routes import modalidades_bp
    from app.controllers.users.routes import usuarios_bp
    from app.controllers.avisos.routes import avisos_bp
    from app.controllers.rankings.routes import rankings_bp
    from app.controllers.notificacoes.routes import notificacoes_bp

    app.register_blueprint(rankings_bp)
    app.register_blueprint(avisos_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(treinos_bp)
    app.register_blueprint(modalidades_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(notificacoes_bp)

    with app.app_context():
        db.create_all()
        inserir_conquistas()


    return app