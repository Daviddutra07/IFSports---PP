from datetime import datetime
from app.extensions import db


class Notificacao(db.Model):
    __tablename__ = "tb_notificacoes"
    not_id = db.Column(db.Integer, primary_key=True)
    not_usr_id = db.Column(db.Integer, db.ForeignKey("tb_usuarios.usr_id"), nullable=False, index=True)
    not_tipo = db.Column(db.Enum("aviso", "treino_criado", "treino_alterado", "treino_cancelado", "validacao", "conquista", name="notificacao_tipo"),nullable=False)
    not_titulo = db.Column(db.String(150), nullable=False)
    not_descricao = db.Column(db.String(255))
    not_link = db.Column(db.String(255))
    not_lida = db.Column(db.Boolean, default=False, nullable=False, index=True)
    not_created_at = db.Column(db.DateTime,default=datetime.now,nullable=False,index=True)
    not_publico = db.Column(db.Enum( "usuario", "modalidade", "treino", "global", name="notificacao_publico"),nullable=False)
    not_referencia_id = db.Column(db.Integer)
    not_referencia_tipo = db.Column(db.String(30))
    not_expira_em = db.Column(db.DateTime)

    usuario = db.relationship("User", backref="notificacoes")