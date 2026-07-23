"""
機能: アプリケーション設定の読み込み
ロジック: 環境変数から設定値を取得し、Settings インスタンスとして管理する
作成者: 馬 猛
作成日: 2026/07/02
修正日: 2026/07/22
"""

from pydantic_settings import BaseSettings

# from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーションの設定を定義する"""

    # Application
    app_name: str
    host: str
    port: int

    # Ollama
    ollama_url: str
    ollama_model: str
    embedding_model: str
    embedding_dimension: int

    # CORS
    allow_origins: str

    # PostgreSQL
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    # Qdrant
    qdrant_url: str
    qdrant_collection: str

    # RAG
    rag_enabled: bool = True
    rag_search_limit: int = 3
    rag_score_threshold: float = 0.5

    class Config:
        """設定クラスの構成を定義する"""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
