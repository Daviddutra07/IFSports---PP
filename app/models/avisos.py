from datetime import datetime
from app.extensions import db

class Aviso(db.Model):
    __tablename__ = "tb_avisos"

    avs_id = db.Column(db.Integer, primary_key=True)
    avs_titulo = db.Column(db.String(150), nullable=False)
    avs_mensagem = db.Column(db.Text, nullable=False)

    avs_autor_id = db.Column(db.Integer, db.ForeignKey("tb_usuarios.usr_id"), nullable=False)
    avs_modalidade_id = db.Column(db.Integer, db.ForeignKey("tb_modalidades.mod_id"), nullable=True)
    avs_treino_id = db.Column(db.Integer, db.ForeignKey("tb_treinos.trn_id"), nullable=True)

    avs_fixado = db.Column(db.Boolean, default=False)
    avs_ativo = db.Column(db.Boolean, default=True)
    avs_created_at = db.Column(db.DateTime, default=datetime.now)
    avs_expira_em = db.Column(db.DateTime, nullable=True)

    autor = db.relationship("User", backref="avisos_criados")
    modalidade = db.relationship("Modalidade", backref="avisos")
    treino = db.relationship("Treino", backref="avisos")