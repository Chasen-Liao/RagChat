import re
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from .config import settings


class IntentClassifier:
    """意图识别：判断是否需要检索文档"""

    # 不需要检索的意图关键词
    CHITCHAT_PATTERNS = [
        r"^(你好|您好|嗨|hello|hi|hey)",
        r"^(谢谢|感谢|thank)",
        r"^(再见|拜拜|bye)",
        r"^(你是?谁|你叫什么|你的名字)",
        r"^(你会做什么|你能做什么|你能帮我什么)",
        r"^(今天|明天|现在|时间|日期)",
        r"^(嗯|哦|啊|好的|OK|ok)$",
    ]

    # 需要检索的意图关键词
    RETRIEVAL_KEYWORDS = [
        "根据文档",
        "根据资料",
        "查一下",
        "找一下",
        "文档里",
        "资料里",
        "记录中",
        "提到了",
        "什么是",
        "为什么",
        "怎么做",
        "如何",
        "解释",
        "说明",
        "介绍",
        "详细",
    ]

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_api_base,
            model="deepseek-ai/DeepSeek-V3",  # 使用轻量级模型
            temperature=0.1,
            streaming=False,
        )

    def rule_based_classify(self, query: str) -> tuple[bool, float]:
        """基于规则的快速分类"""
        query_lower = query.lower().strip()

        # 检查是否为闲聊
        for pattern in self.CHITCHAT_PATTERNS:
            if re.search(pattern, query_lower):
                return False, 0.95

        # 检查是否明确需要检索
        for keyword in self.RETRIEVAL_KEYWORDS:
            if keyword in query_lower:
                return True, 0.9

        # 无法确定，需要 LLM 判断
        return None, 0.0

    def llm_classify(self, query: str) -> bool:
        """使用 LLM 判断是否需要检索"""
        prompt = f"""请判断以下用户问题是否需要查阅文档才能回答。

用户问题：{query}

判断标准：
- 如果是闲聊、问候、简单问答（如"你好"、"谢谢"），回答"否"
- 如果是询问具体知识、需要事实依据的问题，回答"是"
- 如果不确定，回答"是"（宁可多检索也不少检索）

只需回答一个字"是"或"否"："""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()
            return "是" in result or "yes" in result.lower()
        except Exception as e:
            print(f"Intent classification error: {e}")
            # 出错时默认需要检索
            return True

    def should_retrieve(self, query: str) -> bool:
        """判断是否需要检索"""
        # 先用规则判断
        rule_result, confidence = self.rule_based_classify(query)

        if rule_result is not None and confidence > 0.9:
            print(f"Intent (rule-based): {'retrieve' if rule_result else 'chat'}")
            return rule_result

        # 规则无法确定，使用 LLM
        llm_result = self.llm_classify(query)
        print(f"Intent (LLM-based): {'retrieve' if llm_result else 'chat'}")
        return llm_result


# 全局实例
intent_classifier = IntentClassifier()
