"""
機能: リクエストログ出力ミドルウェア
ロジック: リクエストごとに一意のIDを付与し、リクエスト情報、
         レスポンス情報、および処理時間をログへ出力する
作成者: 馬 猛
作成日: 2026/7/3
"""

import time
import uuid
import logging

from fastapi import Request

# ロガーを取得
logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    """
    リクエストとレスポンスのログを出力する。

    各リクエストに一意のリクエストIDを付与し、
    リクエスト情報、レスポンス情報、および処理時間を
    ログへ出力する。

    Args:
        request (Request): クライアントから送信されたHTTPリクエスト
        call_next: 次のミドルウェアまたはエンドポイントを呼び出す関数

    Returns:
        Response: エンドポイントから返却されたHTTPレスポンス
    """
    # リクエストごとの一意なIDを生成（8文字短縮版）
    request_id = str(uuid.uuid4())[:8]  

    # フルUUIDを使用する場合
    # request_id = str(uuid.uuid4())  

    # 処理開始時間を記録
    start_time   = time.time()  

    # リクエスト情報をログに出力
    logger.info(
        f"[{request_id}] {request.method} {request.url.path}"
    )

    # 次のミドルウェアまたはエンドポイントを実行
    response = await call_next(request)

    # 処理時間を計算
    process_time = time.time() - start_time

    # レスポンス情報をログに出力
    logger.info(
        f"[{request_id}] {response.status_code} Completed in {process_time:.3f}s"
    )

    return response