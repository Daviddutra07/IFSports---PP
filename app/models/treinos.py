from datetime import datetime

from flask_login import current_user
from app.extensions import db
from app.models.frequencia import Frequencia

class Treino(db.Model):
    __tablename__ = "tb_treinos"
    trn_id = db.Column(db.Integer, primary_key=True)
    trn_nome = db.Column(db.String(70), nullable=False)
    trn_descricao = db.Column(db.Text, nullable=True)
    trn_created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    trn_data = db.Column(db.DateTime)
    trn_proxima_data = db.Column(db.DateTime)
    trn_fixo = db.Column(db.Boolean, default=False, nullable=False)
    trn_ativo = db.Column(db.Boolean, default=True, nullable=False)
    trn_dia_semana = db.Column(db.Integer)
    trn_horario = db.Column(db.Time)
    trn_quantidade = db.Column(db.Integer, nullable=False)
    trn_mod_id = db.Column(db.Integer, db.ForeignKey("tb_modalidades.mod_id"), nullable=False)
    trn_pro_id = db.Column(db.Integer,db.ForeignKey('tb_usuarios.usr_id'), nullable=False)
    trn_deleted_at = db.Column(db.DateTime, nullable=True)
    trn_vagas_ocupadas = db.Column(db.Integer, default=0, nullable=False)
    professor = db.relationship('User', backref='treinos_criados')
    
    @property
    def vagas_ocupadas(self):
        return self.trn_vagas_ocupadas

    @property
    def vagas_restantes(self):
        return self.trn_quantidade - self.trn_vagas_ocupadas
    
    @property
    def ja_fez_checkin(self):
        if current_user.usr_tipo != "aluno":
            return False
        return Frequencia.query.filter_by(
            frq_treino_id=self.trn_id,
            frq_aluno_id=current_user.usr_id,
            frq_data_ocorrencia=self.trn_data
        ).first() is not None