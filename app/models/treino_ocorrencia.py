from datetime import datetime
from app.extensions import db


class TreinoOcorrencia(db.Model):
    __tablename__ = "tb_treino_ocorrencias"

    tro_id = db.Column(db.Integer, primary_key=True)
    tro_treino_id = db.Column(
        db.Integer,
        db.ForeignKey("tb_treinos.trn_id"),
        nullable=False
    )
    tro_data = db.Column(db.DateTime, nullable=False)
    tro_vagas_ocupadas = db.Column(db.Integer, default=0, nullable=False)
    tro_ativo = db.Column(db.Boolean, default=True, nullable=False)
    tro_validado_em = db.Column(db.DateTime, nullable=True)
    tro_created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    treino = db.relationship("Treino", back_populates="ocorrencias")

    __table_args__ = (
        db.UniqueConstraint("tro_treino_id", "tro_data", name="uq_treino_ocorrencia_data"),
        db.Index("idx_tro_treino_data", "tro_treino_id", "tro_data"),
    )

    @property
    def vagas_restantes(self):
        return self.treino.trn_quantidade - self.tro_vagas_ocupadas

    @property
    def ja_validado(self):
        return self.tro_validado_em is not None