"""
セッション状態の管理モジュール
"""

import streamlit as st
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def init_session_state():
    """アプリケーション全体で使用するセッション状態の初期化"""
    
    # 認証関連の状態
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"
    
    # 機能別データの状態
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "documents" not in st.session_state:
        # モックデータ（実際の実装ではAPIから取得）
        st.session_state.documents = [
            {"id": 1, "name": "プロジェクト仕様書.pdf", "uploaded": "2023-03-01", "size": "2.4 MB", "type": "PDF", "confidentiality": 2},
            {"id": 2, "name": "システム設計書.docx", "uploaded": "2023-03-02", "size": "1.8 MB", "type": "Word", "confidentiality": 2},
            {"id": 3, "name": "テスト計画書.xlsx", "uploaded": "2023-03-03", "size": "1.2 MB", "type": "Excel", "confidentiality": 1},
            {"id": 4, "name": "議事録.txt", "uploaded": "2023-03-04", "size": "0.1 MB", "type": "Text", "confidentiality": 1},
            {"id": 5, "name": "API仕様書.pdf", "uploaded": "2023-03-05", "size": "3.5 MB", "type": "PDF", "confidentiality": 2},
        ]

def set_authenticated(username, role):
    """ユーザー認証状態を設定"""
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.user_role = role
    st.session_state.current_page = "ホーム"
    logger.info(f"User authenticated: {username}, role: {role}")

def logout():
    """ログアウト処理"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.current_page = "login"
    logger.info("User logged out")

def add_chat_message(message, is_user=True):
    """チャット履歴にメッセージを追加"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    st.session_state.chat_history.append({
        "message": message,
        "is_user": is_user,
        "timestamp": datetime.now().isoformat()
    })

def get_chat_history():
    """チャット履歴を取得"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    return st.session_state.chat_history

def add_document(doc_data):
    """ドキュメントリストに新しいドキュメントを追加"""
    if "documents" not in st.session_state:
        st.session_state.documents = []
    
    st.session_state.documents.append(doc_data)
    logger.info(f"Document added: {doc_data['name']}")

def get_documents():
    """ドキュメントリストを取得"""
    if "documents" not in st.session_state:
        st.session_state.documents = []
    
    return st.session_state.documents

def filter_documents(search_query=None, doc_type=None, confidentiality=None):
    """条件に基づいてドキュメントをフィルタリング"""
    docs = get_documents()
    
    if search_query:
        docs = [doc for doc in docs if search_query.lower() in doc["name"].lower()]
    
    if doc_type and doc_type != "すべて":
        docs = [doc for doc in docs if doc["type"] == doc_type]
    
    if confidentiality and confidentiality != "すべて":
        level = int(confidentiality[0])
        docs = [doc for doc in docs if doc["confidentiality"] == level]
    
    return docs