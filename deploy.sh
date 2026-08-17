#!/usr/bin/env bash

set -Eeuo pipefail

APP_NAME="educassist-api"
APP_DIR="/opt/sintese/apps/educassist-api"
BRANCH="main"
SERVICE="educassist-api"
HEALTH_URL="https://api.educassist.com.br/health"

echo ""
echo "=========================================="
echo "   DEPLOY - EducAssist API"
echo "=========================================="
echo ""

cd "$APP_DIR"

echo "▶ 1. Verificando estado do Git..."
git status --short

echo ""
echo "▶ 2. Atualizando código..."
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo ""
echo "▶ 3. Atualizando dependências..."
uv sync --frozen

echo ""
echo "▶ 4. Verificando Alembic..."
uv run alembic check

echo ""
echo "▶ 5. Aplicando migrations..."
uv run alembic upgrade head

echo ""
echo "▶ 6. Executando seed..."
uv run python -c "
from app.db.database import SessionLocal
from app.services.auth_service import seed_admin_user

db = SessionLocal()

try:
    seed_admin_user(db)
finally:
    db.close()
"

echo ""
echo "▶ 7. Reiniciando API..."
sudo systemctl restart "$SERVICE"

echo ""
echo "▶ 8. Aguardando API iniciar..."
sleep 3

echo ""
echo "▶ 9. Verificando serviço..."

if ! sudo systemctl is-active --quiet "$SERVICE"; then
    echo ""
    echo "❌ ERRO: serviço $SERVICE não está ativo."
    echo ""
    sudo systemctl status "$SERVICE" --no-pager -l
    exit 1
fi

echo "✅ Serviço ativo."

echo ""
echo "▶ 10. Testando healthcheck..."

HTTP_STATUS=$(curl \
    --silent \
    --output /tmp/educassist-health-response \
    --write-out "%{http_code}" \
    "$HEALTH_URL")

if [ "$HTTP_STATUS" != "200" ]; then
    echo ""
    echo "❌ ERRO: healthcheck retornou HTTP $HTTP_STATUS"
    cat /tmp/educassist-health-response
    echo ""
    sudo journalctl -u "$SERVICE" -n 50 --no-pager
    exit 1
fi

echo "✅ API respondeu HTTP 200:"
cat /tmp/educassist-health-response

echo ""
echo "▶ 11. Commit implantado:"
git rev-parse --short HEAD

echo ""
echo "=========================================="
echo "   ✅ DEPLOY CONCLUÍDO COM SUCESSO"
echo "=========================================="
echo ""
