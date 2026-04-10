from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import desc
from app.models.users import User
from app.models.modalidades import Modalidade
from flask import request

rankings_bp = Blueprint("rankings",__name__,url_prefix="/rankings",template_folder="templates/rankings")

@rankings_bp.route("/")
@login_required
def listar():
    modalidade_id = request.args.get("modalidade", type=int)

    modalidades = Modalidade.query.order_by(Modalidade.mod_nome.asc()).all()

    query = User.query.filter(User.usr_tipo == "aluno")

    if modalidade_id:
        query = query.filter(User.usr_mod_id == modalidade_id)

    ranking = query.order_by(
        User.usr_pontos.desc(),
        User.usr_nome.asc()
    ).all()

    exibir = len(ranking) >= 10 
    
    modalidade_selecionada = None
    if modalidade_id:
        modalidade_selecionada = next(
            (m for m in modalidades if m.mod_id == modalidade_id),
            None
        )

    return render_template(
        "rankings/listar.html",
        ranking=ranking,
        modalidades=modalidades,
        modalidade_id=modalidade_id,
        modalidade_selecionada=modalidade_selecionada,
        exibir=exibir
    )
