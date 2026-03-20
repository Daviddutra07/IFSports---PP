from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app.models.treinos import Treino


class AvisoForm(FlaskForm):
    avs_titulo = StringField(
        "Título",
        validators=[
            DataRequired(),
            Length(min=3, max=150)
        ]
    )

    avs_mensagem = TextAreaField(
        "Mensagem",
        validators=[
            DataRequired(),
            Length(min=5, max=1000)
        ]
    )

    avs_modalidade_id = SelectField(
        "Modalidade",
        coerce=int,
        validators=[Optional()]
    )

    avs_treino_id = SelectField(
        "Treino",
        coerce=int,
        validators=[Optional()]
    )

    avs_fixado = BooleanField("Fixar aviso")

    avs_expira_em = DateTimeLocalField(
        "Expira em",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()]
    )

    submit = SubmitField("Salvar")

    def validate_avs_treino_id(self, field):
        if field.data == 0:
            return

        treino = Treino.query.get(field.data)
        if not treino:
            raise ValidationError("Treino inválido.")

        if self.avs_modalidade_id.data not in (None, 0):
            if treino.trn_mod_id != self.avs_modalidade_id.data:
                raise ValidationError(
                    "A modalidade selecionada deve ser a mesma do treino escolhido."
                )