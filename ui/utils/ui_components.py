"""
共通UIコンポーネント
"""

import streamlit as st
from streamlit_extras.colored_header import colored_header
import logging

logger = logging.getLogger(__name__)

def card_container(title=None, description=None, color="blue-70"):
    """
    カードスタイルのコンテナを作成
    
    Args:
        title: カードのタイトル (None の場合はヘッダー無し)
        description: タイトルの説明 (None の場合は説明無し)
        color: ヘッダーの色
    
    Returns:
        コンテナオブジェクト
    """
    container = st.container()
    
    with container:
        st.markdown('<div class="container-card">', unsafe_allow_html=True)
        
        if title:
            colored_header(
                label=title,
                description=description if description else "",
                color_name=color
            )
        
        # ここで yield して中身を他のコードで埋められるようにしたいが、
        # Python の with 構文では複雑なので、代わりに container を返す
        
        # コンテナの終了タグは呼び出し側で追加する必要がある
        # st.markdown('</div>', unsafe_allow_html=True)
    
    return container

def close_card_container():
    """カードコンテナを閉じる"""
    st.markdown('</div>', unsafe_allow_html=True)

def info_card(title, value, delta=None, icon=None):
    """
    情報カード（メトリクス表示用）
    
    Args:
        title: カードのタイトル
        value: 表示する値
        delta: 変化量（オプション）
        icon: アイコン（絵文字）
    """
    with st.container():
        if icon:
            st.subheader(f"{icon} {title}")
        else:
            st.subheader(title)
        
        st.metric(label="", value=value, delta=delta)

def chat_message(message, is_user=True):
    """
    チャットメッセージの表示
    
    Args:
        message: メッセージ内容
        is_user: ユーザーのメッセージかどうか
    """
    if is_user:
        st.markdown(
            f'<div class="user-message"><strong>あなた:</strong> {message}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="bot-message"><strong>AI:</strong> {message}</div>',
            unsafe_allow_html=True
        )

def document_item(doc, on_detail=None, on_delete=None):
    """
    ドキュメントアイテムの表示
    
    Args:
        doc: ドキュメント情報の辞書
        on_detail: 詳細ボタンのコールバック関数
        on_delete: 削除ボタンのコールバック関数
    """
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
        detail_btn = st.button("詳細", key=f"detail_{doc['id']}")
        delete_btn = st.button("削除", key=f"delete_{doc['id']}")
        
        if detail_btn and on_detail:
            on_detail(doc)
        
        if delete_btn and on_delete:
            on_delete(doc)
    
    st.divider()

def section_header(title, description=None):
    """
    セクションヘッダーの表示
    
    Args:
        title: セクションタイトル
        description: 説明文（オプション）
    """
    colored_header(
        label=title,
        description=description if description else "",
        color_name="blue-70"
    )

def status_badge(status):
    """
    ステータスバッジの表示
    
    Args:
        status: ステータス文字列
    """
    if status in ["アクティブ", "回答済み", "完了"]:
        st.success(status)
    elif status in ["進行中", "処理中"]:
        st.info(status)
    elif status in ["非アクティブ", "エラー", "失敗"]:
        st.error(status)
    elif status in ["保留中", "確認待ち"]:
        st.warning(status)
    else:
        st.write(status)