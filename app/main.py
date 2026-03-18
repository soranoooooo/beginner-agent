from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

conversation = [
    {
        "role": "system",
        "content": "你是一个帮助初学者学习编程的 AI 助手，回答要清晰、分步骤。"
    }
]

print("Qwen Agent 已启动（输入 quit 退出）")

while True:
    user_input = input("\n你：")

    if user_input.lower() in ["quit", "exit"]:
        print("已退出")
        break

    conversation.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=conversation
    )

    answer = response.choices[0].message.content

    print("\nAgent：", answer)

    conversation.append({
        "role": "assistant",
        "content": answer
    })