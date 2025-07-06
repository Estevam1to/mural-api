# Mural Map API 🎨

API para exploração de arte urbana desenvolvida com FastAPI e MongoDB.

## 📋 Funcionalidades

### Fase 1 - Entidades Implementadas
- **Mural**: Obras de arte urbana com localização, artistas e tags
- **Artista**: Criadores das obras com biografia e redes sociais  
- **Local**: Localização geográfica com coordenadas e endereço
- **Usuário**: Sistema de usuários para avaliações
- **Avaliação**: Sistema de notas e comentários para murais

### Fase 2 - Banco de Dados
- **MongoDB** com Motor (driver assíncrono)
- **Embedding**: Local incorporado em Mural (1:1)
- **Referências**: artista_ids em Mural (1:N)
- **Relacionamento N:N**: Avaliação ligando Mural e Usuário
- **Índices otimizados** para consultas frequentes

### Fase 3 - Endpoints da API

#### 🎯 Murais
- `POST /murais` - F1: Criar mural
- `GET /murais` - F2: Listar com filtros (bairro, tag, artista)
- `GET /murais/{id}` - F3: CRUD completo
- `PUT /murais/{id}` - F3: CRUD completo  
- `DELETE /murais/{id}` - F3: CRUD completo
- `GET /murais/count` - F4: Contagem por bairro
- `GET /murais/top-artistas` - F7: Top 5 artistas
- `GET /murais/media-avaliacao-bairro` - F7: Média por bairro

#### 👨‍🎨 Artistas
- `POST /artistas` - Criar artista
- `GET /artistas` - Listar com paginação
- `GET /artistas/search` - Buscar por nome
- `GET/PUT/DELETE /artistas/{id}` - CRUD completo

#### 👤 Usuários  
- `POST /usuarios` - Cadastro
- `POST /usuarios/login` - Autenticação
- `GET/PUT/DELETE /usuarios/{id}` - CRUD completo

#### ⭐ Avaliações
- `POST /avaliacoes` - Criar avaliação (1-5)
- `GET /avaliacoes/mural/{id}` - Por mural
- `GET /avaliacoes/usuario/{id}` - Por usuário
- `GET /avaliacoes/mural/{id}/estatisticas` - Média e distribuição

#### 📍 Locais
- `POST /locais` - Criar local
- `GET /locais/search/cidade` - Buscar por cidade
- `GET /locais/search/bairro` - Buscar por bairro

### Fase 4 - Funcionalidades Avançadas
- **F5**: Paginação com `page` e `limit`
- **F6**: Filtros por atributos múltiplos
- **F7**: Agregações MongoDB para estatísticas

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10+
- MongoDB rodando na porta 27017

### Instalação

1. Clone o repositório:
```bash
git clone <url-do-repo>
cd mural_map
```

2. Instale as dependências:
```bash
pip install -e .
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. Execute a aplicação:
```bash
python main.py
```

A API estará disponível em: http://localhost:8000

## 📚 Documentação da API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗂️ Estrutura do Projeto

```
app/
├── models/          # Pydantic models
│   ├── mural.py
│   ├── artista.py
│   ├── usuario.py
│   ├── avaliacao.py
│   └── local.py
├── routes/          # FastAPI routers
│   ├── murais.py
│   ├── artistas.py
│   ├── usuarios.py
│   ├── avaliacoes.py
│   └── locais.py
├── services/        # Business logic
│   ├── base.py
│   ├── mural_service.py
│   └── ...
├── config/          # Database & settings
│   ├── database.py
│   └── settings.py
└── main.py          # FastAPI app
```

## 🗄️ Modelagem de Dados

### Mural (Coleção Principal)
```json
{
  "_id": "ObjectId",
  "titulo": "string",
  "descricao": "string",
  "data_criacao": "datetime",
  "imagem_url": "url",
  "local": {                    
    "nome": "string",
    "latitude": "float",
    "longitude": "float", 
    "bairro": "string",
    "cidade": "string"
  },
  "artista_ids": ["ObjectId"],  
  "tags": ["string"]
}
```

### Avaliação (Relacionamento N:N)
```json
{
  "_id": "ObjectId",
  "mural_id": "ObjectId",     
  "usuario_id": "ObjectId",    
  "nota": "int (1-5)",
  "comentario": "string",
  "data": "datetime"
}
```

## 🔍 Índices MongoDB

```python
// Otimização de consultas
db.murais.createIndex({"tags": 1})
db.murais.createIndex({"local.bairro": 1})
db.murais.createIndex({"artista_ids": 1})
db.avaliacoes.createIndex({"mural_id": 1, "usuario_id": 1}, {unique: true})
```

## 📊 Exemplos de Uso

### Criar um mural
```bash
curl -X POST "http://localhost:8000/murais" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Grafite Colorido",
    "descricao": "Obra vibrante no centro da cidade",
    "imagem_url": "https://example.com/image.jpg",
    "local": {
      "nome": "Praça Central",
      "latitude": -23.550520,
      "longitude": -46.633308,
      "bairro": "Centro",
      "cidade": "São Paulo"
    },
    "artista_ids": ["60d21b4667d0d8992e610c85"],
    "tags": ["colorido", "urbano", "street-art"]
  }'
```

### Listar murais com filtros
```bash
curl "http://localhost:8000/murais?bairro=Centro&tag=urbano&page=1&limit=10"
```

### Top artistas
```bash
curl "http://localhost:8000/murais/top-artistas?limit=5"
```

## 📝 Validações Implementadas

- **Latitude**: -90 a 90
- **Longitude**: -180 a 180  
- **Nota**: 1 a 5
- **Email**: Formato válido
- **Senha**: Mínimo 6 caracteres
- **Avaliação única**: Por usuário/mural

## 🔧 Tecnologias

- **FastAPI**: Framework web moderno
- **MongoDB**: Banco NoSQL com Motor
- **Pydantic**: Validação de dados
- **Uvicorn**: Servidor ASGI
- **BCrypt**: Hash de senhas
