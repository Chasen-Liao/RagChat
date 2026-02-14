from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .config import settings


class ConversationCompressor:
    """对话历史压缩：长对话时压缩早期历史"""

    def __init__(self, max_messages: int = 10, max_summary_tokens: int = 500):
        self.max_messages = max_messages
        self.max_summary_tokens = max_summary_tokens
        self.llm = ChatOpenAI(
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_api_base,
            model="deepseek-ai/DeepSeek-V3",
            temperature=0.3,
            streaming=False,
        )

    def count_tokens_approx(self, text: str) -> int:
        """估算 token 数（中文约 1 token/字，英文约 1 token/单词）"""
        # 简单估算：总字符数 / 2
        return len(text) // 2

    def compress_messages(self, messages: List[Dict]) -> List[Dict]:
        """压缩消息历史"""
        if len(messages) <= self.max_messages:
            return messages

        # 保留最近的几轮完整对话
        keep_recent = 4  # 保留最近 2 轮（用户+助手各2条）
        recent_messages = messages[-keep_recent:]

        # 早期对话需要压缩
        early_messages = messages[:-keep_recent]

        # 生成摘要
        summary = self._generate_summary(early_messages)

        # 构建压缩后的历史
        compressed = []
        if summary:
            compressed.append(
                {
                    "role": "system",
                    "content": f"[历史对话摘要] {summary}",
                    "timestamp": early_messages[0].get("timestamp", ""),
                }
            )

        compressed.extend(recent_messages)

        print(f"Compressed {len(messages)} messages -> {len(compressed)} messages")
        return compressed

    def _generate_summary(self, messages: List[Dict]) -> str:
        """生成对话摘要"""
        # 构建对话文本
        dialogue_text = ""
        for msg in messages:
            role = "用户" if msg["role"] == "user" else "助手"
            content = msg["content"][:200]  # 限制每条长度
            dialogue_text += f"{role}：{content}\n"

        prompt = f"""请用简洁的语言总结以下对话的主要内容和关键信息，不超过100字：

{dialogue_text}

摘要（简洁明了）："""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            summary = response.content.strip()
            # 限制长度
            if len(summary) > 150:
                summary = summary[:150] + "..."
            return summary
        except Exception as e:
            print(f"Summary generation error: {e}")
            return "之前讨论了多个话题"

    def should_compress(self, messages: List[Dict]) -> bool:
        """判断是否需要压缩"""
        if len(messages) <= self.max_messages:
            return False

        # 计算总 token 数
        total_text = " ".join([m["content"] for m in messages])
        total_tokens = self.count_tokens_approx(total_text)

        return total_tokens > self.max_summary_tokens


# 全局实例
conversation_compressor = ConversationCompressor()
