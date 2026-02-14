from typing import AsyncGenerator, Optional
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from .config import settings
from .vectorstore import vectorstore_manager
from .memory import history_manager


PROMPT_TEMPLATE = """你是一个专业的AI助手，请根据以下上下文信息回答用户问题。
如果上下文中没有相关信息，请诚实地说明你不知道，不要编造答案。

上下文信息：
{context}

聊天历史：
{chat_history}

用户问题：{question}

请用中文详细回答："""


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.siliconflow_api_key,
        base_url=settings.siliconflow_api_base,
        model=settings.llm_model,
        streaming=True,
        temperature=0.7,
    )


def get_chain(session_id: str = "default"):
    llm = get_llm()
    retriever = vectorstore_manager.get_retriever(k=4)

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "chat_history", "question"],
    )

    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        input_key="question",
        output_key="answer",
        chat_memory=history_manager.get_session_history(session_id),
        k=settings.max_history_length,
        return_messages=True,
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt},
        verbose=True,
    )

    return chain


async def stream_chat(
    query: str, session_id: str = "default"
) -> AsyncGenerator[str, None]:
    chain = get_chain(session_id)

    async for chunk in chain.astream({"question": query}):
        if "answer" in chunk:
            yield chunk["answer"]


def chat(query: str, session_id: str = "default") -> dict:
    chain = get_chain(session_id)
    result = chain({"question": query})

    sources = []
    if "source_documents" in result:
        for doc in result["source_documents"]:
            sources.append(
                {
                    "content": doc.page_content[:200] + "..."
                    if len(doc.page_content) > 200
                    else doc.page_content,
                    "metadata": doc.metadata,
                }
            )

    return {"answer": result["answer"], "sources": sources}
