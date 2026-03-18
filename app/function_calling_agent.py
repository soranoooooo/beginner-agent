import json

from openai import OpenAI
from dotenv import load_dotenv

from tools.calculator import add_numbers, multiply_numbers
from tools.date_tool import get_today_date

load_dotenv()

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 1. 定义工具（标准 function calling 写法）
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "计算两个数字的和",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字"
                    }
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "multiply_numbers",
            "description": "计算两个数字的乘积",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字"
                    }
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_today_date",
            "description": "获取今天的日期，格式为 YYYY-MM-DD",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

# 2. 对话历史
messages = [
    {
        "role": "system",
        "content": "你是一个会调用工具的 AI 助手。需要计算、获取日期时，优先调用工具。"
    }
]

print("标准 Function Calling Agent 已启动（输入 quit 退出）")

while True:
    user_input = input("\n你：").strip()

    if user_input.lower() in ["quit", "exit"]:
        print("已退出")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    # 3. 第一次请求：让模型决定是否调用工具
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # 4. 如果模型决定调用工具
    if assistant_message.tool_calls:
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in assistant_message.tool_calls
            ]
        })

        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # 执行本地工具
            if function_name == "add_numbers":
                tool_result = add_numbers(arguments["a"], arguments["b"])

            elif function_name == "multiply_numbers":
                tool_result = multiply_numbers(arguments["a"], arguments["b"])

            elif function_name == "get_today_date":
                tool_result = get_today_date()

            else:
                tool_result = f"未知工具：{function_name}"

            print(f"\n[工具调用] {function_name}({arguments}) -> {tool_result}")

            # 5. 把工具结果加回消息列表
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": str(tool_result)
            })

        # 6. 第二次请求：把工具结果交给模型，生成最终自然语言回答
        final_response = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            tools=tools
        )

        final_answer = final_response.choices[0].message.content
        print("\nAgent：", final_answer)

        messages.append({
            "role": "assistant",
            "content": final_answer
        })

    else:
        # 7. 如果不需要工具，直接回答
        answer = assistant_message.content
        print("\nAgent：", answer)

        messages.append({
            "role": "assistant",
            "content": answer
        })