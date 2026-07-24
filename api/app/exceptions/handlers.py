"""
機能: 例外ハンドラー設定
ロジック: FastAPIアプリケーションに共通の例外ハンドラーを登録し、
         エラー発生時に統一したレスポンスとログを出力する
作成者: 馬 猛
作成日: 2026/07/03
"""

import logging

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# ロガーを取得
logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    """
    FastAPIアプリケーションへ共通の例外ハンドラーを登録する。

    HTTPException、Ollama通信エラー、および予期しない例外を
    捕捉し、ログを出力するとともに統一したJSONレスポンスを返却する。

    Args:
        app (FastAPI): 例外ハンドラーを登録するFastAPIアプリケーション

    Returns:
        None
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ):
        """
        HTTPExceptionを処理する。

        FastAPIが送出したHTTPExceptionを捕捉し、
        ログへ出力した後、統一フォーマットのJSONレスポンスを返却する。

        Args:
            request (Request): HTTPリクエスト
            exc (HTTPException): 発生したHTTP例外

        Returns:
            JSONResponse: エラー情報を含むJSONレスポンス
        """
        # HTTP例外の内容をログへ出力
        logger.warning(exc.detail)

        # エラーレスポンスを返却
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.detail},
        )

    @app.exception_handler(requests.exceptions.RequestException)
    async def request_exception_handler(
        request: Request, exc: requests.exceptions.RequestException
    ):
        """
        Ollamaとの通信例外を処理する。

        requestsライブラリで発生した通信エラーを捕捉し、
        ログへ出力した後、503(Service Unavailable)を返却する。

        Args:
            request (Request): HTTPリクエスト
            exc (RequestException): 通信時に発生した例外

        Returns:
            JSONResponse: エラー情報を含むJSONレスポンス
        """

        # 通信エラーをログへ出力
        logger.exception("Ollama Connection Error")

        # サービス利用不可レスポンスを返却
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": "Ollama service is unavailable.",
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ):
        """
        予期しない例外を処理する。

        アプリケーションで発生した未処理例外を捕捉し、
        ログへ出力した後、500(Internal Server Error)を返却する。

        Args:
            request (Request): HTTPリクエスト
            exc (Exception): 発生した例外

        Returns:
            JSONResponse: エラー情報を含むJSONレスポンス
        """

        # 例外が発生した場合の共通ハンドラー
        logger.exception("Unhandled Exception")

        # 内部サーバーエラーレスポンスを返却
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal Server Error",
            },
        )
