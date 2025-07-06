#!/bin/bash

# Script para testar a API Mural Map
# Certifique-se de que a API está rodando em localhost:8000

BASE_URL="http://localhost:8000"

echo "🎨 Testando API Mural Map"
echo "========================="

# Função para fazer requisições e mostrar resposta
make_request() {
    echo -e "\n🔵 $1"
    echo "Endpoint: $2"
    echo "---"
    curl -s "$2" | jq '.' || echo "Erro na requisição"
    echo ""
}

# Função para POST com dados
post_request() {
    echo -e "\n🟢 $1"
    echo "Endpoint: $2"
    echo "---"
    curl -s -X POST "$2" \
         -H "Content-Type: application/json" \
         -d "$3" | jq '.' || echo "Erro na requisição"
    echo ""
}

# 1. Health Check
make_request "Health Check" "$BASE_URL/health"

# 2. Criar um artista
post_request "Criar Artista" "$BASE_URL/artistas" '{
    "nome": "Banksy SP",
    "biografia": "Artista urbano anônimo inspirado no estilo Banksy",
    "site": "https://banksysp.art",
    "redes_sociais": {
        "instagram": "@banksy_sp",
        "twitter": "@banksysp_art"
    }
}'

# 3. Criar um usuário
post_request "Criar Usuário" "$BASE_URL/usuarios" '{
    "nome": "João Silva",
    "email": "joao@email.com", 
    "senha": "senha123"
}'

# 4. Criar um mural
post_request "Criar Mural" "$BASE_URL/murais" '{
    "titulo": "A Resistência",
    "descricao": "Mural que retrata a luta pela democracia",
    "imagem_url": "https://example.com/resistencia.jpg",
    "local": {
        "nome": "Praça da República",
        "latitude": -23.5437,
        "longitude": -46.6417,
        "bairro": "República",
        "cidade": "São Paulo"
    },
    "artista_ids": [],
    "tags": ["resistencia", "democracia", "colorido"]
}'

# 5. Listar murais
make_request "Listar Murais" "$BASE_URL/murais"

# 6. Listar artistas
make_request "Listar Artistas" "$BASE_URL/artistas"

# 7. Listar usuários
make_request "Listar Usuários" "$BASE_URL/usuarios"

# 8. Buscar murais por bairro
make_request "Buscar Murais por Bairro" "$BASE_URL/murais?bairro=República"

# 9. Contar murais por bairro
make_request "Contar Murais por Bairro" "$BASE_URL/murais/count?bairro=República"

# 10. Top artistas
make_request "Top Artistas" "$BASE_URL/murais/top-artistas"

echo "✅ Testes concluídos!"
echo "📚 Documentação: $BASE_URL/docs"
