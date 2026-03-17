from datetime import datetime, timezone
from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "tb_usuarios"
    usr_id = db.Column(db.Integer, primary_key=True)
    usr_email = db.Column(db.String(120), unique=True, nullable=False)
    usr_nome = db.Column(db.String(70))
    usr_tipo = db.Column(db.String(20), nullable=False)
    usr_senha_hash = db.Column(db.String(255), nullable=False)
    usr_created_At = db.Column(db.DateTime, default=datetime.now, nullable=False)
    usr_confirmed = db.Column(db.Boolean, default=False)
    usr_confirmed_at = db.Column(db.DateTime, nullable=True)
    usr_is_active = db.Column(db.Boolean, default=True)
    usr_pontos = db.Column(db.Integer, default=0, nullable = False)
    usr_img = usr_img = db.Column(db.String(255), nullable=True, default="images/default_profile.png")
    usr_mod_id = db.Column(db.Integer, db.ForeignKey("tb_modalidades.mod_id"))
    usr_primeiro_login = db.Column(db.Boolean, default=True)

    conquistas = db.relationship("UsuarioConquista", back_populates="usuario")
    modalidade = db.relationship("Modalidade", backref="usuarios")


    def get_id(self):
        return str(self.usr_id)