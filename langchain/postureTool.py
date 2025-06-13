from langchain_community.chat_models import ChatTongyi # 用阿里Owen
from langchain.agents import initialize_agent,AgentType# 智能代理/代理的类型（全部决策/半决策）
from langchain.memory import ConversationBufferMemory # 简单记忆模块
from langchain.tools import BaseTool # 自定义工具
from langchain.schema import HumanMessage
import requests
from typing import Optional,Type
from pydantic import Field,BaseModel
import os
from dotenv import load_dotenv
from function import describe_user_info
from datetime import datetime,timedelta
import dateparser
import re
from pymongo import MongoClient
from collections import defaultdict
import json
from app import *
from database import *
from typing import Annotated
from langchain.tools import Tool


#加载.env 文件中的API密钥
load_dotenv()
dashscope_api_key = os.getenv("DASHSCOPE_API_KEY") # 通义千问API Key
#heweather_api_key= os.getenV("HEWEATHER_API_KEY") #和风天气API Key
#--------------------------------0.过程中使用的函数--------------------------
def format_posture_records(records: list) -> str:
    label_map = {
        "head": {
            "upright": "头部直立",
            "forward": "头部前倾",
            "backward": "头部后仰"
        },
        "torso": {
            "upright": "躯干直立",
            "forward": "躯干前倾",
            "backward": "躯干后仰"
        },
        "leg": {
            "none": "双腿自然放置",
            "left": "左腿在上",
            "right": "右腿在上"
        },
        "overall": {
            "good": "坐姿良好",
            "bad": "坐姿不良"
        }
    }
    formatted = []
    for r in records:
        timestamp = r["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        # head = {"forward": "头部前倾", "backward": "头部后仰", "upright": "头部直立"}.get(r["head"], r["head"])
        # torso = {"lean_left": "躯干左倾", "lean_right": "躯干右倾", "upright": "躯干保持平衡"}.get(r["torso"], r["torso"])
        # leg = {"cross_left": "双腿左交叉", "cross_right": "双腿右交叉", "none": "双腿自然放置"}.get(r["leg"], r["leg"])
        # overall = {"good": "坐姿良好", "bad": "坐姿不良"}.get(r["overall"], r["overall"])
        # formatted.append(f"- 【{time}】{head}，{torso}，{leg}，{overall}")
        head = label_map["head"].get(r["head"], r["head"])
        torso = label_map["torso"].get(r["torso"], r["torso"])
        leg = label_map["leg"].get(r["leg"], r["leg"])
        overall = label_map["overall"].get(r["overall"], r["overall"])
        formatted.append(f"- 【{timestamp}】{head}，{torso}，{leg}，{overall}")
    return "\n".join(formatted[:10])  # 限制最多10条，避免 prompt 太长


def format_posture_stats(stats: dict) -> str:
    def to_line(part, stat_map):
        return "\n".join([f"- {k}：{v:.1f} 秒" for k, v in stat_map.items()])

    return (
        f"【头部姿势统计】\n{to_line('head', stats['head'])}\n\n"
        f"【躯干姿势统计】\n{to_line('torso', stats['torso'])}\n\n"
        f"【腿部姿势统计】\n{to_line('leg', stats['leg'])}\n\n"
        f"【整体坐姿质量】\n{to_line('overall', stats['overall'])}"
    )


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
    print(user_id)
    print(start_date, end_date)
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
    print({
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
    })
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



def generate_posture_analysis_prompt(user_description: str, posture_summary: str) -> str:
    prompt = f"""
你是一名专业健康助手，请根据以下信息生成一份简洁、准确的坐姿健康分析报告，包括：

1. 总体健康评估；
2. 坐姿问题分析；
3. 改善建议。

【用户信息】
{user_description}

【坐姿数据摘要】
{posture_summary}


请用中文输出报告，语气专业、易于理解，段落清晰。
"""
    return prompt

def parse_time_range(query: str) -> tuple[datetime, datetime]:
    """
        从 query 中提取时间范围，返回起止时间（start_time, end_time）
        """
    query = query.strip()
    now = datetime.utcnow()  # 你系统以 UTC 为准
    delta = timedelta(hours=24)  # 默认时间范围

    if "小时" in query:
        hours = int("".join(filter(str.isdigit, query)))
        delta = timedelta(hours=hours)
    elif "天" in query:
        days = int("".join(filter(str.isdigit, query)))
        delta = timedelta(days=days)
    elif "周" in query:
        weeks = int("".join(filter(str.isdigit, query)))
        delta = timedelta(weeks=weeks)
    elif "月" in query:
        # 约当作30天
        months = int("".join(filter(str.isdigit, query)))
        delta = timedelta(days=30 * months)
    start_time = now - delta
    return start_time, now


def parse_time_range1(query_dict) -> tuple[datetime, datetime]:
    """
    输入一个 query 字典，例如：
    {
        "phone_number": "13700137000",
        "start_date": "30 days ago",
        "end_date": "today"
    }
    返回两个 datetime 类型的 start_time, end_time
    """
    start_text = query_dict.get("start_date", "7 days ago")
    end_text = query_dict.get("end_date", "today")
    # 使用 dateparser 处理自然语言
    start_time = dateparser.parse(start_text)
    end_time = dateparser.parse(end_text)
    # 若解析失败使用默认
    if not start_time:
        start_time = datetime.now() - timedelta(days=7)
    if not end_time:
        end_time = datetime.now()
        print("parser time",start_time,end_time)
    return start_time, end_time



def extract_phone_from_query(query: str) -> str:
    # 匹配中国大陆的手机号：11位数字、1 开头
    match = re.search(r'1[3-9]\d{9}', query)
    return match.group(0) if match else None

def analyze_posture_data(raw_data: str) -> str:
    """
    raw_data 是一个 JSON 字符串，里面包含 user_description, posture_summary, posture_records 三个字段
    """
    try:
        data = json.loads(raw_data)
        print("posture_data",data)
        user_profile = data["user_profile"]
        posture_summary = data["posture_summary"]
        #posture_records = data["posture_records"]
    except Exception as e:
        return f"数据解析失败: {e}"
    prompt = generate_posture_analysis_prompt(user_profile, posture_summary)

    llm = ChatTongyi(
        model_name="qwen-turbo",
        temperature=0.2,
        dashscope_api_key=dashscope_api_key
    )

    res = llm([HumanMessage(content=prompt)])
    print("analyze_posture_data",res)
    return res.content


def generate_health_suggestion(input_summary: str) -> str:
    """
    input_summary 是 JSON 字符串，包含 user_description 和 analysis_result
    """
    try:
        data = json.loads(input_summary)
        user_profile = data["user_profile"]
        analysis_result = data["analysis_result"]
    except Exception as e:
        return f"输入解析失败: {e}"

    prompt = f"""
你是一名专业健康顾问，请根据以下用户信息和坐姿健康分析报告，为用户提供简洁实用的健康建议，包括：

1. 针对性改善方向
2. 可执行的日常建议（如锻炼、习惯调整）
3. 关注重点

【用户资料】
{user_profile}

【姿势分析结果】
{analysis_result}

请用中文输出建议，语气温和专业，适合用户理解和执行。如果你认为有必要了解用户的训练进展，你可以询问用户
"""

    llm = ChatTongyi(
        model_name="qwen-turbo",
        dashscope_api_key=dashscope_api_key,
        temperature=0.4
    )

    response = llm([HumanMessage(content=prompt)])
    return response.content

#------------------------------1.定义工具----------------------------------------
# Tool 1: 获取用户信息

class UserProfileInput(BaseModel):
    phone: str = Field(..., description="用户的手机号")

class UserProfileTool(BaseTool):
    name: str = "user_profile_tool"
    description: str = "获取指定手机号用户的健康档案信息，用于生成个性化建议"
    args_schema: Type[BaseModel] = UserProfileInput  # ✅ 添加类型注解！

    def _run(self, phonestr: str, run_manager: Optional[object] = None) -> str:
        data = json.loads(phonestr)  # 转成字典
        phone_number = data.get("phone_number")
        print("user_profile_tool",phone_number)
        if not phone_number:
            return "错误：没有找到手机号"
        return describe_user_info(phone_number)



# Tool 2: 获取坐姿历史数据
class PostureHistoryTool(BaseTool):
    name: str = "posture_history_tool"
    description: str= (
        "该工具用于获取指定用户在某段时间内的坐姿监测数据，用于评估健康状态。如果用户使用了1个月内，一周内，三天内，那么可以认为结束日期是today,倒推开始日期即可。"
        "如果用户给出的表述是从xx日到xxx日，那么你可以认为直接提取开始时间和结束时间\n\n"
        "如果用户只是笼统地说询问我这段时间的健康表现，那么可以认为开始时间是七天前，结束时间是今天。你给出的时间要能够被dateparser解析"
    #     "输入参数应包括：\n"
    # # "1. phone_number：用户手机号，字符串格式，如 '13700137000'\n"
    # "2. start_date：起始日期，格式为 'YYYY-MM-DD'或者能被dateparser解析的文本"
    # "3. end_date：结束日期，格式为 'YYYY-MM-DD'或能够被dateparser解析的文本，end_date应不早于 start_date\n\n"
    #     "如果用户未说明时间范围，默认查询最近7天（start_date='7 days ago', end_date='today'）。\n\n"
    #     "示例输入：{'phone_number': '13700137000', 'start_date': '7 days ago', 'end_date': 'today'}"
    )

    def _run(self, query: str, run_manager: Optional[object] = None) -> str:
        # query: "近24小时"
        from pymongo import MongoClient
        import datetime
        query_dict = json.loads(query)
        user_id = extract_phone_from_query(query)
        print(f"[DEBUG] 输入 phone: {user_id}")
        print("query",query)
        if not user_id:
            return "无法从您的请求中识别手机号，请提供有效的手机号。"
        start_time, end_time = parse_time_range1(query_dict)
        result = get_posture_report(user_id, start_time, end_time)
        if not result["records"]:
            return f"在 {start_time.date()} 到 {end_time.date()} 期间没有坐姿记录。"
        posture_summary = format_posture_stats(result["stats"])
        posture_records = format_posture_records(result["records"])  # 截取前10条展示
        return f"在 {start_time.date()} 到 {end_time.date()} 期间,【摘要】\n{posture_summary}\n\n【记录片段】\n{posture_records}"


# Tool 3: 评估坐姿状态
class PostureEvaluationTool(BaseTool):
    name: str = "posture_evaluation_tool"
    description: str =( "根据用户信息与其近期坐姿统计数据，生成一份中文坐姿健康分析报告。"
    "输入应为一个包含 user_profile、posture_summary的 JSON 字符串,分别是用户画像，坐姿的统计结果"
    "返回内容包括总体评价、主要问题、健康建议。")

    def _run(self, raw_data: str, run_manager: Optional[object] = None) -> str:
        # 示例逻辑（你也可以在这里调用已有分析代码）
        print(raw_data)
        evaluation = analyze_posture_data(raw_data)
        return evaluation  # 如“前倾率为45%，高于健康标准，弯腰次数偏多”

# Tool 4: 生成健康建议
class PostureSuggestionTool(BaseTool):
    name: str = "posture_suggestion_tool"
    description: str = ("根据姿势评估结果和用户信息，为用户生成简洁的健康建议,输入应为一个包含 user_profile和analysis_result的 JSON 字符串。"
                        " user_profile来自于工具UserProfileTool(),analysis_result来自于工具PostureEvaluationTool(),")

    def _run(self, input_summary: str, run_manager: Optional[object] = None) -> str:
        # 模拟建议，也可以交给 LLM 执行进一步总结
        return generate_health_suggestion(input_summary)

# 定义输入参数模型，如果函数有参数的话
# class WorkbenchQueryInput(BaseModel):
#     query: str  # 假设你的 query_workbench_doc 接收一个字符串问题
#
# Tool 5:RAG工具，效果不好，删去
# class WorkbenchRAGTool(BaseTool):
#     name: str = "workbench_RAG_tool"
#     description: str = "根据工作台布置相关文档回答用户问题。如果问题涉及工位摆放、桌椅高度、工作姿势等，请使用此工具。"
#     args_schema: Type[BaseModel] = WorkbenchQueryInput
#     def _run(self, query: str) -> str:
#         return query_workbench_doc(query)
#         # return query_from_doc(query)
#
#     def _arun(self, query: str) -> str:
#         raise NotImplementedError("WorkbenchRAGTool 暂不支持异步执行")

#------------------------------2.初始化LLM模型(通义千问qwen-turbo)----------------------------------------
#2:初始化LLM模型(通义千问qwen-turbo)
llm = ChatTongyi(model_name="qwen-turbo", temperature=0, dashscope_api_key=dashscope_api_key)
#------------------------------3.初始化记忆系统(对话缓冲记忆)----------------------------------------
#3:初始化记忆系统(对话缓冲记忆)
memory = ConversationBufferMemory(memory_key="chat history", return_messages=True)

# 工具列表
tools = [
    UserProfileTool(),
    PostureHistoryTool(),
    PostureEvaluationTool(),
    PostureSuggestionTool(),
    #WorkbenchRAGTool(),
]
#------------------------------4.初始化LangChain Agent----------------------------------------
# 初始化LangChain Agent
agent_executor = initialize_agent(
    tools, # 注册工具
    llm, # 使用通用千问模型
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,# 使用Zero-Shot ReAct模式
    MEMORY=memory,# 挂载记忆系统
    verbose=True # 开启详细日志
)

if __name__ == "__main__":
    with app.app_context():
        # 用户输入：你只是传入一个手机号，Agent 自动完成后续逻辑
        #query = "我过去1个月坐得健康吗？我的手机号是 13700137000"
        query="正常坐姿下，眼睛距离书本屏幕的距离应该是多少?"
        try:
            response = agent_executor.run(query)
        except Exception as e:
            # 工具链失败后，fallback 到大模型自由回答
            print("[Agent 工具未能处理，已 fallback 到 Qwen LLM 自由回答]")
            response = llm.predict(query)  # 或 llm.generate(prompt) 也可
        print(response)