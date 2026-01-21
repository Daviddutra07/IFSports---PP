import os

class Config:
    #Chave Secreta
    SECRET_KEY = os.getenv("SECRET_KEY")

    #Configuração da confirmação por email
    MAIL_USERNAME = os.getenv("EMAIL_USER")
    MAIL_PASSWORD = os.getenv("EMAIL_PASS")
    MAIL_SERVER = os.getenv("SMTP_SERVER")
    MAIL_PORT = int(os.getenv("SMTP_PORT"))
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    #Configuraçção do banco de dados
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")