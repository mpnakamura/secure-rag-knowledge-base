"""
チャットページ
ドキュメントに対する質問応答インターフェース
"""

import streamlit as st
import asyncio
from utils.ui_components import card_container, close_card_container, section_header  # chat_message は下記で定義
from utils.session import add_chat_message, get_chat_history
from utils.api_client import get_api_client

# --------------------------------------------------
# カスタム CSS の適用（ChatGPT 風デザイン）
# --------------------------------------------------
st.markdown(
    """
    <style>
    body {
        background-color: #F7F7F8;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    /* チャットメッセージ全体のコンテナ */
    .chat-container {
        padding: 10px;
        margin: 10px 0;
        border-radius: 8px;
    }
    /* ユーザーメッセージ（右寄せ） */
    .user-message {
        background-color: #DCF8C6;
        border-radius: 15px;
        padding: 8px 12px;
        margin: 8px 0;
        display: block;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    /* アシスタント（ChatGPT）メッセージ（左寄せ） */
    .assistant-message {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 8px 12px;
        margin: 8px 0;
        display: block;
        max-width: 80%;
        margin-right: auto;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# メッセージ表示用の関数（ChatGPT 風に整形）
# --------------------------------------------------
def chat_message(message, is_user):
    css_class = "user-message" if is_user else "assistant-message"
    st.markdown(f'<div class="chat-container {css_class}">{message}</div>', unsafe_allow_html=True)

# --------------------------------------------------
# 質問処理：API からレスポンスを取得
# --------------------------------------------------
async def process_query(query):
    """
    質問を処理してレスポンスを取得
    
    Args:
        query: ユーザーの質問
    
    Returns:
        APIからのレスポンス
    """
    # チャット履歴にユーザーの質問を追加
    add_chat_message(query, is_user=True)
    
    # スピナーを表示しながら API 呼び出し
    with st.spinner("回答を生成中..."):
        # API クライアントの取得
        client = await get_api_client()
        
        try:
            # 質問を API に送信
            response = await client.send_query(query)
            
            # API の回答をチャット履歴に追加
            add_chat_message(response["answer"], is_user=False)
            return response
        except Exception as e:
            # エラー発生時はエラーメッセージを追加
            error_message = f"エラーが発生しました: {str(e)}"
            add_chat_message(error_message, is_user=False)
            return {"error": str(e)}

# --------------------------------------------------
# チャットページ表示
# --------------------------------------------------
def display_chat_page():
    """チャットページを表示"""
    st.title("ドキュメント質問")
    
    # レイアウト: 左側にチャット、右側に参照情報
    col1, col2 = st.columns([2, 1])
    
    # 左側：チャットインターフェース
    with col1:
        chat_container = card_container("チャットインターフェース", "ドキュメントに関する質問を入力してください")
        with chat_container:
            # チャット履歴の表示
            history_container = st.container()
            with history_container:
                for chat in get_chat_history():
                    chat_message(chat["message"], chat["is_user"])
            
            # 入力フォーム
            with st.form(key="chat_form", clear_on_submit=True):
                user_input = st.text_area("質問を入力", placeholder="ドキュメントについて質問してください...", height=100)
                submit_button = st.form_submit_button("送信", use_container_width=True)
                
                if submit_button and user_input:
                    # 非同期処理の実行（同期的に実行）
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(process_query(user_input))
                    loop.close()
                    st.experimental_rerun()
        close_card_container()
    
    # 右側：参照コンテキスト
    with col2:
        context_container = card_container("参照コンテキスト", "質問に関連するドキュメント")
        with context_container:
            history = get_chat_history()
            if len(history) > 0:
                st.info("以下のドキュメントが参照されました：")
                st.markdown("🔍 **プロジェクト仕様書.pdf** (ページ: 5-7)")
                st.markdown("```\n機能要件には、ドキュメント管理機能、検索・質問応答機能、LLM連携機能が含まれる。\n```")
                st.markdown("🔍 **システム設計書.docx** (ページ: 12)")
                st.markdown("```\nシステムは4つのコンポーネントで構成：UI、API、RAGエンジン、ベクトルDB\n```")
                st.markdown("### 回答の信頼性")
                st.progress(0.87, text="87% 一致")
                st.caption("この回答は複数のドキュメントからの情報に基づいています。")
            else:
                st.write("まだ質問がありません。何か質問してみてください。")
                st.markdown("### サンプル質問")
                sample_questions = [
                    "プロジェクトの概要について教えてください",
                    "システム設計書のセキュリティ要件はどこに記載されていますか？",
                    "APIの認証方式は何を使用していますか？"
                ]
                for q in sample_questions:
                    if st.button(q, key=f"sample_{hash(q)}"):
                        asyncio.run(process_query(q))
                        st.experimental_rerun()
        close_card_container()
        
        # LLM 情報表示
        llm_container = card_container("LLM情報", "使用中のモデル")
        with llm_container:
            st.info("使用モデル: OpenAI GPT-4o")
            st.caption("機密レベル制限: レベル2まで")
            if st.button("LLM設定を変更", key="change_llm"):
                st.session_state.current_page = "設定"
                st.experimental_rerun()
        close_card_container()
