"""
作成者: 馬 猛
作成日: 2026/07/07
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.config import settings
from app.repositories.prompt_template_repository import PromptTemplateRepository

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.conversation import ConversationCreate
from app.schemas.conversation_message import ConversationMessageCreate
from app.services.conversation_service import ConversationService
from app.services.conversation_message_service import ConversationMessageService
from app.services.ollama_service import OllamaService


class ChatService:
    
    def __init__(self):
        self.ollama_service = OllamaService()
        self.prompt_repository = PromptTemplateRepository()
        self.conversation_service = ConversationService()
        self.conversation_message_service = ConversationMessageService()

    def chat(
        self,
        db: Session,
        request: ChatRequest
    ) -> ChatResponse:

        #Conversation取得
        if request.conversation_id:
            conversation = self.conversation_service.get(
                db,
                request.conversation_id
            )

            if conversation is None:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found"
                )
        else:
            conversation = self.conversation_service.create(
                db,
                ConversationCreate(
                    user_id=request.user_id,
                    title=request.message[:30]
                )
            )

        # promptを取得
        prompt = self.prompt_repository.find_by_id(
            db,
            request.prompt_template_id
        )

        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Prompt Template not found"
            )
           

         # ollamaへ渡すmessage生成
        messages = [
            {
                "role": "system",
                "content": prompt.system_prompt
            }
        ]

        conversation_messages = (
            self.conversation_message_service.get_by_conversation(                                            
                db,
                conversation.id 
            )
        )

        for history in conversation_messages:
            messages.append(
                {
                    "role": history.role,
                    "content": history.content
                }
            )

        # 今回のユーザ入力も追加
        messages.append(
            {
                "role": "user",
                "content": request.message
            }
        )

        # ollama呼び出し
        answer = self.ollama_service.chat(messages)

        # User保存
        self.conversation_message_service.create(
            db,
            ConversationMessageCreate(
                conversation_id=conversation.id,
                role="user",
                content=request.message,
                model=settings.ollama_model,
                prompt_tokens=0,
                completion_tokens=0
            )
        )  
        
        # Assitant保存
        self.conversation_message_service.create(
            db,
            ConversationMessageCreate(
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
                model=settings.ollama_model,
                prompt_tokens=0,
                completion_tokens=0
            )
        )

        # レスポンス
        return ChatResponse(
            conversation_id=conversation.id,
            answer=answer
        )
        
        