from typing import List
from ..models.chat import ChatMessage
import os
import requests
from fastapi import HTTPException
import logging
from .scraper import ERNETScraper
from chatbot_knowledge import (
    get_domain_info,
    get_eligibility_info,
    get_domain_rules,
    get_registration_policies,
    get_value_added_services,
    get_support_info
)
from difflib import get_close_matches

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REGISTRATION_LINK = "https://www.registry.ernet.in/"  # Update if you have a more specific link
SUPPORT_EMAIL = "helpdesk@domain.ernet.in"

# Helper to detect main topic
TOPIC_KEYWORDS = {
    'waas': ['waas', 'website as a service'],
    'lmaas': ['lmaas', 'learning management'],
    'registration': ['register', 'registration', 'how do i register', 'how to register', 'registration process'],
    'pricing': ['price', 'cost', 'fee', 'charges', 'amount'],
    'about': ['about', 'objective', 'ernets objective', 'goal', 'purpose'],
    'support': ['support', 'contact', 'help', 'email', 'phone'],
}

def detect_topic(message: str) -> str:
    message = message.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(word in message for word in keywords):
            return topic
    return ''

def get_pricing_info_from_scraper(scraper) -> str:
    if hasattr(scraper, 'data') and 'pricing' in scraper.data and scraper.data['pricing']:
        lines = []
        for domain_type, price in scraper.data['pricing'].items():
            lines.append(f"- {domain_type}: {price}")
        return "\n".join(lines)
    return ""

def get_summary_of_all_data(scraper) -> str:
    summary = []
    # Pricing
    pricing = get_pricing_info_from_scraper(scraper)
    if pricing:
        summary.append("Pricing Information:\n" + pricing)
    # Policies
    if hasattr(scraper, 'data') and 'policies' in scraper.data and scraper.data['policies']:
        summary.append("Policies:\n" + "\n".join(f"- {k}: {v}" for k, v in scraper.data['policies'].items()))
    # Registration Process
    if hasattr(scraper, 'data') and 'registration_process' in scraper.data and scraper.data['registration_process']:
        summary.append("Registration Process:\n" + "\n".join(f"- {k}: {v}" for k, v in scraper.data['registration_process'].items()))
    # FAQ
    if hasattr(scraper, 'data') and 'faq' in scraper.data and scraper.data['faq']:
        summary.append("FAQ:\n" + "\n".join(f"Q: {k}\nA: {v}" for k, v in scraper.data['faq'].items()))
    # Contact Info
    if hasattr(scraper, 'data') and 'contact_info' in scraper.data and scraper.data['contact_info']:
        summary.append("Contact Info:\n" + "\n".join(f"- {k}: {v}" for k, v in scraper.data['contact_info'].items()))
    # General Info
    if hasattr(scraper, 'data') and 'general_info' in scraper.data and scraper.data['general_info']:
        summary.append("General Info:\n" + "\n".join(f"- {k}: {v}" for k, v in scraper.data['general_info'].items()))
    return "\n\n".join(summary)

def extract_relevant_info(message: str, scraper, conversation_history=None) -> str:
    message = message.lower()
    info = []
    last_topic = ''
    if conversation_history:
        for msg in reversed(conversation_history):
            if msg.role == 'user':
                last_topic = detect_topic(msg.content)
                if last_topic:
                    break
    current_topic = detect_topic(message)
    # Topic tracking for follow-ups
    if current_topic and last_topic and current_topic == last_topic:
        # Provide deeper or more personalized info
        if current_topic == 'waas':
            info.append("WaaS (Website as a Service) helps your institution by providing a secure, customizable, and easy-to-manage website platform. Would you like to know about pricing or how to get started?")
            return "\n\n".join(info)
        if current_topic == 'registration':
            info.append("If you need help with a specific step in registration, let me know which part you need assistance with!")
            return "\n\n".join(info)
        # Add more topic-specific follow-ups as needed
    # Pricing
    if any(word in message for word in ['price', 'cost', 'fee', 'charges', 'amount']):
        pricing_info = get_pricing_info_from_scraper(scraper)
        if pricing_info:
            info.append("Pricing Information:\n" + pricing_info)
            info.append("Would you like to proceed with registration or know about required documents?")
        return "\n\n".join(info)
    # Domain type
    domain_types = ["ac.in", "edu.in", "res.in", "विद्या.भारत", "शिक्षा.भारत", "शोध.भारत"]
    for dt in domain_types:
        if dt in message:
            info.append(f"About {dt}: {get_domain_info(dt)}")
            return "\n\n".join(info)
    # Eligibility
    if any(word in message for word in ['eligible', 'qualify', 'requirements', 'eligibility']):
        eligibility = get_eligibility_info()
        info.append("Institution Types:\n" + "\n".join(f"- {t}" for t in eligibility['institution_types']))
        return "\n\n".join(info)
    # Required documents
    if any(word in message for word in ['document', 'documents', 'paper', 'papers']):
        eligibility = get_eligibility_info()
        info.append("Required Documents:\n" + "\n".join(f"- {d}" for d in eligibility['required_documents']))
        info.append("Would you like to know the registration steps or pricing?")
        return "\n\n".join(info)
    # Domain rules
    if any(word in message for word in ['rules', 'naming', 'domain name', 'format']):
        rules = get_domain_rules()
        info.append(f"Domain Naming Rules:\n- Length: {rules['length']}\n- Allowed characters: {rules['allowed_characters']}\nRestrictions:\n" + "\n".join(f"- {r}" for r in rules['restrictions']))
        return "\n\n".join(info)
    # Registration policies
    if any(word in message for word in ['duration', 'period', 'renewal', 'expiry', 'fees', 'charges']):
        policies = get_registration_policies()
        info.append(f"Registration Policies:\nDuration:\n- Minimum: {policies['duration']['minimum']}\n- Maximum: {policies['duration']['maximum']}\n- Maximum renewal: {policies['duration']['renewal_max']}\nExpiry Handling:\n" + "\n".join(f"- {k.title()}: {v}" for k, v in policies['expiry_handling'].items()) + "\nFees:\n" + "\n".join(f"- {k.title()}: {v}" for k, v in policies['fees'].items()))
        return "\n\n".join(info)
    # Value added services
    if any(word in message for word in ['waas', 'lmaas', 'website', 'learning', 'services']):
        services = get_value_added_services()
        for service_key, service_info in services.items():
            if service_key.lower() in message or service_info['name'].lower() in message or any(word in message for word in ['waas', 'website']) and service_key == 'WaaS' or any(word in message for word in ['lmaas', 'learning']) and service_key == 'LMaaS':
                info.append(f"{service_info['name']} ({service_key}):\n" + "\n".join(f"- {f}" for f in service_info['features']))
                info.append("Would you like to know about pricing or how to get started?")
                return "\n\n".join(info)
        info.append("ERNET provides the following value-added services: Website as a Service (WaaS), Learning Management as a Service (LMaaS).")
        return "\n\n".join(info)
    # Support
    if any(word in message for word in ['support', 'help', 'contact', 'email']):
        support = get_support_info()
        info.append(f"Support Information:\n- Email: {support['email']}\n- Response Time: {support['response_time']}\n- Phone Support: {support['phone_support']}")
        info.append(f"You can also visit our support page: {REGISTRATION_LINK}contact-us")
        return "\n\n".join(info)
    # Registration process
    if any(word in message for word in ['register', 'registration process', 'how do i register', 'how to register']):
        if hasattr(scraper, 'data') and 'registration_process' in scraper.data and scraper.data['registration_process']:
            steps = [v for k, v in sorted(scraper.data['registration_process'].items())]
            info.append("Registration Process:\n" + "\n".join(f"- {step}" for step in steps))
            info.append(f"You can start your registration here: {REGISTRATION_LINK}")
            return "\n\n".join(info)
    # About/General Info
    if any(word in message for word in ['about', 'objective', 'goal', 'purpose', 'ernets objective']):
        if hasattr(scraper, 'data') and 'general_info' in scraper.data and scraper.data['general_info']:
            for k, v in scraper.data['general_info'].items():
                if 'about' in k.lower() or 'objective' in k.lower() or 'goal' in k.lower() or 'purpose' in k.lower():
                    info.append(f"{k}: {v}")
            if info:
                return "\n\n".join(info)
    # FAQ (try to match question)
    if hasattr(scraper, 'data') and 'faq' in scraper.data and scraper.data['faq']:
        user_question = message.strip().lower()
        matches = get_close_matches(user_question, [q.lower() for q in scraper.data['faq'].keys()], n=1, cutoff=0.6)
        if matches:
            for q, a in scraper.data['faq'].items():
                if q.lower() == matches[0]:
                    info.append(f"Q: {q}\nA: {a}")
                    return "\n\n".join(info)
    # If nothing matched, provide a summary of all data (as fallback)
    info.append(get_summary_of_all_data(scraper))
    return "\n\n".join(info)

GEMINI_API_KEY = "AIzaSyAzz-eM9Z0Dk6dAReqybE57rfhFCZVkwvY"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

class ChatService:
    def __init__(self):
        try:
            # Scrape website data on startup
            self.scraper = ERNETScraper()
            self.scraper.scrape_website()
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize scraper: {str(e)}"
            )

    def process_message(self, message: str, conversation_history: List[ChatMessage]) -> tuple[str, List[ChatMessage]]:
        try:
            if not message or message.strip() == "" or message.lower() == "string":
                welcome_message = "Welcome to ERNET Domain Registry! I'm here to help you with domain registration, pricing, and any other queries you might have. What would you like to know about?"
                conversation_history.append(ChatMessage(role="user", content=message or "Hello"))
                conversation_history.append(ChatMessage(role="assistant", content=welcome_message))
                return welcome_message, conversation_history

            # Extract relevant info from both scraper and offline knowledge base
            relevant_info = extract_relevant_info(message, self.scraper, conversation_history)
            prompt = f"""
You are ERNET India's official domain registration assistant—a knowledgeable, friendly, and professional expert in all ERNET domain and service matters.

Your job is to help users with domain registration, policies, pricing, services, and support. Always answer as an authoritative ERNET representative.

Use only the information below to answer the user's question. Do NOT say things like "according to the information provided," "as per documentation," or "currently." Speak as the system itself.

Only answer what the user has specifically asked. Do not provide extra or unrelated information. If the answer is a list, use clear bullet points. If the answer is not present, say: "I'm sorry, I do not have that information at the moment. Please contact ERNET support for further assistance."

Be concise, direct, and clear. Use a professional and friendly tone. If helpful, suggest next steps or how to get more help.

Relevant ERNET information:
{relevant_info}

User question: {message}

Your answer:
"""
            # Add last 5 messages for context
            for msg in conversation_history[-5:]:
                prompt += f"\n{msg.role}: {msg.content}"
            prompt += f"\nUser: {message}\nAssistant:"

            # Call Gemini API directly
            data = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ]
            }
            response = requests.post(GEMINI_ENDPOINT, json=data)
            if response.status_code == 200:
                gemini_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                gemini_text = f"Error from Gemini API: {response.status_code} {response.text}"
            if not gemini_text:
                gemini_text = "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            conversation_history.append(ChatMessage(role="user", content=message))
            conversation_history.append(ChatMessage(role="assistant", content=gemini_text))
            return gemini_text, conversation_history
        except Exception as e:
            logger.error(f"Error processing message with Gemini: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing message with Gemini: {str(e)}"
            ) 