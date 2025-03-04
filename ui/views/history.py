"""
履歴ページ

質問・回答履歴の表示と管理
"""

import streamlit as st
import asyncio
from datetime import datetime
from utils.ui_components import card_container, close_card_container, section_header
from utils.session import add_chat_message
from utils.api_client import get_api_client

async def get_history_data():
    """
    質問履歴データを取得
    
    Returns:
        履歴リスト
    """
    # APIクライアントを取得
    client = await get_api_client()
    
    try:
        # 履歴を取得
        return await client.get_history()
    except Exception as e:
        st.error(f"履歴取得エラー: {str(e)}")
        return []

async def recreate_query(query):
    """
    過去の質問を再度実行
    
    Args:
        query: 再実行する質問内容
    """
    # APIクライアントを取得
    client = await get_api_client()
    
    try:
        # 質問を送信し、回答を取得
        response = await client.send_query(query)
        
        # チャット履歴に追加
        add_chat_message(query, is_user=True)
        add_chat_message(response["answer"], is_user=False)
        
        # チャットページに遷移
        st.session_state.current_page = "チャット"
        
        return response
    except Exception as e:
        st.error(f"質問エラー: {str(e)}")
        return None

def display_history_page():
    """履歴ページを表示"""
    st.title("質問・回答履歴")
    
    # 検索・フィルター
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        history_search = st.text_input("履歴検索", placeholder="質問内容を入力...")
    with search_col2:
        date_range = st.date_input("日付", value=[])
    
    # 履歴リストを取得（非同期）
    history_data = asyncio.run(get_history_data())
    
    # 検索フィルタリング
    if history_search:
        history_data = [h for h in history_data if history_search.lower() in h["query"].lower()]
    
    # 日付フィルタリング（日付範囲が選択されている場合）
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        # 実装注意: ここでは日付文字列形式に依存しているため、APIレスポンスの日付形式に合わせて調整が必要
        history_data = [h for h in history_data if start_date <= datetime.strptime(h["date"], "%Y-%m-%d").date() <= end_date]
    
    # 履歴一覧
    history_container = card_container("質問履歴", "過去の質問と回答の履歴")
    
    with history_container:
        if not history_data:
            st.info("履歴がありません。チャットページで質問してみましょう。")
        else:
            for item in history_data:
                with st.expander(f"Q: {item['query']} ({item['date']})"):
                    # 質問
                    st.write("**質問:**")
                    st.info(item["query"])
                    
                    # 回答（実際のAPIレスポンスでは回答内容が含まれるはず）
                    st.write("**回答:**")
                    sample_response = "このプロジェクトは、社内ドキュメントを検索・質問できるRAGシステムの開発です。仕様書によると、Excelやテキストなど様々な形式のドキュメントをインデックス化し、自然言語で質問できる機能を提供します。"
                    st.success(sample_response)
                    
                    # 参照ドキュメント
                    st.write("**参照ドキュメント:**")
                    for doc in item["documents"]:
                        st.write(f"- {doc}")
                    
                    # アクションボタン
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("類似質問を検索", key=f"similar_{item['id']}"):
                            st.info("この機能はまだ実装されていません。")
                    with col2:
                        if st.button("再質問する", key=f"retry_{item['id']}"):
                            # 非同期で質問を再実行
                            asyncio.run(recreate_query(item["query"]))
                            st.experimental_rerun()
                    with col3:
                        if st.button("ダウンロード", key=f"download_{item['id']}"):
                            st.info("この機能はまだ実装されていません。")
    
    close_card_container()
    
    # 統計情報
    stats_container = card_container("履歴統計")
    
    with stats_container:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("質問カテゴリ")
            # ダミーデータ（実際の実装ではAPIから取得）
            categories = {
                "プロジェクト情報": 15,
                "技術情報": 12,
                "仕様": 8,
                "スケジュール": 5
            }
            
            # 簡易グラフ表示
            st.bar_chart(categories)
        
        with col2:
            st.subheader("よく参照されるドキュメント")
            # ダミーデータ
            documents = {
                "プロジェクト仕様書.pdf": 18,
                "システム設計書.docx": 14,
                "API仕様書.pdf": 10,
                "テスト計画書.xlsx": 7,
                "議事録.txt": 4
            }
            
            # 簡易グラフ表示
            st.bar_chart(documents)
    
    close_card_container()
    
    # 一括操作
    action_container = card_container("一括操作")
    
    with action_container:
        st.write("履歴の一括操作")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("すべての履歴をダウンロード"):
                st.info("この機能はまだ実装されていません。")
        with col2:
            if st.button("履歴をクリア"):
                if st.checkbox("本当に履歴をクリアしますか？"):
                    st.warning("この操作は取り消せません。")
                    if st.button("はい、クリアします"):
                        st.success("履歴がクリアされました。")
                        # 実際にはAPIリクエストを送信して履歴をクリア
    
    close_card_container()
