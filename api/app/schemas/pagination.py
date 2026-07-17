"""
機能: ページネーションAPIの共通レスポンススキーマ
ロジック: 一覧取得APIで利用するページング情報とデータ一覧を定義する
作成者: 馬 猛
作成日: 2026/07/15
"""

from typing import Generic, TypeVar

from pydantic.generics import GenericModel

# ジェネリック型を定義
T = TypeVar("T")


class PageResponse(GenericModel, Generic[T]):
    """
    ページネーション付きレスポンススキーマ。

    一覧取得APIで共通利用するページング情報と、
    取得したデータ一覧を定義する。

    Attributes:
        total (int): 全件数
        page (int): 現在のページ番号
        size (int): 1ページあたりの取得件数
        items (list[T]): 取得したデータ一覧
    """

    total: int
    page: int
    size: int
    items: list[T]
