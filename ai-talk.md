secure-rag-knowledge-base/
│
├── .github/                          # GitHub関連ファイル
│   └── workflows/                    # GitHub Actions ワークフロー
│       └── ci.yml                    # CI設定
│
├── api/                              # バックエンドAPI
│   ├── Dockerfile                    # APIサーバーのDockerfile
│   ├── requirements.txt              # Pythonパッケージ依存関係
│   ├── main.py                       # FastAPIエントリーポイント
│   ├── core/                         # コアモジュール
│   │   ├── __init__.py
│   │   ├── config.py                 # 設定管理
│   │   ├── security.py               # セキュリティユーティリティ
│   │   └── logging.py                # ロギング設定
│   │
│   ├── routers/                      # APIルーター
│   │   ├── __init__.py
│   │   ├── auth.py                   # 認証エンドポイント
│   │   ├── documents.py              # ドキュメント管理エンドポイント
│   │   ├── query.py                  # 質問応答エンドポイント
│   │   ├── settings.py               # 設定管理エンドポイント
│   │   └── admin.py                  # 管理者エンドポイント
│   │
│   ├── services/                     # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── auth_service.py           # 認証サービス
│   │   ├── document_service.py       # ドキュメント処理サービス
│   │   ├── query_service.py          # 質問応答サービス
│   │   └── admin_service.py          # 管理サービス
│   │
│   ├── models/                       # データモデル
│   │   ├── __init__.py
│   │   ├── document.py               # ドキュメントモデル
│   │   ├── user.py                   # ユーザーモデル
│   │   ├── query.py                  # クエリ・応答モデル
│   │   └── settings.py               # 設定モデル
│   │
│   ├── dependencies/                 # FastAPI依存関係
│   │   ├── __init__.py
│   │   ├── auth.py                   # 認証依存関係
│   │   └── db.py                     # データベース依存関係
│   │
│   └── tests/                        # APIテスト
│       ├── __init__.py
│       ├── test_auth.py              # 認証テスト
│       └── test_query.py             # クエリテスト
│
├── rag_engine/                       # RAGエンジン
│   ├── Dockerfile                    # RAGエンジンのDockerfile
│   ├── requirements.txt              # パッケージ依存関係
│   ├── __init__.py
│   ├── indexer/                      # インデクシング
│   │   ├── __init__.py
│   │   ├── document_processor.py     # ドキュメント処理
│   │   ├── chunking.py               # チャンキング
│   │   └── embedding.py              # 埋め込み生成
│   │
│   ├── retriever/                    # 検索エンジン
│   │   ├── __init__.py
│   │   ├── vector_store.py           # ベクトルストア連携
│   │   └── hybrid_search.py          # ハイブリッド検索
│   │
│   ├── llm/                          # LLM連携
│   │   ├── __init__.py
│   │   ├── router.py                 # LLMルーター
│   │   ├── openai_client.py          # OpenAI API クライアント
│   │   ├── claude_client.py          # Claude API クライアント
│   │   ├── gemini_client.py          # Gemini API クライアント
│   │   └── local_client.py           # ローカルLLMクライアント（オプション）
│   │
│   ├── security/                     # セキュリティ機能
│   │   ├── __init__.py
│   │   ├── encryption.py             # 暗号化ユーティリティ
│   │   ├── pii_detection.py          # 個人情報検出
│   │   └── content_filter.py         # コンテンツフィルター
│   │
│   └── tests/                        # RAGエンジンテスト
│       ├── __init__.py
│       ├── test_indexer.py           # インデクサーテスト
│       └── test_retriever.py         # 検索エンジンテスト
│
├── parsers/                          # ドキュメントパーサー
│   ├── __init__.py
│   ├── excel_parser.py               # Excelパーサー
│   ├── pdf_parser.py                 # PDFパーサー
│   ├── word_parser.py                # Wordパーサー
│   ├── text_parser.py                # テキストパーサー
│   └── utils/                        # パーサーユーティリティ
│       ├── __init__.py
│       └── text_extraction.py        # テキスト抽出共通関数
│
├── ui/                               # フロントエンド（Streamlit）
│   ├── Dockerfile                    # UIのDockerfile
│   ├── requirements.txt              # パッケージ依存関係
│   ├── app.py                        # メインアプリ
│   ├── utils/                        # UIユーティリティ
│   │   ├── __init__.py
│   │   ├── api_client.py             # APIクライアント
│   │   ├── session.py                # セッション管理
│   │   └── ui_components.py          # 共通UIコンポーネント
│   │
│   └── pages/                        # Streamlitページ
│       ├── __init__.py
│       ├── login.py                  # ログイン画面
│       ├── chat.py                   # チャット画面
│       ├── documents.py              # ドキュメント管理画面
│       ├── history.py                # 履歴画面
│       └── settings.py               # 設定画面
│
├── data/                             # データディレクトリ（Dockerボリューム）
│   ├── .gitignore                    # Git除外設定
│   ├── documents/                    # ドキュメント保存用
│   ├── vector_db/                    # ベクトルDB保存用
│   ├── settings/                     # 設定ファイル保存用
│   └── history/                      # 履歴保存用
│
├── scripts/                          # スクリプト類
│   ├── setup.sh                      # セットアップスクリプト
│   ├── dev.sh                        # 開発環境起動スクリプト
│   └── backup.sh                     # バックアップスクリプト
│
├── docker-compose.yml                # Dockerコンポーネント定義
├── docker-compose.dev.yml            # 開発用オーバーライド
├── docker-compose.prod.yml           # 本番用オーバーライド
├── .env.example                      # 環境変数サンプル
├── .gitignore                        # Git除外設定
├── README.md                         # プロジェクト説明
└── LICENSE                           # ライセンス



