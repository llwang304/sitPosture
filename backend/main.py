from app import *
from detection import process_frame
import llm
from audioProcess import process_audio
from mongoPostureRecord import PostureMonitor
from detectPose import judge_posture
from database import *
from mongoDatabase import *
from flask import request, jsonify, session
from flask_socketio import emit, join_room, leave_room,disconnect
from werkzeug.security import generate_password_hash,check_password_hash
from collections import defaultdict

# from sqlalchemy import func, desc, and_
import re
from threading import Thread
import time
import random
import string
from datetime import datetime, timedelta,time
import jwt
from functools import wraps
import cv2
import base64
import numpy as np
import threading
import json
import asyncio

static_path = app.static_folder

lock = threading.Lock()  # 在全局范围创建锁

IMAGE_PATH="posture.jpg"

# 全局缓存每个用户的姿态监测器
user_monitors = {}

@socketio.on('pose_landmarks')
def handle_pose_landmarks(data):
    # data 是一个 dict，包含一个 key：landmarks -> list of 33 dicts
    print("Received landmarks:")
    phone = data.get("phone")
    landmarks = data.get("landmarks")
    mode=data.get("mode")
    if not landmarks or len(landmarks) != 33:
        print("无效的关键点数据")
        return
    print(phone)
    if mode=='video':
        # 初始化每个用户一个姿态监测器
        if phone not in user_monitors:
            user_monitors[phone] = PostureMonitor(user_id=phone)
        # 调用姿态监测器，喂入新的一帧关键点数据
        user_monitors[phone].add_data(landmarks)
        # 直接把最新的姿态状态结果发回给前端
        posture_state_video = user_monitors[phone].get_latest_posture_state()
        # 给当前连接的客户端发消息（假设是单用户或同一个用户设备）
        socketio.emit('posture_result_video', posture_state_video,room=phone)
    else:
        posture_state_image=judge_posture(landmarks)
        # 给当前连接的客户端发消息（假设是单用户或同一个用户设备）
        socketio.emit('posture_result_image', posture_state_image, room=phone)

previous_timestamp = 0


# 生成令牌的函数
def generate_token(phone):
    payload = {
        'phone': phone,
        'exp': datetime.utcnow() + timedelta(minutes=60)  # 令牌有效期为 30 分钟
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token


# 验证令牌的装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('h-token')
        if not token:
            return jsonify({'code': -1, 'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.phone = data['phone']
        except jwt.ExpiredSignatureError:
            return jsonify({'code': -2, 'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': -1, 'message': 'Invalid token!'}), 401
        return f(*args, **kwargs)
    return decorated



def describe_user_info(phone):
    """
    将用户信息字典转换成一段中文描述。

    Args:
        phone: 用户电话
    Returns:
        str: 中文描述字符串。
    """
    user = db.session.query(User).filter_by(phone=phone).first()
    health = user.health_info
    description = (
        f"用户 {user.username}，手机号 {user.phone}，是一名 {health.gender} 性，出生于 {health.birthday}，今年 {health.age} 岁。"
        f"他的身高为 {health.height} 厘米，体重为 {health.weight} 公斤，职业是 {health.occupation}。"
        f"他的脊柱健康状况为 {health.spineHealth}，锻炼习惯是 {health.exerciseHabit}。"
        f"他的坐姿是 {health.sittingStyle}，每天坐着的时间大约为 {health.sittingTime} 小时。"
        f"他的健康目标是 {health.healthGoal}，提醒频率为 {health.reminderFrequency}。"
        f"其他信息:{health.otherInfo}你是一个专业的坐姿健康助手，请为用户提供健康建议，用简洁中文回答。"
    )
    return description


# 登录接口
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    # 从数据库中查找用户
    user = db.session.query(User).filter_by(phone=phone).first()
    if user and check_password_hash(user.password, password):
        token = generate_token(phone)
        user_info = {
            'username': user.username,
            'phone': user.phone,
            'avatar': user.avatar
        }
        return jsonify({'code': 10000, 'data': {'token': token, 'userInfo': user_info}})
    return jsonify({'code': -1, 'message': 'Invalid phone number or password'}), 401


@app.route('/resetPassword', methods=['POST'])
def forgot_password():
    data = request.get_json()
    phone = data.get('phone')
    username = data.get('username')
    new_password = data.get('newPassword')

    user = db.session.query(User).filter_by(phone=phone).first()
    if not user:
        return jsonify({"code": 40001, "message": "用户未注册"}), 200
    if user.username!= username:
        return jsonify({"code": 40002, "message": "昵称错误，无法修改密码"}), 200

    user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"code": 10000, "message": "密码修改成功"}),200

# 注册接口
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    phone = data.get('phone')
    password = data.get('password')

    # 检查用户是否已存在
    user = db.session.query(User).filter_by(phone=phone).first()
    if user:
        return jsonify({'code': 400, 'message': 'User already exists'}), 400

    # 加密密码
    hashed_password = generate_password_hash(password)
    # 创建新用户
    new_user = User(username=username, phone=phone, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    # 注册完成后，给新用户创建一条空的健康信息
    new_health_info = HealthInfo(
        user_id=new_user.id,
        name='',
        gender='',
        birthday='',
        age=0,
        height=0,
        weight=0,
        occupation='',
        spineHealth='',
        exerciseHabit='',
        sittingStyle='',
        sittingTime=0,
        healthGoal='',
        reminderFrequency='',
        otherInfo=''
    )
    db.session.add(new_health_info)
    db.session.commit()

    # 生成token
    token = generate_token(phone)
    # 返回成功响应
    user_info = {
        'username': new_user.username,
        'phone': new_user.phone,
        'avatar': new_user.avatar
    }
    return jsonify({'code': 10000, 'data': {'token': token, 'userInfo': user_info}})


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


@app.route('/dateRange', methods=['POST'])
def receive_date_range():
    try:
        data = request.get_json()
        phone=data.get('phone')
        start_date_str = data.get('startDate')
        end_date_str = data.get('endDate')
        # 解析日期字符串为 datetime 对象
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        print(f"开始日期: {start_date}, 结束日期: {end_date}")
        # 添加时间：start从00:00:00开始，end到23:59:59结束
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        # 在这里进行你的日期处理逻辑
        # 例如，查询数据库或生成统计数据
        report = get_posture_report(phone, start_datetime, end_datetime)
        print("所有记录：")
        for r in report["records"]:
            print(r)

        print("\n统计结果：")
        for k, v in report["stats"].items():
            print(f"{k}:")
            for label, seconds in v.items():
                print(f"  {label}: {seconds:.1f} 秒")
        return jsonify(
            {
                "status": "success",
                "data": {
                    "records": report["records"],  # 时间线表格数据
                    "stats": report["stats"]  # 饼图统计数据
                },
                "message": "报告生成成功"
            }
            ), 200
    except Exception as e:
        print(f"日期范围解析失败: {e}")
        return jsonify({"status":'error',"message": '日期范围解析失败'}), 400





# 获取用户信息
@app.route('/getUserInfo', methods=['GET'])
@token_required
def get_user_info():
    phone = request.phone
    user = db.session.query(User).filter_by(phone=phone).first()
    if not user:
        return jsonify({'code': -1, 'message': 'User not found'}), 404
    health_info = user.health_info
    if not health_info:
        return jsonify({'code': -1, 'message': 'there is no healthInfo'}), 404
    return jsonify({'code': 10000, 'data': {
            "name": health_info.name,
            "gender": health_info.gender,
            "birthday": health_info.birthday,
            "age": health_info.age,
            "height": health_info.height,
            "weight": health_info.weight,
            "occupation": health_info.occupation,
            "spineHealth": health_info.spineHealth,
            "exerciseHabit": health_info.exerciseHabit,
            "sittingStyle": health_info.sittingStyle,
            "sittingTime": health_info.sittingTime,
            "healthGoal": health_info.healthGoal,
            "reminderFrequency": health_info.reminderFrequency,
            "otherInfo": health_info.otherInfo
        }
    })


# 更新用户信息
@app.route('/updateUserInfo', methods=['POST'])
@token_required
def update_user_info():
    phone = request.phone
    data = request.get_json()
    user = db.session.query(User).filter_by(phone=phone).first()
    if not user:
        return jsonify({"code": 404, "message": "User not found"}), 404

    health_info = user.health_info
    if not health_info:
        # 没有健康信息就创建一个
        health_info = HealthInfo(user=user)

    # 批量更新字段（只更新存在的键）
    for field in [
        "name", "gender", "birthday", "age", "height", "weight", "occupation",
        "spineHealth", "exerciseHabit", "sittingStyle", "sittingTime",
        "healthGoal", "reminderFrequency", "otherInfo"
    ]:
        if field in data:
            setattr(health_info, field, data[field])

    db.session.add(health_info)
    db.session.commit()
    return jsonify({'code': 10000, 'message': 'User info updated successfully'})


@socketio.on('receiveUserMessage')
def receive_user_message(data):
    phone = session.get('phone')
    print('进入receiveUserMessage函数')
    try:
        print("收到聊天信息", data)
        conversation_id = data.get('conversation_id')
        user_message = data.get('content')
        description = describe_user_info(phone)
        response = asyncio.run(llm.get_gemini_response(user_message, description))
        if response["success"]:
            # 操作成功，获取回复内容
            reply = response["content"]
            print("回复：", reply)
            now = datetime.now()
            new_messages = [
                {"role": "user", "content": user_message, "timestamp": now},
                {"role": "assistant", "content": reply, "timestamp": now.replace(second=now.second + 5)}
            ]
            # 加入数据库
            append_messages_to_conversation(phone, conversation_id, new_messages)
            # 将 reply 发送给用户
            socketio.emit('chat_response', {"success": True, "content": reply}, room=phone)
        else:
            # 操作失败，获取错误信息
            error_message = response["content"]
            print("错误：", error_message)
            # 处理错误信息
            socketio.emit('chat_response', {"success": False, "content": error_message}, room=phone)

    except Exception as e:
        socketio.emit('chat_response', {"success": False, "content": f"请求失败：{str(e)}"}, room=phone)


# 静音功能
@socketio.on('update_settings')
def handle_settings_update(data):
    phone = session.get('phone')
    phone = data.get('phone')
    isMicMuted = data.get('isMicMuted')
    isVolumeMuted = data.get('isVolumeMuted')

    if not phone:
        socketio.emit('update_response', {'status': 'error', 'message': '手机号不能为空'}, room=phone)
    # 查询用户
    user = db.session.query(User).filter_by(phone=phone).first()
    if not user:
        socketio.emit('update_response', {'status': 'error', 'message': '用户不存在'}, room=phone)
    # 更新数据库中的用户设置
    user.isMicMuted = isMicMuted
    user.isVolumeMuted = isVolumeMuted
    db.session.commit()
    # 更新PostureMonitor
    if phone in user_monitors:
        user_monitors[phone].update_voice_settings(is_muted=isVolumeMuted, interval_seconds=user.reminderFrequency or 2)

    print(f"用户 {phone} 设置已更新: 麦克风: {isMicMuted}, 音量: {isVolumeMuted}")
    socketio.emit('update_response', {'status': 'success', 'message': '设置已更新'}, room=phone)
    # # 更新用户的设置
    # if phone in users:
    #     users[phone]['isMicOn'] = isMicMuted
    #     users[phone]['isVolumeOn'] = isVolumeMuted
    #     print(f"用户 {phone} 设置已更新: 麦克风: {isMicMuted}, 音量: {isVolumeMuted}")
    #
    #     # 返回一个成功的消息
    #     emit('update_response', {'status': 'success', 'message': '设置已更新'})
    # else:
    #     emit('update_response', {'status': 'error', 'message': '用户不存在'})


# 语音功能
def generate_text():
    # 这里可以根据你的需求生成文本
    text = llm.get_sitting_posture_advice(IMAGE_PATH)
    textProcessed = llm.remove_markdown(text)
    print(text)
    print(llm.remove_markdown(text))
    return textProcessed


@socketio.on('getVoice')
def handle_get_voice():
    phone = session.get('phone')
    text = generate_text()
    process_audio(text, lambda audio: socketio.emit('voiceData', audio, room=phone))


# 版本2
# 处理视频帧并发送回前端
@socketio.on('video_frame')
def handle_video_frame(data):
    phone = session.get('phone')
    # 将前端发送的 base64 编码的图像解码
    global previous_timestamp
    socketio.emit('enterFrame', {'message': '进入video_frame函数'}, room=phone)
    data_url = data['frame']
    timestamp = data['timestamp']  # 获取时间戳
    if 'data:image/jpeg;base64,' not in data_url:
        print("Invalid image data format.")
        return
    img_data = base64.b64decode(data_url.split('data:image/jpeg;base64,')[1])
    np_img = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    # 设置时间戳容忍度，容忍小的时间戳差异（比如 10 毫秒以内的差异视作有效）
    timestamp_tolerance = 10  # 容忍的时间戳差异，单位是毫秒
    # 使用 MediaPipe 进行人体姿态检测
    # 处理每一帧
    if (timestamp > previous_timestamp or
            (previous_timestamp - timestamp) < timestamp_tolerance):  # previous_timestamp 是上一次的时间戳
        previous_timestamp = timestamp
        # 使用锁来保证单线程执行 pose.process
        with lock:
            processed_frame = process_frame(frame)
            print(timestamp)
            print("成功处理一帧")
    else:
        print("Received a frame with an invalid timestamp.")
        return  # 直接返回不处理该帧
    # processed_frame = process_frame(frame)
    # 将处理后的图像编码为 JPEG
    _, buffer = cv2.imencode('.jpg', processed_frame)
    frame_bytes = buffer.tobytes()
    # 将图像转换为 base64 字符串
    frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
    # 将处理后的图像返回给前端
    socketio.emit('processed_frame', {'frame': frame_base64, 'timestamp': timestamp}, room=phone)
    print('已发送processed_frame')


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    phone = request.args.get('token')

    if phone:
        session['phone'] = phone
        join_room(phone)
        print(f"用户 {phone} 已连接并加入房间 {phone}")
        user = db.session.query(User).filter_by(phone=phone).first()
        # 将用户加入特定房间（可以使用用户的 phone 作为房间名）
        socketio.emit('init_setting', {
            'isMicMuted': user.isMicMuted,
            'isVolumeMuted': user.isVolumeMuted,
        }, room=phone)


@app.route("/api/conversations", methods=["GET"])
def get_conversations():  # edit: 新增接口
    # user_id = int(request.args.get("user_id"))
    phone = request.args.get("phone")
    print("触发了conversations,phone=", phone)
    conversations = mongodb["conversations"]
    cursor = conversations.find({"phone": phone}).sort("updated_at", -1)
    result = []
    for convo in cursor:
        print(f"[MongoDB] 读取到会话：{convo.get('title', '无标题')}，更新时间：{convo.get('updated_at')}")
        result.append({
            "conversation_id": convo["conversation_id"],
            "title": convo["title"],
            "updated_at": convo["updated_at"].isoformat()
        })
    return jsonify(result)


@app.route('/api/conversations/create', methods=['POST'])
def create_conversation():
    data = request.json
    phone = data.get("phone")
    title = data.get("title")
    conversations = mongodb["conversations"]
    user = conversations.find_one({"phone": phone})
    user_id = user["user_id"]
    last = conversations.find_one(
        {"phone": phone},
        sort=[("conversation_id", -1)]
    )
    last_id = last["conversation_id"] if last else 0
    new_conversation = {
        "user_id": user_id,
        "phone": phone,
        "conversation_id": last_id + 1,
        "title": title,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "messages": []
    }

    conversations.insert_one(new_conversation)
    # 打印插入后的所有数据
    print("\n 当前 conversations 中的所有数据：")
    for doc in conversations.find():
        print(doc)
    print("插入成功conversations，conversation_id=", last_id+1)
    return jsonify({"status": "success", "message": "创建成功",
                    "conversation_id": new_conversation["conversation_id"]}), 200


@app.route('/api/conversations/delete', methods=['POST'])
def delete_conversation():
    data = request.json
    phone = data.get("phone")
    conversation_id = int(data.get("conversation_id"))
    conversations = mongodb["conversations"]
    result = conversations.delete_one({"phone": phone, "conversation_id": conversation_id})
    print("删除成功,phone=,conversation_id=,", phone, conversation_id)
    # 打印插入后的所有数据
    print("\n 当前 conversations 中的所有数据：")
    for doc in conversations.find():
        print(doc)
    if result.deleted_count == 0:
        print("result.deleted_count = ", result.deleted_count)
        return jsonify({"error": "对话未找到"}), 404
    return jsonify({"message": "删除成功"}), 200


@app.route('/api/conversations/rename', methods=['POST'])
def rename_conversation():
    data = request.json
    phone = data.get("phone")
    conversation_id = data.get("conversation_id")
    new_title = data.get("title")

    conversations = mongodb["conversations"]
    result = conversations.update_one(
        {"phone": phone, "conversation_id": conversation_id},
        {"$set": {"title": new_title, "updated_at": datetime.utcnow()}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "对话未找到"}), 404
    return jsonify({"message": "重命名成功"}), 200


@app.route('/api/messages/history', methods=['GET'])
def get_messages():
    phone = request.args.get('phone')
    conversation_id = int(request.args.get('conversation_id'))
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    skip = (page - 1) * page_size
    conversations = mongodb["conversations"]
    conversation = conversations.find_one(
        {"phone": phone, "conversation_id": conversation_id},
        {"_id": 0, "messages": 1}  # 只返回 messages 字段
    )

    if conversation:
        sorted_messages = sorted(conversation.get("messages", []), key=lambda msg: msg.get("timestamp"))
        print("发送messages,sorted_messages=", sorted_messages)
        return jsonify({"messages": sorted_messages})
    else:
        return jsonify({"messages": []})


def append_messages_to_conversation(phone, conversation_id, new_messages):
    """
        给指定用户的某个会话追加消息。
        参数：
            user_id (int): 用户 ID
            conversation_id (int): 会话 ID
            new_messages (list): 要追加的消息列表（必须是两个）
        """
    if not isinstance(new_messages, list) or len(new_messages) != 2:
        print("❌ 错误：new_messages 必须是包含两条消息的列表")
        return
    conversations = mongodb["conversations"]

    # # 找到 user_id 对应的会话（你可以按需用 find_one 或多个）
    # conversation = conversations.find_one({"user_id": user_id})
    #
    # if not conversation:
    #     print(f"没找到 user_id={user_id} 的对话")
    #     return
    #
    # # 在原有 messages 列表中追加一条
    # conversations.update_one(
    #     {"_id": conversation["_id"]},  # 用 _id 是因为 user_id 可能重复
    #     {"$push": {"messages": new_message}}
    # )
    #
    # print(f"向 user_id={user_id} 的对话中添加了一条消息✅")
    result = conversations.update_one(
        {"phone": phone, "conversation_id": conversation_id},
        {"$push": {"messages": {"$each": new_messages}}}
    )

    if result.modified_count:
        print(f"✅ 成功为 phone={phone}, conversation_id={conversation_id} 追加了消息")
    else:
        print("⚠️ 未找到匹配的会话或未进行更新")

    # 打印插入后的所有数据
    print("\n 当前 conversations 中的所有数据：")
    for doc in conversations.find():
        print(doc)


new_msgs = [
    {"role": "user", "content": "坐太久会有什么危害？", "timestamp": datetime(2025, 4, 16, 15, 30, 20)},
    {"role": "assistant", "content": "长时间久坐会导致血液循环变慢，建议定期活动。", "timestamp": datetime(2025, 4, 16, 15, 30, 25)}
]


if __name__ == '__main__':
    # host='0.0.0.0': 指定了应用的主机地址为 0.0.0.0，这表示应用会监听所有可用的网络接口，而不仅仅是本地主机。
    # db_init()
    # mongodb_init()
    append_messages_to_conversation(phone="13800138000", conversation_id=1, new_messages=new_msgs)
    # app.run(port=5000,debug=True,host='0.0.0.0')
    socketio.run(app, host='localhost', port=5000, debug=True)
