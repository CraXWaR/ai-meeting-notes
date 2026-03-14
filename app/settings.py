from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    GROQ_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    GOOGLE_SERVICE_ACCOUNT_JSON: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
