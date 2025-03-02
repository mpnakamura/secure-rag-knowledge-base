import streamlit as st
import os
import sys
import logging
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") == "true" else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# アプリケーション設定
st.set_page_config(
    page_title="セキュアRAGナレッジベース",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# セッション状態の初期化
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# スタイル設定
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stApp {
        background-color: #f8f9fa;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ページの表示
def main():
    # サイドバー
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=RAG+KB", width=150)
        st.title("セキュアRAGナレッジベース")
        
        # 認証済みの場合はメニュー表示
        if st.session_state.authenticated:
            st.write(f"ログインユーザー: {st.session_state.username}")
            st.write(f"ユーザーロール: {st.session_state.user_role}")
            
            # ナビゲーションメニュー
            st.subheader("メニュー")
            pages = {
                "チャット": "chat",
                "ドキュメント管理": "documents",
                "履歴": "history",
                "設定": "settings",
            }
            selection = st.radio("ページ選択", list(pages.keys()))
            
            # ログアウトボタン
            if st.button("ログアウト"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_role = None
                st.experimental_rerun()
        
        # フッター
        st.markdown("---")
        st.markdown("© 2025 セキュアRAGナレッジベース")
    
    # 認証されていない場合はログイン画面を表示
    if not st.session_state.authenticated:
        display_login_page()
    else:
        # 選択されたページを表示
        if selection == "チャット":
            display_chat_page()
        elif selection == "ドキュメント管理":
            display_documents_page()
        elif selection == "履歴":
            display_history_page()
        elif selection == "設定":
            display_settings_page()

# ログイン画面
def display_login_page():
    st.title("ログイン")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### アカウント情報を入力してください")
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type="password")
        
        if st.button("ログイン"):
            # 開発環境ではダミー認証を使用
            if username == "admin" and password == "admin":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_role = "admin"
                st.success("ログインに成功しました！")
                st.experimental_rerun()
            else:
                st.error("ユーザー名またはパスワードが正しくありません。")
    
    with col2:
        st.markdown("#### セキュアRAGナレッジベースについて")
        st.info(
            """
            本システムは社内ドキュメントを安全に検索・質問できるAIチャットボットです。
            
            **主な機能:**
            - 複数形式ドキュメントのインデックス化
            - 自然言語での質問応答
            - セキュリティ対策（暗号化、機密情報マスキング）
            
            初めてご利用の方は管理者にアカウント発行を依頼してください。
            """
        )

# チャット画面（仮）
def display_chat_page():
    st.title("チャット")
    st.info("ここにチャットインターフェースが表示されます。")
    
    # チャット履歴の表示（実装予定）
    
    # 質問入力フォーム
    query = st.text_area("質問を入力してください", height=100)
    if st.button("送信"):
        st.info(f"質問「{query}」を処理中...")
        # ここに実際の処理を実装（APIリクエスト等）

# ドキュメント管理画面（仮）
def display_documents_page():
    st.title("ドキュメント管理")
    st.info("ここにドキュメント管理インターフェースが表示されます。")
    
    # ファイルアップロードセクション
    uploaded_file = st.file_uploader("ドキュメントをアップロード", 
                                     type=["pdf", "docx", "xlsx", "txt"])
    if uploaded_file is not None:
        st.success(f"ファイル「{uploaded_file.name}」がアップロードされました。")
        # ここに実際の処理を実装（APIリクエスト等）

# 履歴画面（仮）
def display_history_page():
    st.title("質問・回答履歴")
    st.info("ここに質問・回答履歴が表示されます。")

# 設定画面（仮）
def display_settings_page():
    st.title("設定")
    st.info("ここに設定画面が表示されます。")
    
    # LLM設定
    st.subheader("LLMプロバイダー設定")
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
        
    if st.button("設定を保存"):
        st.success("設定が保存されました。（開発環境のためデータは保存されません）")

if __name__ == "__main__":
    main()