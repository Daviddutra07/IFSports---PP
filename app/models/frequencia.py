from datetime import datetime, timezone
from app.extensions import db


class Frequencia(db.Model):
    __tablename__ = "tb_frequencias"
    frq_id = db.Column(db.Integer, primary_key=True)
    frq_aluno_id = db.Column(db.Integer,db.ForeignKey("tb_usuarios.usr_id"), nullable=False)
    frq_treino_id = db.Column(db.Integer, db.ForeignKey("tb_treinos.trn_id"), nullable=False)
    frq_data_ocorrencia = db.Column(db.DateTime, nullable=False)
    frq_checkin_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    frq_status = db.Column(db.Enum( "checkin","presente","ausente", name="status_frequencia"), default="checkin", nullable=False)
    frq_validado_em = db.Column(db.DateTime, nullable=True)
    aluno = db.relationship("User", foreign_keys=[frq_aluno_id])
    treino = db.relationship("Treino", backref="frequencias")

    __table_args__ = (
        db.UniqueConstraint(
            "frq_aluno_id",
            "frq_treino_id",
            "frq_data_ocorrencia",
            name="uq_aluno_treino_data"
        ),
    )