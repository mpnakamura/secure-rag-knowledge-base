import streamlit as st
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
import json

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") == "true" else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# アプリケーション設定
st.set_page_config(
    page_title="Secure RAG Knowledge Base",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# カスタムCSSの追加
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 0.5rem 1rem;
        font-size: 1rem;
    }
    
    div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }
    
    div[data-testid="stDecoration"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }
    
    div[data-testid="stStatusWidget"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }
    
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    .card-container {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    
    .card-container:hover {
        transform: translateY(-5px);
    }
    
    /* チャットスタイル */
    .user-message {
        background-color: #e1f5fe;
        padding: 15px;
        border-radius: 15px 15px 0 15px;
        margin: 10px 0;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .bot-message {
        background-color: #f0f4f9;
        padding: 15px;
        border-radius: 15px 15px 15px 0;
        margin: 10px 0;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    /* サイドバーのスタイル調整 */
    .css-1d391kg {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "documents" not in st.session_state:
    st.session_state.documents = [
        {"id": 1, "name": "プロジェクト仕様書.pdf", "uploaded": "2023-03-01", "size": "2.4 MB", "type": "PDF", "confidentiality": 2},
        {"id": 2, "name": "システム設計書.docx", "uploaded": "2023-03-02", "size": "1.8 MB", "type": "Word", "confidentiality": 2},
        {"id": 3, "name": "テスト計画書.xlsx", "uploaded": "2023-03-03", "size": "1.2 MB", "type": "Excel", "confidentiality": 1},
        {"id": 4, "name": "議事録.txt", "uploaded": "2023-03-04", "size": "0.1 MB", "type": "Text", "confidentiality": 1},
        {"id": 5, "name": "API仕様書.pdf", "uploaded": "2023-03-05", "size": "3.5 MB", "type": "PDF", "confidentiality": 2},
    ]

# モック関数：チャット履歴にメッセージを追加
def add_message(message, is_user=True):
    st.session_state.chat_history.append({"message": message, "is_user": is_user})

# モック関数：チャットボットからの応答生成
def generate_response(query):
    responses = {
        "プロジェクトの概要": "このプロジェクトは、社内ドキュメントを検索・質問できるRAGシステムの開発です。仕様書によると、Excelやテキストなど様々な形式のドキュメントをインデックス化し、自然言語で質問できる機能を提供します。",
        "システム": "システムは主に4つのコンポーネントで構成されています：UI（Streamlit）、API（FastAPI）、RAGエンジン、およびベクトルデータベース（Qdrant）。Docker環境で動作し、セキュリティには特に配慮されています。",
        "機能要件": "主な機能要件には、ドキュメント管理機能、検索・質問応答機能、LLM連携機能、ユーザー管理機能、履歴管理機能が含まれます。特に重要なのはセキュリティ機能で、データ保護、機密情報検出・マスキング、ログ記録などがあります。",
    }
    
    for key in responses:
        if key.lower() in query.lower():
            return responses[key]
    
    return "申し訳ありませんが、関連する情報が見つかりませんでした。別の質問をお試しください。なお、これはモックレスポンスです。"

# モック関数：LLM設定の保存
def save_llm_settings(provider, api_key, model):
    st.success(f"{provider}の設定を保存しました。選択モデル：{model}")
    return True

# メインアプリケーション
def main():
    # サイドバー
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=RAG+KB", width=150)
        st.title("Secure RAG KB")
        
        if st.session_state.authenticated:
            st.write(f"ようこそ、{st.session_state.username}さん")
            
            # ナビゲーションメニュー
            selected = option_menu(
                menu_title="メニュー",
                options=["ホーム", "チャット", "ドキュメント", "履歴", "設定"],
                icons=["house", "chat-dots", "file-earmark-text", "clock-history", "gear"],
                menu_icon="cast",
                default_index=0,
            )
            
            st.session_state.current_page = selected.lower()
            
            # ログアウトボタン
            if st.button("ログアウト", type="primary"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_role = None
                st.session_state.current_page = "login"
                st.experimental_rerun()
        
        # フッター
        add_vertical_space(5)
        st.caption("© 2025 Secure RAG Knowledge Base")
    
    # メインコンテンツ
    if not st.session_state.authenticated:
        display_login_page()
    else:
        if st.session_state.current_page == "ホーム":
            display_home_page()
        elif st.session_state.current_page == "チャット":
            display_chat_page()
        elif st.session_state.current_page == "ドキュメント":
            display_documents_page()
        elif st.session_state.current_page == "履歴":
            display_history_page()
        elif st.session_state.current_page == "設定":
            display_settings_page()

# ログイン画面
def display_login_page():
    st.title("Secure RAG Knowledge Base")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.container(border=True):
            colored_header(
                label="ログイン",
                description="アカウント情報を入力してください",
                color_name="blue-70"
            )
            
            username = st.text_input("ユーザー名")
            password = st.text_input("パスワード", type="password")
            
            login_button = st.button("ログイン", type="primary", use_container_width=True)
            if login_button:
                # モック認証（開発用）
                if username == "admin" and password == "admin":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = "admin"
                    st.session_state.current_page = "ホーム"
                    st.success("ログインに成功しました！")
                    st.experimental_rerun()
                else:
                    st.error("ユーザー名またはパスワードが正しくありません。")
    
    with col2:
        with st.container(border=True):
            colored_header(
                label="セキュアRAGナレッジベース",
                description="プロジェクト概要",
                color_name="blue-70"
            )
            
            st.info(
                """
                本システムは社内ドキュメントを安全に検索・質問できるAIチャットボットです。
                
                **主な機能:**
                - 複数形式ドキュメントのインデックス化
                - 自然言語での質問応答
                - セキュリティ対策（暗号化、機密情報マスキング）
                
                **特徴：**
                - 外部LLM（OpenAI/Claude/Gemini）との連携
                - Docker環境での簡単デプロイ
                - 高度なアクセス制御
                
                初めてご利用の方は管理者にアカウント発行を依頼してください。
                """
            )

# ホーム画面
def display_home_page():
    st.title("ダッシュボード")
    
    # 概要カード
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True, height=150):
            st.subheader("📄 ドキュメント数")
            st.metric("総数", "5", "2 件 新規追加")
    
    with col2:
        with st.container(border=True, height=150):
            st.subheader("💬 質問数")
            st.metric("今週", "27", "5% 増加")
    
    with col3:
        with st.container(border=True, height=150):
            st.subheader("🔍 検索精度")
            st.metric("正確性", "87%", "3% 向上")
    
    # 最近の質問
    with st.container(border=True):
        colored_header(
            label="最近の質問",
            description="直近の質問内容",
            color_name="blue-70"
        )
        
        recent_questions = [
            {"question": "プロジェクトの概要について教えてください", "date": "2023-03-10", "status": "回答済み"},
            {"question": "システム設計書のセキュリティ要件はどこに記載されていますか？", "date": "2023-03-09", "status": "回答済み"},
            {"question": "APIの認証方式は何を使用していますか？", "date": "2023-03-08", "status": "回答済み"},
        ]
        
        for q in recent_questions:
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.write(f"**{q['question']}**")
            with cols[1]:
                st.write(q['date'])
            with cols[2]:
                if q['status'] == "回答済み":
                    st.success(q['status'])
                else:
                    st.warning(q['status'])
            st.divider()
    
    # 最近のドキュメント
    with st.container(border=True):
        colored_header(
            label="最近追加されたドキュメント",
            description="直近でアップロードされたドキュメント",
            color_name="blue-70"
        )
        
        recent_docs = [doc for doc in st.session_state.documents[:3]]
        
        for doc in recent_docs:
            cols = st.columns([3, 1, 1, 1])
            with cols[0]:
                st.write(f"**{doc['name']}**")
            with cols[1]:
                st.write(f"種類: {doc['type']}")
            with cols[2]:
                st.write(f"サイズ: {doc['size']}")
            with cols[3]:
                st.write(f"アップロード: {doc['uploaded']}")
            st.divider()

# チャット画面
def display_chat_page():
    st.title("ドキュメント質問")
    
    # 左側：チャットインターフェース
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container(border=True):
            colored_header(
                label="チャットインターフェース",
                description="ドキュメントに関する質問を入力してください",
                color_name="blue-70"
            )
            
            # チャット履歴の表示
            chat_container = st.container()
            with chat_container:
                for chat in st.session_state.chat_history:
                    if chat["is_user"]:
                        st.markdown(f'<div class="user-message"><strong>あなた:</strong> {chat["message"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="bot-message"><strong>AI:</strong> {chat["message"]}</div>', unsafe_allow_html=True)
            
            # 入力フォーム
            with st.form(key="chat_form", clear_on_submit=True):
                user_input = st.text_area("質問を入力", placeholder="ドキュメントについて質問してください...", height=100)
                submit_button = st.form_submit_button("送信", use_container_width=True)
                
                if submit_button and user_input:
                    # ユーザーメッセージを追加
                    add_message(user_input, is_user=True)
                    
                    # モックレスポンスを生成
                    response = generate_response(user_input)
                    add_message(response, is_user=False)
                    
                    # 再描画
                    st.experimental_rerun()
    
    # 右側：関連ドキュメント
    with col2:
        with st.container(border=True):
            colored_header(
                label="参照コンテキスト",
                description="質問に関連するドキュメント",
                color_name="blue-70"
            )
            
            if len(st.session_state.chat_history) > 0:
                st.info("以下のドキュメントが参照されました：")
                
                st.markdown("🔍 **プロジェクト仕様書.pdf** (ページ: 5-7)")
                st.markdown("```\n機能要件には、ドキュメント管理機能、検索・質問応答機能、LLM連携機能が含まれる。\n```")
                
                st.markdown("🔍 **システム設計書.docx** (ページ: 12)")
                st.markdown("```\nシステムは4つのコンポーネントで構成：UI、API、RAGエンジン、ベクトルDB\n```")
            else:
                st.write("まだ質問がありません。何か質問してみてください。")

# ドキュメント管理画面
def display_documents_page():
    st.title("ドキュメント管理")
    
    # タブでセクションを分ける
    tab1, tab2 = st.tabs(["ドキュメント一覧", "アップロード"])
    
    # タブ1: ドキュメント一覧
    with tab1:
        with st.container(border=True):
            # 検索・フィルター
            search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
            with search_col1:
                search_query = st.text_input("ドキュメント検索", placeholder="ファイル名を入力...")
            with search_col2:
                doc_type = st.selectbox("ファイルタイプ", ["すべて", "PDF", "Excel", "Word", "テキスト"])
            with search_col3:
                confidence_level = st.selectbox("機密レベル", ["すべて", "1 - 社内", "2 - 社外秘", "3 - 極秘"])
            
            # ドキュメント一覧
            st.subheader("ドキュメント一覧")
            
            filtered_docs = st.session_state.documents
            if search_query:
                filtered_docs = [doc for doc in filtered_docs if search_query.lower() in doc["name"].lower()]
            if doc_type != "すべて":
                filtered_docs = [doc for doc in filtered_docs if doc["type"] == doc_type]
            if confidence_level != "すべて":
                level = int(confidence_level[0])
                filtered_docs = [doc for doc in filtered_docs if doc["confidentiality"] == level]
            
            if not filtered_docs:
                st.warning("条件に一致するドキュメントがありません。")
            else:
                for doc in filtered_docs:
                    cols = st.columns([3, 1, 1, 1, 1])
                    with cols[0]:
                        st.write(f"**{doc['name']}**")
                    with cols[1]:
                        st.write(f"種類: {doc['type']}")
                    with cols[2]:
                        st.write(f"サイズ: {doc['size']}")
                    with cols[3]:
                        st.write(f"機密度: {doc['confidentiality']}")
                    with cols[4]:
                        st.button("詳細", key=f"detail_{doc['id']}")
                        st.button("削除", key=f"delete_{doc['id']}")
                    st.divider()
    
    # タブ2: アップロード
    with tab2:
        with st.container(border=True):
            colored_header(
                label="ドキュメントアップロード",
                description="新しいドキュメントをアップロードします",
                color_name="blue-70"
            )
            
            # アップロードフォーム
            uploaded_file = st.file_uploader("ファイルを選択", type=["pdf", "xlsx", "xls", "docx", "txt"])
            
            if uploaded_file is not None:
                file_details = {
                    "ファイル名": uploaded_file.name,
                    "ファイルタイプ": uploaded_file.type,
                    "サイズ": f"{uploaded_file.size / 1024:.1f} KB"
                }
                
                st.json(file_details)
                
                # メタデータ入力
                conf_level = st.radio("機密レベル", ["1 - 社内", "2 - 社外秘", "3 - 極秘"], horizontal=True)
                tags = st.text_input("タグ (カンマ区切り)", "ドキュメント, 仕様書")
                
                if st.button("処理開始", type="primary"):
                    with st.spinner("ドキュメントを処理中..."):
                        # モック処理（実際はAPIリクエスト）
                        import time
                        time.sleep(2)
                        
                        new_doc = {
                            "id": len(st.session_state.documents) + 1,
                            "name": uploaded_file.name,
                            "uploaded": datetime.now().strftime("%Y-%m-%d"),
                            "size": f"{uploaded_file.size / (1024 * 1024):.1f} MB",
                            "type": uploaded_file.name.split(".")[-1].upper(),
                            "confidentiality": int(conf_level[0])
                        }
                        
                        st.session_state.documents.append(new_doc)
                        st.success(f"ファイル「{uploaded_file.name}」の処理が完了しました！")

# 履歴画面
def display_history_page():
    st.title("質問・回答履歴")
    
    # モック履歴データ
    history_data = [
        {"id": 1, "query": "プロジェクトの概要について教えてください", "date": "2023-03-10", "documents": ["プロジェクト仕様書.pdf"]},
        {"id": 2, "query": "システム設計書のセキュリティ要件はどこに記載されていますか？", "date": "2023-03-09", "documents": ["システム設計書.docx"]},
        {"id": 3, "query": "APIの認証方式は何を使用していますか？", "date": "2023-03-08", "documents": ["API仕様書.pdf", "システム設計書.docx"]},
        {"id": 4, "query": "テスト計画書の進捗状況はどうなっていますか？", "date": "2023-03-07", "documents": ["テスト計画書.xlsx", "議事録.txt"]},
        {"id": 5, "query": "プロジェクトのタイムラインを教えてください", "date": "2023-03-06", "documents": ["プロジェクト仕様書.pdf", "議事録.txt"]},
    ]
    
    # 検索・フィルター
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        history_search = st.text_input("履歴検索", placeholder="質問内容を入力...")
    with search_col2:
        date_range = st.date_input("日付", value=[])
    
    # 履歴一覧
    with st.container(border=True):
        colored_header(
            label="質問履歴",
            description="過去の質問と回答の履歴",
            color_name="blue-70"
        )
        
        filtered_history = history_data
        if history_search:
            filtered_history = [h for h in filtered_history if history_search.lower() in h["query"].lower()]
        
        for item in filtered_history:
            with st.expander(f"Q: {item['query']} ({item['date']})"):
                st.write("**質問:**")
                st.info(item["query"])
                
                st.write("**回答:**")
                st.success(generate_response(item["query"]))
                
                st.write("**参照ドキュメント:**")
                for doc in item["documents"]:
                    st.write(f"- {doc}")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("類似質問を検索", key=f"similar_{item['id']}"):
                        st.info("この機能はモックです。実装されると類似質問が表示されます。")
                with col2:
                    if st.button("再質問する", key=f"retry_{item['id']}"):
                        add_message(item["query"], is_user=True)
                        add_message(generate_response(item["query"]), is_user=False)
                        st.session_state.current_page = "チャット"
                        st.experimental_rerun()

# 設定画面
def display_settings_page():
    st.title("設定")
    
    # タブでセクションを分ける
    tab1, tab2, tab3 = st.tabs(["LLM設定", "セキュリティ設定", "ユーザー管理"])
    
    # タブ1: LLM設定
    with tab1:
        with st.container(border=True):
            colored_header(
                label="LLMプロバイダー設定",
                description="使用するLLMプロバイダーと設定を選択します",
                color_name="blue-70"
            )
            
            provider = st.selectbox("使用するLLM", ["OpenAI", "Claude", "Gemini", "ローカルLLM"])
            
            if provider == "OpenAI":
                api_key = st.text_input("OpenAI API Key", type="password")
                model = st.selectbox("モデル", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
            elif provider == "Claude":
                api_key = st.text_input("Claude API Key", type="password")
                model = st.selectbox("モデル", ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"])
            elif provider == "Gemini":
                api_key = st.text_input("Gemini API Key", type="password")
                model = st.selectbox("モデル", ["gemini-1.5-pro", "gemini-1.5-flash"])
            elif provider == "ローカルLLM":
                st.info("ローカルLLMを使用する場合は、Docker環境で起動する必要があります。")
                api_key = None
                model = "local-model"
            
            if st.button("設定を保存", type="primary"):
                if provider != "ローカルLLM" and not api_key:
                    st.error("APIキーを入力してください。")
                else:
                    save_llm_settings(provider, api_key, model)
    
    # タブ2: セキュリティ設定
    with tab2:
        with st.container(border=True):
            colored_header(
                label="セキュリティ設定",
                description="システムのセキュリティ関連設定",
                color_name="blue-70"
            )
            
            st.subheader("機密レベル設定")
            st.write("各LLMに送信可能な最大機密レベルを設定します")
            
            col1, col2 = st.columns(2)
            with col1:
                openai_level = st.slider("OpenAI 最大機密レベル", 0, 3, 1)
                claude_level = st.slider("Claude 最大機密レベル", 0, 3, 1)
            with col2:
                gemini_level = st.slider("Gemini 最大機密レベル", 0, 3, 1)
                local_level = st.slider("ローカルLLM 最大機密レベル", 0, 3, 2)
            
            st.subheader("個人情報マスキング")
            pii_masking = st.toggle("個人情報の自動マスキング", value=True)
            
            pii_types = st.multiselect(
                "マスキングする情報タイプ",
                ["メールアドレス", "電話番号", "住所", "氏名", "社員番号", "クレジットカード番号"],
                ["メールアドレス", "電話番号", "クレジットカード番号"]
            )
            
            st.subheader("データ暗号化")
            encryption_enabled = st.toggle("保存データの暗号化", value=True)
            st.info("暗号化キーはシステム管理者のみが変更できます")
            
            if st.button("セキュリティ設定を保存", type="primary"):
                st.success("セキュリティ設定が保存されました")
    
    # タブ3: ユーザー管理
    with tab3:
        if st.session_state.user_role == "admin":
            with st.container(border=True):
                colored_header(
                    label="ユーザー管理",
                    description="システムユーザーの管理",
                    color_name="blue-70"
                )
                
                # モックユーザーデータ
                users = [
                    {"id": 1, "username": "admin", "email": "admin@example.com", "role": "管理者", "status": "アクティブ"},
                    {"id": 2, "username": "user1", "email": "user1@example.com", "role": "一般ユーザー", "status": "アクティブ"},
                    {"id": 3, "username": "user2", "email": "user2@example.com", "role": "アップローダー", "status": "非アクティブ"},
                ]
                
                st.subheader("ユーザー一覧")
                for user in users:
                    cols = st.columns([2, 2, 2, 1, 1])
                    with cols[0]:
                        st.write(f"**{user['username']}**")
                    with cols[1]:
                        st.write(user['email'])
                    with cols[2]:
                        st.write(user['role'])
                    with cols[3]:
                        if user['status'] == "アクティブ":
                            st.success(user['status'])
                        else:
                            st.error(user['status'])
                    with cols[4]:
                        st.button("編集", key=f"edit_{user['id']}")
                    st.divider()
                
                st.subheader("新規ユーザー追加")
                with st.form(key="new_user_form"):
                    new_username = st.text_input("ユーザー名")
                    new_email = st.text_input("メールアドレス")
                    new_password = st.text_input("パスワード", type="password")
                    new_role = st.selectbox("ロール", ["管理者", "アップローダー", "一般ユーザー"])
                    
                    if st.form_submit_button("ユーザーを追加", type="primary"):
                        if new_username and new_email and new_password:
                            st.success(f"ユーザー '{new_username}' が追加されました")
                        else:
                            st.error("すべてのフィールドを入力してください")
        else:
            st.warning("ユーザー管理へのアクセス権限がありません。管理者アカウントでログインしてください。")

# アプリケーション実行
if __name__ == "__main__":
    main()