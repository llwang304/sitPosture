# from openai import OpenAI
# from dotenv import load_dotenv
# import openai
# import os
#
# # 加载环境变量
# load_dotenv()
#
# # 配置OpenAI
# openai.api_key = os.getenv("OPENAI_API_KEY")
#
# client = OpenAI()
#
# def get_chat_response_openai(user_message):
#     """
#     接收用户消息，并返回OpenAI生成的回复内容。
#
#     Args:
#         user_message (str): 用户发送的消息。
#
#     Returns:
#         str: OpenAI生成的回复内容。
#     """
#     try:
#         completion = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "你是一个专业的坐姿健康助手，用简洁中文回答 ."},
#                 {"role": "user", "content": user_message}
#             ]
#         )
#         return {"success": True, "content": completion.choices[0].message.content}
#     except Exception as e:
#         print(f"发生错误：{e}")
#         return {"success": False, "content": f"抱歉，出现了一些问题，请稍后再试。错误信息：{e}"}

# # 示例用法
# user_input = "我的颈椎感觉很僵硬，有什么好的建议吗？"
# response = get_chat_response(user_input)
# print(response)
#
# user_input2 = "123"
# response2 = get_chat_response(user_input2)
# print(response2)

# -------------------gemini--------------------
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY, http_options={'api_version': 'v1alpha'})
chat = client.aio.chats.create(
            model='gemini-2.0-flash-thinking-exp',
            # config=types.GenerateContentConfig(
            #     max_output_tokens=300,
            #     temperature=0.1
            # )
        )
# async def main():
#     response = await chat.send_message('What is your name?')
#     print(response.text)
#     response = await chat.send_message('What did you just say before this?')
#     print(response.text)
#
# if __name__ == "__main__":
#     asyncio.run(main())


async def get_gemini_response(user_message, chat_history=None):
    """
    接收用户消息，调用 Gemini API，并返回指定格式的响应。

    Args:
        user_message (str): 用户发送的消息。
        chat_history (list, optional): 历史对话列表，用于多轮对话。

    Returns:
        dict: 包含 'success' (bool) 和 'content' (str) 键的字典。
    """
    try:
        # client = genai.GenerativeModel(model_name='gemini-2.0-flash-thinking-exp', api_key=GOOGLE_API_KEY)
        # if chat_history:
        #     chat = client.start_chat(history=chat_history)
        # else:
        #     chat = client.start_chat()
        # response_pre = await chat.send_message(chat_history)

        response = await chat.send_message(user_message)
        return {"success": True, "content": response.text}
    except Exception as e:
        return {"success": False, "content": f"抱歉，出现了一些问题，请稍后再试。错误信息：{e}"}





from PIL import Image
from google import genai
import re


def remove_markdown(text):
    """移除文本中的 Markdown 标记。"""
    text = re.sub(r'#+\s', '', text)  # 移除标题
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # 移除粗体
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # 移除斜体
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', text)  # 移除链接
    text = re.sub(r'`(.*?)`', r'\1', text)  # 移除代码
    text = re.sub(r'---', '', text) # 移除分隔符
    text = re.sub(r'>', '', text) #移除引用
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'\1', text) #移除图片
    text = re.sub(r'[\*\~`\>#\-\!\[\]\(\)\.\+\=\<\>]', '', text) #移除其他特殊符号
    text = re.sub(r'\n', '', text) #移除换行符号
    text = re.sub(r'\s{2,}', ' ', text) #移除多余的空格
    return text.strip()

def get_sitting_posture_advice(image_path):
    """
    使用 Gemini 模型根据图片生成坐姿调整建议。

    Args:
        image_path: 图片文件的路径。
        google_api_key: 您的 Google API 密钥。

    Returns:
        调整坐姿的建议文本，或者在出现错误时返回 None。
    """
    try:
        client1 = genai.Client(api_key=GOOGLE_API_KEY)
        image = Image.open(image_path)
        response = client1.models.generate_content(
            model="gemini-2.0-flash",
            contents=[image, "请用中文给出图片中的人的坐姿存在的问题，并给出简短建议，提示：你需要观察人的头颈部，躯干，肩手部和腿部给出综合结论，"
                             "以“坐姿存在问题：xxxx,建议xxxx。”你的回答要简短，不得超过50个字"]
        )
        return response.text
    except Exception as e:
        print(f"发生错误: {e}")
        return None