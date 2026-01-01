from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings


def call_llm():
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=settings.GOOGLE_API_KEY)
    return llm