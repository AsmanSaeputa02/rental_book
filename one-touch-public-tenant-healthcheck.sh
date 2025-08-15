#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
BASE_URL_PUBLIC="${BASE_URL_PUBLIC:-http://localhost:8003/book_project}"
PUBLIC_LOGIN_PATH="${PUBLIC_LOGIN_PATH:-/api/admin/login/}"
TENANT_LOGIN_PATH="${TENANT_LOGIN_PATH:-/api/auth/login/}"
TENANT_BOOK_LIST_PATH="${TENANT_BOOK_LIST_PATH:-/api/book/}"

# Public superadmin
ADMIN_EMAIL="${ADMIN_EMAIL:-superadmin@example.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-P@ssw0rdasman}"

# Tenant defaults
TENANT_HOST="${TENANT_HOST:-branch-a.localhost}"
TENANT_EMAIL="${TENANT_EMAIL:-owner@branch-a.com}"
TENANT_PASSWORD="${TENANT_PASSWORD:-passA}"

jget() { echo "$1" | jq -r "$2"; }

# --- Public login ---
PUB_RESP=$(curl -sS -X POST "$BASE_URL_PUBLIC$PUBLIC_LOGIN_PATH" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")
echo "$PUB_RESP" | jq . >/dev/null 2>&1 || { echo "Public login not JSON: $PUB_RESP"; exit 1; }
PUB_TOKEN=$(jget "$PUB_RESP" '.access')
[[ -z "$PUB_TOKEN" || "$PUB_TOKEN" == "null" ]] && { echo "No public access token: $PUB_RESP"; exit 1; }
echo "[OK] Public login: token acquired"

# --- Tenant login ---
BASE_TENANT="http://$TENANT_HOST:8003/book_project"
TEN_RESP=$(curl -sS -X POST "$BASE_TENANT$TENANT_LOGIN_PATH" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TENANT_EMAIL\",\"password\":\"$TENANT_PASSWORD\"}")
echo "$TEN_RESP" | jq . >/dev/null 2>&1 || { echo "Tenant login not JSON: $TEN_RESP"; exit 1; }
TEN_TOKEN=$(jget "$TEN_RESP" '.access')
[[ -z "$TEN_TOKEN" || "$TEN_TOKEN" == "null" ]] && { echo "No tenant access token: $TEN_RESP"; exit 1; }
echo "[OK] Tenant login on $TENANT_HOST: token acquired"

# --- List books ---
BOOKS=$(curl -sS -X GET "$BASE_TENANT$TENANT_BOOK_LIST_PATH" \
  -H "Authorization: Bearer $TEN_TOKEN")
echo "$BOOKS" | jq . >/dev/null 2>&1 || { echo "/api/book/ not JSON: $BOOKS"; exit 1; }
echo "[OK] $TENANT_HOST$TENANT_BOOK_LIST_PATH reachable"

echo "Done."
