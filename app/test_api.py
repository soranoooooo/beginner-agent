from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# client = OpenAI()

# response = client.responses.create(
#     model="gpt-5.4",
#     input="请用一句话解释什么是 agent"
# )

# print(response.output_text)

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    # api_key='sk-aafe3202593140b8bd852fe414c10b5a',
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "请用一句话解释什么是 agent"},
    ]
)
print(completion.choices[0].message.content)