# Gerador de Conteúdo com IA – Backend (Django + Railway)

Backend oficial do sistema de geração de conteúdo com IA desenvolvido para o projeto do Marcelo Levek.  
Ele fornece:

- Autenticação JWT
- Cadastro e login de usuários
- Controle de planos e assinaturas
- Webhook para validação automática de pagamento
- API protegida para geração de conteúdo via OpenAI
- Deploy totalmente compatível com Railway

---

## 🚀 Tecnologias

- Python 3.10+
- Django 5+
- Django REST Framework
- SimpleJWT (autenticação)
- PostgreSQL (Railway)
- Gunicorn (produção)

---

## 📂 Estrutura do Projeto

gerador_conteudo_backend/
│
├── core/ # Configurações principais do Django
├── accounts/ # Cadastro, login e autenticação JWT
├── billing/ # Planos, assinaturas e webhook do gateway
├── api/ # Endpoint de geração de conteúdo (IA)
│
├── requirements.txt
├── Procfile
├── .env.example # Modelo das variáveis de ambiente
└── README.md



---

## 🔧 Configuração Local

1. Criar ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate


pip install -r requirements.txt


DEBUG=True
SECRET_KEY=uma_chave_local
DATABASE_URL=sqlite:///db.sqlite3
OPENAI_API_KEY=sua_chave


python manage.py migrate


python manage.py runserver

### Autenticação
POST /auth/register/
POST /auth/login/

### Webhook do gateway de pagamento
POST /billing/webhook/

### GePOST /api/gerar/
POST /api/gerar/
Authorization: Bearer <token JWT>


### 🚀 Deploy no Railway

Subir o projeto no GitHub.

No Railway → New Project > Deploy from GitHub.

Adicionar variáveis no Railway:
* DEBUG=False
* SECRET_KEY=chave_producao
* OPENAI_API_KEY=sua_chave
* DATABASE_URL=URL do PostgreSQL do Railway

### Rodar Migrações
railway run python manage.py migrate

### Pronto! API disponível em:
https://seu-app.railway.app/