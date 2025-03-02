#!/bin/bash
set -e

# Docker環境の起動
docker-compose up -d

echo "開発環境が起動しました。"
echo "UI: http://localhost:8501"
echo "API: http://localhost:8000"
echo "Qdrant: http://localhost:6333"