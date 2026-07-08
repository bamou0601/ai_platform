from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ollama_service import OllamaService
from app.services.chat_history_service import ChatHistoryService
from app.schemas.chat_history import ChatHistoryCreate
from app.config import settings

class ChatService:
    
    def __init__(self):
        self.ollama_service = OllamaService()
        self.chat_history_service = ChatHistoryService()

    def chat(
        self,
        db: Session,
        request: ChatRequest
    ) -> ChatResponse:

        # ollamaへ質問
        response = self.ollama_service.chat(request.message)

        #　履歴作成
        history = ChatHistoryCreate(
            user_id=request.user_id,
            question=request.message,
            answer=response.answer,
            model=settings.ollama_model
        )

        # DB保存
        self.chat_history_service.create_chat(
            db,
            history
        )

        # AI応答を返す
        return response
        