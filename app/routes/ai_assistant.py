from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.ai_assistant import ElDoradoAIAssistant
from ..schemas import *
from pydantic import BaseModel, Field
from typing import List

router = APIRouter(prefix="/api/v1/ai-assistant", tags=["AI Assistant"])

# Schemas
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Mensagem do usuário")

class ChatResponse(BaseModel):
    success: bool
    response: str
    suggestions: List[str] = []

class SuggestionsResponse(BaseModel):
    suggestions: List[str]

# Initialize AI Assistant
ai_assistant = ElDoradoAIAssistant()

@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(
    request: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Chat com o assistente AI da El Dorado
    
    O assistente tem acesso completo aos dados dos influenciadores, vídeos e analytics.
    Pode responder perguntas como:
    - "Como está a performance do Samuel este mês?"
    - "Quais são os top 5 vídeos com mais likes?"
    - "Me mostra o engagement da Bianca"
    - "Quantos influenciadores temos ativos?"
    """
    try:
        response = ai_assistant.process_user_message(request.message, db)
        suggestions = ai_assistant.get_suggestions(db)
        
        return ChatResponse(
            success=True,
            response=response,
            suggestions=suggestions[:4]  # Limit suggestions
        )
        
    except Exception as e:
        return ChatResponse(
            success=False,
            response=f"❌ Erro interno: {str(e)}",
            suggestions=[]
        )

@router.get("/suggestions", response_model=SuggestionsResponse)
def get_chat_suggestions(db: Session = Depends(get_db)):
    """
    Obter sugestões de perguntas para o chat
    """
    try:
        suggestions = ai_assistant.get_suggestions(db)
        return SuggestionsResponse(suggestions=suggestions)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter sugestões: {str(e)}"
        )

@router.get("/health")
def ai_assistant_health():
    """Health check do assistente AI"""
    return {
        "status": "healthy",
        "service": "El Dorado AI Assistant",
        "features": [
            "Chat conversacional",
            "Acesso aos dados dos influenciadores", 
            "Analytics em tempo real",
            "Insights baseados em dados",
            "Sugestões de perguntas"
        ]
    }