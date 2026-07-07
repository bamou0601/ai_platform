"""
機能: ORMモデルを一括で読み込む
ロジック: Base.metadata.create_all() が全モデルを認識できるようにする
作成者: 馬 猛
作成日: 2026/07/06
"""

from app.models.user import User

__all__ = [
    "User",
]