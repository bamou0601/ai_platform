import time
import uuid
import logging

from fastapi import Request

logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    """リクエストとレスポンスのログを出力するミドルウェア"""
    request_id = str(uuid.uuid4())[:8]  # リクエストごとの一意なIDを生成（短縮版）
    # request_id = str(uuid.uuid4())  # リクエストごとの一意なIDを生成
    start_time   = time.time()  # 処理開始時間を記録

    # リクエスト情報をログに出力
    logger.info(
        f"[{request_id}] {request.method} {request.url.path}"
    )
    # logger.info(f"Request ID: {request_id} - {request.method} {request.url}")

    # リクエストを処理
    response = await call_next(request)

    # 処理時間を計算
    process_time = time.time() - start_time

    # レスポンス情報をログに出力
    logger.info(
        f"[{request_id}] Completed in {process_time:.3f}s"
    )
    # logger.info(
    #     f"Request ID: {request_id} 
    #     - Status Code: {response.status_code} 
    #     - Process Time: {process_time:.4f}s"
    # )

    return response