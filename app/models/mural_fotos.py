from datetime import datetime

from app.extensions import db

class MuralFotos(db.Model):
    __tablename__ = "tb_mural"

    mft_id = db.Column(db.Integer, primary_key=True)
    mft_img_id = db.Column(db.String(255), nullable=False)
    mft_legenda = db.Column(db.String(50), nullable=False)
    mft_created_at = db.Column(db.DateTime,nullable=False,default=datetime.now)
    mft_usr_id = db.Column(db.Integer,db.ForeignKey("tb_usuarios.usr_id"),nullable=False)
    mft_deleted_at = db.Column(db.DateTime)

    usuario = db.relationship("User", backref="fotos_mural")