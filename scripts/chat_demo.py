import os
import requests

API_KEY = os.getenv("SILICONFLOW_API_KEY")
url = "https://api.siliconflow.cn/v1/chat/completions"

data = {
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [{"role": "user", "content": "你好，帮我总结一下 Day1 要做什么？"}]
}

resp = requests.post(url, json=data, headers={"Authorization": f"Bearer {API_KEY}"})
print(resp.json()["choices"][0]["message"]["content"])
