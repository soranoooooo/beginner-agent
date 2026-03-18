from openai import OpenAI
from dotenv import load_dotenv
from tools.calculator import add_numbers

load_dotenv()

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

conversation = [
    {
        "role": "system",
        "content": (
            "你是一个会使用工具的 AI 助手。\n"
            "当用户要求你做加法计算时，不要直接给答案。\n"
            "你必须严格按以下格式输出：\n"
            "TOOL: add_numbers\n"
            "ARGS: 数字1, 数字2\n"
            "例如：\n"
            "TOOL: add_numbers\n"
            "ARGS: 12, 30\n"
            "如果用户不是在请求加法计算，就正常直接回答。"
        )
    }
]

print("Tool Agent 已启动（输入 quit 退出）")

while True:
    user_input = input("\n你：").strip()

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

    assistant_reply = response.choices[0].message.content
    print("\n模型原始输出：")
    print(assistant_reply)

    # 判断是否要调用工具
    if assistant_reply.startswith("TOOL: add_numbers"):
        try:
            lines = assistant_reply.strip().splitlines()
            args_line = None

            for line in lines:
                if line.startswith("ARGS:"):
                    args_line = line
                    break

            if args_line is None:
                raise ValueError("没有找到 ARGS 行")

            args_text = args_line.replace("ARGS:", "").strip()
            a_str, b_str = args_text.split(",")

            a = float(a_str.strip())
            b = float(b_str.strip())

            tool_result = add_numbers(a, b)

            tool_message = f"工具 add_numbers 的计算结果是：{tool_result}"

            conversation.append({
                "role": "assistant",
                "content": assistant_reply
            })

            conversation.append({
                "role": "user",
                "content": (
                    f"{tool_message}。"
                    "请你基于这个工具结果，给用户一个自然语言回答。"
                )
            })

            final_response = client.chat.completions.create(
                model="qwen-plus",
                messages=conversation
            )

            final_answer = final_response.choices[0].message.content

            print("\nAgent：", final_answer)

            conversation.append({
                "role": "assistant",
                "content": final_answer
            })

        except Exception as e:
            error_msg = f"工具调用失败：{e}"
            print("\nAgent：", error_msg)

            conversation.append({
                "role": "assistant",
                "content": error_msg
            })

    else:
        print("\nAgent：", assistant_reply)

        conversation.append({
            "role": "assistant",
            "content": assistant_reply
        })