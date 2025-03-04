"""
ログイン画面の実装
"""

import streamlit as st
import asyncio
from utils.api_client import get_api_client
from utils.session import set_authenticated
from utils.ui_components import card_container, close_card_container, section_header

async def attempt_login(username, password):
    """
    ログイン試行
    
    Args:
        username: ユーザー名
        password: パスワード
        
    Returns:
        (成功したかどうか, エラーメッセージ)
    """
    try:
        client = await get_api_client()
        response = await client.login(username, password)
        
        # ログイン成功
        set_authenticated(
            username=response["user"]["username"],
            role=response["user"]["role"]
        )
        return True, None
        
    except Exception as e:
        return False, str(e)

def display_login_page():
    """ログイン画面を表示"""
    st.title("Secure RAG Knowledge Base")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        container = card_container("ログイン", "アカウント情報を入力してください")
        
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type="password")
        
        login_button = st.button("ログイン", type="primary", use_container_width=True)
        
        # セッション状態にエラーがあれば表示
        if "login_error" in st.session_state and st.session_state.login_error:
            st.error(st.session_state.login_error)
            # エラーを表示したらクリア
            st.session_state.login_error = None
        
        if login_button:
            if not username or not password:
                st.error("ユーザー名とパスワードを入力してください。")
            else:
                # ログイン処理
                with st.spinner("認証中..."):
                    # streamlitではAsyncIOの直接実行ができないため、syncに変換
                    success, error = asyncio.run(attempt_login(username, password))
                    
                    if success:
                        st.success("ログインに成功しました！")
                        st.experimental_rerun()
                    else:
                        st.error(f"ログインに失敗しました: {error}")
        
        close_card_container()
    
    with col2:
        container = card_container("セキュアRAGナレッジベース", "プロジェクト概要")
        
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
        
        close_card_container()

if __name__ == "__main__":
    # 単体テスト用
    display_login_page()
