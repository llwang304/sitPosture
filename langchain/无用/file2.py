# from langchain_community.chat_models import ChatTongyi # 用阿里Owen
# from langchain.prompts import ChatPromptTemplate
# from langchain.chains import LLMChain # 创建对话链
# from langchain.memory import ConversationBufferMemory # 简单记忆模块

from langchain_community.chat_models import ChatTongyi # 用阿里Owen
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chains import LLMChain # 创建对话链
# from langchain.memory import ConversationBufferMemory # 简单记忆模块
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
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
prompt = ChatPromptTemplate.from_messages([
    ("system","你是一个有帮助的AI助手"),# 定义角色
    MessagesPlaceholder(variable_name="history"),# 对话的历史
    ("human","{input}")
]
)

#拼接成链
chain=prompt | llm #管道拼接

#
message_history=ChatMessageHistory()
chain_with_history= RunnableWithMessageHistory(
    chain,
    lambda session_id:message_history,#简化所有对话使用一个memory
    input_messages_key="input",
    history_messages_key="history"
    )

session_id="test-session"
#开始多轮对话
response1=chain_with_history.invoke({"input":"你好，你是谁？"},config={"configurable":{"session_id":session_id}})
print(response1.content)

response2=chain_with_history.invoke({"input":"我的第一个问题是什么？"},config={"configurable":{"session_id":session_id}})
print(response2.content)