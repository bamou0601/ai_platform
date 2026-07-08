from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ollama_service import OllamaService
from app.services.chat_history_service import ChatHistoryService

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

        # 履歴保存を追加
        return response
        