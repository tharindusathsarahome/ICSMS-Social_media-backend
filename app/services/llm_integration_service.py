import google.generativeai as genai
from app.core.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)


def get_gemini_chat():
    """
    Starts a chat session with the Gemini LLM.
    """
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    return chat


def get_gemini_response(chat, message):
    """
    Sends a message to the ongoing chat session and returns the response.
    """
    response = chat.send_message(message)
    return response.text