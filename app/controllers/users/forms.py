from flask_wtf import FlaskForm
from wtforms import BooleanField, FileField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Optional
from flask_wtf.file import FileAllowed

class FormProfessor(FlaskForm):
    imagem = FileField(
        "Foto de perfil",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Somente imagens são permitidas."
            ),
            Optional()
        ]
    )
    submit = SubmitField("Salvar")

class FormAluno(FlaskForm):
    imagem = FileField(
        "Foto de perfil",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Somente imagens são permitidas."
            ),
            Optional()
        ]
    )

    modalidade = SelectField(
        "Modalidade principal",
        coerce=int,
        validators=[DataRequired()]
    )
    submit = SubmitField("Salvar")

class FormEditarProfessor(FlaskForm):
    nome = StringField(
        "Nome completo",
        validators=[DataRequired(), Length(min=3, max=70)]
    )

    imagem = FileField(
        "Foto de perfil",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Somente imagens são permitidas."
            ),
            Optional()
        ]
    )

    remover_imagem = BooleanField("Remover foto de perfil")

    senha = PasswordField(
        "Nova senha",
        validators=[
            Optional(),
            Length(min=8, message="A senha deve ter ao menos 8 caracteres")
        ]
    )

    confirmar_senha = PasswordField(
        "Confirmar senha",
        validators=[
            EqualTo("senha", message="As senhas devem coincidir"),
            Optional()
        ]
    )

    submit = SubmitField("Atualizar")

class FormEditarAluno(FlaskForm):
    nome = StringField(
        "Nome completo",
        validators=[DataRequired(), Length(min=3, max=70)]
    )

    modalidade = SelectField(
        "Modalidade principal",
        coerce=int,
        validators=[DataRequired()]
    )

    imagem = FileField(
        "Foto de perfil",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Somente imagens são permitidas."
            ),
            Optional()
        ]
    )

    remover_imagem = BooleanField("Remover foto de perfil")

    senha = PasswordField(
        "Nova senha",
        validators=[
            Optional(),
            Length(min=8, message="A senha deve ter ao menos 8 caracteres")
        ]
    )

    confirmar_senha = PasswordField(
        "Confirmar senha",
        validators=[
            EqualTo("senha", message="As senhas devem coincidir"),
            Optional()
        ]
    )

    submit = SubmitField("Atualizar")