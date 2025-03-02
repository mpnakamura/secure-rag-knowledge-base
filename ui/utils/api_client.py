"""
APIクライアント

バックエンドAPIとの通信を担当するモジュール
"""

import httpx
import json
import streamlit as st
import logging
from typing import Dict, List, Any, Optional
import os

logger = logging.getLogger(__name__)

# API設定
API_URL = os.environ.get("API_URL", "http://api:8000")
TIMEOUT = 30.0  # リクエストタイムアウト（秒）

class APIClient:
    """バックエンドAPIクライアント"""
    
    def __init__(self, base_url: str = API_URL):
        """
        初期化
        
        Args:
            base_url: APIのベースURL
        """
        self.base_url = base_url
        self.token = None
    
    def _get_headers(self) -> Dict[str, str]:
        """
        APIリクエスト用のヘッダーを取得
        
        Returns:
            ヘッダー辞書
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        return headers
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None, 
        params: Optional[Dict] = None
    ) -> Dict:
        """
        APIリクエストを実行
        
        Args:
            method: HTTPメソッド（GET, POST, PUT, DELETE）
            endpoint: APIエンドポイント
            data: リクエストボディ（オプション）
            params: クエリパラメータ（オプション）
            
        Returns:
            レスポンス（辞書）
            
        Raises:
            Exception: API通信エラー
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data, params=params)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json=data, params=params)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            try:
                error_data = e.response.json()
                error_message = error_data.get("detail", str(e))
            except:
                error_message = str(e)
            
            raise Exception(f"APIエラー: {error_message}")
            
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"APIリクエストエラー: {str(e)}")
    
    # 認証関連エンドポイント
    async def login(self, username: str, password: str) -> Dict:
        """
        ログイン
        
        Args:
            username: ユーザー名
            password: パスワード
            
        Returns:
            ログイン結果（トークンを含む）
        """
        # 開発環境モック
        if os.getenv("DEVELOPMENT") == "1":
            if username == "admin" and password == "admin":
                self.token = "mock_token"
                return {
                    "access_token": "mock_token",
                    "token_type": "bearer",
                    "user": {
                        "username": username,
                        "role": "admin"
                    }
                }
            else:
                raise Exception("ユーザー名またはパスワードが正しくありません。")
        
        # 実際のAPI呼び出し
        data = {"username": username, "password": password}
        response = await self._make_request("POST", "/api/auth/login", data=data)
        
        if "access_token" in response:
            self.token = response["access_token"]
        
        return response
    
    # ドキュメント関連エンドポイント
    async def get_documents(self, search: Optional[str] = None) -> List[Dict]:
        """
        ドキュメント一覧を取得
        
        Args:
            search: 検索クエリ（オプション）
            
        Returns:
            ドキュメントリスト
        """
        # 開発環境モック
        if os.getenv("DEVELOPMENT") == "1":
            mock_documents = [
                {"id": 1, "name": "プロジェクト仕様書.pdf", "uploaded": "2023-03-01", "size": "2.4 MB", "type": "PDF", "confidentiality": 2},
                {"id": 2, "name": "システム設計書.docx", "uploaded": "2023-03-02", "size": "1.8 MB", "type": "Word", "confidentiality": 2},
                {"id": 3, "name": "テスト計画書.xlsx", "uploaded": "2023-03-03", "size": "1.2 MB", "type": "Excel", "confidentiality": 1},
                {"id": 4, "name": "議事録.txt", "uploaded": "2023-03-04", "size": "0.1 MB", "type": "Text", "confidentiality": 1},
                {"id": 5, "name": "API仕様書.pdf", "uploaded": "2023-03-05", "size": "3.5 MB", "type": "PDF", "confidentiality": 2},
            ]
            
            if search:
                return [doc for doc in mock_documents if search.lower() in doc["name"].lower()]
            return mock_documents
        
        # 実際のAPI呼び出し
        params = {"search": search} if search else None
        response = await self._make_request("GET", "/api/documents", params=params)
        return response.get("items", [])
    
    async def upload_document(self, file, metadata: Dict) -> Dict:
        """
        ドキュメントをアップロード
        
        Args:
            file: アップロードするファイル
            metadata: ドキュメントのメタデータ
            
        Returns:
            アップロード結果
        """
        # 開発環境では実際のアップロードは行わない
        if os.getenv("DEVELOPMENT") == "1":
            return {
                "id": 6,
                "name": file.name,
                "uploaded": "2023-03-10",
                "size": f"{file.size / (1024 * 1024):.1f} MB",
                "type": file.name.split(".")[-1].upper(),
                "confidentiality": metadata.get("confidentiality", 1)
            }
        
        # 実際のAPI呼び出しでは、multipart/form-dataでアップロード
        # この実装はhttpxのファイルアップロード機能を使用
        # 実際のAPIエンドポイントに合わせて調整が必要
        return await self._make_request("POST", "/api/documents/upload", data=metadata)
    
    # チャット関連エンドポイント
    async def send_query(self, query: str) -> Dict:
        """
        質問を送信
        
        Args:
            query: 質問内容
            
        Returns:
            回答結果
        """
        # 開発環境モック
        if os.getenv("DEVELOPMENT") == "1":
            responses = {
                "プロジェクト": "このプロジェクトは、社内ドキュメントを検索・質問できるRAGシステムの開発です。",
                "システム": "システムは主に4つのコンポーネントで構成されています：UI、API、RAGエンジン、ベクトルDB。",
                "機能": "主な機能要件には、ドキュメント管理機能、検索・質問応答機能、LLM連携機能、ユーザー管理機能があります。",
            }
            
            response_text = "申し訳ありませんが、関連する情報が見つかりませんでした。別の質問をお試しください。"
            
            for key, text in responses.items():
                if key.lower() in query.lower():
                    response_text = text
                    break
            
            return {
                "answer": response_text,
                "context": [
                    {"document": "プロジェクト仕様書.pdf", "page": 5, "text": "機能要件には、ドキュメント管理機能、検索・質問応答機能が含まれる。"},
                    {"document": "システム設計書.docx", "page": 12, "text": "システムは4つのコンポーネントで構成：UI、API、RAGエンジン、ベクトルDB"}
                ]
            }
        
        # 実際のAPI呼び出し
        data = {"query": query}
        return await self._make_request("POST", "/api/query", data=data)
    
    # 履歴関連エンドポイント
    async def get_history(self) -> List[Dict]:
        """
        質問履歴を取得
        
        Returns:
            質問履歴リスト
        """
        # 開発環境モック
        if os.getenv("DEVELOPMENT") == "1":
            return [
                {"id": 1, "query": "プロジェクトの概要について教えてください", "date": "2023-03-10", "documents": ["プロジェクト仕様書.pdf"]},
                {"id": 2, "query": "システム設計書のセキュリティ要件はどこに記載されていますか？", "date": "2023-03-09", "documents": ["システム設計書.docx"]},
                {"id": 3, "query": "APIの認証方式は何を使用していますか？", "date": "2023-03-08", "documents": ["API仕様書.pdf", "システム設計書.docx"]},
                {"id": 4, "query": "テスト計画書の進捗状況はどうなっていますか？", "date": "2023-03-07", "documents": ["テスト計画書.xlsx", "議事録.txt"]},
                {"id": 5, "query": "プロジェクトのタイムラインを教えてください", "date": "2023-03-06", "documents": ["プロジェクト仕様書.pdf", "議事録.txt"]},
            ]
        
        # 実際のAPI呼び出し
        response = await self._make_request("GET", "/api/history")
        return response.get("items", [])
    
    # 設定関連エンドポイント
    async def update_llm_settings(self, settings: Dict) -> Dict:
        """
        LLM設定を更新
        
        Args:
            settings: LLM設定
            
        Returns:
            更新結果
        """
        # 開発環境モック
        if os.getenv("DEVELOPMENT") == "1":
            return {"status": "success", "message": "設定が更新されました"}
        
        # 実際のAPI呼び出し
        return await self._make_request("POST", "/api/settings/llm", data=settings)

# シングルトンインスタンス
client = APIClient()

# 簡易アクセス関数
async def get_api_client() -> APIClient:
    """APIクライアントのシングルトンインスタンスを取得"""
    return client