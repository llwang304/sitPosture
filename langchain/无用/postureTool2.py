# posture_tool.py
from datetime import datetime, timedelta
from typing import Tuple, Dict, List
from pydantic import BaseModel
from langchain.tools import StructuredTool


# -----------------------
# 🧩 参数模型
# -----------------------
class PostureQuery(BaseModel):
    phone_number: str
    start_date: str   # 比如 "30 days ago"
    end_date: str     # 比如 "today"


# -----------------------
# ⏱️ 时间解析函数（伪实现）
# -----------------------
def parse_time_range(start: str, end: str) -> Tuple[datetime, datetime]:
    now = datetime.now()

    if "today" in end:
        end_time = now
    elif "yesterday" in end:
        end_time = now - timedelta(days=1)
    else:
        end_time = now

    if "30 days" in start:
        start_time = end_time - timedelta(days=30)
    elif "7 days" in start:
        start_time = end_time - timedelta(days=7)
    else:
        start_time = end_time - timedelta(days=1)

    return start_time, end_time


# -----------------------
# 📊 伪造数据的主函数
# -----------------------
def get_posture_report(user_id: str, start_time: datetime, end_time: datetime) -> Dict:
    # 你应从 MongoDB 中查询并处理，但这里用假数据模拟
    return {
        "stats": {
            "total_records": 100,
            "bad_posture_count": 25,
            "upright_ratio": 0.75,
            "hunchback_ratio": 0.20,
            "leg_cross_ratio": 0.10
        },
        "records": [
            {"timestamp": "2025-05-20 10:00", "label": "hunchback"},
            {"timestamp": "2025-05-20 10:05", "label": "upright"},
            {"timestamp": "2025-05-20 10:10", "label": "leg_cross"},
        ]
    }


# -----------------------
# ✅ 格式化输出函数
# -----------------------
def format_posture_stats(stats: Dict) -> str:
    return (
        f"总记录数: {stats['total_records']} 条\n"
        f"不良坐姿次数: {stats['bad_posture_count']} 次\n"
        f"保持良好坐姿的比例: {stats['upright_ratio'] * 100:.1f}%\n"
        f"驼背比例: {stats['hunchback_ratio'] * 100:.1f}%\n"
        f"跷腿比例: {stats['leg_cross_ratio'] * 100:.1f}%"
    )


def format_posture_records(records: List[Dict]) -> str:
    lines = []
    for r in records[:10]:
        lines.append(f"{r['timestamp']} - 状态: {r['label']}")
    return "\n".join(lines)


# -----------------------
# 🛠️ 工具函数
# -----------------------
def get_posture_history(phone_number: str, start_date: str, end_date: str) -> str:
    # 构造 Pydantic 对象，方便后续调用
    query = PostureQuery(phone_number=phone_number, start_date=start_date, end_date=end_date)
    user_id = query.phone_number
    print(f"[DEBUG] 输入 phone: {user_id}")
    print("[DEBUG] query:", query)

    start_time, end_time = parse_time_range(query.start_date, query.end_date)
    result = get_posture_report(user_id, start_time, end_time)

    summary = format_posture_stats(result["stats"])
    records = format_posture_records(result["records"])

    return f"【摘要】\n{summary}\n\n【记录片段】\n{records}"


# -----------------------
# 🧠 LangChain StructuredTool 注册
# -----------------------
posture_history_tool = StructuredTool.from_function(
    func=get_posture_history,
    name="posture_history_tool",
    description=(
        "根据用户手机号与时间范围查询坐姿监测数据，返回健康摘要和部分原始记录。\n"
        "输入参数格式为 JSON，对象应包含字段：phone_number、start_date、end_date。"
    ),
    args_schema=PostureQuery
)


# 创建一个“模拟大模型”的请求
query = {
    "phone_number": "13700137000",
    "start_date": "30 days ago",
    "end_date": "today"
}

result = posture_history_tool.invoke(query)
print(result)