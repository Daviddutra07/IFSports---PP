# Requisitos Não Funcionais

Este documento lista os requisitos não funcionais (RNF) do sistema IFSports, levantados durante o desenvolvimento do projeto.

| ID     | Categoria                            | Descrição |
| ------ | ------------------------------------- | --------- |
| RNF01  | Responsividade                        | O sistema deve ser responsivo, permitindo sua utilização em computadores, tablets e smartphones, adaptando automaticamente sua interface aos diferentes tamanhos de tela. |
| RNF02  | Usabilidade e Acessibilidade          | O sistema deve oferecer uma interface intuitiva e responsiva, adotando boas práticas de usabilidade e acessibilidade, como contraste adequado entre elementos, identificação dos campos dos formulários, feedback visual das ações do usuário, navegação consistente e compatibilidade com navegação por teclado sempre que possível. |
| RNF03  | Segurança                             | O sistema deve garantir que apenas usuários autenticados tenham acesso às funcionalidades restritas, utilizando autenticação baseada em sessões, armazenamento seguro de senhas por meio de hash criptográfico, controle de permissões por perfil de usuário e mecanismos de confirmação de identidade para operações sensíveis, como confirmação de e-mail e redefinição de senha. |
| RNF04  | Desempenho                            | O sistema deve apresentar tempo de resposta adequado para as principais funcionalidades, proporcionando navegação fluida mesmo em conexões de velocidade reduzida. |
| RNF05  | Persistência e Integridade dos Dados  | O sistema deve armazenar as informações em banco de dados relacional normalizado, preservando a integridade, consistência e persistência dos dados. |
| RNF06  | Tecnologias Utilizadas                | O sistema deve ser desenvolvido utilizando tecnologias consolidadas para aplicações web, incluindo HTML5, CSS3, JavaScript, Python, Flask, Jinja2 e MySQL. |
| RNF07  | Manutenibilidade                      | O sistema deve possuir arquitetura modular baseada no padrão MVC, com separação entre modelos, controladores, serviços e templates, facilitando futuras correções, manutenção e evolução do software. |
| RNF08  | Disponibilidade                       | O sistema deve permanecer disponível para utilização sempre que o servidor da aplicação estiver em funcionamento, permitindo o acesso simultâneo dos usuários por meio de navegadores web. |
