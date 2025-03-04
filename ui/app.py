import streamlit as st
import os
import sys
import logging
from pathlib import Path
from streamlit_option_menu import option_menu
from streamlit_extras.add_vertical_space import add_vertical_space

# 自作モジュールをインポート
from utils.session import init_session_state
from views.login import display_login_page
from views.home import display_home_page
from views.chat import display_chat_page
from views.documents import display_documents_page
from views.history import display_history_page
#from views.settings import display_settings_page

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
)

os.environ["DEVELOPMENT"] = "1"

# カスタムCSSの読み込み
def load_css():
    css_file = Path(__file__).parent / "static" / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # CSSファイルがない場合はインラインCSSを使用
        st.markdown("""
        <style>       
            .container-card:empty {
                display: none !important;
            }    

            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 95%;
            }
            
            .stApp {
                background-color: #f8f9fa;
            }
            
            /* 全体のテキスト色調整 */
            body, .stTextInput, .stSelectbox, .stDateInput {
                color: #31333F !important;
            }
            
            p, span, label, div {
                color: #31333F;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #31333F !important;
            }
            
            /* コンテナスタイル - border代替 */
            .container-card {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            
            /* チャットスタイル */
            .user-message {
                background-color: #e1f5fe;
                padding: 15px;
                border-radius: 15px 15px 0 15px;
                margin: 10px 0;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                color: #333;
            }
            
            .bot-message {
                background-color: #f0f4f9;
                padding: 15px;
                border-radius: 15px 15px 15px 0;
                margin: 10px 0;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                color: #333;
            }
        </style>
        """, unsafe_allow_html=True)

# メインアプリケーション
def main():
    # CSSの読み込み
    load_css()
    
    # セッション状態の初期化
    init_session_state()
    
    # サイドバー
    with st.sidebar:
        st.image("https://placehold.jp/300x150.png", width=150)
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
        #elif st.session_state.current_page == "設定":
        #    display_settings_page()

# アプリケーション実行
if __name__ == "__main__":
    main()
