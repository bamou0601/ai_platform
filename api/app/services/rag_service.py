"""
機能: RAGチャットサービス
ロジック: 関連文書を検索し、検索結果をコンテキストとしてLLMへ渡す
作成者: 馬 猛
作成日: 2026/07/23
"""

import logging

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

        self.embedding_service = EmbeddingService()
        self.vector_repository = VectorRepository()
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

        normalized_question = question.strip()

        if not normalized_question:
            raise ValueError("Question must not be empty.")

        # 質問文からEmbeddingを生成する
        query_vector = self.embedding_service.embed(
            normalized_question,
        )

        # Qdrantから関連文書を検索する
        search_results = self.vector_repository.search_similar(
            vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

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

        references = [
            DocumentSearchResult(
                point_id=result["point_id"],
                score=result["score"],
                text=result["text"],
                source=result["source"],
            )
            for result in search_results
        ]

        # 検索結果からLLMへ渡すコンテキストを作成する
        context = self._build_context(references)

        # RAG用のメッセージを作成する
        messages = self._build_messages(
            question=normalized_question,
            context=context,
        )

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
            response = self.llm_service.chat(request)

        except Exception as exception:
            logger.exception("Failed to generate a RAG answer.")

            raise RuntimeError(
                "Failed to generate a RAG answer."
            ) from exception

        if not response.choices:
            raise RuntimeError("The LLM returned no answer choices.")

        answer = response.choices[0].message.content

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

        if not references:
            return "No relevant documents were found."

        context_parts: list[str] = []

        for index, reference in enumerate(
            references,
            start=1,
        ):
            source = reference.source or "unknown"

            context_parts.append(
                f"[Document {index}]\n"
                f"Source: {source}\n"
                f"Content: {reference.text}"
            )
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

        Args:
            messages: OpenAI互換APIから受け取った会話メッセージ

        Returns:
            list[Message]: RAGコンテキストを追加したメッセージ

        Raises:
            ValueError: ユーザーの質問が取得できない場合
            RuntimeError: 関連文書検索に失敗した場合
        """

        question = self._get_latest_user_question(messages)

        logger.info(
            "RAG search question: %s",
            question,
        )

        # 質問文からEmbeddingを生成する
        query_vector = self.embedding_service.embed(question)

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

        # 検索結果からRAG用のSystemメッセージを作成する
        rag_system_message = Message(
            role="system",
            content=self._build_rag_system_prompt(search_results),
        )

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

        for message in reversed(messages):
            if message.role != "user":
                continue

            content = message.content.strip()

            if content:
                return content

        raise ValueError(
            "No valid user message was found for RAG search."
        )

    def _build_rag_system_prompt(
        self,
        search_results: list[dict],
    ) -> str:
        """
        検索結果からRAG用のSystemプロンプトを作成する。

        Args:
            search_results: Qdrantから取得した類似文書

        Returns:
            str: RAG用Systemプロンプト
        """

        if not search_results:
            return (
                "You must answer using only the registered reference "
                "documents. No relevant documents were found. "
                "Tell the user that the requested information is not "
                "available in the registered documents. "
                "Answer in the same language as the user."
            )

        context_parts: list[str] = []

        for index, result in enumerate(
            search_results,
            start=1,
        ):
            source = result.get("source") or "unknown"

            context_parts.append(
                f"[Document {index}]\n"
                f"Source: {source}\n"
                f"Score: {result['score']:.4f}\n"
                f"Content: {result['text']}"
            )

        context = "\n\n".join(context_parts)

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
