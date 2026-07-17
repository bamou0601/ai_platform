"""
機能: Chat Serviceのビジネスロジック
ロジック: 会話管理、プロンプト取得、Ollamaとの対話、および会話履歴の保存を行う
作成者: 馬 猛
作成日: 2026/07/07
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.prompt_template_repository import (
    PromptTemplateRepository,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.conversation import ConversationCreate
from app.schemas.conversation_message import (
    ConversationMessageCreate,
)
from app.services.conversation_message_service import (
    ConversationMessageService,
)
from app.services.conversation_service import (
    ConversationService,
)
from app.services.ollama_service import OllamaService


class ChatService:
    """
    Chat機能のビジネスロジックを提供するService。

    Conversationの管理、PromptTemplateの取得、
    Ollamaとのチャット実行、および会話履歴の保存を行う。
    """

    def __init__(self):
        """
        ChatServiceを初期化する。

        利用するRepositoryおよびServiceのインスタンスを生成する。

        Returns:
            None
        """
        self.ollama_service = OllamaService()
        self.prompt_repository = PromptTemplateRepository()
        self.conversation_service = ConversationService()
        self.conversation_message_service = (
            ConversationMessageService()
        )

    def chat(self, db: Session, request: ChatRequest) -> ChatResponse:
        """
        チャットを実行する。

        Conversationの取得または新規作成を行い、
        PromptTemplateおよび会話履歴を基にOllamaへ問い合わせる。
        AIの回答を取得後、ユーザーとAI双方のメッセージを保存し、
        レスポンスを返却する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            request (ChatRequest):
                チャットリクエスト情報

        Returns:
            ChatResponse:
                Conversation IDとAIの回答
        """

        # Conversationを取得または新規作成
        if request.conversation_id:
            conversation = self.conversation_service.get(
                db, request.conversation_id
            )

            if conversation is None:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found",
                )
        else:
            conversation = self.conversation_service.create(
                db,
                ConversationCreate(
                    user_id=request.user_id,
                    title=request.message[:30],
                ),
            )

        # プロンプトテンプレートを取得
        prompt = self.prompt_repository.find_by_id(
            db, request.prompt_template_id
        )

        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Prompt Template not found",
            )

        # ollamaへ渡すmessage生成
        messages = [
            {
                "role": "system",
                "content": prompt.system_prompt,
            }
        ]

        # 過去の会話履歴を取得
        conversation_messages = (
            self.conversation_message_service.get_by_conversation(
                db, conversation.id
            )
        )

        # 過去の会話履歴を追加
        for history in conversation_messages:
            messages.append(
                {
                    "role": history.role,
                    "content": history.content,
                }
            )

        # 今回のユーザ入力も追加
        messages.append({"role": "user", "content": request.message})

        # ollama呼び出し
        answer = self.ollama_service.chat(messages)

        # ユーザーの発言を保存
        self.conversation_message_service.create(
            db,
            ConversationMessageCreate(
                conversation_id=conversation.id,
                role="user",
                content=request.message,
                model=settings.ollama_model,
                prompt_tokens=0,
                completion_tokens=0,
            ),
        )

        # AIの回答を保存
        self.conversation_message_service.create(
            db,
            ConversationMessageCreate(
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
                model=settings.ollama_model,
                prompt_tokens=0,
                completion_tokens=0,
            ),
        )

        # レスポンスを返却
        return ChatResponse(
            conversation_id=conversation.id, answer=answer
        )
