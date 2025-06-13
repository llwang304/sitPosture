from app import *

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date
db = SQLAlchemy(app)
import random

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)# primary_key=True, id自增
    phone = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(200),default="http://localhost:8000/user1.jpg",nullable=False)
    isMicMuted = db.Column(db.Boolean, default=True)
    isVolumeMuted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间

    health_info = db.relationship("HealthInfo", backref="user", uselist=False)

    def __repr__(self):
        return f'<User {self.username} ({self.phone})>'


# 用户健康信息表（单独拆出）
class HealthInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.String(20))
    age = db.Column(db.Integer)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    occupation = db.Column(db.String(50))

    spineHealth = db.Column(db.String(50))
    exerciseHabit = db.Column(db.String(200))
    sittingStyle = db.Column(db.String(50))
    sittingTime = db.Column(db.Integer)  # 单位：小时

    healthGoal = db.Column(db.String(100))
    reminderFrequency = db.Column(db.String(50))
    otherInfo = db.Column(db.Text)

    def __repr__(self):
        return f'<HealthInfo for User {self.user_id}>'


class PostureRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # date = db.Column(db.Date, default=DT.utcnow)
    date = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间
    posture_type = db.Column(db.String(50))  # e.g. 正确 / 弯腰驼背
    score = db.Column(db.Float)              # 0~100 的评分
    duration_minutes = db.Column(db.Integer) # 检测时长
    is_qualified = db.Column(db.Boolean)     # 是否达标

    def __repr__(self):
        return f"<PostureRecord for user {self.user_id} on {self.date}>"


# class ChatSession(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
#     title = db.Column(db.String(100), default="新对话")
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#
#     # relationships
#     user = db.relationship('User', backref=db.backref('chat_sessions', lazy=True))
#
# class ChatMessage(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
#     role = db.Column(db.String(10), nullable=False)  # "user" or "assistant"
#     message = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     session = db.relationship('ChatSession', backref=db.backref('messages', lazy=True, order_by="ChatMessage.created_at"))


# 数据库初始化函数
def db_init():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # 创建示例用户1
        user1 = User(
            phone='13800138000',
            password='password1',
            username='菜菜',
            avatar='http://localhost:8000/user1.jpg',
            isMicMuted=True,
            isVolumeMuted=False
        )
        user1_info = HealthInfo(
            user=user1,
            name='张三',
            gender='男',
            birthday='1995-06-15',
            age=28,
            height=175,
            weight=70,
            occupation='工程师',
            spineHealth='良好',
            exerciseHabit='每周3次慢跑，健身房上肢练习',
            sittingStyle='直立',
            sittingTime=6,
            healthGoal='改善坐姿',
            reminderFrequency='每小时',
            otherInfo='希望能带来一些关于按摩的知识。'
        )

        # 创建示例用户2
        user2 = User(
            phone='13900139000',
            password='password2',
            username='user2',
            avatar='http://localhost:8000/user1.jpg',
            isMicMuted=False,
            isVolumeMuted=False
        )
        user2_info = HealthInfo(
            user=user2,
            name='李四',
            gender='女',
            birthday='1992-02-18',
            age=33,
            height=160,
            weight=55,
            occupation='设计师',
            spineHealth='一般',
            exerciseHabit='偶尔跑步',
            sittingStyle='弯曲',
            sittingTime=5,
            healthGoal='改善坐姿',
            reminderFrequency='每2小时',
            otherInfo='没有'
        )

        db.session.add_all([user1, user1_info, user2, user2_info])
        db.session.commit()

        # 模拟为 user1 和 user2 插入几条坐姿记录
        records = [
            PostureRecord(user_id=1, date=date(2024, 4, 10), posture_type='直立', score=90.5, duration_minutes=60,
                          is_qualified=True),
            PostureRecord(user_id=1, date=date(2024, 4, 11), posture_type='驼背', score=60.0, duration_minutes=50,
                          is_qualified=False),
            PostureRecord(user_id=2, date=date(2024, 4, 10), posture_type='侧倾', score=75.0, duration_minutes=45,
                          is_qualified=False),
            PostureRecord(user_id=2, date=date(2024, 4, 11), posture_type='直立', score=85.0, duration_minutes=55,
                          is_qualified=True),
        ]

        db.session.add_all(records)
        db.session.commit()