from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField
from flask_wtf.file import FileAllowed
from wtforms.validators import Length, DataRequired


class FormFotos(FlaskForm):
    imagem = FileField(
"Foto",
validators=[
    FileAllowed(
        ["jpg", "jpeg", "png", "webp"],
        "Somente imagens são permitidas."
    ), DataRequired(message="Selecione uma imagem.")
]
    )

    legenda = StringField("Legenda",validators=[Length(min=3, max=50), DataRequired(message="A legenda deve possuir entre 3 e 50 caracteres.")])

    submit = SubmitField("Enviar")

class FormEditarFoto(FlaskForm):
    legenda = StringField(
        "Legenda",
        validators=[Length(min=3, max=50, message="A legenda deve possuir entre 3 e 50 caracteres."), DataRequired(message="Selecione uma imagem.")]
    )

    submit = SubmitField("Salvar Alterações")