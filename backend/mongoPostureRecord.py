# posture_monitor.py
import time
from datetime import datetime
from collections import deque
from pymongo import MongoClient
from detectPose import judge_head_tilt, judge_leg_cross, judge_tilt_forward_backward_sideview
from database import db,User
class PostureMonitor:
    def __init__(self, user_id, window_seconds=5, max_queue_len=150):
        self.user_id = user_id
        self.window_seconds = window_seconds
        self.window = deque()
        self.max_queue_len = max_queue_len
        self.last_alert = None
        self.latest_state = None  # 记录最新分析结果
        self.last_voice_reminder_time = None

        # 初始化 MongoDB
        mongo_uri = "mongodb://localhost:27017/"
        client = MongoClient(mongo_uri)
        self.db = client["sitPostureApp"]
        self.records_col = self.db["posture_records"]
        self.alerts_col = self.db["alerts"]
        # 通过 SQLAlchemy 查询语音设置
        user = db.session.query(User).filter_by(phone=user_id).first()
        # 初始化语音播报设置（从 MySQL）
        self.muted = user.isVolumeMuted if user else False
        self.voice_interval = user.reminderFrequency * 60 if user and user.reminderFrequency else 120
        print(f">>> 初始化 PostureMonitor: 用户={user_id}, 静音={self.muted}, 间隔={self.voice_interval}s")

        print(f">>> PostureMonitor 实例初始化: {user_id}")


    def add_data(self, landmarks, timestamp=None):
        print(f"添加姿态数据: {len(landmarks)} 个关键点")
        """添加一帧姿态关键点数据，进入滑动窗口"""
        timestamp = timestamp or time.time()
        self.window.append((timestamp, landmarks))

        # 控制窗口大小
        while self.window and (timestamp - self.window[0][0] > self.window_seconds):
            self.window.popleft()
        print(f"当前时间戳: {timestamp}, 窗口起始: {self.window[0][0] if self.window else '空'}")

        # 触发分析
        if len(self.window) >= 5:  # 至少收集到一定数据才分析
            print(f"[{self.user_id}] 已收集{len(self.window)}帧，开始姿态分析")
            self.analyze_window()


    def analyze_window(self):
        """对当前窗口中的数据进行分析，存储结果和必要报警"""
        head_states = []
        leg_states = []
        torso_states = []

        for _, lm in self.window:
            head_states.append(judge_head_tilt(lm))
            leg_states.append(judge_leg_cross(lm))
            torso_states.append(judge_tilt_forward_backward_sideview(lm))

        # 统计最多出现的结果
        def most_common(state_list):
            return max(set(state_list), key=state_list.count)

        head = most_common(head_states)
        leg = most_common(leg_states)
        torso = most_common(torso_states)

        overall_state = self.evaluate_posture(head, leg, torso)
        # 保存最新状态
        self.latest_state = {
            "head": head,
            "torso": torso,
            "leg": leg,
            "overall": overall_state
        }

        now = datetime.now()
        # 存入 posture_records
        self.records_col.insert_one({
            "user_id": self.user_id,
            "timestamp": now,
            "head": head,
            "torso": torso,
            "leg": leg,
            "overall": overall_state,
        })

        # 判断是否报警
        if overall_state != "good":
            self.trigger_alert(overall_state, now)
        else:
            self.resolve_alert(now)
        print(f"[{self.user_id}] 分析结果：头={head}, 躯干={torso}, 腿={leg}, 总体={overall_state}")

    def evaluate_posture(self, head, leg, torso):
        """简单判断good / bad"""
        if head == "upright" and torso == "upright" and leg == "none":
            return "good"
        return "bad"

    def trigger_alert(self, state, now):
        """生成或更新一个报警"""
        if not self.last_alert:
            self.last_alert = {
                "start": now,
                "type": state
            }
        elif self.last_alert["type"] != state:
            # 状态变化时提交之前的报警
            self.alerts_col.insert_one({
                "user_id": self.user_id,
                "type": self.last_alert["type"],
                "start": self.last_alert["start"],
                "end": now
            })
            self.last_alert = {
                "start": now,
                "type": state
            }

    def resolve_alert(self, now):
        """当前恢复为good时，结束现有报警"""
        if self.last_alert:
            self.alerts_col.insert_one({
                "user_id": self.user_id,
                "type": self.last_alert["type"],
                "start": self.last_alert["start"],
                "end": now
            })
            self.last_alert = None


    def get_latest_posture_state(self):
        return self.latest_state or {}

    def update_voice_settings(self, is_muted, interval_seconds):
        self.muted = is_muted
        self.voice_interval = interval_seconds