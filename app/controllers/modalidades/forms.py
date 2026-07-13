from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from app.models.modalidades import Modalidade
from app.extensions import db


class ModalidadeForm(FlaskForm):
    mod_id = HiddenField()

    mod_nome = StringField(
        "Nome da Modalidade",
        validators=[
            DataRequired(message="O nome é obrigatório."),
            Length(min=3, max=70, message="O nome deve possuir entre 3 e 70 caracteres."),
            
        ]
    )

    submit = SubmitField("Salvar")

    def validate_mod_nome(self, field):
        nome = field.data.strip()

        query = Modalidade.query.filter(
            db.func.lower(Modalidade.mod_nome) == nome.lower()
        )

        if self.mod_id.data:
            query = query.filter(
                Modalidade.mod_id != int(self.mod_id.data)
            )

        if query.first():
            raise ValidationError(
                "Já existe uma modalidade com esse nome."
            )