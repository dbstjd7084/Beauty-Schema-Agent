from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

def call_llm(model_name="gemini-2.5-flash-lite", max_retries=0):
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=settings.GOOGLE_API_KEY,
        max_retries=max_retries, 
        temperature=0
    )