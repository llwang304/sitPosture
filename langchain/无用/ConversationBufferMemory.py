from langchain_community.chat_models import ChatTongyi # 用阿里Owen
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain # 创建对话链
from langchain.memory import ConversationBufferMemory # 简单记忆模块
import os
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("DASHSCOPE_API_KEY")
# 初始化Qwen模型
llm = ChatTongyi(
    model_name="qwen-turbo",
    dashscope_api_key=api_key
)
#定义一个简单Prompt模板
prompt = ChatPromptTemplate.from_template("""
你是一位贴心的AI助手，现在和用户聊天。
请根据对话历史和最新提问，给出自然、有帮助的回答。
对话历史:
{history}
用户提问:
{input}
请回答:
"""
)

# 初始化记忆模块
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

#创建一个LangChain对话链
chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
)

#开始多轮对话
print(chain.invoke({"input":"你好，你是谁?"})["text"])
print(chain.invoke({"input":"你能帮我写一个Python Hello World程序吗?"})["text"])
print(chain.invoke({"input":"再帮我写一个Java版本的吧!"})["text"])
