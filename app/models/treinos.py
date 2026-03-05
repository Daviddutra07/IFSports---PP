from datetime import datetime, timezone
from app.extensions import db

class Treino(db.Model):
    __tablename__ = "tb_treinos"
    trn_id = db.Column(db.Integer, primary_key=True)
    trn_nome = db.Column(db.String(70), nullable=False)
    trn_descricao = db.Column(db.Text, nullable=False)
    trn_created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),nullable=False)
    trn_data = db.Column(db.DateTime)
    trn_fixo = db.Column(db.Boolean, default=False, nullable=False)
    trn_dia_semana = db.Column(db.Integer)
    trn_horario = db.Column(db.Time)
    trn_proxima_data = db.Column(db.DateTime)
    trn_quantidade = db.Column(db.Integer, nullable=False)
    trn_mod_id = db.Column(db.Integer, db.ForeignKey("tb_modalidades.mod_id"), nullable=False)
    trn_pro_id = db.Column(db.Integer, db.ForeignKey('tb_usuarios.usr_id'), nullable=False)

    professor = db.relationship('User', backref='treinos_criados')