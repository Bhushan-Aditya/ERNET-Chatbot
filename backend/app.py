from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import re
import os
from dotenv import load_dotenv
import google.generativeai as genai
from chatbot_knowledge import (
    get_domain_info,
    get_eligibility_info,
    get_domain_rules,
    get_registration_policies,
    get_value_added_services,
    get_support_info
)

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Message]

def extract_domain_type(text):
    """Extract domain type from text"""
    domain_patterns = {
        r'ac\.in': 'ac.in',
        r'edu\.in': 'edu.in',
        r'res\.in': 'res.in',
        r'विद्या\.भारत': 'विद्या.भारत',
        r'शिक्षा\.भारत': 'शिक्षा.भारत',
        r'शोध\.भारत': 'शोध.भारत'
    }
    
    for pattern, domain in domain_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return domain
    return None

def get_offline_response(message: str) -> Optional[str]:
    """Get response from offline knowledge base"""
    message = message.lower()
    
    # Check for domain type queries
    domain_type = extract_domain_type(message)
    if domain_type:
        domain_info = get_domain_info(domain_type)
        return f"About {domain_type}: {domain_info}"
    
    # Check for eligibility queries
    if any(word in message for word in ['eligible', 'qualify', 'requirements', 'documents']):
        eligibility = get_eligibility_info()
        response = "To be eligible for ERNET domain registration:\n\n"
        response += "Institution Types:\n"
        for inst_type in eligibility['institution_types']:
            response += f"- {inst_type}\n"
        response += "\nRequired Documents:\n"
        for doc in eligibility['required_documents']:
            response += f"- {doc}\n"
        return response
    
    # Check for domain rules queries
    if any(word in message for word in ['rules', 'naming', 'domain name', 'format']):
        rules = get_domain_rules()
        response = "Domain Naming Rules:\n\n"
        response += f"- Length: {rules['length']}\n"
        response += f"- Allowed characters: {rules['allowed_characters']}\n"
        response += "Restrictions:\n"
        for restriction in rules['restrictions']:
            response += f"- {restriction}\n"
        return response
    
    # Check for registration policy queries
    if any(word in message for word in ['duration', 'period', 'renewal', 'expiry']):
        policies = get_registration_policies()
        response = "Registration Policies:\n\n"
        response += f"Duration:\n- Minimum: {policies['duration']['minimum']}\n"
        response += f"- Maximum: {policies['duration']['maximum']}\n"
        response += f"- Maximum renewal: {policies['duration']['renewal_max']}\n\n"
        response += "Expiry Handling:\n"
        for key, value in policies['expiry_handling'].items():
            response += f"- {key.title()}: {value}\n"
        response += "\nFees:\n"
        for key, value in policies['fees'].items():
            response += f"- {key.title()}: {value}\n"
        return response
    
    # Check for value added services queries
    if any(word in message for word in ['waas', 'lmaas', 'website', 'learning', 'services']):
        services = get_value_added_services()
        response = "Value Added Services:\n\n"
        for service_key, service_info in services.items():
            response += f"{service_info['name']} ({service_key}):\n"
            for feature in service_info['features']:
                response += f"- {feature}\n"
            response += "\n"
        return response
    
    # Check for support queries
    if any(word in message for word in ['support', 'help', 'contact', 'email']):
        support = get_support_info()
        response = "Support Information:\n\n"
        response += f"- Email: {support['email']}\n"
        response += f"- Response Time: {support['response_time']}\n"
        response += f"- Phone Support: {support['phone_support']}\n"
        return response
    
    return None

def get_gemini_response(message: str, conversation_history: List[Message]) -> str:
    """Get response from Gemini AI"""
    try:
        # Create context from offline knowledge base
        context = f"""You are an ERNET domain registration assistant. Use the following information to help answer questions:

Domain Types:
{get_domain_info('ac.in')}
{get_domain_info('edu.in')}
{get_domain_info('res.in')}

Eligibility Requirements:
{get_eligibility_info()}

Domain Rules:
{get_domain_rules()}

Registration Policies:
{get_registration_policies()}

Value Added Services:
{get_value_added_services()}

Support Information:
{get_support_info()}

Please provide accurate and helpful responses based on this information. If the question is not related to ERNET domain registration, politely inform the user that you can only help with ERNET domain-related queries."""

        # Create chat history for context
        chat = model.start_chat(history=[])
        chat.send_message(context)
        
        # Add conversation history for context
        for msg in conversation_history[-5:]:  # Use last 5 messages for context
            chat.send_message(f"{msg.role}: {msg.content}")
        
        # Get response from Gemini
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {str(e)}")
        return None

def generate_response(message: str, conversation_history: List[Message]) -> str:
    if not message:
        return "Hello! I'm the ERNET domain registration assistant. How can I help you today?"
    # First try to get response from offline knowledge base
    offline_response = get_offline_response(message)
    if offline_response:
        return offline_response
    # If no offline response, try Gemini AI
    gemini_response = get_gemini_response(message, conversation_history)
    if gemini_response:
        return gemini_response
    # Default response if both methods fail
    if len(conversation_history) <= 1:
        return "Hello! I'm the ERNET domain registration assistant. How can I help you today?"
    return "Sorry, I didn't understand that. Please ask about domain registration, renewal, transfer, or support."

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    try:
        # Check if the last message was already a default response
        if request.conversation_history and request.conversation_history[-1].role == "assistant" and \
           "I can help you with information about" in request.conversation_history[-1].content:
            return {"conversation_history": request.conversation_history}
        
        response = generate_response(request.message, request.conversation_history)
        # Add the new messages to the conversation history
        conversation_history = request.conversation_history + [
            Message(role="assistant", content=response)
        ]
        # Remove consecutive duplicate messages
        filtered_history = []
        for msg in conversation_history:
            if not filtered_history or (msg.role != filtered_history[-1].role or msg.content != filtered_history[-1].content):
                filtered_history.append(msg)
        return {"conversation_history": filtered_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 