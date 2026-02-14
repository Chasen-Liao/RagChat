import os
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import settings
from .embeddings import get_embeddings


class VectorStoreManager:
    def __init__(self):
        self.embeddings = get_embeddings()
        self._vectorstore = None
        os.makedirs(settings.chroma_persist_dir, exist_ok=True)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            self._vectorstore = Chroma(
                persist_directory=settings.chroma_persist_dir,
                embedding_function=self.embeddings,
            )
        return self._vectorstore

    def add_documents(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> int:
        documents = []
        for i, text in enumerate(texts):
            print(f"DEBUG: Processing text of length {len(text)}")
            chunks = self.text_splitter.split_text(text)
            print(f"DEBUG: Split into {len(chunks)} chunks")
            for j, chunk in enumerate(chunks):
                # Count approximate tokens (rough estimate: 1 token ≈ 1.5 chars for Chinese)
                approx_tokens = len(chunk) // 1.5
                print(
                    f"DEBUG: Chunk {j} length: {len(chunk)}, approx tokens: {approx_tokens}"
                )
                metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
                metadata["chunk_index"] = j
                documents.append(Document(page_content=chunk, metadata=metadata))

        if documents:
            print(f"DEBUG: Adding {len(documents)} documents to vectorstore")
            # Add in batches of 32 (API limit)
            batch_size = 32
            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]
                print(f"DEBUG: Adding batch {i // batch_size + 1}, size: {len(batch)}")
                self.vectorstore.add_documents(batch)
            print(f"DEBUG: Added successfully")

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


vectorstore_manager = VectorStoreManager()
