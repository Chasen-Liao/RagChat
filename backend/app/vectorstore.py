import os
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .config import settings
from .embeddings import get_embeddings


class VectorStoreManager:
    def __init__(self):
        self.embeddings = get_embeddings()
        os.makedirs(settings.chroma_persist_dir, exist_ok=True)
        self.vectorstore = Chroma(
            persist_directory=settings.chroma_persist_dir,
            embedding_function=self.embeddings,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )

    def add_documents(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> int:
        documents = []
        for i, text in enumerate(texts):
            chunks = self.text_splitter.split_text(text)
            for j, chunk in enumerate(chunks):
                metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
                metadata["chunk_index"] = j
                documents.append(Document(page_content=chunk, metadata=metadata))

        if documents:
            self.vectorstore.add_documents(documents)
            self.vectorstore.persist()

        return len(documents)

    def add_file(self, file_path: str) -> int:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        metadata = {"source": file_path}
        return self.add_documents([text], [metadata])

    def get_retriever(self, k: int = 4):
        return self.vectorstore.as_retriever(search_kwargs={"k": k})

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        return self.vectorstore.similarity_search(query, k=k)

    def delete_collection(self):
        self.vectorstore.delete_collection()


vectorstore_manager = VectorStoreManager()
