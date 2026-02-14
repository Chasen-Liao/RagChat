from langchain_openai import OpenAIEmbeddings
from .config import settings


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        api_key=settings.siliconflow_api_key,
        base_url=settings.siliconflow_api_base,
        model=settings.embedding_model,
    )
