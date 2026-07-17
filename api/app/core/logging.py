"""
機能: アプリケーションログ設定
ロジック: コンソールとファイルへログを出力するハンドラーを構成する
作成者: 馬 猛
作成日: 2026/7/2
"""

import logging
import os
import sys

from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    アプリケーションのログ設定を初期化する。

    コンソール、通常ログファイル(app.log)、エラーログファイル(error.log)
    のログハンドラーを構成し、ログレベル、出力形式、および
    ログローテーション設定を適用する。

    Returns:
        None
    """
    
    # ログディレクトリを作成（存在しない場合）
    os.makedirs("logs", exist_ok=True)

    # ログのフォーマットを設定
    log_format = "%(asctime)s %(levelname)s %(name)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # 標準出力用のハンドラーを作成
    console_handler = logging.StreamHandler(sys.stdout)

    # ログのフォーマットを設定
    console_handler.setFormatter(formatter)
    
    # ファイル出力用のハンドラーを作成（ローテーション設定）
    file_handler = RotatingFileHandler(
        filename="logs/app.log",  # ログファイルのパス
        maxBytes=5 * 1024 * 1024,  # ログファイルの最大サイズ（5MB）
        backupCount=5,     # ログファイルのバックアップ数
        encoding="utf-8",  # ログファイルのエンコーディング
    )

    # ログのフォーマットを設定
    file_handler.setFormatter(formatter)

    # エラーログ用のハンドラーを作成（ローテーション設定）
    error_handler = RotatingFileHandler(
        filename="logs/error.log",  # エラーログファイルのパス
        maxBytes=5 * 1024 * 1024,  # エラーログファイルの最大サイズ（5MB）
        backupCount=5,     # エラーログファイルのバックアップ数
        encoding="utf-8",  # エラーログファイルのエンコーディング
    )

    error_handler.setLevel(logging.ERROR) # エラーログレベルを設定
    error_handler.setFormatter(formatter) # エラーログのフォーマットを設定

    # ルートロガーの設定
    logging.basicConfig(
        level=logging.INFO,
        # ログのハンドラーを設定
        handlers=[
            console_handler,  #  標準出力用のハンドラー
            file_handler,  # ファイル出力用のハンドラー
            error_handler  # エラーログ用のハンドラー
        ],
    )


    