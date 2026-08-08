<div align='center'>
    <img
        src='docs/assets/logo.jpg'
        loading='lazy'
        alt='Logo IFSports'
        width='500'
    >
</div>

## 🏆 O que é o IFSports

O **IFSports** é uma plataforma web de gestão esportiva desenvolvida para o **IFRN** - campus Caicó. O sistema visa substituir processos manuais e aplicativos de mensagens na organização de treinos escolares, centralizando toda a gestão das atividades esportivas em um único lugar, tanto para professores quanto para estudantes.

<!-- Imagem ou GIF do sistema -->
<div align='center'>
    <!-- Espaço reservado para screenshot ou GIF do sistema em uso -->
</div>

### 📖 Funcionalidades

O sistema oferece funcionalidades distintas para professores e alunos, além de um módulo de gamificação para incentivar a participação. Abaixo está uma tabela com as principais funcionalidades.

| Funcionalidade                | Como funciona                                                                                          |
| ------------------------------ | -------------------------------------------------------------------------------------------------------- |
| **Gestão de treinos**          | Professores criam treinos avulsos ou fixos semanais, definindo modalidade, horário e limite de vagas    |
| **Inscrição e check-in**       | Alunos se inscrevem em treinos disponíveis e confirmam presença por meio de check-in                    |
| **Validação de frequência**    | Professores validam presença ou ausência dos alunos inscritos em cada ocorrência de treino               |
| **Treinos recorrentes**        | Treinos fixos semanais geram automaticamente uma nova ocorrência a cada validação, sem recriação manual  |
| **Gamificação**                | Sistema de pontos, níveis e conquistas desbloqueadas conforme a participação do aluno                    |
| **Ranking**                    | Classificação geral dos alunos por pontuação acumulada                                                  |
| **Avisos e FAQ**                | Espaço para comunicados gerais e perguntas frequentes                                                    |
| **Mural de fotos**              | Galeria de fotos das atividades esportivas                                                               |
| **Notificações**                | Notificações em tempo real sobre validações, conquistas e avisos                                          |
| **Autenticação institucional**  | Cadastro e login restritos a e-mails institucionais do IFRN, com confirmação de conta por e-mail          |

### ⚒️ Tecnologias

Abaixo está uma tabela com as principais tecnologias usadas no desenvolvimento do sistema.

| Tecnologia        | Funcionalidade                                                              |
| ------------------ | ----------------------------------------------------------------------------- |
| `Flask`            | Microframework `Python` usado como base do sistema (backend e renderização)  |
| `Flask-SQLAlchemy` | ORM utilizado para modelagem e acesso ao banco de dados                      |
| `Flask-Login`      | Gerenciamento de autenticação e sessão de usuários                           |
| `Flask-WTF`        | Criação e validação de formulários                                           |
| `Flask-Mail`       | Envio de e-mails de confirmação de conta e redefinição de senha              |
| `Flask-SocketIO`   | Comunicação em tempo real (notificações)                                     |
| `MySQL`            | Banco de dados relacional utilizado para armazenar dados e informações       |
| `pytest`           | Framework de testes automatizados (unitários e de integração)                |

---

## ▶️ Como executar o projeto

> [!IMPORTANT]
> O projeto usa `Flask` com `Python`. É necessário ter o `Python` e o `MySQL` instalados.

### 🧑‍💻 Modo desenvolvedor

1. **Clone o repositório e acesse-o**

    ```git
    git clone https://github.com/Daviddutra07/IFSports---PP.git
    cd IFSports---PP
    ```

2. **Crie e ative um ambiente virtual**

    ```bash
    python -m venv venv

    # Windows
    venv\Scripts\activate

    # Linux/Mac
    source venv/bin/activate
    ```

3. **Instale as dependências**

    ```bash
    pip install -r requirements.txt
    ```

4. **Crie um arquivo `.env` na raiz do projeto para as variáveis de ambiente e adicione**

    ```.env
    # =====================< Autenticação >=====================
    SECRET_KEY=<SUA-CHAVE-SECRETA>

    # ====================< Banco de dados >====================
    DATABASE_URL=mysql://usuario:senha@localhost:3306/nome_do_banco

    # ======================< E-mail >===========================
    EMAIL_USER=<SEU-EMAIL>
    EMAIL_PASS=<SUA-SENHA-DE-APP>
    SMTP_SERVER=<SEU-SERVIDOR-SMTP>
    SMTP_PORT=<PORTA-SMTP>
    ```

5. **Crie o banco de dados no MySQL**

    ```sql
    CREATE DATABASE nome_do_banco;
    ```

6. **Inicie o servidor**

    ```bash
    python run.py
    ```

> [!TIP]
> Use ambiente virtual 😉

Após finalizar esse passo a passo, a aplicação estará disponível em [`http://localhost:5000`](http://localhost:5000)

### 🧪 Executando os testes

O projeto conta com uma suíte de testes automatizados (unitários e de integração) construída com `pytest`.

```bash
pip install -r requirements-devtests.txt
python -m pytest tests/ -v
```

---

## 📄 Documentos

- [Sobre o Projeto](docs/sobre_o_projeto.md)
- [Requisitos Funcionais](docs/requisitos_funcionais.md)
- [Requisitos Não Funcionais](docs/requisitos_nao_funcionais.md)
- [Trabalhos Relacionados](docs/trabalhos_relacionados.md)
- [Relatório de Testes (Unitários, Integração e Sistema)](docs/relatorio_de_testes.pdf)

## 😁 Equipe

| Nome                                                      | Papel no projeto |
| ----------------------------------------------------------- | ----------------- |
| [Carla Gabriele](https://github.com/CarlaGabriiele)         | Desenvolvedora     |
| [David Gabriel](https://github.com/Daviddutra07)            | Desenvolvedor      |
| [Emmily Kettily](https://github.com/Emmily01)                | Desenvolvedora     |
| [Guilherme David](https://github.com/Guilherme-David)        | Desenvolvedor      |
| [Ingrid Monteiro](https://github.com/ingridmont)              | Desenvolvedora     |
| [Romerito Campos](https://github.com/RoCampos)                | Orientador         |
| Hudson Pablo de Oliveira Bezerra                             | Coorientador       |

## ⚖️ Licença

O sistema foi construído como **Trabalho de Conclusão de Curso (TCC)** pelos alunos do **IFRN** - campus Caicó.

- [Licença MIT](LICENSE)
