"""
機能: Prompt Template APIのリクエスト・レスポンススキーマ
ロジック: Pydanticでプロンプトテンプレートの入力値検証とレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/14
"""

from datetime import datetime

from pydantic import BaseModel

from app.schemas.pagination import PageResponse


class PromptTemplateCreate(BaseModel):
    """
    プロンプトテンプレート作成用リクエストモデル。
    処理内容:
        API経由で新しいプロンプトテンプレートを登録する際の
        入力パラメータを定義する。
        temperature、top_pにはLLM生成パラメータの初期値を設定する。

    Args:
        name(str): プロンプトテンプレート名。
        category(str): プロンプト分類カテゴリ。
        description(str): プロンプトテンプレートの説明。
        system_prompt(str): LLMへ送信するシステムプロンプト本文。

        temperature(float): LLM回答のランダム性を制御するパラメータ。
        top_p(float): LLM生成時の候補単語選択範囲を制御するパラメータ。

        is_default(bool):デフォルトテンプレートとして利用するかどうか。
    """

    # プロンプトテンプレート名
    name: str

    # 分類カテゴリ
    category: str | None = None

    # 説明文
    description: str | None = None

    # LLMへ渡すシステムプロンプト
    system_prompt: str

    # LLM生成パラメータ
    temperature: float = 0.7
    top_p: float = 0.9

    # デフォルト設定
    is_default: bool = False


class PromptTemplateUpdate(BaseModel):
    """
    プロンプトテンプレート更新用リクエストモデル。

    処理内容:
        既存のプロンプトテンプレートを更新する際に利用する。
        すべての項目をOptionalにすることで、
        部分更新(PATCH)に対応する。

        name(str): 更新後のテンプレート名。
        category(str): 更新後のカテゴリ。。
        description(str): 更新後の説明。
        system_prompt(str): 更新後のシステムプロンプト。

        temperature(float): 更新後LLM回答のランダム性を制御するパラメータ。
        top_p(float): 更新後のLLM生成パラメータ。

        is_default(bool): デフォルト設定状態。
        is_active(bool): 有効状態。
    """

    # 更新対象のテンプレート名
    name: str | None = None

    # 更新対象カテゴリ
    category: str | None = None

    # 更新対象説明
    description: str | None = None

    # 更新対象システムプロンプト
    system_prompt: str | None = None

    # 更新対象LLMパラメータ
    temperature: float | None = None
    top_p: float | None = None

    # 更新対象フラグ
    is_default: bool | None = None
    is_active: bool | None = None


class PromptTemplateResponse(BaseModel):
    """
    プロンプトテンプレートレスポンスモデル。

    処理内容:
        DBから取得したプロンプトテンプレート情報を
        APIレスポンス形式として返却する。

        from_attributesを有効化することで、
        SQLAlchemy ORMモデルから直接変換可能にする。

        id: プロンプトテンプレートID。
        name: テンプレート名。
        system_prompt: システムプロンプト本文。
        temperature: LLM生成パラメータ。

        top_p: LLM生成パラメータ。
        is_default: デフォルトテンプレート判定。
        is_active: 有効状態。
        created_at: 作成日時。
        updated_at: 更新日時。
    Returns:
        APIレスポンス用プロンプトテンプレート情報。
    """

    # プロンプトテンプレートID
    id: int

    # 基本情報
    name: str
    category: str | None
    description: str | None

    # LLM設定
    system_prompt: str
    temperature: float
    top_p: float

    # 状態管理
    is_default: bool
    is_active: bool

    # 監査情報
    created_at: datetime
    updated_at: datetime

    # SQLAlchemy ORMモデルから変換可能にする設定
    model_config = {"from_attributes": True}


class PromptTemplatePage(
    PageResponse[PromptTemplateResponse]
):
    """
    プロンプトテンプレート一覧ページングレスポンス。

    処理内容:
        PromptTemplateResponseをページ単位で返却するための
        共通ページングレスポンスモデル。
        ページ番号、総件数、データ一覧などの情報を含む。

    Returns:
        ページング形式のプロンプトテンプレート一覧。
    """

    pass
