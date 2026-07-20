#
# 機能: アプリケーション設定の読み込み
# ロジック: 環境変数から設定値を取得し、Settings インスタンスとして管理する
# 作成者: 馬 猛
# 作成日: 2026/7/2
#

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーションの設定を定義する"""

    app_name: str
    host: str
    port: int
    ollama_url: str
    ollama_model: str
    allow_origins: str

    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    class Config:
        """設定クラスの構成を定義する"""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
