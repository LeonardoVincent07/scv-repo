from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    ENV: str = "local"  # local | dev | prod
    # Default to a local Postgres instance; override via .env in real use.
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/scv"

    class Config:
        env_file = ".env"


settings = Settings()
