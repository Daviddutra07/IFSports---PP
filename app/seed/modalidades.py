from app.extensions import db
from app.models.modalidades import Modalidade

def inserir_modalidades():

    if Modalidade.query.first():
        return
    
    modalidades = [

    Modalidade(
        mod_nome = "Futebol" 
    ),
    Modalidade(
        mod_nome = "Vôlei" 
    ),
    Modalidade(
        mod_nome = "Basquete" 
    ),
    Modalidade(
        mod_nome = "Natação" 
    ),
    Modalidade(
        mod_nome = "Handebol" 
    ),
    Modalidade(
        mod_nome = "Atletismo" 
    ),

    ]

    db.session.add_all(modalidades)
    db.session.commit()