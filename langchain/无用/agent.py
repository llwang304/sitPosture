# 天气+景点推荐
from langchain_community.chat_models import ChatTongyi # 用阿里Owen
from langchain.agents import initialize_agent,AgentType# 智能代理/代理的类型（全部决策/半决策）
from langchain.memory import ConversationBufferMemory # 简单记忆模块
from langchain.tools import BaseTool # 自定义工具
import requests
from typing import Optional
from pydantic import Field
import os
from dotenv import load_dotenv

#1.加载.env 文件中的API密钥
load_dotenv()
dashscope_api_key = os.getenv("DASHSCOPE_API_KEY") # 通义チ问API Key
heweather_api_key= os.getenv("HEWEATHER_API_KEY") #和风天气API Key

#2:初始化LLM模型(通义千问qwen-turbo)
llm = ChatTongyi(model_name="gwen-turbo", temperature=0, dashscope_api_key=dashscope_api_key)
#3:初始化记忆系统(对话缓冲记忆)
memory = ConversationBufferMemory(memory_key="chat history", return_messages=True)

class HeWeatherTool(BaseTool):
    name: str = Field(default="heweather tool", description="工具名称")
    description: str = Field(default="用来査询指定城市的实时天气，支持中文城市名")
    #工具的同步运行逻辑
    def _run(self, query: str, run_manager: Optional[object]= None) -> str:
    # 4.1先查城市location id
        location_url = f"https://geoapi.qweather.com/v2/city/lookup?location={query}&key={heweather_api_key}"
        loc_response =requests.get(location_url)
        if loc_response.status_code == 200:
            loc_data = loc_response.json()
            if loc_data["code"] == "200" and loc_data["location"]:
                location_id = loc_data["location"][0]["id"]  # 提取location id
            else:
                return f"城市查询失败，错误码:{loc_data['code']}"
        else:
            return f"城市查询请求失败，状态码:{loc_response.status_code}"

        # 4.2用ocation id查实时天气
        weather_url = f"https://devapi.gweather.com/v7/weather/now?location={location_id}&key={heweather_api_key}"
        weather_response = requests.get(weather_url)
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            if weather_data["code"] == "200":
                weather = weather_data["now"]  # 拼接天气信息
                weather_info = f"{query}当前天气:{weather['text']},温度:{weather['temp']}°C"
                # 4.3将天气信息主动存储到内存中
                memory.save_context({"input": query}, {"output": weather_info})
                return weather_info
            else:
                return f"天气查询失败，错误码: {weather_data['code']}"
        else:
            return f"天气请求失败，状态码: {weather_response.status_code}"

# 5:把工具注册到LangChain系统中
tools = [HeWeatherTool()]
#6:初始化LangChain Agent
agent = initialize_agent(
    tools, # 注册工具
    llm, # 使用通用千问模型
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,# 使用Zero-Shot ReAct模式
    MEMORY=memory,# 挂载记忆系统
    verbose=True # 开启详细日志
)
#8.第一次查询天气→会自动存入内存
weather_response = agent.run("今天北京的天气如何?")
# 9、打印内存内容(已经有了对话历史)
print("查询后的内存内容:",memory.load_memory_variables({}))
#10、打印这次查询的结果
print("天气查询结果:",weather_response)

#11:模拟用户后续对话→读取内存
print("询问之前的天气信息:")
memory_history =memory.load_memory_variables({})
print("内存中的历史记录:",memory_history)
#12、第二次提问→会利用记忆(如天气上下文)
history_response = agent.run("今天去旅游适合穿什么衣服?")

#13、再次打印内存内容(对话历史又增加了)
print("查询后的内存内容:",memory.load_memory_variables({})) # 打印查询后的内存内容

#14:读取完整对话历史
chat_history = memory.load_memory_variables({})["chat_history"] # 读取历史记忆
print("当前对话历史:",chat_history) # 打印历史

#15.手动拼接历史上下文→强制模型参考历史数据
question = f"根据之前你提到的地点和天气:\n{chat_history}\n请告诉我:去这个地方有哪些景点推荐?"
response =agent.run(question)#调用代理
print("景点推荐:",response)