#!/bin/bash
set -e

# ディレクトリ作成
mkdir -p data/documents data/vector_db data/settings data/history

# 環境変数ファイルのセットアップ
if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env ファイルを作成しました。必要に応じて編集してください。"
fi

# 初期設定ファイルの作成
mkdir -p data/settings
if [ ! -f data/settings/llm_settings.json ]; then
  cat > data/settings/llm_settings.json << EOF
{
  "active_provider": "openai",
  "openai": {
    "api_key": "",
    "model": "gpt-4o"
  },
  "claude": {
    "api_key": "",
    "model": "claude-3-5-sonnet"
  },
  "gemini": {
    "api_key": "",
    "model": "gemini-1.5-pro"
  },
  "use_local_llm": false
}
EOF
  echo "LLM設定ファイルを作成しました。"
fi

# Pythonの仮想環境セットアップ (オプション)
if [ ! -d "venv" ]; then
  echo "Pythonの仮想環境をセットアップしています..."
  python -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  echo "仮想環境がセットアップされました。"
fi

echo "セットアップが完了しました。"