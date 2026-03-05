from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class ModalidadeForm(FlaskForm):
    mod_nome = StringField("Nome do treino", validators=[DataRequired(message="O nome é obrigatório."), Length(min=3, max=70)])

    submit = SubmitField("Inserir Modalidade")