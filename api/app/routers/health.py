"""
機能: ヘルスチェック API
ロジック: サービス稼働状態を示す JSON を返す
作成者: 馬 猛
作成日: 2026/07/2
"""

from fastapi import APIRouter

# ヘルスチェック用のルーター
router = APIRouter(prefix="/health", tags=["Health"])


# サーバー状態を確認するためのエンドポイント
@router.get("")
def health():
    """サービスの稼働状態を返す"""
    return {"status": "up", "message": "AI Platform is running"}
