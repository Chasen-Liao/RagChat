import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    siliconflow_api_key: str = os.getenv("SILICONFLOW_API_KEY", "")
    siliconflow_api_base: str = os.getenv(
        "SILICONFLOW_API_BASE", "https://api.siliconflow.cn/v1"
    )
    llm_model: str = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-72B-Instruct")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_history_length: int = 10

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
