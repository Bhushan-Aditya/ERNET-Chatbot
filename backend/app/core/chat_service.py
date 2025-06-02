from typing import List
from ..models.chat import ChatMessage
import os
import google.generativeai as genai
from fastapi import HTTPException
import logging
from .scraper import ERNETScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        try:
            # Configure the Gemini API
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Scrape website data
            self.scraper = ERNETScraper()
            self.website_data = self.scraper.scrape_website()
            self.formatted_data = self.scraper.get_formatted_data()
            
            self.system_prompt = f"""You are a helpful assistant for the ERNET Domain Registry (https://www.registry.ernet.in/).
            Your main responsibilities are:
            1. Help users register new domains
            2. Answer questions about domain registration process
            3. Provide information about domain pricing and policies
            4. Guide users through the registration process
            5. Help with common issues and troubleshooting

            Always be professional, clear, and concise in your responses.
            If you're unsure about something, acknowledge it and suggest contacting ERNET support.
            
            Here is the current information from the ERNET website:
            {self.formatted_data}
            
            Important: Always base your responses on the provided website data. If the information is not available in the data, 
            acknowledge that and suggest contacting ERNET support for the most up-to-date information."""
            
            # Test the model with a simple message
            test_response = self.model.generate_content("Hello")
            logger.info("Model initialization successful")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Gemini model: {str(e)}"
            )

    def process_message(self, message: str, conversation_history: List[ChatMessage]) -> tuple[str, List[ChatMessage]]:
        try:
            # Handle test or empty messages
            if not message or message.strip() == "" or message.lower() == "string":
                # For empty or test messages, use a predefined welcome message
                welcome_message = "Welcome to ERNET Domain Registry! I'm here to help you with domain registration, pricing, and any other queries you might have. What would you like to know about?"
                
                # Update conversation history
                conversation_history.append(ChatMessage(role="user", content=message or "Hello"))
                conversation_history.append(ChatMessage(role="assistant", content=welcome_message))
                
                return welcome_message, conversation_history

            # Generate content for actual queries
            prompt = self.system_prompt + "\n\nPrevious conversation:\n"
            for msg in conversation_history:
                prompt += f"{msg.role}: {msg.content}\n"
            prompt += f"\nUser: {message}\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Clean and format the response
            response_text = response.text.strip()
            if not response_text:
                response_text = "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            
            # Update conversation history
            conversation_history.append(ChatMessage(role="user", content=message))
            conversation_history.append(ChatMessage(role="assistant", content=response_text))

            return response_text, conversation_history
        except Exception as e:
            logger.error(f"Error processing message with Gemini: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing message with Gemini: {str(e)}"
            ) 