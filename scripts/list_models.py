import os
from openai import OpenAI

def main():
    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")
    if not base_url or not api_key:
        raise SystemExit("Missing OPENAI_BASE_URL or OPENAI_API_KEY")

    client = OpenAI(base_url=base_url, api_key=api_key)
    models = client.models.list()

    print("== Available model ids ==")
    for m in models.data:
        print(m.id)

if __name__ == "__main__":
    main()
