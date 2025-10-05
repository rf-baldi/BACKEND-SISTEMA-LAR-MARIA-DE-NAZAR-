# Backend - Sistema de Gerenciamento de Cestas Básicas

Backend desenvolvido em Flask para o sistema de gerenciamento de cestas básicas do Lar Maria de Nazaré.

## Tecnologias Utilizadas

- **Python 3.11**
- **Flask** - Framework web
- **PostgreSQL** - Banco de dados (Supabase)
- **JWT** - Autenticação
- **bcrypt** - Hash de senhas
- **Gunicorn** - Servidor WSGI para produção

## Estrutura do Projeto

```
backend_cestas/
├── app/
│   ├── __init__.py          # Inicialização da aplicação Flask
│   ├── routes/              # Rotas da API
│   │   ├── __init__.py
│   │   ├── auth.py          # Autenticação
│   │   ├── families.py      # Gerenciamento de famílias
│   │   ├── donations.py     # Gerenciamento de doações
│   │   ├── distributions.py # Gerenciamento de distribuições
│   │   └── dashboard.py     # Estatísticas e dashboard
│   ├── models/              # Modelos de dados (futuro)
│   │   └── __init__.py
│   └── utils/               # Utilitários
│       ├── __init__.py
│       ├── database.py      # Conexão e inicialização do banco
│       └── auth.py          # Funções de autenticação
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore               # Arquivos ignorados pelo Git
├── requirements.txt         # Dependências Python
├── run.py                   # Arquivo principal para executar a aplicação
└── README.md                # Este arquivo
```

## Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com base no `.env.example`:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:@123456@@db.muxvqmwvscevwjarjjoc.supabase.co:5432/postgres

# Supabase Configuration
SUPABASE_URL=https://muxvqmwvscevwjarjjoc.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-aqui

# CORS Configuration
FRONTEND_URL=https://seu-frontend.com
```

### 2. Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 3. Inicialização do Banco de Dados

O banco de dados será inicializado automaticamente na primeira execução. As seguintes tabelas serão criadas:

- `users` - Usuários do sistema
- `families` - Famílias cadastradas
- `children` - Filhos das famílias
- `donations` - Doações recebidas
- `distributions` - Distribuições realizadas

**Usuário padrão criado:**
- Username: `admin`
- Password: `admin123`

## Executando Localmente

### Modo Desenvolvimento

```bash
export FLASK_ENV=development
python run.py
```

### Modo Produção (com Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## API Endpoints

### Autenticação

#### POST /api/auth/login
Login de usuário.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "username": "admin"
  }
}
```

#### GET /api/auth/me
Retorna informações do usuário autenticado.

**Headers:**
```
Authorization: Bearer <token>
```

#### POST /api/auth/logout
Logout do usuário (simbólico).

### Famílias

#### GET /api/families
Lista todas as famílias.

#### POST /api/families
Cria uma nova família.

**Request:**
```json
{
  "name": "Família Silva",
  "fatherName": "João Silva",
  "motherName": "Maria Silva",
  "numberOfChildren": 2,
  "children": [
    {"name": "Pedro", "age": 10},
    {"name": "Ana", "age": 8}
  ],
  "isEmployed": false,
  "receivesGovernmentAid": true,
  "governmentAidType": "Bolsa Família",
  "hasCriticalFactor": false,
  "criticalFactorNotes": ""
}
```

#### GET /api/families/:id
Busca uma família por ID.

#### PUT /api/families/:id
Atualiza uma família.

#### DELETE /api/families/:id
Deleta uma família.

### Doações

#### GET /api/donations
Lista todas as doações.

#### POST /api/donations
Cria uma nova doação (entrada de cestas).

**Request:**
```json
{
  "responsibleName": "João Doador",
  "cpf": "123.456.789-00",
  "phone": "(11) 98765-4321",
  "quantity": 10,
  "type": "entry"
}
```

#### GET /api/donations/total
Retorna o total de cestas doadas.

### Distribuições

#### GET /api/distributions
Lista todas as distribuições.

#### POST /api/distributions
Cria uma nova distribuição (saída de cestas).

**Request:**
```json
{
  "familyId": "uuid",
  "familyName": "Família Silva",
  "pickupPersonName": "Maria Silva",
  "quantity": 1,
  "date": "2025-10-05T10:00:00Z"
}
```

#### GET /api/distributions/total
Retorna o total de cestas distribuídas.

### Dashboard

#### GET /api/dashboard/stats
Retorna estatísticas gerais do sistema.

**Response:**
```json
{
  "totalFamilies": 50,
  "totalDonations": 200,
  "totalDistributions": 150,
  "availableBaskets": 50,
  "recentDistributions": [...]
}
```

## Deploy no Render

### 1. Criar Web Service

1. Acesse [Render](https://render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name:** backend-cestas-basicas
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app()"`

### 2. Configurar Variáveis de Ambiente

No dashboard do Render, adicione as seguintes variáveis de ambiente:

- `DATABASE_URL` - URL de conexão do PostgreSQL (Supabase)
- `SUPABASE_URL` - URL do projeto Supabase
- `SUPABASE_ANON_KEY` - Chave anônima do Supabase
- `SUPABASE_SERVICE_KEY` - Chave de serviço do Supabase
- `SECRET_KEY` - Chave secreta para JWT
- `FRONTEND_URL` - URL do frontend (para CORS)
- `FLASK_ENV` - `production`

### 3. Deploy

O Render fará o deploy automaticamente após o push para o repositório.

## Segurança

- Senhas são hasheadas com bcrypt
- Autenticação via JWT com expiração de 7 dias
- CORS configurado para permitir apenas origens específicas
- Validação de dados em todas as rotas
- Proteção contra SQL Injection (uso de prepared statements)

## Suporte

Para dúvidas ou problemas, entre em contato com o desenvolvedor.

## Licença

Este projeto é de uso interno do Lar Maria de Nazaré.
