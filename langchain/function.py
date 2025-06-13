from flask_sqlalchemy import SQLAlchemy
from app import *
from database import *


def describe_user_info(phone):
    """
    将用户信息字典转换成一段中文描述。

    Args:
        phone: 用户电话
    Returns:
        str: 中文描述字符串。
    """
    user = db.session.query(User).filter_by(phone=phone).first()
    print("describeuserinfo phone=",phone)
    health = user.health_info
    description = (
        f"用户 {user.username}，手机号 {user.phone}，是一名 {health.gender} 性，出生于 {health.birthday}，今年 {health.age} 岁。"
        f"他的身高为 {health.height} 厘米，体重为 {health.weight} 公斤，职业是 {health.occupation}。"
        f"他的脊柱健康状况为 {health.spineHealth}，锻炼习惯是 {health.exerciseHabit}。"
        f"他的坐姿是 {health.sittingStyle}，每天坐着的时间大约为 {health.sittingTime} 小时。"
        f"他的健康目标是 {health.healthGoal}，提醒频率为 {health.reminderFrequency}。"
        f"其他信息:{health.otherInfo}。"
    )
    print(description)
    return description

def insert_health_info_for_13700137000():
    user = User.query.filter_by(phone='13700137000').first()
    if not user:
        print("用户不存在")
        return

    # 检查是否已有 HealthInfo，防止重复插入
    if user.health_info:
        print("该用户已存在健康信息，跳过插入")
        return

    user_info = HealthInfo(
        user=user,
        name='露露',
        gender='女',
        birthday='1998-09-20',
        age=26,
        height=162,
        weight=52,
        occupation='设计师',
        spineHealth='轻度驼背',
        exerciseHabit='每周瑜伽2次，散步3次',
        sittingStyle='偏向前倾',
        sittingTime=8,
        healthGoal='缓解腰背酸痛，提高专注力',
        reminderFrequency='每45分钟',
        otherInfo='近期刚换了工学椅，希望评估其效果。'
    )

    db.session.add(user_info)
    db.session.commit()
    print("健康档案信息插入完成")


def fill_healthinfo_for_13700137000():
    user = User.query.filter_by(phone='13700137000').first()
    if not user:
        print("用户不存在")
        return

    # 如果该用户已有 HealthInfo，更新它
    if user.health_info:
        hi = user.health_info
        print("已存在 HealthInfo，进行补全...")
    else:
        hi = HealthInfo(user=user)
        db.session.add(hi)
        print("未存在 HealthInfo，新建...")

    hi.name = '李四'
    hi.gender = '女'
    hi.birthday = '1990-08-25'
    hi.age = 34
    hi.height = 160
    hi.weight = 52
    hi.occupation = '设计师'
    hi.spineHealth = '一般'
    hi.exerciseHabit = '每周两次瑜伽'
    hi.sittingStyle = '偏左倾斜'
    hi.sittingTime = 8
    hi.healthGoal = '改善腰背酸痛'
    hi.reminderFrequency = '每两小时'
    hi.otherInfo = '平时久坐较多，希望了解办公室坐姿改善建议。'

    db.session.commit()
    print("更新完成！")

if __name__ == "__main__":
    with app.app_context():
        print(describe_user_info(13700137000))
        # insert_health_info_for_13700137000()
        # fill_healthinfo_for_13700137000()