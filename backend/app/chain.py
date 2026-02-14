from typing import AsyncGenerator, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from .config import settings
from .rag_manager import rag_manager
from .session_manager import session_manager
from .semantic_cache import semantic_cache
from .intent_classifier import intent_classifier
from .conversation_compressor import conversation_compressor

# 全局
System_Prompt = """
你是一个专业的AI助手，名叫小正。你知识渊博，回答准确、详细、有帮助。使用中文回答，语气友好专业。
"""


def get_llm(streaming: bool = True) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.siliconflow_api_key,
        base_url=settings.siliconflow_api_base,
        model=settings.llm_model,
        streaming=streaming,
        temperature=0.7,
    )


def generate_session_name(first_message: str) -> str:
    llm = ChatOpenAI(
        api_key=settings.siliconflow_api_key,
        base_url=settings.siliconflow_api_base,
        model="deepseek-ai/DeepSeek-V3",
        streaming=False,
        temperature=0.3,
    )

    prompt = f"""请用不超过10个字总结以下对话主题，只输出标题，不要有其他内容：

用户问题：{first_message}

标题："""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        name = response.content.strip().replace('"', "").replace("标题：", "")[:10]
        return name or "新会话"
    except:
        return "新会话"


async def stream_chat_with_rag(query: str) -> AsyncGenerator[str, None]:
    # 意图识别：判断是否需要检索
    should_retrieve = intent_classifier.should_retrieve(query)

    docs = []
    if should_retrieve:
        docs = rag_manager.similarity_search(query, k=4)

    if docs:
        context = "\n\n".join([doc["page_content"] for doc in docs])
        system_prompt = (
            System_Prompt
            + "请根据以下上下文信息回答用户的问题。\n"
            "如果上下文中没有相关信息，请结合你的知识回答，但要说明这一点。\n\n"
            "上下文：\n"
            f"{context}\n\n"
            "用户问题：{input}\n\n"
            "请用中文详细回答："
        )
    else:
        system_prompt = (
            System_Prompt
            + "\n\n用户问题：{input}\n\n请用中文详细回答："
        )

    llm = get_llm(streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", "{input}")]
    )

    chain = prompt | llm

    async for chunk in chain.astream({"input": query}):
        if chunk.content:
            yield chunk.content


async def stream_chat_normal(query: str) -> AsyncGenerator[str, None]:
    llm = get_llm(streaming=True)
    messages = [
        SystemMessage(content=System_Prompt),
        HumanMessage(content=query),
    ]

    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content


def chat_with_rag(query: str) -> Dict[str, Any]:
    # 意图识别
    should_retrieve = intent_classifier.should_retrieve(query)

    docs = []
    if should_retrieve:
        docs = rag_manager.similarity_search(query, k=4)

    if docs:
        context = "\n\n".join([doc["page_content"] for doc in docs])
        system_prompt = (
            System_Prompt
            + "请根据以下上下文信息回答用户的问题。\n"
            "如果上下文中没有相关信息，请结合你的知识回答，但要说明这一点。\n\n"
            "上下文：\n"
            f"{context}\n\n"
            "用户问题：{input}\n\n"
            "请用中文详细回答："
        )
    else:
        system_prompt = (
            System_Prompt
            + "\n\n用户问题：{input}\n\n请用中文详细回答："
        )

    llm = get_llm(streaming=False)
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", "{input}")]
    )

    chain = prompt | llm
    response = chain.invoke({"input": query})
    answer = response.content

    sources = []
    for doc in docs:
        sources.append(
            {
                "content": doc["page_content"][:200] + "..."
                if len(doc["page_content"]) > 200
                else doc["page_content"],
                "metadata": doc["metadata"],
            }
        )

    return {"answer": answer, "sources": sources, "retrieved": should_retrieve}


def chat_normal(query: str) -> Dict[str, Any]:
    llm = get_llm(streaming=False)
    messages = [
        SystemMessage(content=System_Prompt),
        HumanMessage(content=query),
    ]
    response = llm.invoke(messages)

    return {"answer": response.content, "sources": [], "retrieved": False}


def chat(query: str, session_id: str = "default") -> Dict[str, Any]:
    # 检查语义缓存
    cached_answer = semantic_cache.get(query)
    if cached_answer:
        return {
            "answer": cached_answer,
            "sources": [],
            "retrieved": False,
            "cached": True,
        }

    session = session_manager.get_session(session_id)
    is_first_message = not session or len(session.get("messages", [])) == 0

    session_manager.add_message(session_id, "user", query)

    if rag_manager.enabled:
        result = chat_with_rag(query)
    else:
        result = chat_normal(query)

    session_manager.add_message(session_id, "assistant", result["answer"])

    # 存入缓存
    semantic_cache.set(query, result["answer"])

    if is_first_message:
        name = generate_session_name(query)
        session_manager.update_name(session_id, name)

    return result


async def stream_chat(
    query: str, session_id: str = "default"
) -> AsyncGenerator[str, None]:
    # 检查语义缓存
    cached_answer = semantic_cache.get(query)
    if cached_answer:
        yield cached_answer
        # 仍然记录消息
        session_manager.add_message(session_id, "user", query)
        session_manager.add_message(session_id, "assistant", cached_answer)
        return

    session = session_manager.get_session(session_id)
    is_first_message = not session or len(session.get("messages", [])) == 0

    session_manager.add_message(session_id, "user", query)

    full_answer = ""

    if rag_manager.enabled:
        async for chunk in stream_chat_with_rag(query):
            full_answer += chunk
            yield chunk
    else:
        async for chunk in stream_chat_normal(query):
            full_answer += chunk
            yield chunk

    session_manager.add_message(session_id, "assistant", full_answer)

    # 存入缓存
    semantic_cache.set(query, full_answer)

    if is_first_message:
        name = generate_session_name(query)
        session_manager.update_name(session_id, name)
