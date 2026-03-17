from datetime import datetime
from app.extensions import db

class Frequencia(db.Model):
    __tablename__ = "tb_frequencias"
    frq_id = db.Column(db.Integer, primary_key=True)
    frq_aluno_id = db.Column(db.Integer,db.ForeignKey("tb_usuarios.usr_id"), nullable=False)
    frq_treino_id = db.Column(db.Integer, db.ForeignKey("tb_treinos.trn_id"), nullable=False)
    frq_data_ocorrencia = db.Column(db.DateTime, nullable=False)
    frq_reserva_em = db.Column(db.DateTime, default=datetime.now, nullable=False)
    frq_status = db.Column(db.Enum( "inscricao","presente","ausente", name="status_frequencia"), default="inscricao", nullable=False)
    frq_validado_em = db.Column(db.DateTime, nullable=True)
    frq_aluno_nota = db.Column(db.Integer, nullable=True)
    frq_trn_nome = db.Column(db.String(100), nullable=True) #Apenas para fim de registro histórico de treinos semanais
    frq_mod_nome = db.Column(db.String(50), nullable=True) #Apenas para fim de registro histórico de treinos semanais
    aluno = db.relationship("User", foreign_keys=[frq_aluno_id])
    treino = db.relationship("Treino", backref="frequencias")

    __table_args__ = (
        db.UniqueConstraint(
            "frq_aluno_id",
            "frq_treino_id",
            "frq_data_ocorrencia",
            name="uq_aluno_treino_data"
        ),
        db.Index("idx_frq_treino_data", "frq_treino_id", "frq_data_ocorrencia"),
        db.Index("idx_frq_aluno", "frq_aluno_id"),
        )

    @classmethod
    def treino_ja_validado(cls, treino_id, data_ocorrencia):
        return db.session.query(cls.frq_id).filter_by(
            frq_treino_id=treino_id,
            frq_data_ocorrencia=data_ocorrencia
        ).filter(cls.frq_validado_em != None).first() is not None