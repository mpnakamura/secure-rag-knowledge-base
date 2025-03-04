"""
ホーム画面（ダッシュボード）の実装
"""

import streamlit as st
from utils.session import get_documents
from utils.ui_components import card_container, close_card_container, info_card, section_header, status_badge

def display_home_page():
    """ホーム画面（ダッシュボード）を表示"""
    st.title("ダッシュボード")
    
    # 概要カード
    col1, col2, col3 = st.columns(3)
    
    with col1:
        info_card("📄 ドキュメント数", "5", "2 件 新規追加")
    
    with col2:
        info_card("💬 質問数", "27", "5% 増加")
    
    with col3:
        info_card("🔍 検索精度", "87%", "3% 向上")
    
    # 最近の質問
    container = card_container("最近の質問", "直近の質問内容")
    
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
            status_badge(q['status'])
        st.divider()
    
    close_card_container()
    
    # 最近のドキュメント
    container = card_container("最近追加されたドキュメント", "直近でアップロードされたドキュメント")
    
    documents = get_documents()
    recent_docs = documents[:3] if len(documents) > 3 else documents
    
    if not recent_docs:
        st.info("最近追加されたドキュメントはありません。")
    else:
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
    
    close_card_container()
    
    # アクティビティログ
    container = card_container("システム状態", "現在のシステム状況")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("CPU使用率", "12%", "-5%")
        st.metric("メモリ使用率", "35%", "2%")
    
    with col2:
        st.metric("ストレージ", "1.2GB / 10GB", "")
        st.metric("API呼び出し回数（今日）", "127回", "15%")
    
    close_card_container()

if __name__ == "__main__":
    # 単体テスト用
    display_home_page()
