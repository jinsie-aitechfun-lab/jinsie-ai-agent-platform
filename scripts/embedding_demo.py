import os
import requests

API_KEY = os.getenv("SILICONFLOW_API_KEY")
url = "https://api.siliconflow.cn/v1/embeddings"

data = {"model": "BAAI/bge-large-zh-v1.5", "input": "这是一个用于生成 embedding 的示例文本。"}

resp = requests.post(url, json=data, headers={"Authorization": f"Bearer {API_KEY}"})
print("Embedding dim:", len(resp.json()["data"][0]["embedding"]))
print("Embedding:", resp.json()["data"][0]["embedding"])