from pymongo import MongoClient

def print_collection_data(db_name, collection_name, limit=10):
    mongo_uri = "mongodb://localhost:27017/"
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    print(f"\n--- {collection_name} 集合的前 {limit} 条记录 ---\n")
    for doc in collection.find().sort("timestamp", 1).limit(limit):
        print(doc)

from datetime import datetime
from pymongo import MongoClient
from collections import defaultdict

def get_posture_report(user_id, start_date, end_date):
    """
    获取某个用户在指定时间范围内的健康记录和指标统计报告

    参数:
    - user_id: 用户 ID（字符串）
    - start_date: 开始时间（datetime 对象）
    - end_date: 结束时间（datetime 对象）

    返回：
    {
        "records": [...],  # 所有健康记录
        "stats": {
            "head": {状态A: 总时长, 状态B: 总时长, ...},
            "torso": {...},
            "leg": {...},
            "overall": {...}
        }
    }
    """
    mongo_uri = "mongodb://localhost:27017/"
    client = MongoClient(mongo_uri)
    db = client["sitPostureApp"]
    records_col = db["posture_records"]

    # 获取记录（时间戳 + 四个指标）
    cursor = records_col.find({
        "user_id": user_id,
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }).sort("timestamp", 1)

    records = list(cursor)

    # 统计每个指标每种状态的持续时间（秒）
    stats = {
        "head": defaultdict(float),
        "torso": defaultdict(float),
        "leg": defaultdict(float),
        "overall": defaultdict(float)
    }

    # 遍历每两条记录，统计时间差
    for i in range(len(records) - 1):
        current = records[i]
        next_record = records[i + 1]
        delta = (next_record["timestamp"] - current["timestamp"]).total_seconds()
        for key in ["head", "torso", "leg", "overall"]:
            stats[key][current[key]] += delta

    # 最后一条数据暂时不计入时间（或可用默认采样周期处理）
    # 你也可以假设最后一条持续5秒：
    # if records:
    #     for key in ["head", "torso", "leg", "overall"]:
    #         stats[key][records[-1][key]] += 5

    # 将 defaultdict 转成普通 dict
    stats = {k: dict(v) for k, v in stats.items()}

    return {
        "records": [
            {
                "timestamp": r["timestamp"],
                "head": r["head"],
                "torso": r["torso"],
                "leg": r["leg"],
                "overall": r["overall"]
            } for r in records
        ],
        "stats": stats
    }


# 示例：查看 posture_records 和 alerts
print_collection_data("sitPostureApp", "posture_records", limit=10)
print_collection_data("sitPostureApp", "alerts", limit=10)



from datetime import datetime

start = datetime(2025, 5, 17, 10, 0, 0)
end = datetime(2025, 5, 20, 12, 0, 0)
report = get_posture_report("13700137000", start, end)

print("所有记录：")
for r in report["records"]:
    print(r)

print("\n统计结果：")
for k, v in report["stats"].items():
    print(f"{k}:")
    for label, seconds in v.items():
        print(f"  {label}: {seconds:.1f} 秒")