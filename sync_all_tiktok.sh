#!/bin/bash

# Script para sincronizar TikTok IDs de todos os influenciadores
API_BASE="http://localhost:8000"

echo "🎯 Sincronização de TikTok IDs - El Dorado API"
echo "=================================================="

# Obter lista de influenciadores sem TikTok ID via SQL
echo "📊 Consultando influenciadores sem TikTok ID..."

USERNAMES=$(PGPASSWORD=PLLfLHcQoBSLlPmsQLRytEtDOmBQptwi psql -h yamanote.proxy.rlwy.net -p 28818 -U postgres -d railway -t -c "
SELECT eldorado_username 
FROM influencer_ids 
WHERE tiktok_username IS NOT NULL 
AND (tiktok_id IS NULL OR tiktok_id = '')
LIMIT 50;
" | tr -d ' ' | grep -v '^$')

if [ -z "$USERNAMES" ]; then
    echo "✅ Todos os influenciadores já possuem TikTok ID!"
    exit 0
fi

echo "🚀 Processando $(echo "$USERNAMES" | wc -l) influenciadores..."

SUCCESS=0
ERRORS=0

for USERNAME in $USERNAMES; do
    if [ ! -z "$USERNAME" ]; then
        echo ""
        echo "🔄 Sincronizando: $USERNAME"
        
        RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/influencers/$USERNAME/sync-tiktok-id" -H "accept: application/json")
        
        if echo "$RESPONSE" | grep -q '"success":true'; then
            TIKTOK_ID=$(echo "$RESPONSE" | grep -o '"tiktok_id":"[^"]*"' | cut -d'"' -f4)
            echo "  ✅ Sucesso! TikTok ID: $TIKTOK_ID"
            ((SUCCESS++))
        else
            ERROR=$(echo "$RESPONSE" | grep -o '"detail":"[^"]*"' | cut -d'"' -f4)
            echo "  ❌ Erro: $ERROR"
            ((ERRORS++))
        fi
        
        # Aguardar 1 segundo entre requisições para evitar rate limit
        sleep 1
    fi
done

echo ""
echo "=================================================="
echo "📈 RESUMO:"
echo "  Sucessos: $SUCCESS"
echo "  Erros: $ERRORS"
echo "=================================================="