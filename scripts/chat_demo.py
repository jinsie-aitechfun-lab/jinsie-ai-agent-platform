from app.services.chat_completion_service import ChatCompletionService

def main() -> None:
    service = ChatCompletionService()
    text = service.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你好，请用一句话介绍你自己。"},
        ]
    )
    print(text)

if __name__ == "__main__":
    main()
