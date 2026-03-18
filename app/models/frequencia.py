from datetime import datetime
from app.extensions import db


class Frequencia(db.Model):
    __tablename__ = "tb_frequencias"
    frq_id = db.Column(db.Integer, primary_key=True)
    frq_aluno_id = db.Column(db.Integer,db.ForeignKey("tb_usuarios.usr_id"),nullable=False)
    frq_treino_id = db.Column(db.Integer,db.ForeignKey("tb_treinos.trn_id"),nullable=False)
    frq_ocorrencia_id = db.Column(db.Integer,db.ForeignKey("tb_treino_ocorrencias.tro_id"),nullable=False)
    frq_data_ocorrencia = db.Column(db.DateTime, nullable=False)
    frq_reserva_em = db.Column(db.DateTime, default=datetime.now, nullable=False)
    frq_status = db.Column(db.Enum("inscricao", "presente", "ausente", name="status_frequencia"),default="inscricao",nullable=False)
    frq_validado_em = db.Column(db.DateTime, nullable=True)
    frq_aluno_nota = db.Column(db.Integer, nullable=True)
    frq_trn_nome = db.Column(db.String(100), nullable=True)
    frq_mod_nome = db.Column(db.String(50), nullable=True)

    aluno = db.relationship("User", foreign_keys=[frq_aluno_id])
    treino = db.relationship("Treino", backref="frequencias")
    ocorrencia = db.relationship("TreinoOcorrencia", backref="frequencias")

    __table_args__ = (db.UniqueConstraint("frq_aluno_id", "frq_ocorrencia_id", name="uq_aluno_ocorrencia"),
        db.Index("idx_frq_ocorrencia", "frq_ocorrencia_id"),
        db.Index("idx_frq_treino_data", "frq_treino_id", "frq_data_ocorrencia"),
        db.Index("idx_frq_aluno", "frq_aluno_id"),
    )

    @classmethod
    def treino_ja_validado(cls, ocorrencia_id):
        return db.session.query(cls.frq_id).filter_by(
            frq_ocorrencia_id=ocorrencia_id
        ).filter(cls.frq_validado_em.is_not(None)).first() is not None