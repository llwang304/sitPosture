# import os
#
# from dotenv import load_dotenv, find_dotenv
# _ = load_dotenv(find_dotenv()) # read local .env file
#
# # account for deprecation of LLM model
# import datetime
# # Get the current date
# current_date = datetime.datetime.now().date()
#
# # Define the date after which the model should be set to "gpt-3.5-turbo"
# target_date = datetime.date(2024, 6, 12)
#
# # Set the model variable based on the current date
# if current_date > target_date:
#     llm_model = "gpt-3.5-turbo"
# else:
#     llm_model = "gpt-3.5-turbo-0301"
#
#
#
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from buildvectorstore import build_vectorstore
from mongoConversationLoader import MongoConversationLoader
from langchain.chains import ConversationChain

# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key='AIzaSyD_YZRrOIZ11clBspqGhZyRkwvvrikRX-A')

phone = "13800138000"
conversation_id = 1

# 从 MongoDB 加载历史记忆
mongo_loader = MongoConversationLoader(
    mongo_uri="mongodb://localhost:27017/",
    db_name="sitPostureApp",
    collection_name="conversations",
    llm=llm
)
#方法1 适用于长对话，记忆组成：langchain.summarymemory
# memory = mongo_loader.load_conversation_memory(phone, conversation_id)
#方法2 适用于短对话，记忆组成：内存
memory = ConversationBufferMemory(memory_key="history", return_messages=True)
#方法3 适用于长对话，记忆组成：历史记录经手动拼接由大模型生成总结
# 将总结内容作为历史对话的一部分加入到 memory
# summary=mongo_loader.get_conversation_summary(phone=phone, conversation_id=conversation_id)
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# # 保存助手的总结到 memory
# memory.save_context(inputs={"user": ""}, outputs={"assistant": summary})  # 这里保存助手的消息




# 你可以创建一个方法来处理从 retriever 和 llm 获取答案

    # 尝试从 retriever 获取答案
    # 测试对话（你可以改成 flask 接口或 UI 页面等）
user_input = "工作相关肌肉骨骼疾患的预防？"
# 构建对话链（无RAG）
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)
response = conversation.predict(input=user_input)
print(response)

# 🚀 开始提问：
# response = qa_chain.invoke({"question": "我之前问过你什么问题？"})
# print(response["answer"])


# 调用这个方法获取回答
# response = get_answer("工作相关肌肉骨骼疾患的预防？")
# print(response)
#
