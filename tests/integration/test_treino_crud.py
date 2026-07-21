from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.treinos import Treino
from app.models.users import User
from tests.factories import criar_treino
from tests.fixtures import *


def _payload_avulso(modalidade, nome="Treino Teste", quantidade="10", data="2026-08-01T18:00"):
    return {
        "trn_nome": nome,
        "trn_descricao": "Descrição de teste",
        "trn_quantidade": quantidade,
        "trn_mod_id": str(modalidade.mod_id),
        "trn_data": data,
    }


# ---------------------------------------------------------------------------
# criar
# ---------------------------------------------------------------------------

def test_criar_treino_sucesso(client, login_professor, modalidade):
    response = client.post(
        "/treinos/criar",
        data=_payload_avulso(modalidade),
        follow_redirects=True
    )

    assert response.status_code == 200
    assert "Treino criado com sucesso".encode("utf-8") in response.data

    treino = Treino.query.filter_by(trn_nome="Treino Teste").first()
    assert treino is not None
    assert treino.trn_pro_id == login_professor.usr_id


# ---------------------------------------------------------------------------
# editar
# ---------------------------------------------------------------------------

def test_editar_treino_sucesso(client, login_professor, treino, modalidade):
    response = client.post(
        f"/treinos/editar/{treino.trn_id}",
        data=_payload_avulso(modalidade, nome="Treino Editado", quantidade="15"),
        follow_redirects=True
    )

    assert response.status_code == 200
    assert "Treino editado com sucesso".encode("utf-8") in response.data

    treino_atualizado = Treino.query.get(treino.trn_id)
    assert treino_atualizado.trn_nome == "Treino Editado"
    assert treino_atualizado.trn_quantidade == 15


def test_editar_treino_de_outro_professor_nao_e_bloqueado(client, login_professor, modalidade):
    """
    Documenta um comportamento identificado no código-fonte: diferente de
    remover(), a rota editar() não verifica se o treino pertence ao
    professor autenticado. Hoje, qualquer professor logado consegue editar
    o treino de outro professor. Este teste registra o comportamento atual
    (não o comportamento desejável) para efeito de rastreabilidade.
    """
    outro_professor = User(
        usr_nome="Outro Professor",
        usr_email="outroprof@ifrn.edu.br",
        usr_senha_hash=generate_password_hash("12345678"),
        usr_tipo="professor",
        usr_confirmed=True,
        usr_is_active=True,
        usr_primeiro_login=False,
        usr_pontos=0,
        usr_img="images/default_profile.png"
    )
    db.session.add(outro_professor)
    db.session.commit()

    treino_do_outro = criar_treino(outro_professor, modalidade, nome="Treino do Outro Professor")

    response = client.post(
        f"/treinos/editar/{treino_do_outro.trn_id}",
        data=_payload_avulso(modalidade, nome="Nome Alterado Por Outro Professor"),
        follow_redirects=True
    )

    assert response.status_code == 200

    treino_atualizado = Treino.query.get(treino_do_outro.trn_id)
    assert treino_atualizado.trn_nome == "Nome Alterado Por Outro Professor"


# ---------------------------------------------------------------------------
# remover
# ---------------------------------------------------------------------------

def test_remover_treino_sucesso(client, login_professor, treino):
    response = client.post(
        f"/treinos/deletar/{treino.trn_id}",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert "Treino removido com sucesso".encode("utf-8") in response.data

    treino_atualizado = Treino.query.get(treino.trn_id)
    assert treino_atualizado.trn_ativo is False


def test_remover_treino_de_outro_professor_e_bloqueado(client, login_professor, modalidade):
    outro_professor = User(
        usr_nome="Outro Professor",
        usr_email="outroprof2@ifrn.edu.br",
        usr_senha_hash=generate_password_hash("12345678"),
        usr_tipo="professor",
        usr_confirmed=True,
        usr_is_active=True,
        usr_primeiro_login=False,
        usr_pontos=0,
        usr_img="images/default_profile.png"
    )
    db.session.add(outro_professor)
    db.session.commit()

    treino_do_outro = criar_treino(outro_professor, modalidade, nome="Treino Protegido")

    response = client.post(f"/treinos/deletar/{treino_do_outro.trn_id}")

    assert response.status_code == 404

    treino_intacto = Treino.query.get(treino_do_outro.trn_id)
    assert treino_intacto.trn_ativo is True
