import time

# 全局状态缓存
last_bad_posture_time = None
last_record_time = 0
pose_cache = []

# 倾向判断函数
# def detect_tilt_fb(landmarks):
#     """
#     根据关键点 Z 坐标判断人体是前倾、直立还是后仰
#     返回: 'forward' | 'upright' | 'backward'
#     """
#     try:
#         nose_z = landmarks[0]['z']
#         shoulder_z = (landmarks[11]['z'] + landmarks[12]['z']) / 2
#         hip_z = (landmarks[23]['z'] + landmarks[24]['z']) / 2
#         upper_body_z = (shoulder_z + hip_z) / 2
#
#         dz = nose_z - upper_body_z
#
#         # 阈值根据实际情况微调（假设单位为米）
#         if dz < -0.1:
#             return 'forward'
#         elif dz > 0.1:
#             return 'backward'
#         else:
#             return 'upright'
#     except (IndexError, KeyError, TypeError):
#         return 'invalid'

import math

def calculate_angle(p1, p2):
    """
    计算两点连线与竖直线的夹角（单位：度）
    p1, p2 是 dict，包含 x, y, z 三个坐标，侧面摄像头 x 轴为左右，y 轴为垂直
    """
    # 计算向量 p1->p2
    dx = p2['x'] - p1['x']
    dy = p2['y'] - p1['y']

    # 竖直向量（0, 1）
    # 计算向量与竖直线夹角，利用点积公式
    dot = dy  # p1->p2 dot (0,1) = dy*1 + dx*0 = dy
    mag_v = math.sqrt(dx*dx + dy*dy)
    mag_vertical = 1

    if mag_v == 0:
        return 0

    cos_angle = dot / (mag_v * mag_vertical)
    angle_rad = math.acos(min(1, max(-1, cos_angle)))  # 防止浮点误差
    angle_deg = math.degrees(angle_rad)

    return angle_deg
def calculate_angle_2d(p1, p2):
    """
    计算2D点p1到p2向量与竖直方向(y轴正方向)的夹角，单位：度，取绝对值。
    """
    dx = p2['x'] - p1['x']
    dy = p2['y'] - p1['y']
    angle_rad = math.atan2(dx, dy)  # 注意这里是dx在前，dy在后，求与y轴夹角
    angle_deg = math.degrees(angle_rad)
    return abs(angle_deg)


def judge_tilt_forward_backward_sideview(landmarks):
    """
    基于侧面摄像头的姿态关键点，判断前倾、后仰、直立
    主要用x,y坐标，不用z轴
    """
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    # 颈部取两个肩膀x,y均值
    neck = {
        'x': (left_shoulder['x'] + right_shoulder['x']) / 2,
        'y': (left_shoulder['y'] + right_shoulder['y']) / 2
    }

    left_hip = landmarks[23]
    right_hip = landmarks[24]

    hip = {
        'x': (left_hip['x'] + right_hip['x']) / 2,
        'y': (left_hip['y'] + right_hip['y']) / 2
    }

    angle = calculate_angle_2d(neck, hip)

    forward_thresh = 15  # 角度阈值，可调
    backward_thresh = 5

    # 判断方向
    if angle > forward_thresh and neck['x'] > hip['x']:
        return 'forward'  # 前倾，头肩往前偏
    elif angle > forward_thresh and neck['x'] < hip['x']:
        return 'backward'  # 后仰，头肩往后偏
    else:
        return 'upright'

def judge_head_tilt(landmarks):
    """
    基于侧面摄像头的鼻子和颈部关键点，判断头部前倾/后仰/直立
    输入 landmarks 是33个关键点字典列表
    返回 'forward' / 'backward' / 'upright'
    """
    nose = landmarks[0]
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    # 颈部点取两肩中点
    neck = {
        'x': (left_shoulder['x'] + right_shoulder['x']) / 2,
        'y': (left_shoulder['y'] + right_shoulder['y']) / 2
    }

    angle = calculate_angle_2d(nose, neck)

    forward_thresh = 15  # 头部前倾角度阈值（度）
    backward_thresh = 7  # 头部后仰角度阈值（度）

    # 判断头部前倾还是后仰
    if angle > forward_thresh and nose['x'] > neck['x']:
        return 'forward'  # 鼻子相对于颈部向前偏
    elif angle > backward_thresh and nose['x'] < neck['x']:
        return 'backward'  # 鼻子相对于颈部向后偏
    else:
        return 'upright'

def judge_leg_cross(landmarks):
    left_knee = landmarks[25]
    right_knee = landmarks[26]
    left_ankle = landmarks[27]
    right_ankle = landmarks[28]

    knee_diff = left_knee['y'] - right_knee['y']
    ankle_diff = left_ankle['y'] - right_ankle['y']
    ankle_x_diff = abs(left_ankle['x'] - right_ankle['x'])

    height_threshold = 0.05
    overlap_threshold = 0.02  # 越小越重叠

    # 强化条件：不仅高度差大，还需要靠得近
    if ankle_x_diff < overlap_threshold:
        if ankle_diff < -height_threshold:
            return 'left'
        elif ankle_diff > height_threshold:
            return 'right'

    # 退而求其次，只判断高度差
    if knee_diff < -height_threshold or ankle_diff < -height_threshold:
        return 'left'
    elif knee_diff > height_threshold or ankle_diff > height_threshold:
        return 'right'
    else:
        return 'none'


def evaluate_posture(head, leg, torso):
    """简单判断good / bad"""
    if head == "upright" and torso == "upright" and leg == "none":
        return "good"
    return "bad"


def judge_posture(landmarks):
    head_state=judge_head_tilt(landmarks)
    leg_state=judge_leg_cross(landmarks)
    torso_state=judge_tilt_forward_backward_sideview(landmarks)

    overall_state=evaluate_posture(head_state, leg_state, torso_state)
    state = {
        "head": head_state,
        "torso": torso_state,
        "leg": leg_state,
        "overall": overall_state
    }
    return state

