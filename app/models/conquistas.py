from datetime import datetime
from app.extensions import db

class Conquista(db.Model):
    __tablename__ = "tb_conquistas"
    cnq_id = db.Column(db.Integer, primary_key=True)
    cnq_nome = db.Column(db.String(100), nullable=False)
    cnq_descricao = db.Column(db.String(255))
    cnq_tipo = db.Column(db.String(50)) 
    cnq_meta = db.Column(db.Float)
    cnq_pontos_bonus = db.Column(db.Integer, default=10, nullable=False)
    cnq_tier = db.Column(db.String(20))
    cnq_tier_valor = db.Column(db.Integer)

    usuarios = db.relationship("UsuarioConquista", back_populates="conquista")

class UsuarioConquista(db.Model):
    __tablename__ = "tb_usuario_conquistas"
    usc_id = db.Column(db.Integer, primary_key=True)
    usc_usr_id = db.Column(db.Integer, db.ForeignKey("tb_usuarios.usr_id"))
    usc_cnq_id = db.Column(db.Integer, db.ForeignKey("tb_conquistas.cnq_id"))
    usc_registered_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    usuario = db.relationship("User", back_populates="conquistas")
    conquista = db.relationship("Conquista", back_populates="usuarios")

    __table_args__ = (db.UniqueConstraint("usc_usr_id", "usc_cnq_id"),)