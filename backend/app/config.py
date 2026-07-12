from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MESH_API_KEY: str = "YOUR_API_KEY_HERE"
    MODEL_NAME: str = "mention_model"

settings = Settings()
