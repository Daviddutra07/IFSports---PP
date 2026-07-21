import pytest

from app import create_app
from app.extensions import db


@pytest.fixture(scope="session")
def app():

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "MAIL_SUPPRESS_SEND": True,
        "LOGIN_DISABLED": False,
        "SERVER_NAME": "localhost"
    })

    with app.app_context():

        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def limpar_banco(app):

    with app.app_context():

        yield

        db.session.rollback()

        for tabela in reversed(db.metadata.sorted_tables):
            db.session.execute(tabela.delete())

        db.session.commit()