from app.extensions import db
from app.models.faq import FAQ


def inserir_faqs():

    if FAQ.query.first():
        return

    faqs = [

        FAQ(
            faq_pergunta="O que é o IFSports?",
            faq_resposta=(
                "O IFSports é uma plataforma desenvolvida para auxiliar na gestão "
                "das atividades esportivas do IFRN Campus Caicó. O sistema permite que alunos "
                "acompanhem treinos, realizem inscrições, registrem sua participação "
                "e acompanhem seu desempenho nas modalidades esportivas."
            ),
            faq_categoria="Sobre o IFSports",
            faq_ordem=1
        ),

        FAQ(
            faq_pergunta="Como faço inscrição em um treino?",
            faq_resposta=(
                "Para participar de um treino, acesse a área de treinos disponíveis, "
                "escolha a modalidade desejada e realize sua inscrição. Após a "
                "confirmação, sua vaga será registrada e você poderá acompanhar "
                "informações como data, horário e professor responsável."
            ),
            faq_categoria="Treinos",
            faq_ordem=2
        ),

        FAQ(
            faq_pergunta="Como ganho pontos?",
            faq_resposta=(
                "Os pontos são conquistados através da participação nas atividades "
                "esportivas. A presença nos treinos, avaliações de desempenho em cada treino e "
                "alcançar conquistas da plataforma contribuem para aumentar sua "
                "pontuação e evolução no sistema."
            ),
            faq_categoria="Gamificação",
            faq_ordem=3
        ),

        FAQ(
            faq_pergunta="O que são as conquistas do IFSports?",
            faq_resposta=(
                "As conquistas são recompensas virtuais obtidas pelos alunos ao "
                "atingirem determinados objetivos dentro da plataforma. Elas "
                "representam marcos de participação, dedicação e desempenho "
                "nas atividades esportivas."
            ),
            faq_categoria="Gamificação",
            faq_ordem=4
        ),

        FAQ(
            faq_pergunta="Como funciona o ranking?",
            faq_resposta=(
                "O ranking organiza os participantes conforme a pontuação acumulada "
                "nas atividades esportivas. Ele permite acompanhar o desempenho dos "
                "alunos e valoriza aqueles que possuem maior participação e "
                "dedicação nas atividades."
            ),
            faq_categoria="Gamificação",
            faq_ordem=5
        ),

        FAQ(
            faq_pergunta="Como vejo os avisos?",
            faq_resposta=(
                "Os avisos publicados pelos professores podem ser acessados através "
                "da área de comunicação do sistema. Nela, os alunos podem acompanhar "
                "informações sobre treinos, eventos, alterações de horários e "
                "outras novidades relacionadas às atividades esportivas."
            ),
            faq_categoria="Comunicação",
            faq_ordem=6
        ),

        FAQ(
            faq_pergunta="Quem pode utilizar o IFSports?",
            faq_resposta=(
                "O IFSports é destinado aos participantes das atividades esportivas "
                "do IFRN. Alunos podem realizar inscrições, acompanhar sua evolução "
                "e participar da gamificação, enquanto professores podem gerenciar "
                "treinos, validar frequências e publicar informações."
            ),
            faq_categoria="Sobre o IFSports",
            faq_ordem=7
        ),

        FAQ(
            faq_pergunta="Como acompanho minha evolução esportiva?",
            faq_resposta=(
                "A evolução esportiva pode ser acompanhada através do painel do "
                "aluno, onde são exibidas informações como pontuação, frequência "
                "nos treinos, conquistas alcançadas e desempenho nas modalidades."
            ),
            faq_categoria="Desempenho",
            faq_ordem=8
        ),

        FAQ(
            faq_pergunta="Como nasceu o IFSports?",
            faq_resposta=("O IFSports nasceu com o objetivo de aproximar alunos e esporte, tornando a participação esportiva mais organizada, acessível e integrada dentro do IFRN."
            ),
            faq_categoria="Sobre o IFSports",
            faq_ordem=9
        )

    ]

    db.session.add_all(faqs)
    db.session.commit()