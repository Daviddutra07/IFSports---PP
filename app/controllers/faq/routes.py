from flask import Blueprint
from app.controllers.faq import routes
from flask import render_template,redirect, url_for, flash
from app.models.faq import FAQ
from app.decorators.auth import professor_required
from app import db
from app.models.faq import FAQ
from app.controllers.faq.forms import FAQForm
from flask_login import current_user, login_required

faq_bp = Blueprint('faq',__name__,url_prefix='/faq')

@faq_bp.route('/')
@login_required
def listar():


    perguntas = FAQ.query.filter_by(
            faq_ativo=True
        ).order_by(
            FAQ.faq_ordem.asc()
        ).all()


    return render_template(
        'faq/listar.html',
        perguntas=perguntas
    )

@faq_bp.route('/criar', methods=['GET','POST'])
@professor_required
def criar():

    form = FAQForm()


    if form.validate_on_submit():

        faq = FAQ(
            faq_pergunta=form.pergunta.data,
            faq_resposta=form.resposta.data,
            faq_categoria=form.categoria.data,
            faq_ordem=form.ordem.data
        )


        db.session.add(faq)
        db.session.commit()


        flash(
            "Pergunta adicionada com sucesso!",
            "success"
        )


        return redirect(
            url_for('faq.listar')
        )


    return render_template(
        '/faq/form.html',
        form=form
    )

@faq_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@professor_required
def editar(id):

    faq = FAQ.query.get_or_404(id)

    form = FAQForm()

    if form.validate_on_submit():

        faq.faq_pergunta = form.pergunta.data
        faq.faq_resposta = form.resposta.data
        faq.faq_categoria = form.categoria.data
        faq.faq_ordem = form.ordem.data

        db.session.commit()

        flash(
            "Pergunta atualizada!",
            "success"
        )

        return redirect(url_for("faq.listar"))


    if not form.is_submitted():
        form.pergunta.data = faq.faq_pergunta
        form.resposta.data = faq.faq_resposta
        form.categoria.data = faq.faq_categoria
        form.ordem.data = faq.faq_ordem

    return render_template(
        "faq/form.html",
        form=form,
        faq=faq
    )

@faq_bp.route('/excluir/<int:id>', methods=["POST"])
@professor_required
def excluir(id):

    faq = FAQ.query.get_or_404(id)


    faq.faq_ativo = False

    db.session.commit()


    flash(
        "Pergunta removida da FAQ.",
        "success"
    )


    return redirect(
        url_for('faq.listar')
    )