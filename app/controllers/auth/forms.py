from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=70, message="O nome deve ter entre 2 e 70 caracteres")])
    email = StringField('E-mail', validators=[DataRequired(), Email(message="Digite um e-mail válido")])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=8, message="A senha deve possuir pelo menos 8 caracteres."), EqualTo('confirmar_senha', message="As senhas devem ser iguais")])
    role_provisorio= SelectField('Você é', choices=[('aluno', 'Aluno'), ('professor', 'Professor')],validators=[DataRequired()])
    confirmar_senha = PasswordField('Confirme a Senha',validators=[DataRequired(message="Confirme sua senha.")])
    submit = SubmitField('Cadastrar')

    def validate_email(self, field):
        email = field.data.lower()

        if email.endswith('@escolar.ifrn.edu.br'):
            self.user_role = 'aluno'
        elif email.endswith('@ifrn.edu.br'):
            self.user_role = 'professor'
        else:
            raise ValidationError('Use seu email institucional do IFRN.')
        
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="Informe seu e-mail."), Email(message="Digite um e-mail válido."), ])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class LogoutForm(FlaskForm):
    submit = SubmitField("Sair")