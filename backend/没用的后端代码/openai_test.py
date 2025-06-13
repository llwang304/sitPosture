from openai import OpenAI
from dotenv import load_dotenv
import openai
import os
# 加载环境变量
load_dotenv()
# 配置OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "你是一个专业的坐姿健康助手，用简洁中文回答 ."},
        {
            "role": "user",
            "content": "你好，我背部很痛，请告诉我如何缓解."
        }
    ]
)

print(completion.choices[0].message)