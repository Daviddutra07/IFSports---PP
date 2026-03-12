from app.extensions import db

class Modalidade(db.Model):
    __tablename__ = "tb_modalidades"

    mod_id = db.Column(db.Integer, primary_key=True)
    mod_nome = db.Column(db.String(50), nullable=False, unique=True)

    treinos = db.relationship("Treino", backref="modalidade")