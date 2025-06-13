from pymongo import MongoClient
import datetime
import uuid

# 本地 MongoDB 连接 URI
mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)
mongodb = client["sitPostureApp"]

def mongodb_init():
    # 选择数据库和集合

    conversations = mongodb["conversations"]

    # 清空原有的对话数据
    conversations.delete_many({})  # 删除集合中的所有文档

    # 要插入的数据
    data = [
        {
            "user_id": 1,
            "phone":"13800138000",
            "conversation_id":1,
            "title": "颈椎问题初步咨询",
            "created_at": datetime.datetime(2025, 4, 16, 15, 30),
            "updated_at": datetime.datetime(2025, 4, 16, 15, 30),
            "messages": [
                {"role": "user", "content": "我最近脖子酸痛","timestamp": datetime.datetime(2025, 4, 16, 15, 30, 1)},
                {"role": "assistant", "content": "建议注意坐姿，屏幕抬高至视线平行。","timestamp": datetime.datetime(2025, 4, 16, 15, 30, 3)}

            ]
        },
        {
            "user_id": 1,
            "phone":"13800138000",
            "conversation_id":2,
            "title": "电脑的放置",
            "created_at": datetime.datetime(2025, 4, 16, 15, 45),
            "updated_at": datetime.datetime(2025, 4, 16, 15, 45),
            "messages": [
                {"role": "user", "content": "我最近看电脑觉得脖子很痛","timestamp": datetime.datetime(2025, 4, 16, 15, 45, 5)},
                {"role": "assistant", "content": "建议抬高电脑，使屏幕和视线平行。下面这篇文章或许会有帮助。","timestamp": datetime.datetime(2025, 4, 16, 15, 45, 10)}

            ]
        },
        {
            "user_id": 2,
            "phone": "13900139000",
            "conversation_id":1,
            "title": "久坐导致臀部不适",
            "created_at": datetime.datetime(2025, 4, 16, 16, 0),
            "updated_at": datetime.datetime(2025, 4, 16, 16, 0),
            "messages": [
                {"role": "user", "content": "久坐一天屁股很痛"},
                {"role": "assistant", "content": "可以用透气坐垫，并每小时起身活动一次。"}
            ]
        }
    ]

    conversations.insert_many(data)
    print("用户对话初始化成功 ✅")




