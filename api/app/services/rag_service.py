"""
機能: RAGチャットサービス
ロジック: 関連文書を検索し、検索結果をコンテキストとしてLLMへ渡す
作成者: 馬 猛
作成日: 2026/07/23
"""

import logging
from typing import Any

from app.config import settings
from app.llm.ollama import OllamaService
from app.repositories.vector_repository import VectorRepository
from app.schemas.document import DocumentSearchResult
from app.schemas.openai import (
    ChatCompletionRequest,
    Message,
)
from app.schemas.rag import RagChatResponse
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class RagService:
    """関連文書検索とLLM回答生成を管理する。"""

    def __init__(self) -> None:
        """必要なServiceおよびRepositoryを初期化する。"""

        # ユーザーの質問をEmbeddingベクトルへ変換するService
        self.embedding_service = EmbeddingService()

        # Qdrantへの類似検索を担当するRepository
        self.vector_repository = VectorRepository()

        # 検索した関連文書を利用して回答を生成するLLM Service
        self.llm_service = OllamaService()

    def chat(
        self,
        question: str,
        limit: int = 3,
        score_threshold: float | None = 0.5,
    ) -> RagChatResponse:
        """
        関連文書を検索して質問への回答を生成する。

        Args:
            question: ユーザーからの質問
            limit: 取得する関連文書の最大件数
            score_threshold: 関連文書として使用する最低類似度

        Returns:
            RagChatResponse: 回答および参照文書

        Raises:
            ValueError: 質問または検索結果が不正な場合
            RuntimeError: RAGチャット処理に失敗した場合
        """

        # 質問の前後にある不要な空白や改行を削除する
        normalized_question = question.strip()

        # 空白を削除した結果、質問が空の場合は
        # Embedding生成や検索ができないためエラーにする
        if not normalized_question:
            raise ValueError("Question must not be empty.")

        # ユーザーの質問をEmbeddingベクトルへ変換する
        #
        # 登録文書と質問を同じEmbeddingモデルでベクトル化することで、
        # Qdrant上で意味的な類似度を比較できる
        query_vector = self.embedding_service.embed(
            normalized_question,
        )

        # Qdrantから質問内容に近い文書を検索する
        #
        # limit:
        #   最大何件まで取得するか
        #
        # score_threshold:
        #   どの程度以上の類似度を関連文書とみなすか
        search_results = self.vector_repository.search_similar(
            vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        # 関連文書が1件も見つからなかった場合は、
        # LLMを呼び出さずにそのまま回答を返す
        #
        # 関連情報がない状態でLLMへ質問すると、
        # モデルが推測して回答する可能性があるため、
        # RAGとして不要な回答生成を防止する
        if not search_results:
            return RagChatResponse(
                success=True,
                question=normalized_question,
                answer=(
                    "No relevant information was found in the "
                    "registered documents."
                ),
                references=[],
            )

        # Repositoryから返されたdict形式の検索結果を、
        # APIレスポンスでも使用できるDocumentSearchResultへ変換する
        references = [
            DocumentSearchResult(
                point_id=result["point_id"],
                score=result["score"],
                text=result["text"],
                source=result["source"],
            )
            for result in search_results
        ]

        # 検索結果をLLMが読みやすい文章形式へ変換する
        #
        # 例:
        # [Document 1]
        # Source: manual
        # Content: Qdrantを利用して...
        context = self._build_context(references)

        # 関連文書をSystem Promptへ含め、
        # ユーザーの質問と合わせてLLMへ送信する
        messages = self._build_messages(
            question=normalized_question,
            context=context,
        )

        # OllamaServiceへ渡すOpenAI互換リクエストを作成する
        #
        # このRAG専用APIでは通常レスポンスを使用するため、
        # stream=Falseを指定する
        request = ChatCompletionRequest(
            model=settings.ollama_model,
            messages=messages,
            stream=False,
        )

        logger.info(
            "Generating RAG answer. reference_count=%d",
            len(references),
        )

        try:
            # 関連文書を含むリクエストをLLMへ送り、
            # 文書内容に基づいた回答を生成する
            response = self.llm_service.chat(request)

        except Exception as exception:
            # Ollama通信や回答生成中にエラーが発生した場合、
            # 元の例外情報をログへ記録する
            logger.exception("Failed to generate a RAG answer.")

            raise RuntimeError(
                "Failed to generate a RAG answer."
            ) from exception

        # OpenAI互換レスポンスでは回答がchoicesに格納されるため、
        # choicesが空の場合は正常な回答を取得できていないと判断する
        if not response.choices:
            raise RuntimeError("The LLM returned no answer choices.")

        # 最初のchoiceからassistantの回答本文を取得する
        answer = response.choices[0].message.content

        # LLMの回答と、
        # 回答生成時に参照した文書をまとめて返す
        return RagChatResponse(
            success=True,
            question=normalized_question,
            answer=answer,
            references=references,
        )

    def _build_context(
        self,
        references: list[DocumentSearchResult],
    ) -> str:
        """
        検索結果からLLMへ渡すコンテキストを作成する。

        Args:
            references: Qdrantから取得した関連文書

        Returns:
            str: 整形されたコンテキスト
        """

        # 関連文書が存在しない場合は、
        # LLMへ渡すためのメッセージを返す
        #
        # 通常はchat()側で0件を処理するため、
        # ここは安全対策として残している
        if not references:
            return "No relevant documents were found."

        # 複数の関連文書を一度にまとめるためのリスト
        context_parts: list[str] = []

        # enumerate(..., start=1)を使用することで、
        # Document 1、Document 2のように1から番号を付ける
        for index, reference in enumerate(
            references,
            start=1,
        ):
            # sourceが登録されていない場合は
            # "unknown"として扱う
            source = reference.source or "unknown"

            # LLMが各文書を区別しやすい形式へ整形する
            context_parts.append(
                f"[Document {index}]\n"
                f"Source: {source}\n"
                f"Content: {reference.text}"
            )

        # 各文書の間に空行を入れて、
        # 1つのコンテキスト文字列として結合する
        return "\n\n".join(context_parts)

    def _build_messages(
        self,
        question: str,
        context: str,
    ) -> list[Message]:
        """
        RAG回答生成用のメッセージを作成する。

        Args:
            question: ユーザーからの質問
            context: 関連文書から作成したコンテキスト

        Returns:
            list[Message]: LLMへ送信するメッセージ一覧
        """

        # LLMにRAG回答時のルールを指示する
        #
        # 特に、
        # ・検索文書だけを根拠に回答する
        # ・情報がなければ推測しない
        # ・質問と同じ言語で回答する
        #
        # というルールを明示してHallucinationを抑制する
        system_prompt = (
            "You are an assistant that answers questions using the "
            "provided reference documents.\n"
            "Follow these rules:\n"
            "1. Answer based only on the reference documents.\n"
            "2. If the documents do not contain enough information, "
            "say that the information is not available.\n"
            "3. Do not invent facts.\n"
            "4. Answer in the same language as the user's question.\n\n"
            f"Reference documents:\n{context}"
        )

        # Systemメッセージを先に配置し、
        # その後に実際のユーザー質問を追加する
        return [
            Message(
                role="system",
                content=system_prompt,
            ),
            Message(
                role="user",
                content=question,
            ),
        ]

    def build_rag_messages(
        self,
        messages: list[Message],
    ) -> list[Message]:
        """
        会話メッセージへRAG検索結果を追加する。

        OpenAI互換APIやOpen WebUIから受け取った会話履歴から
        最新のユーザー質問を取得し、Qdrant検索結果を
        RAG用Systemメッセージとして追加する。

        Args:
            messages: OpenAI互換APIから受け取った会話メッセージ

        Returns:
            list[Message]: RAGコンテキストを追加したメッセージ

        Raises:
            ValueError: ユーザーの質問が取得できない場合
            RuntimeError: 関連文書検索に失敗した場合
        """

        # 会話履歴の中から、
        # 最も新しいuserロールのメッセージを取得する
        #
        # RAG検索では過去のassistant回答ではなく、
        # 最新のユーザー質問を検索キーワードとして使用する
        question = self._get_latest_user_question(messages)

        logger.info(
            "RAG search question: %s",
            question,
        )

        # 最新のユーザー質問をEmbeddingベクトルへ変換する
        query_vector = self.embedding_service.embed(question)

        # .envで設定した検索条件を利用して、
        # Qdrantから関連文書を検索する
        search_results = self.vector_repository.search_similar(
            vector=query_vector,
            limit=settings.rag_search_limit,
            score_threshold=settings.rag_score_threshold,
        )

        logger.info(
            "RAG context search completed. result_count=%d",
            len(search_results),
        )

        # Qdrantの検索結果から、
        # LLMへ与えるRAG専用Systemメッセージを生成する
        rag_system_message = Message(
            role="system",
            content=self._build_rag_system_prompt(search_results),
        )

        # RAG用Systemメッセージを会話履歴の先頭へ追加する
        #
        # 例:
        #
        # RAG System Message
        # ↓
        # 元のSystem Message
        # ↓
        # 過去の会話
        # ↓
        # 最新のUser Message
        return [
            rag_system_message,
            *messages,
        ]

    def _get_latest_user_question(
        self, messages: list[Message]
    ) -> str:
        """
        会話履歴から最新のユーザーメッセージを取得する。

        Args:
            messages: 会話メッセージ一覧

        Returns:
            str: 最新のユーザーメッセージ

        Raises:
            ValueError: 有効なユーザーメッセージがない場合
        """
        # reversed()を使用して末尾から確認することで、
        # 最新のuserメッセージを効率よく取得する
        for message in reversed(messages):
            # user以外のメッセージは検索対象ではないため、
            # 次のメッセージへ進む
            #
            # 例:
            # system / assistant → スキップ
            if message.role != "user":
                continue

            # 前後の空白や改行を削除する
            content = message.content.strip()

            # 空文字でなければ、
            # 最新の有効なユーザー質問として返す
            if content:
                return content

        # userメッセージが存在しない、
        # またはすべて空文字の場合はRAG検索できないためエラーにする
        raise ValueError(
            "No valid user message was found for RAG search."
        )

    def _build_rag_system_prompt(
        self,
        search_results: list[dict[str, Any]],
    ) -> str:
        """
        検索結果からRAG用のSystemプロンプトを作成する。

        Args:
            search_results: Qdrantから取得した類似文書

        Returns:
            str: RAG用Systemプロンプト
        """

        # Qdrantから関連文書が取得できなかった場合は、
        # LLMに「登録文書に情報がない」と明示的に伝える
        #
        # これにより、LLMが自身の知識だけで
        # 推測した回答を生成することを防止する
        if not search_results:
            return (
                "You must answer using only the registered reference "
                "documents. No relevant documents were found. "
                "Tell the user that the requested information is not "
                "available in the registered documents. "
                "Answer in the same language as the user."
            )

        # 複数の検索結果をSystem Promptへまとめるためのリスト
        context_parts: list[str] = []

        for index, result in enumerate(
            search_results,
            start=1,
        ):
            # sourceが存在しない場合はunknownとして表示する
            source = result.get("source") or "unknown"

            # 各検索結果に番号・取得元・類似度・本文を付けて、
            # LLMが参照しやすい形式へ整形する
            context_parts.append(
                f"[Document {index}]\n"
                f"Source: {source}\n"
                f"Score: {result['score']:.4f}\n"
                f"Content: {result['text']}"
            )

        # 複数文書を空行で区切って1つの文字列へまとめる
        context = "\n\n".join(context_parts)

        # 検索した文書とRAG回答時のルールを
        # System PromptとしてLLMへ渡す
        return (
            "You are a retrieval-augmented assistant.\n"
            "Follow these rules:\n"
            "1. Answer using only the reference documents below.\n"
            "2. Do not invent information that is not in the documents.\n"
            "3. If the documents are insufficient, clearly say so.\n"
            "4. Answer in the same language as the user.\n"
            "5. Refer to supporting documents as [Document 1], "
            "[Document 2], and so on when appropriate.\n\n"
            f"Reference documents:\n{context}"
        )
