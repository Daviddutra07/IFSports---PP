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
    trn_fixo = db.Column(db.Boolean, default=False, nullable=False)
    trn_ativo = db.Column(db.Boolean, default=True, nullable=False)
    trn_dia_semana = db.Column(db.Integer, nullable=True)
    trn_horario = db.Column(db.Time, nullable=True)
    trn_quantidade = db.Column(db.Integer, nullable=False)
    trn_mod_id = db.Column(db.Integer, db.ForeignKey("tb_modalidades.mod_id"), nullable=False)
    trn_pro_id = db.Column(db.Integer, db.ForeignKey("tb_usuarios.usr_id"), nullable=False)
    trn_deleted_at = db.Column(db.DateTime, nullable=True)

    professor = db.relationship("User", backref="treinos_criados")
    ocorrencias = db.relationship(
        "TreinoOcorrencia",
        back_populates="treino",
        cascade="all, delete-orphan",
        order_by="TreinoOcorrencia.tro_data.asc()"
    )

    @property
    def ocorrencia_aberta(self):
        for ocorrencia in self.ocorrencias:
            if ocorrencia.tro_ativo and not ocorrencia.tro_validado_em:
                return ocorrencia
        return None

    @property
    def vagas_ocupadas(self):
        ocorrencia = self.ocorrencia_aberta
        return ocorrencia.tro_vagas_ocupadas if ocorrencia else 0

    @property
    def vagas_restantes(self):
        ocorrencia = self.ocorrencia_aberta
        if not ocorrencia:
            return self.trn_quantidade
        return self.trn_quantidade - ocorrencia.tro_vagas_ocupadas

    @property
    def data_exibicao(self):
        ocorrencia = self.ocorrencia_aberta
        return ocorrencia.tro_data if ocorrencia else None

    @property
    def ja_fez_checkin(self):
        if current_user.usr_tipo != "aluno":
            return False

        ocorrencia = self.ocorrencia_aberta
        if not ocorrencia:
            return False

        return Frequencia.query.filter_by(
            frq_treino_id=self.trn_id,
            frq_ocorrencia_id=ocorrencia.tro_id,
            frq_aluno_id=current_user.usr_id
        ).first() is not None