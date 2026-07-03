import logging
import requests

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI):
    """FastAPI アプリケーションに例外ハンドラーを登録する関数"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException
    ):

        logger.warning(exc.detail)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail
            }
        )

    @app.exception_handler(requests.exceptions.RequestException)
    async def request_exception_handler(
        request: Request,
        exc: requests.exceptions.RequestException
    ):

        logger.exception("Ollama Connection Error")

        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": "Ollama service is unavailable."
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception
    ):
        
        # 例外が発生した場合の共通ハンドラー
        logger.exception("Unhandled Exception")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal Server Error"
            }
        )
    
    


