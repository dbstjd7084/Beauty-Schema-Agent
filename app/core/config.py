from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "GlowSchema"
    OPENAI_API_KEY: str = "sk-placeholder"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        extra='ignore' # .env에 클래스에 없는 변수가 있어도 에러내지 않음
    )

settings = Settings()