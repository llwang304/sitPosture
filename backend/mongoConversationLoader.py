from pymongo import MongoClient
from langchain.memory import ConversationSummaryMemory
# from langchain.chat_models import ChatGoogleGenerativeAI
from llm import get_gemini_response,remove_markdown
import asyncio
class MongoConversationLoader:
    def __init__(self, mongo_uri, db_name, collection_name, llm):
        self.client = MongoClient(mongo_uri)
        self.collection = self.client[db_name][collection_name]
        self.llm = llm

    # todo:通过langchain.conversationSummaryMemory总结历史信息，但与gemini兼容性差，无法运行
    def load_conversation_memory(self, phone, conversation_id):
        # 打印当前查询条件
        print(f"🔍 正在查询 MongoDB 中 phone = {phone} 且 conversation_id = {conversation_id} 的会话...")

        self.debug_all_documents()  # 打印全部文档，便于 debug
        query = {"phone": phone, "conversation_id": conversation_id}
        document = self.collection.find_one(query)
        if not document:
            raise ValueError(f"❌ 未找到用户 {phone} 的会话 ID：{conversation_id}")

        messages = document.get("messages", [])
        memory = ConversationSummaryMemory(llm=self.llm, memory_key="chat_history", return_messages=True)

        for i in range(0, len(messages), 2):
            user_msg = messages[i]["content"] if messages[i]["role"] == "user" else ""
            ai_msg = messages[i + 1]["content"] if i + 1 < len(messages) and messages[i + 1][
                "role"] == "assistant" else ""
            if user_msg:
                memory.save_context({"input": user_msg}, {"output": ai_msg})

        return memory


    # 打印mongodb对话文档
    def debug_all_documents(self):
        print("📄 正在打印 MongoDB 中的所有对话文档（仅限前10条）:")
        for doc in self.collection.find().limit(10):
            print(
                f"📌 phone: {doc.get('phone')}, conversation_id: {doc.get('conversation_id')}, messages_len: {len(doc.get('messages', []))}")


    # todo:手动调用geimini进行总结
    # 从 MongoDB 获取会话历史
    def get_conversation_history(self, phone, conversation_id):
        conversation = self.collection.find_one({"phone": phone, "conversation_id": conversation_id})
        if not conversation:
            raise ValueError(f"❌ 未找到用户 {phone} 的会话 ID：{conversation_id}")
        return conversation['messages']

    # 拼接历史对话生成 prompt
    def create_summary_prompt(self, messages):
        prompt = "以下是对话历史，简要总结用户和助手的互动内容：\n\n"
        # 遍历消息列表，将用户和助手的消息拼接成对话
        for msg in messages:
            if msg["role"] == "user":
                prompt += f"用户: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"助手: {msg['content']}\n"
        prompt += "\n总结："
        print("prompt", prompt)
        return prompt

    # 使用 Gemini 或其他 LLM 做总结
    def generate_summary(self, prompt):
        #response = self.llm.invoke(prompt)
        response= asyncio.run(get_gemini_response(prompt))
        print('response',response)
        return response["content"]

    # 获取并总结会话
    def get_conversation_summary(self, phone, conversation_id):
        print(f"🔍 正在查询 MongoDB 中 phone = {phone} 且 conversation_id = {conversation_id} 的会话...")
        messages = self.get_conversation_history(phone, conversation_id)
        self.debug_all_documents()  # 打印全部文档，便于 debug
        # 拼接 prompt 并生成总结
        prompt = self.create_summary_prompt(messages)
        summary =self.generate_summary(prompt)

        return remove_markdown(summary)