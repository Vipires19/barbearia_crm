# 💈 Sistema de Gestão de Barbearia

Sistema web completo desenvolvido em Django para gerenciamento de barbearia, incluindo agendamentos online, gestão de profissionais, serviços, vendas de vestuário e integração com WhatsApp.

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Funcionalidades](#-funcionalidades)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Deploy](#-deploy)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

## 🎯 Sobre o Projeto

Sistema completo de gestão para barbearias modernas, oferecendo uma plataforma web intuitiva para administradores e clientes. O sistema permite gerenciar serviços, profissionais, agendamentos, vendas de produtos e comunicação automatizada via WhatsApp.

## 🛠 Tecnologias Utilizadas

### Backend
- **Django 4.2.7** - Framework web Python
- **MongoDB** - Banco de dados NoSQL via MongoEngine
- **MongoEngine 0.24.2** - ODM para MongoDB
- **Django-MongoEngine 0.5.6** - Integração Django + MongoDB

### Integrações e APIs
- **WAHA API** - Integração WhatsApp Business
- **Requests 2.31.0** - Cliente HTTP para APIs externas
- **Django CORS Headers 4.3.1** - Controle de CORS

### Processamento de Imagens
- **Pillow 10.0.1** - Manipulação de imagens

### Deployment e Servidor
- **WhiteNoise 6.5.0** - Servir arquivos estáticos
- **Gunicorn** - Servidor WSGI para produção
- **Docker** - Containerização

### Utilitários
- **Python-dotenv 1.0.0** - Gerenciamento de variáveis de ambiente

## ✨ Funcionalidades

### 👥 Gestão de Clientes
- Cadastro e perfil de clientes
- Histórico de agendamentos e compras
- Identificação de clientes frequentes
- Estatísticas de consumo por cliente
- Preferências e observações

### 💇 Gestão de Serviços
- Cadastro de serviços com categorias
- Definição de preços e duração
- Upload de imagens dos serviços
- Atribuição de profissionais habilitados
- Controle de disponibilidade

### 👨‍💼 Gestão de Profissionais
- Cadastro completo de profissionais
- Perfil com foto, bio e especialidades
- Sistema de avaliações e notas
- Controle de horários de disponibilidade
- Configuração de dias e horários de trabalho
- Estatísticas de atendimentos

### 📅 Sistema de Agendamentos
- Agendamento online de serviços
- Seleção de profissional e horário disponível
- Visualização de agenda em tempo real
- Status de agendamentos (Agendado, Confirmado, Em Andamento, Concluído, Cancelado, Falta)
- Fila de agendamentos para administradores
- Histórico completo de agendamentos
- Cancelamento e reagendamento

### 🛍️ Loja de Vestuário
- Cadastro de categorias de produtos
- Gestão de produtos com estoque
- Controle de vendas
- Relatórios de vendas
- Integração com sistema de clientes

### 📊 Dashboard Administrativo
- Estatísticas gerais da barbearia
- Receita e agendamentos do dia
- Gráficos de vendas e serviços mais procurados
- Relatórios de desempenho
- Controle de status da barbearia (aberta/fechada)

### 📱 Integração WhatsApp
- Confirmação automática de agendamentos
- Envio de lembretes
- Notificações de status
- Integração com agente de WhatsApp
- API para comunicação automatizada

### 🔐 Autenticação e Segurança
- Sistema de login/logout
- Controle de acesso administrativo
- Proteção CSRF
- Validação de dados

## 📦 Pré-requisitos

Antes de começar, você precisa ter instalado:

- **Python 3.12+**
- **MongoDB** (local ou MongoDB Atlas)
- **pip** (gerenciador de pacotes Python)
- **Git** (para clonar o repositório)
- **Docker** (opcional, para deploy via container)

## 🚀 Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/barbearia.git
cd barbearia
```

2. **Crie um ambiente virtual**
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

4. **Configure as variáveis de ambiente**
```bash
# Copie o arquivo de exemplo
cp env.example local.env

# Edite o arquivo local.env com suas configurações
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` ou `local.env` na raiz do projeto com as seguintes variáveis:

```env
# MongoDB
MONGO_USER=seu_usuario_mongodb
MONGO_PASS=sua_senha_mongodb

# WhatsApp (WAHA API)
WAHA_API_URL=http://localhost:3000
WAHA_SESSION_NAME=default
WAHA_TIMEOUT=30

# Django Secret Key (gerar uma nova para produção)
SECRET_KEY=sua_secret_key_aqui

# Configurações Django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Configuração do MongoDB

O sistema utiliza MongoDB Atlas ou MongoDB local. Configure a string de conexão no arquivo `settings.py` ou através das variáveis de ambiente.

### Migrações e Banco de Dados

Como o sistema utiliza MongoDB, não são necessárias migrações tradicionais do Django. O SQLite é usado apenas para o Django Admin.

```bash
# Criar superusuário (para acesso ao admin)
python manage.py createsuperuser
```

## 🎮 Uso

### Iniciar o Servidor de Desenvolvimento

```bash
# Windows
python manage.py runserver

# Ou usando o script batch
start.bat
```

O servidor estará disponível em `http://localhost:8000`

### Acessar o Sistema

- **Página Principal**: `http://localhost:8000/`
- **Login Admin**: `http://localhost:8000/login/`
- **Dashboard**: `http://localhost:8000/dashboard/`
- **Loja de Vestuário**: `http://localhost:8000/vestuario/`

### População de Dados Iniciais

```bash
# Popular dados de exemplo no MongoDB
python populate_mongo.py
```

## 📁 Estrutura do Projeto

```
barbearia/
├── barbearia/              # Configurações principais do Django
│   ├── settings.py         # Configurações do projeto
│   ├── urls.py            # URLs principais
│   └── wsgi.py            # WSGI para produção
│
├── servicos/              # App principal de serviços
│   ├── models_mongo.py    # Modelos MongoDB
│   ├── views.py           # Views públicas
│   ├── admin_views.py     # Views administrativas
│   ├── urls.py            # Rotas do app
│   └── templates/         # Templates HTML
│
├── agendamentos/          # App de agendamentos
│   ├── views.py           # Views de agendamentos
│   └── webhook_views.py   # Webhooks WhatsApp
│
├── templates/             # Templates base
├── static/                # Arquivos estáticos (CSS, JS, imagens)
├── media/                 # Upload de arquivos
├── requirements.txt       # Dependências Python
├── Dockerfile             # Configuração Docker
├── docker-compose.yml     # Orquestração Docker
└── README.md             # Este arquivo
```

## 🐳 Deploy

### Docker

```bash
# Build da imagem
docker build -t barbearia-app .

# Executar container
docker run -p 8000:8000 --env-file local.env barbearia-app
```

### Docker Compose

```bash
docker-compose up -d
```

### Produção

Para produção, recomendamos:

1. Configurar `DEBUG=False` em `settings.py`
2. Configurar `ALLOWED_HOSTS` adequadamente
3. Usar um servidor WSGI como Gunicorn
4. Configurar servidor web (Nginx/Apache)
5. Configurar SSL/HTTPS
6. Usar variáveis de ambiente seguras

## 🤝 Contribuindo

Contribuições são sempre bem-vindas! Para contribuir:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Desenvolvido com ❤️ para modernizar a gestão de barbearias.

## 📞 Suporte

Para dúvidas, sugestões ou problemas, abra uma [issue](https://github.com/seu-usuario/barbearia/issues) no repositório.

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!
