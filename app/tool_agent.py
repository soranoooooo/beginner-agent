from openai import OpenAI
from dotenv import load_dotenv

from tools.calculator import add_numbers, multiply_numbers
from tools.date_tool import get_today_date

load_dotenv()

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

conversation = [
    {
        "role": "system",
        "content": (
            "你是一个会使用工具的 AI 助手。\n"
            "你有以下工具：\n"
            "1. add_numbers(a, b)：加法\n"
            "2. multiply_numbers(a, b)：乘法\n"
            "3. get_today_date()：获取今天日期\n\n"
            "规则：\n"
            "如果需要用工具，必须严格按以下格式输出：\n"
            "TOOL: 工具名\n"
            "ARGS: 参数\n\n"
            "示例：\n"
            "TOOL: add_numbers\n"
            "ARGS: 12, 30\n\n"
            "如果不需要工具，直接正常回答。"
        )
    }
]

print("Multi-Tool Agent 已启动（输入 quit 退出）")

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

    reply = response.choices[0].message.content

    print("\n模型原始输出：")
    print(reply)

    # 判断是否调用工具
    if reply.startswith("TOOL:"):
        try:
            lines = reply.strip().splitlines()

            tool_name = lines[0].replace("TOOL:", "").strip()
            args_line = next((l for l in lines if l.startswith("ARGS:")), None)

            args = []
            if args_line:
                args_text = args_line.replace("ARGS:", "").strip()
                args = [x.strip() for x in args_text.split(",") if x.strip()]

            # 调用工具
            if tool_name == "add_numbers":
                result = add_numbers(float(args[0]), float(args[1]))

            elif tool_name == "multiply_numbers":
                result = multiply_numbers(float(args[0]), float(args[1]))

            elif tool_name == "get_today_date":
                result = get_today_date()

            else:
                raise ValueError(f"未知工具: {tool_name}")

            tool_msg = f"工具 {tool_name} 的结果是：{result}"

            conversation.append({
                "role": "assistant",
                "content": reply
            })

            conversation.append({
                "role": "user",
                "content": tool_msg + "，请给出自然语言回答"
            })

            final = client.chat.completions.create(
                model="qwen-plus",
                messages=conversation
            )

            answer = final.choices[0].message.content

            print("\nAgent：", answer)

            conversation.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:
            print("\nAgent：工具调用失败 ->", e)

    else:
        print("\nAgent：", reply)

        conversation.append({
            "role": "assistant",
            "content": reply
        })