PedroBarbearia — Sistema de Agendamento Online

Sistema fullstack desenvolvido para simular um ambiente real de agendamento de horários para barbearia.

O cliente pode escolher barbeiro, serviço e horário disponível, realizando o agendamento com validação de conflito de horários e integração completa entre frontend e backend.

Projeto desenvolvido com foco em portfólio, aplicando conceitos reais de API REST, regras de negócio e persistência em banco de dados.

Funcionalidades

Cadastro de barbeiros

Cadastro de serviços vinculados a barbeiros

Agendamento de horário pelo cliente

Bloqueio automático de horários ocupados

Validação de conflito por intervalo de tempo

Interface dark premium com animações suaves

Mensagem persistente de confirmação

Tecnologias Utilizadas
Backend

Python

FastAPI

SQLAlchemy

SQLite

Uvicorn

Frontend

HTML5

CSS3

JavaScript (Fetch API)

Regras de Negócio

Cada serviço possui duração em minutos

Um barbeiro não pode atender dois clientes em horários que se sobrepõem

Horários já agendados ficam automaticamente indisponíveis

A API garante integridade dos dados antes de criar um agendamento

Estrutura do Projeto
PedroBarbearia/
│
├── main.py
├── agendamento.db
│
├── static/
│   └── index.html
│
└── README.md

Como Executar o Projeto Localmente
1. Clonar o repositório
git clone https://github.com/seu-usuario/pedrobarbearia.git
cd pedrobarbearia

2. Criar ambiente virtual (opcional)

Windows:

python -m venv venv
venv\Scripts\activate


Linux/Mac:

python -m venv venv
source venv/bin/activate

3. Instalar dependências
pip install fastapi uvicorn sqlalchemy

4. Rodar o backend
python -m uvicorn main:app --reload


A API ficará disponível em:

http://127.0.0.1:8000


Documentação automática (Swagger):

http://127.0.0.1:8000/docs

5. Rodar o frontend

Abrir o arquivo:

static/index.html


Ou utilizar um servidor local:

python -m http.server 5500


E acessar:

http://127.0.0.1:5500/static/index.html

Melhorias Futuras

Painel administrativo separado

Autenticação para administrador

Deploy em ambiente de produção

Integração com PostgreSQL

Melhor responsividade para dispositivos móveis

Autor

Pedro Henrique
Projeto desenvolvido para portfólio com foco em backend Python e desenvolvimento de APIs REST.