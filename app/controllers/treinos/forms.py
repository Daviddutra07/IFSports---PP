from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, TextAreaField,  SubmitField,  StringField, TimeField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError


class TreinoForm(FlaskForm):

    trn_nome = StringField("Nome do treino", validators=[DataRequired(message="O nome é obrigatório."), Length(min=3, max=70)])

    trn_descricao = TextAreaField("Descrição",validators=[Optional()])

    trn_fixo = BooleanField("Treino fixo semanal?")

    trn_dia_semana = SelectField("Dia da semana",
        choices=[
            (0, "Segunda-feira"),
            (1, "Terça-feira"),
            (2, "Quarta-feira"),
            (3, "Quinta-feira"),
            (4, "Sexta-feira"),
            (5, "Sábado"),
            (6, "Domingo"),
        ], coerce=int, validators=[Optional()])

    trn_horario = TimeField( "Horário", format="%H:%M", validators=[Optional()])

    trn_data = DateTimeLocalField("Data e Horário do treino", format="%Y-%m-%dT%H:%M", validators=[Optional()])

    trn_quantidade = IntegerField('Quantidade de Vagas', validators=[DataRequired(message="Informe a quantidade de vagas."),
        NumberRange(min=1, message="A quantidade deve ser maior que 0.")])

    trn_mod_id = SelectField("Modalidade Esportiva", coerce=int, validators=[DataRequired(message="Selecione uma modalidade.")])   

    def validate(self, extra_validators=None):
        if self.trn_fixo.data:
            # limpa data antes de validar
            self.trn_data.data = None

        else:
            # limpa campos de fixo
            self.trn_dia_semana.data = None
            self.trn_horario.data = None


        if not super().validate():
            return False

        if self.trn_fixo.data:
            if self.trn_dia_semana.data is None:
                self.trn_dia_semana.errors.append("Informe o dia da semana.")
                return False
            if not self.trn_horario.data:
                self.trn_horario.errors.append("Informe o horário.")
                return False
            if self.trn_data.data:
                self.trn_data.errors.append("Treino fixo não deve ter data específica.")
                return False

        else:
            if not self.trn_data.data:
                self.trn_data.errors.append("Informe a data do treino.")
                return False

        return True
    
class TreinoExcluir(FlaskForm):
    submit = SubmitField("Remover")

class TreinoCheckIn(FlaskForm):
    submit = SubmitField("CheckIn")