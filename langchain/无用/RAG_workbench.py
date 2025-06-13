import os
from langchain_community.chat_models import ChatTongyi # 用阿里Owen
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from buildvectorstore import build_vectorstore
#from mongoConversationLoader import MongoConversationLoader
from dotenv import load_dotenv
#1.加载.env 文件中的API密钥
load_dotenv()
dashscope_api_key = os.getenv("DASHSCOPE_API_KEY") # 通义千问API Key
def load_vectorstore(doc_path: str, vectorstore_path: str, build_vectorstore_fn):
    #初始化
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                            model_kwargs={'device': 'cpu'})
    # 如果已存在 vectorstore，就直接加载
    if os.path.exists(vectorstore_path):
        print("🟢 已检测到向量库，正在加载...")
        vectorstore = FAISS.load_local(
            vectorstore_path,
            embedding_model,
            allow_dangerous_deserialization=True
        )
    else:
        print("🟡 未检测到向量库，开始向量化...")
        build_vectorstore(doc_path,vectorstore_path)
        vectorstore = FAISS.load_local(
            vectorstore_path,
            embedding_model,
            allow_dangerous_deserialization=True
        )
    return vectorstore



# phone = "13800138000"
# conversation_id = 1
#
# # 从 MongoDB 加载历史记忆
# mongo_loader = MongoConversationLoader(
#     mongo_uri="mongodb://localhost:27017/",
#     db_name="sitPostureApp",
#     collection_name="conversations",
#     llm=llm
# )
def query_workbench_doc(query:str):
    # llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-2.0-flash",
    #     google_api_key='AIzaSyD_YZRrOIZ11clBspqGhZyRkwvvrikRX-A')
    llm = ChatTongyi(model_name="qwen-turbo", temperature=0, dashscope_api_key=dashscope_api_key)
    # 从 MongoDB 加载历史记忆
    # mongo_loader = MongoConversationLoader(
    #     mongo_uri="mongodb://localhost:27017/",
    #     db_name="sitPostureApp",
    #     collection_name="conversations",
    #     llm=llm
    # )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    output_key = "answer"
    )
    doc_path = "doc_new"
    vectorstore_path = "vectorstore"
    vectorstore=load_vectorstore(doc_path, vectorstore_path, build_vectorstore)
    # todo:retriever参数见gpt
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3})  #score_threshold 	只返回相似度高于该阈值的文档（比如 0.7）
    # 启动 RAG
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        verbose=True,
        return_source_documents=True,
    # output_key = "answer"  # 👈 加上这个就能解决报错
    )
    response = qa_chain.invoke(query)
    return response["answer"] if isinstance(response, dict) and "answer" in response else response

# from langchain.llms import HuggingFacePipeline
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# prompt_template = """
# 你是一个人体工效学专家，请根据以下资料内容回答用户关于工作台布置的问题。如果没有相关内容，请诚实地说你不知道。
#
# ----------------
# {context}
# ----------------
# 用户问题：{question}
# 专家回答：
# """
# model_id = "Qwen/Qwen1.5-4B-Chat"
#
# tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
# model = AutoModelForCausalLM.from_pretrained(
#     model_id,
#     # device_map="auto",
#     trust_remote_code=True,
#     torch_dtype="auto"
# )
#
# qwen_pipeline = pipeline(
#     "text-generation",
#     model=model,
#     tokenizer=tokenizer,
#     max_new_tokens=512,
#     do_sample=True,
#     temperature=0.7,
#     top_p=0.95,
# )
#
# llm = HuggingFacePipeline(pipeline=qwen_pipeline)
# prompt = PromptTemplate(
#     input_variables=["context", "question"],
#     template=prompt_template
# )
#
#
#
#
# def query_from_doc(query:str):
#     # 推荐模型
#     doc_path = "doc_new"
#     vectorstore_path = "vectorstore"
#     vectorstore = load_vectorstore(doc_path, vectorstore_path, build_vectorstore)
#     retriever = vectorstore.as_retriever(
#         search_kwargs={"k": 3})  # score_threshold 	只返回相似度高于该阈值的文档（比如 0.7）
#     rag_chain = RetrievalQA.from_chain_type(
#         llm=llm,
#         chain_type="stuff",
#         retriever=retriever,
#         return_source_documents=True,
#         chain_type_kwargs={"prompt": prompt}
#     )
#     result = rag_chain({"query": query})
#     return result
#

import requests
# 1. Qwen API 调用函数（替换成你自己的API KEY和地址）
# def qwen_api_generate(prompt, max_tokens=512):
#     api_url = "https://api.qwen.com/v1/chat/completions"  # 举例接口
#     headers = {
#         "Authorization": dashscope_api_key,
#         "Content-Type": "application/json"
#     }
#     data = {
#         "model": "qwen-turbo",  # 或 qwen-1.5b，按你API支持的型号填
#         "messages": [{"role": "user", "content": prompt}],
#         "max_tokens": max_tokens,
#         "temperature": 0.7,
#     }
#     response = requests.post(api_url, json=data, headers=headers)
#     resp_json = response.json()
#     return resp_json["choices"][0]["message"]["content"]

# Qwen API 调用函数示范（替换为你的API地址和参数）
def query_qwen_api(prompt: str) -> str:
    url = "https://api.qwen.example/v1/chat/completions"  # 替换成实际API地址
    headers = {
        "Authorization": "Bearer your_api_key",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-turbo",  # 具体模型名根据API
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    res_json = response.json()
    # 按Qwen API返回格式解析回答，示范用res_json["choices"][0]["message"]["content"]
    return res_json["choices"][0]["message"]["content"]


# 2. 简易文本检索函数（模拟）
def retrieve_relevant_docs(query, docs, top_k=3):
    # 这里简单用包含关键词的文本过滤代替向量检索
    relevant = [doc for doc in docs if query.lower() in doc.lower()]
    return relevant[:top_k]

# 自定义一个简单的 Chain 来结合检索和Qwen API
from langchain.chains.base import Chain
from typing import Dict
from langchain.schema import BaseRetriever
from pydantic import Field

class QwenRAGChain(Chain):
    retriever: BaseRetriever = Field()


    @property
    def input_keys(self):
        return ["question"]

    @property
    def output_keys(self):
        return ["answer"]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        question = inputs["question"]
        # 用retriever检索相关文档片段
        docs = self.retriever.get_relevant_documents(question)
        context = "\n".join([doc.page_content for doc in docs])
        # 拼接检索结果和问题做提示
        prompt = f"根据以下内容回答问题：\n{context}\n问题：{question}\n回答："
        # 调用远程Qwen API生成答案
        answer = query_qwen_api(prompt)
        return {"answer": answer}


# 使用示例
if __name__ == "__main__":
    doc_path = "doc_new"  # 你文档路径
    vectorstore_path = "vectorstore"

    # 加载或构建向量库
    vectorstore = load_vectorstore(doc_path, vectorstore_path, build_vectorstore)

    # 创建RAG chain
    rag_chain = QwenRAGChain(retriever=vectorstore.as_retriever())

    # 测试问答
    question = "在工作台布置中，椅子有什么注意事项？"
    result = rag_chain.run(question)
    print("问：", question)
    print("答：", result)