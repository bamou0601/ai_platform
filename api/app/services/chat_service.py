"""
機能: Chat Serviceのビジネスロジック
ロジック: 会話管理、プロンプト取得、Ollamaとの対話、および会話履歴の保存を行う
作成者: 馬 猛
作成日: 2026/07/07
修正日: 2026/07/23
"""

import logging
from collections.abc import Iterator

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.llm.base import LLMService
from app.llm.ollama import OllamaService
from app.models.conversation import Conversation
from app.repositories.prompt_template_repository import (
    PromptTemplateRepository,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.conversation import ConversationCreate
from app.schemas.conversation_message import (
    ConversationMessageCreate,
)
from app.schemas.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Message,
)
from app.services.conversation_message_service import (
    ConversationMessageService,
)
from app.services.conversation_service import (
    ConversationService,
)
from app.services.rag_service import RagService

logger = logging.getLogger(__name__)


class ChatService:
    """
    Chat機能のビジネスロジックを提供するService。

    Conversationの取得・新規作成、Prompt Templateの取得、
    過去の会話履歴を含むOpenAI互換リクエストの生成、
    LLMへの問い合わせ、および会話メッセージの保存を行う。
    """

    def __init__(self):
        """
        ChatServiceを初期化する。

        LLMサービス、Repository、および各業務Serviceの
        インスタンスを生成する。

        Returns:
            None
        """

        # LLM抽象型としてOllama実装を設定
        self.llm_service: LLMService = OllamaService()

        # Prompt Template Repositoryを生成
        self.prompt_repository = PromptTemplateRepository()

        # Conversation Serviceを生成
        self.conversation_service = ConversationService()

        # Conversation Message Serviceを生成
        self.conversation_message_service = (
            ConversationMessageService()
        )

        # rag Serviceを生成
        self.rag_service = RagService()

    def chat(self, db: Session, request: ChatRequest) -> ChatResponse:
        """
        チャットを実行する。

        Conversationを取得または新規作成し、Prompt Templateと
        過去の会話履歴からOpenAI互換リクエストを生成する。
        LLMの回答取得後、ユーザー入力とAI回答を保存し、
        独自Chat APIのレスポンスを返却する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            request (ChatRequest):
                ユーザーID、Conversation ID、メッセージ、
                Prompt Template IDを含むチャットリクエスト

        Returns:
            ChatResponse:
                Conversation IDとAI回答を含むレスポンス

        Raises:
            HTTPException:
                ConversationまたはPrompt Templateが
                存在しない場合

        """
        # Conversationを取得または新規作成
        conversation = self._get_or_create_conversation(db, request)

        # プロンプトテンプレートを取得
        prompt = self.prompt_repository.find_by_id(
            db, request.prompt_template_id
        )

        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Prompt Template not found",
            )

        # Ollamaへ送信するメッセージ一覧を生成
        messages = self._build_messages(
            db=db,
            conversation_id=conversation.id,
            system_prompt=prompt.system_prompt,
            user_message=request.message,
        )

        # OpenAI互換リクエストを生成
        completion_request = ChatCompletionRequest(
            model=settings.ollama_model,
            messages=messages,
            temperature=prompt.temperature,
            top_p=prompt.top_p,
            stream=False,
        )

        # LLMへ問い合わせ
        completion_response = self.llm_service.chat(
            completion_request
        )

        # 最初のAI回答を取得
        answer = completion_response.choices[0].message.content

        # ユーザー入力とAI回答を保存
        self._save_messages(
            db=db,
            conversation_id=conversation.id,
            user_message=request.message,
            assistant_message=answer,
            model=completion_response.model,
            prompt_tokens=completion_response.usage.prompt_tokens,
            completion_tokens=completion_response.usage.completion_tokens,
        )

        # 既存Chat API形式のレスポンスを返却
        return ChatResponse(
            conversation_id=conversation.id,
            answer=answer,
        )

    def chat_completion(
        self,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse:
        """
        OpenAI互換チャットを実行する。

        OpenAI互換形式のチャットリクエストをLLMサービスへ渡し、
        OpenAI互換形式のチャットレスポンスを返却する。

        Args:
            request (ChatCompletionRequest):
                OpenAI互換のチャットリクエスト

        Returns:
            ChatCompletionResponse:
                OpenAI互換のチャットレスポンス

        Raises:
            ValueError: リクエスト内容が不正な場合
            RuntimeError: チャット回答の生成に失敗した場合
        """

        # 通常チャットリクエストを受信したことをログへ記録する
        # stream=Falseの場合は、回答生成完了後にJSON形式で返却する
        logger.info(
            "Chat completion request received. stream=%s",
            request.stream,
        )

        # RAGが有効な場合は、
        # ユーザーの質問に関連する文書をQdrantから検索し、
        # 検索結果をSystemメッセージとして追加する
        processed_request = self._apply_rag(request)

        # RAG適用後のリクエストをLLMへ渡し、
        # 回答生成が完了してからレスポンスを返す
        return self.llm_service.chat(processed_request)

    def chat_completion_stream(
        self,
        request: ChatCompletionRequest,
    ) -> Iterator[str]:
        """
        OpenAI互換ストリーミングチャットを実行する。

        Args:
            request (ChatCompletionRequest):
                OpenAI互換チャットリクエスト

        Returns:
            Iterator[str]: OpenAI互換SSEレスポンス
        """

        # ストリーミングの場合も通常チャットと同じように、
        # LLMへ送信する前にRAGコンテキストを追加する
        processed_request = self._apply_rag(request)

        # Ollamaから生成途中の回答を順番に受け取り、
        # OpenAI互換SSE形式としてそのまま呼び出し元へ返す
        #
        # yield fromを使用することで、
        # 回答全体の生成完了を待たずに少しずつ返却できる
        yield from self.llm_service.chat_stream(
            processed_request,
        )

    def _get_or_create_conversation(
        self, db: Session, request: ChatRequest
    ) -> Conversation:
        """
        Conversationを取得または新規作成する。

        Conversation IDが指定されている場合は既存データを取得し、
        指定されていない場合はユーザー入力をタイトルとして
        新しいConversationを作成する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            request (ChatRequest):
                チャットリクエスト

        Returns:
            Conversation:
                取得または新規作成したConversation

        Raises:
            HTTPException:
                指定されたConversationが存在しない場合
        """
        # conversation_idが指定されている場合は、
        # 新しい会話を作成せず既存Conversationを利用する
        if request.conversation_id is not None:
            # DBから指定されたConversationを取得する
            conversation = self.conversation_service.get(
                db, request.conversation_id
            )

            # 指定されたIDのConversationが存在しない場合は、
            # 存在しない会話を継続できないため404を返す
            if conversation is None:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found",
                )

            # Conversationが見つかった場合はそのまま返す
            return conversation

        # conversation_idが指定されていない場合は、
        # 新しいConversationとして登録する
        #
        # titleにはユーザー入力の先頭30文字を使用し、
        # 会話一覧で内容を判別しやすくする
        return self.conversation_service.create(
            db,
            ConversationCreate(
                user_id=request.user_id,
                title=request.message[:30],
            ),
        )

    def _build_messages(
        self,
        db: Session,
        conversation_id: int,
        system_prompt: str,
        user_message: str,
    ) -> list[Message]:
        """
        LLMへ送信するメッセージ一覧を生成する。

        System Prompt、過去のConversation Message、
        および今回のユーザー入力をOpenAI互換の
        Message一覧として組み立てる。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            conversation_id (int):
                Conversation ID
            system_prompt (str):
                Prompt TemplateのSystem Prompt
            user_message (str):
                今回のユーザー入力

        Returns:
            list[Message]:
                OpenAI互換のメッセージ一覧
        """
        # LLMへ最初に渡すSystem Promptを追加する
        # System PromptではAIの役割や回答方針などを指定する
        messages = [
            Message(
                role="system",
                content=system_prompt,
            )
        ]

        # DBから現在のConversationに紐づく過去の会話履歴を取得する
        conversation_messages = (
            self.conversation_message_service.get_by_conversation(
                db, conversation_id
            )
        )

        # 過去の会話履歴を古い順にMessageへ変換して追加する
        #
        # これによりLLMは今回の質問だけでなく、
        # それまでの会話内容もコンテキストとして参照できる
        for history in conversation_messages:
            messages.append(
                Message(
                    role=history.role,
                    content=history.content,
                )
            )

        # 最後に今回入力されたユーザーメッセージを追加する
        #
        # System Prompt
        # ↓
        # 過去の会話履歴
        # ↓
        # 今回のユーザー入力
        #
        # という順番でLLMへ送信する
        messages.append(
            Message(
                role="user",
                content=user_message,
            )
        )

        return messages

    def _save_messages(
        self,
        db: Session,
        conversation_id: int,
        user_message: str,
        assistant_message: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        """
        ユーザー入力とAI回答を保存する。

        ユーザー入力には入力トークン数を設定し、
        AI回答には出力トークン数を設定して
        Conversation Messageテーブルへ保存する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            conversation_id (int):
                Conversation ID
            user_message (str):
                ユーザー入力
            assistant_message (str):
                AI回答
            model (str):
                使用したLLMモデル名
            prompt_tokens (int):
                入力トークン数
            completion_tokens (int):
                出力トークン数

        Returns:
            None
        """
        # ユーザーが入力したメッセージをDBへ保存する
        #
        # ユーザーメッセージでは入力トークン数を記録し、
        # completion_tokensは使用しないため0にする
        self.conversation_message_service.create(
            db,
            ConversationMessageCreate(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=0,
            ),
        )

        # LLMが生成した回答をDBへ保存する
        #
        # AI回答では出力トークン数を記録し、
        # prompt_tokensは使用しないため0にする
        self.conversation_message_service.create(
            db,
            ConversationMessageCreate(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_message,
                model=model,
                prompt_tokens=0,
                completion_tokens=completion_tokens,
            ),
        )

    def _apply_rag(
        self,
        request: ChatCompletionRequest,
    ) -> ChatCompletionRequest:
        """
        チャットリクエストへRAGコンテキストを追加する。

        Args:
            request: 元のチャット補完リクエスト

        Returns:
            ChatCompletionRequest: RAG適用後のリクエスト
        """

        # 通常応答かストリーミング応答かを
        # デバッグ時に確認できるようログへ記録する
        logger.info(
            "Applying RAG context. stream=%s",
            request.stream,
        )

        # RAG機能が無効の場合は、
        # Qdrant検索を実行せず元のリクエストをそのまま返す
        #
        # .env:
        # RAG_ENABLED=false
        #
        # の場合にこの分岐へ入る
        if not settings.rag_enabled:
            logger.info("RAG is disabled.")
            return request

        logger.info(
            "Applying RAG context to chat completion request."
        )

        # ユーザーの最新質問をEmbeddingへ変換し、
        # Qdrantから関連文書を検索する
        #
        # 取得した関連文書はRAG用Systemメッセージとして
        # 元の会話メッセージへ追加される
        rag_messages = self.rag_service.build_rag_messages(
            request.messages,
        )

        # request.messagesを直接変更すると、
        # 呼び出し元が保持している元のリクエストまで
        # 意図せず変更される可能性がある
        #
        # model_copy()を使って新しいリクエストを作成し、
        # messagesだけRAG適用後の内容へ置き換える
        return request.model_copy(
            update={
                "messages": rag_messages,
            }
        )
