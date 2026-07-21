from datetime import datetime, timedelta

from werkzeug.datastructures import MultiDict

from app.controllers.treinos.forms import TreinoForm


def criar_form(dados):

    form = TreinoForm(formdata=MultiDict(dados))

    form.trn_mod_id.choices = [
        (1, "Futsal")
    ]

    return form


def test_treino_unico_valido(app):

    with app.test_request_context():

        form = criar_form({
            "trn_nome": "Treino",
            "trn_quantidade": 20,
            "trn_mod_id": 1,
            "trn_data": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        })

        assert form.validate()


def test_treino_fixo_valido(app):

    with app.test_request_context():

        form = criar_form({
            "trn_nome": "Treino",
            "trn_fixo": "y",
            "trn_dia_semana": 2,
            "trn_horario": "19:00",
            "trn_quantidade": 20,
            "trn_mod_id": 1
        })

        assert form.validate()


def test_treino_fixo_sem_horario(app):

    with app.test_request_context():

        form = criar_form({
            "trn_nome": "Treino",
            "trn_fixo": "y",
            "trn_dia_semana": 2,
            "trn_quantidade": 20,
            "trn_mod_id": 1
        })

        assert not form.validate()


def test_treino_unico_sem_data(app):

    with app.test_request_context():

        form = criar_form({
            "trn_nome": "Treino",
            "trn_quantidade": 20,
            "trn_mod_id": 1
        })

        assert not form.validate()


def test_quantidade_menor_que_um(app):

    with app.test_request_context():

        form = criar_form({
            "trn_nome": "Treino",
            "trn_quantidade": 0,
            "trn_mod_id": 1,
            "trn_data": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        })

        assert not form.validate()


def test_quantidade_vagas_invalida(app):

    with app.test_request_context():

        form = criar_form({
            "trn_nome": "Treino",
            "trn_quantidade": -5,
            "trn_mod_id": 1,
            "trn_data": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        })

        assert not form.validate()