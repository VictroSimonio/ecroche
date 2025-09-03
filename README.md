Projeto E-commerce: Crocheteando Nani
## 📖 Sobre o Projeto:

Este projeto consiste no desenvolvimento de um site de e-commerce completo para a cliente Naiara Ribeiro, focado na venda de seus produtos artesanais de crochê.

Atualmente, a cliente utiliza o Instagram como principal canal de vendas. O objetivo deste projeto é criar uma plataforma dedicada que não apenas profissionalize sua presença online, mas também otimize e automatize a gestão de vendas, oferecendo uma experiência de compra mais fluida e segura para seus clientes.

## Funcionalidades Principais:

O projeto foi planejado para incluir as seguintes funcionalidades:

Catálogo de Produtos: Exibição clara e organizada de todos os produtos, com fotos, descrições e preços.

Busca Avançada: Ferramentas de busca e filtros para que os clientes encontrem produtos facilmente.

Carrinho de Compras: Funcionalidade padrão de e-commerce para adicionar e gerenciar itens antes da compra.

Integração com Pagamentos: Integração via API com a plataforma Mercado Pago para processar pagamentos de forma segura e automática.

Cálculo de Frete: Sistema para cálculo automático de frete e opções de envio.

Design Intuitivo e Responsivo: Interface agradável e adaptável para uma ótima experiência de usuário em qualquer dispositivo (desktop, tablets e celulares).

Painel Administrativo: Uma área para a gestão completa do site, incluindo cadastro de produtos, controle de estoque e visualização de pedidos.

Canal de Contato: Formulários e links diretos para facilitar a comunicação entre os clientes e a administradora.

## Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

Tecnologia	Finalidade
Python	Linguagem principal do backend.
Django	Framework robusto para desenvolvimento rápido e seguro da aplicação.
HTML5	Linguagem de marcação para a estrutura das páginas.
CSS3	Estilização e design visual do site.
JavaScript	Interatividade e dinamismo no front-end.
SQLite	Banco de dados para armazenamento de produtos, clientes e pedidos.
Mercado Pago API	Integração para o processamento de pagamentos.

## Como Executar o Projeto Localmente:

Siga os passos abaixo para configurar e executar o projeto em seu ambiente de desenvolvimento.

Clone o repositório:

git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio

Crie e ative um ambiente virtual:

Bash

# Comando para criar o ambiente
python -m venv venv

# Ativar no Windows
.\venv\Scripts\activate

# Ativar no Linux/Mac
source venv/bin/activate
Instale as dependências:

Bash

pip install -r requirements.txt
Aplique as migrações do banco de dados:

Bash

python manage.py migrate
Crie um superusuário para acessar a área de administração:

Bash

python manage.py createsuperuser
Inicie o servidor de desenvolvimento:

Bash

python manage.py runserver
Abra seu navegador e acesse http://127.0.0.1:8000/ para ver o site.

- Autor:

Desenvolvido por Victor Simão e Iago Campanhol.

LinkedIn: https://www.linkedin.com/in/victor-sim%C3%A3o-de-matos-9a3724299/

GitHub: https://github.com/Victrosimao



