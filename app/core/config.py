from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "WMS Notification Service"
    DEBUG: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
