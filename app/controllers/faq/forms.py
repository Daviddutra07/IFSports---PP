from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Length
)


class FAQForm(FlaskForm):

    pergunta = StringField(
        "Pergunta",
        validators=[
            DataRequired(
                message="A pergunta é obrigatória."
            ),
            Length(
                max=200,
                message="A pergunta deve possuir no máximo 200 caracteres."
            )
        ]
    )


    resposta = TextAreaField(
        "Resposta",
        validators=[
            DataRequired(
                message="A resposta é obrigatória."
            )
        ]
    )


    categoria = StringField(
        "Categoria",
        validators=[
            Length(
                max=50,
                message="A categoria deve possuir no máximo 50 caracteres."
            )
        ]
    )


    ordem = IntegerField(
        "Ordem"
    )


    submit = SubmitField(
        "Salvar"
    )