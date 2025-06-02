from fastapi import APIRouter, HTTPException
from ..models.chat import ChatRequest, ChatResponse
from ..core.chat_service import ChatService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = ChatService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Log the incoming request
        logger.info(f"Received chat request: {request.message[:100]}...")
        
        # Validate request
        if not request.message:
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        # Process the message
        response, conversation_history = chat_service.process_message(
            request.message,
            request.conversation_history
        )
        
        # Log the response
        logger.info(f"Generated response: {response[:100]}...")
        
        return ChatResponse(
            response=response,
            conversation_history=conversation_history
        )
    except HTTPException as he:
        logger.error(f"HTTP Error in chat endpoint: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 