# Day1 Prompt Templates

SYSTEM_TEMPLATE = """
你是一名专业的 AI 应用工程师助手，回答要精准、清晰、可执行。
"""

TASK_SUMMARY_TEMPLATE = """
请用 3 点总结以下任务的核心内容：
{task}
"""

RAG_ANSWER_TEMPLATE = """
结合以下知识回答用户问题：
知识：{context}
问题：{question}
请给出简洁、可信的回答。
"""

if __name__ == "__main__":
    print("System Prompt:\n", SYSTEM_TEMPLATE)
    print("Summary Prompt:\n", TASK_SUMMARY_TEMPLATE.format(task="Day1 学习内容"))
    print("RAG Prompt:\n", RAG_ANSWER_TEMPLATE.format(context="示例知识", question="什么是RAG？"))
