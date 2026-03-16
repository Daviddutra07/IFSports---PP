from app.extensions import db
from app.models.conquistas import Conquista


def inserir_conquistas():

    if Conquista.query.first():
        return

    conquistas = [

        Conquista(
            cnq_nome="Primeira inscrição!",
            cnq_descricao="Realize sua primeira inscrição em treino.",
            cnq_tipo="inscricao",
            cnq_meta=1,
            cnq_pontos_bonus=5,
            cnq_tier="normal",
            cnq_tier_valor=2
        ),

        Conquista(
            cnq_nome="Primeiro treino!",
            cnq_descricao="Participe do seu primeiro treino.",
            cnq_tipo="presenca",
            cnq_meta=1,
            cnq_pontos_bonus=5,
            cnq_tier="normal",
            cnq_tier_valor=2
        ),

        Conquista(
            cnq_nome="Primeira avaliação!",
            cnq_descricao="Receba sua primeira avaliação em treino.",
            cnq_tipo="primeira_avaliacao",
            cnq_meta=1,
            cnq_pontos_bonus=5,
            cnq_tier="normal",
            cnq_tier_valor=2
        ),

        Conquista(
            cnq_nome="Atleta ativo!",
            cnq_descricao="Participe de 5 treinos.",
            cnq_tipo="presenca",
            cnq_meta=5,
            cnq_pontos_bonus=10,
            cnq_tier="bronze",
            cnq_tier_valor=3
        ),

        Conquista(
            cnq_nome="Planejador!",
            cnq_descricao="Faça 10 inscrições em treinos.",
            cnq_tipo="inscricao",
            cnq_meta=10,
            cnq_pontos_bonus=10,
            cnq_tier="ativo",
            cnq_tier_valor=2
        ),

        Conquista(
            cnq_nome="Pontuador!",
            cnq_descricao="Alcance 250 pontos.",
            cnq_tipo="pontos",
            cnq_meta=250,
            cnq_pontos_bonus=10,
            cnq_tier="bronze",
            cnq_tier_valor=3
        ),

        Conquista(
            cnq_nome="Entrou no ranking!",
            cnq_descricao="Apareça no ranking de pontuação.",
            cnq_tipo="ranking",
            cnq_meta=9999,
            cnq_pontos_bonus=10,
            cnq_tier="bronze",
            cnq_tier_valor=3
        ),

        Conquista(
            cnq_nome="Nota perfeita!",
            cnq_descricao="Receba uma nota máxima (5).",
            cnq_tipo="nota_perfeita",
            cnq_meta=5,
            cnq_pontos_bonus=10,
            cnq_tier="prata",
            cnq_tier_valor=4
        ),

        Conquista(
            cnq_nome="Atleta dedicado!",
            cnq_descricao="Participe de 10 treinos.",
            cnq_tipo="presenca",
            cnq_meta=10,
            cnq_pontos_bonus=15,
            cnq_tier="prata",
            cnq_tier_valor=4
        ),

        Conquista(
            cnq_nome="Comprometido!",
            cnq_descricao="Faça 25 inscrições em treinos.",
            cnq_tipo="inscricao",
            cnq_meta=25,
            cnq_pontos_bonus=15,
            cnq_tier="prata",
            cnq_tier_valor=4
        ),

        Conquista(
            cnq_nome="Top 10!",
            cnq_descricao="Fique entre os 10 primeiros do ranking.",
            cnq_tipo="ranking",
            cnq_meta=10,
            cnq_pontos_bonus=25,
            cnq_tier="prata",
            cnq_tier_valor=4,
        ),

        Conquista(
            cnq_nome="Competidor!",
            cnq_descricao="Alcance 500 pontos.",
            cnq_tipo="pontos",
            cnq_meta=500,
            cnq_pontos_bonus=20,
            cnq_tier="prata",
            cnq_tier_valor=4
        ),

        Conquista(
            cnq_nome="Alta performance!",
            cnq_descricao="Mantenha média de notas maior ou igual a 4 (mínimo 3 avaliações).",
            cnq_tipo="media",
            cnq_meta=4,
            cnq_pontos_bonus=20,
            cnq_tier="ouro",
            cnq_tier_valor=5,
        ),

        Conquista(
            cnq_nome="Veterano do esporte!",
            cnq_descricao="Participe de 25 treinos.",
            cnq_tipo="presenca",
            cnq_meta=25,
            cnq_pontos_bonus=25,
            cnq_tier="ouro",
            cnq_tier_valor=5
        ),

        Conquista(
            cnq_nome="Top 3!",
            cnq_descricao="Fique entre os 3 primeiros do ranking.",
            cnq_tipo="ranking",
            cnq_meta=3,
            cnq_pontos_bonus=40,
            cnq_tier="ouro",
            cnq_tier_valor=5
        ),

        Conquista(
            cnq_nome="Desafiante!",
            cnq_descricao="Alcance 1000 pontos.",
            cnq_tipo="pontos",
            cnq_meta=1000,
            cnq_pontos_bonus=50,
            cnq_tier="ouro",
            cnq_tier_valor=5
        ),

        Conquista(
            cnq_nome="Sempre inscrito!",
            cnq_descricao="Faça 50 inscrições em treinos.",
            cnq_tipo="inscricao",
            cnq_meta=50,
            cnq_pontos_bonus=25,
            cnq_tier="ouro",
            cnq_tier_valor=5
        ),

        Conquista(
            cnq_nome="Elite esportiva!",
            cnq_descricao="Mantenha média de notas maior ou igual a 4.5 (mínimo 3 avaliações).",
            cnq_tipo="media",
            cnq_meta=4.5,
            cnq_pontos_bonus=35,
            cnq_tier="lendária",
            cnq_tier_valor=6
        ),
        
        Conquista(
            cnq_nome="Campeão!",
            cnq_descricao="Alcance a primeira posição no ranking.",
            cnq_tipo="ranking",
            cnq_meta=1,
            cnq_pontos_bonus=60,
            cnq_tier="lendária",
            cnq_tier_valor=6
        ),


        Conquista(
            cnq_nome="Lenda dos treinos!",
            cnq_descricao="Participe de 50 treinos.",
            cnq_tipo="presenca",
            cnq_meta=50,
            cnq_pontos_bonus=40,
            cnq_tier="lendária",
            cnq_tier_valor=6
        ),

]


    db.session.add_all(conquistas)
    db.session.commit()