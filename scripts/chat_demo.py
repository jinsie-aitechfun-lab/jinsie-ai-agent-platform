import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1",
)

resp = client.embeddings.create(
    model="BAAI/bge-large-zh-v1.5",
    input=["这是一个用于生成 embedding 的示例。"],
)

embedding = resp.data[0].embedding
print("Embedding dim:", len(embedding))
