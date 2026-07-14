from datetime import datetime
from app.extensions import db

class FAQ(db.Model):

    __tablename__ = "tb_faq"

    faq_id = db.Column(
        db.Integer,
        primary_key=True
    )

    faq_pergunta = db.Column(
        db.String(200),
        nullable=False
    )

    faq_resposta = db.Column(
        db.Text,
        nullable=False
    )

    faq_categoria = db.Column(
        db.String(50),
        nullable=True
    )

    faq_ordem = db.Column(
        db.Integer,
        default=0
    )

    faq_ativo = db.Column(
        db.Boolean,
        default=True
    )

    faq_created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )