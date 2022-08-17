from pydantic import BaseSettings

UPLOADED_FILES_PATH = "src/UPLOADED_FILES/"
RECOGNITION_FILES_PATH = "src/RECOGNITION_FILES/"
ARCHIVED_FILES_PATH = "src/ARCHIVED_FILES/"
MODELS_FILES_PATH = "src/models/vosk-model-ru-0.22"


class Settings(BaseSettings):
    server_host: str = '127.0.0.1'
    server_port: int = 8000


settings = Settings(
    _env_file='recognition/.env',
    _env_file_encoding='utf-8',
)
