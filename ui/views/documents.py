"""
ドキュメントページ

ドキュメント管理インターフェース
"""

import streamlit as st
import asyncio
from datetime import datetime
from utils.ui_components import card_container, close_card_container, document_item, section_header
from utils.session import get_documents, add_document, filter_documents
from utils.api_client import get_api_client

async def upload_document(file, metadata):
    """
    ドキュメントをアップロード
    
    Args:
        file: アップロードされたファイル
        metadata: ドキュメントのメタデータ
    
    Returns:
        アップロード結果
    """
    # APIクライアントを取得
    client = await get_api_client()
    
    try:
        # ドキュメントをアップロード
        response = await client.upload_document(file, metadata)
        
        # セッションのドキュメントリストに追加
        add_document(response)
        
        return response
    except Exception as e:
        st.error(f"アップロードエラー: {str(e)}")
        return None

def document_detail(doc_id):
    """
    ドキュメント詳細ページを表示
    
    Args:
        doc_id: ドキュメントID
    """
    # セッションからドキュメントを検索
    documents = get_documents()
    doc = next((d for d in documents if d["id"] == doc_id), None)
    
    if not doc:
        st.error(f"ドキュメントID {doc_id} が見つかりません")
        return
    
    st.title(f"ドキュメント詳細: {doc['name']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        detail_container = card_container("基本情報")
        with detail_container:
            st.write(f"**ファイル名:** {doc['name']}")
            st.write(f"**ファイルタイプ:** {doc['type']}")
            st.write(f"**サイズ:** {doc['size']}")
            st.write(f"**アップロード日:** {doc['uploaded']}")
            st.write(f"**機密レベル:** {doc['confidentiality']}")
            
            # タグ（実際のAPIレスポンスに合わせて調整）
            st.write("**タグ:** ドキュメント, 仕様書")
        close_card_container()
        
        preview_container = card_container("プレビュー")
        with preview_container:
            # ファイルタイプに応じたプレビュー表示
            if doc['type'] == "PDF":
                st.info("PDFプレビューはまだ実装されていません。")
            elif doc['type'] == "Excel":
                st.info("Excelプレビューはまだ実装されていません。")
            elif doc['type'] == "Word":
                st.info("Wordプレビューはまだ実装されていません。")
            elif doc['type'] == "Text":
                st.info("テキストプレビューはまだ実装されていません。")
            else:
                st.info("このファイル形式のプレビューはサポートされていません。")
        close_card_container()
    
    with col2:
        actions_container = card_container("アクション")
        with actions_container:
            st.button("ダウンロード", key="download_doc")
            st.button("削除", key="delete_doc")
            st.button("共有", key="share_doc")
        close_card_container()
        
        usage_container = card_container("使用状況")
        with usage_container:
            st.write("**閲覧回数:** 15回")
            st.write("**直近の閲覧:** 2023-03-09")
            st.write("**質問回数:** 5回")
            
            st.subheader("関連質問")
            st.write("- プロジェクトの概要について")
            st.write("- セキュリティ要件について")
        close_card_container()

def display_documents_page():
    """ドキュメントページを表示"""
    st.title("ドキュメント管理")
    
    # タブでセクションを分ける
    tab1, tab2 = st.tabs(["ドキュメント一覧", "アップロード"])
    
    # タブ1: ドキュメント一覧
    with tab1:
        list_container = card_container()
        
        with list_container:
            # 検索・フィルター
            search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
            with search_col1:
                search_query = st.text_input("ドキュメント検索", placeholder="ファイル名を入力...")
            with search_col2:
                doc_type = st.selectbox("ファイルタイプ", ["すべて", "PDF", "Excel", "Word", "テキスト"])
            with search_col3:
                confidence_level = st.selectbox("機密レベル", ["すべて", "1 - 社内", "2 - 社外秘", "3 - 極秘"])
            
            # ドキュメント一覧
            section_header("ドキュメント一覧")
            
            # ドキュメントのフィルタリング
            filtered_docs = filter_documents(search_query, doc_type, confidence_level)
            
            if not filtered_docs:
                st.warning("条件に一致するドキュメントがありません。")
            else:
                for doc in filtered_docs:
                    # ドキュメントアイテムの表示
                    document_item(
                        doc,
                        on_detail=lambda d=doc: document_detail(d["id"]),
                        on_delete=lambda d=doc: st.warning(f"削除機能はまだ実装されていません: {d['name']}")
                    )
        
        close_card_container()
    
    # タブ2: アップロード
    with tab2:
        upload_container = card_container("ドキュメントアップロード", "新しいドキュメントをアップロードします")
        
        with upload_container:
            # アップロードフォーム
            uploaded_file = st.file_uploader("ファイルを選択", type=["pdf", "xlsx", "xls", "docx", "txt"])
            
            if uploaded_file is not None:
                # ファイル情報表示
                file_details = {
                    "ファイル名": uploaded_file.name,
                    "ファイルタイプ": uploaded_file.type,
                    "サイズ": f"{uploaded_file.size / 1024:.1f} KB"
                }
                
                st.json(file_details)
                
                # メタデータ入力
                with st.form(key="upload_form"):
                    st.subheader("メタデータ")
                    conf_level = st.radio("機密レベル", ["1 - 社内", "2 - 社外秘", "3 - 極秘"], horizontal=True)
                    tags = st.text_input("タグ (カンマ区切り)", "ドキュメント, 仕様書")
                    description = st.text_area("説明", placeholder="ドキュメントの説明を入力...", height=100)
                    
                    # アップロード実行
                    submit_button = st.form_submit_button("処理開始", type="primary")
                    
                    if submit_button:
                        with st.spinner("ドキュメントを処理中..."):
                            # メタデータの準備
                            metadata = {
                                "confidentiality": int(conf_level[0]),
                                "tags": [tag.strip() for tag in tags.split(",")],
                                "description": description
                            }
                            
                            # 非同期でアップロード処理
                            result = asyncio.run(upload_document(uploaded_file, metadata))
                            
                            if result:
                                st.success(f"ファイル「{uploaded_file.name}」の処理が完了しました！")
                                
                                # アップロード後にドキュメント一覧タブに切り替え
                                st.markdown('<script>document.querySelector("button[data-baseweb=\\"tab\\"]").click()</script>', unsafe_allow_html=True)
        
        close_card_container()
        
        # アップロードのヘルプ情報
        help_container = card_container("アップロードのヒント")
        with help_container:
            st.info("""
            **サポートされるファイル形式:**
            - PDF (.pdf)
            - Excel (.xlsx, .xls)
            - Word (.docx)
            - テキスト (.txt)
            
            **機密レベルについて:**
            - **レベル1 (社内)**: 社内での共有は自由
            - **レベル2 (社外秘)**: 許可されたユーザーのみアクセス可能
            - **レベル3 (極秘)**: 厳重な管理が必要、LLMへの送信は制限される
            
            **ファイルサイズ制限:** 100MB
            """)
        close_card_container()
