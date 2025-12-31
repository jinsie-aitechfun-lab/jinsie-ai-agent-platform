import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1",
)

resp = client.chat.completions.create(
    model="Qwen/Qwen2.5-7B-Instruct",
    messages=[
        {"role": "user", "content": "你好，总结一下我 Day1 的任务。"}
    ],
)

print(resp.choices[0].message.content)
