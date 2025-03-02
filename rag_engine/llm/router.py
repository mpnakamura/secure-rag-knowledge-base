"""
LLMプロバイダールーター

複数のLLMプロバイダー（OpenAI, Claude, Gemini）への接続を管理する
"""

from enum import Enum
from typing import Dict, Optional, List, Any
import os
import json
from pathlib import Path
import logging
import asyncio

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    """利用可能なLLMプロバイダー"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LOCAL = "local"

class LLMRouter:
    """複数のLLMプロバイダーへのルーティングを担当"""
    
    def __init__(self, settings_path: str = "/data/settings/llm_settings.json"):
        """
        LLMルーターの初期化
        
        Args:
            settings_path: LLM設定ファイルのパス
        """
        self.settings_path = Path(settings_path)
        self.clients = {}
        self.active_provider = None
        self._load_settings()
        
    def _load_settings(self):
        """設定ファイルからLLM設定を読み込む"""
        try:
            if self.settings_path.exists():
                with open(self.settings_path, "r") as f:
                    settings = json.load(f)
                    self.active_provider = settings.get("active_provider", LLMProvider.LOCAL)
                    
                    # OpenAI
                    if "openai" in settings and settings["openai"].get("api_key"):
                        from .openai_client import OpenAIClient
                        self.clients[LLMProvider.OPENAI] = OpenAIClient(
                            api_key=settings["openai"]["api_key"],
                            model=settings["openai"].get("model", "gpt-4o")
                        )
                        logger.info(f"OpenAI client initialized with model {settings['openai'].get('model', 'gpt-4o')}")
                    
                    # Claude
                    if "claude" in settings and settings["claude"].get("api_key"):
                        from .claude_client import ClaudeClient
                        self.clients[LLMProvider.CLAUDE] = ClaudeClient(
                            api_key=settings["claude"]["api_key"],
                            model=settings["claude"].get("model", "claude-3-5-sonnet")
                        )
                        logger.info(f"Claude client initialized with model {settings['claude'].get('model', 'claude-3-5-sonnet')}")
                    
                    # Gemini
                    if "gemini" in settings and settings["gemini"].get("api_key"):
                        from .gemini_client import GeminiClient
                        self.clients[LLMProvider.GEMINI] = GeminiClient(
                            api_key=settings["gemini"]["api_key"],
                            model=settings["gemini"].get("model", "gemini-1.5-pro")
                        )
                        logger.info(f"Gemini client initialized with model {settings['gemini'].get('model', 'gemini-1.5-pro')}")
                    
                    # ローカルLLM
                    local_llm_url = os.environ.get("LOCAL_LLM_URL")
                    if local_llm_url and settings.get("use_local_llm", False):
                        from .local_client import LocalLLMClient
                        self.clients[LLMProvider.LOCAL] = LocalLLMClient(api_url=local_llm_url)
                        logger.info(f"Local LLM client initialized with URL {local_llm_url}")
            else:
                # 設定ファイルがない場合はローカルLLMがあればそれを使用
                local_llm_url = os.environ.get("LOCAL_LLM_URL")
                if local_llm_url:
                    from .local_client import LocalLLMClient
                    self.clients[LLMProvider.LOCAL] = LocalLLMClient(api_url=local_llm_url)
                    self.active_provider = LLMProvider.LOCAL
                    logger.info(f"Using local LLM at {local_llm_url}")
        except Exception as e:
            logger.error(f"Error loading LLM settings: {e}")
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """
        LLMでレスポンスを生成
        
        Args:
            prompt: プロンプト
            context: コンテキスト（オプション）
            
        Returns:
            生成されたレスポンス
            
        Raises:
            ValueError: アクティブなLLMプロバイダーが設定されていない場合
        """
        if not self.active_provider or self.active_provider not in self.clients:
            # デバッグ用：設定がない場合はダミーの応答を返す
            if os.getenv("DEBUG") == "true":
                return f"[デバッグモード] プロンプト: {prompt}\nコンテキスト: {context}\n\nLLMプロバイダーが設定されていません。"
            raise ValueError("No active LLM provider configured")
        
        client = self.clients[self.active_provider]
        try:
            return await client.generate(prompt, context)
        except Exception as e:
            logger.error(f"Error generating response with {self.active_provider}: {e}")
            return f"エラーが発生しました: {str(e)}"
    
    def update_settings(self, settings: Dict):
        """
        LLM設定を更新
        
        Args:
            settings: 新しい設定
        """
        try:
            # 設定ディレクトリがなければ作成
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_path, "w") as f:
                json.dump(settings, f, indent=2)
            
            # 設定を再読み込み
            self._load_settings()
            logger.info(f"LLM settings updated, active provider: {self.active_provider}")
        except Exception as e:
            logger.error(f"Error updating LLM settings: {e}")
            raise

    def get_available_providers(self) -> List[str]:
        """設定済みのプロバイダー一覧を取得"""
        return list(self.clients.keys())
    
    def get_active_provider(self) -> Optional[str]:
        """現在アクティブなプロバイダーを取得"""
        return self.active_provider

# テスト用コード
if __name__ == "__main__":
    import asyncio
    
    async def test_router():
        # テスト用の設定
        router = LLMRouter()
        
        # デモ設定を作成
        demo_settings = {
            "active_provider": "openai",
            "openai": {
                "api_key": "sk-demo-key",
                "model": "gpt-4o"
            }
        }
        
        # 設定を更新
        router.update_settings(demo_settings)
        
        # レスポンス生成テスト
        response = await router.generate_response(
            "こんにちは、世界!",
            "これはテストです。"
        )
        print(f"Response: {response}")
    
    asyncio.run(test_router())