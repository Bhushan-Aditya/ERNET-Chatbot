import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Optional

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Load Q&A knowledge base
def load_qa_knowledge_base():
    try:
        with open("/Users/adityabhushan/Desktop/ERNET Chat Bot/ernett_qa_knowledge_base.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

qa_knowledge_base = load_qa_knowledge_base()

# Load conversation history from file
def load_conversation_history():
    try:
        with open("conversation_history.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save conversation history to file
def save_conversation_history(history):
    file_path = "conversation_history.json"
    print(f"Saving conversation history to {os.path.abspath(file_path)}")
    with open(file_path, "w") as f:
        json.dump(history, f, indent=4)
    print("Conversation history saved.")

conversation_history = load_conversation_history()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Reload the Q&A knowledge base for each request
        qa_knowledge_base = load_qa_knowledge_base()
        
        # Traverse the knowledge base to find a matching question
        for qa in qa_knowledge_base:
            if qa["question"].lower() in request.message.lower() or request.message.lower() in qa["question"].lower():
                # If found, enhance the answer using Gemini
                prompt = f"Enhance and explain the following answer in a well-defined and accurate way: {qa['answer']}"
                response = model.generate_content(prompt)
                conversation_history.append({"question": request.message, "answer": response.text})
                save_conversation_history(conversation_history)
                return ChatResponse(response=response.text)
        
        # If not found, send the question directly to Gemini
        prompt = f"Answer the following question in a well-defined and accurate way: {request.message}"
        response = model.generate_content(prompt)
        conversation_history.append({"question": request.message, "answer": response.text})
        save_conversation_history(conversation_history)
        return ChatResponse(response=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 