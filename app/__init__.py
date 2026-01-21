from flask import Flask
from dotenv import load_dotenv

from app.config import Config
from app.extensions import db, login_manager, mail

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.models.users import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # Registrar controllers (blueprints)
    from app.controllers.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    return app