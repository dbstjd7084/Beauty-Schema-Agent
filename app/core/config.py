import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "GlowSchema"
    
    OPENAI_API_KEY: str = "sk-placeholder"
    GOOGLE_API_KEY: str = "your-google-key-here"
    
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_PROJECT: str = "amore-beauty-project"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.getcwd(), ".env"),
        env_file_encoding='utf-8',
        extra='ignore' 
    )

settings = Settings()