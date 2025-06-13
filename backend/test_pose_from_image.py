import cv2
import mediapipe as mp
from detectPose import judge_head_tilt, judge_leg_cross,judge_tilt_forward_backward_sideview

def extract_landmarks_from_image(image_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True,  min_detection_confidence=0.5)

    image = cv2.imread(image_path)
    if image is None:
        print("图片读取失败，请检查路径。")
        return None, None

    # 转换颜色
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if not results.pose_landmarks:
        print("未检测到人体关键点")
        return None, image,None

    # 提取33个关键点
    landmarks = []
    for lm in results.pose_landmarks.landmark:
        landmarks.append({'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility})

    return landmarks, image, results.pose_landmarks

def draw_landmarks(image, pose_landmarks):
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    annotated_image = image.copy()
    mp_drawing.draw_landmarks(
        annotated_image,
        pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
        connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
    )
    return annotated_image


if __name__ == "__main__":
    image_path = "trainsetpic/t-54.jpg"  # 替换为你的图片路径
    landmarks, image,pose_landmarks  = extract_landmarks_from_image(image_path)

    if landmarks:
        head_status = judge_head_tilt(landmarks)
        tilt_status=judge_tilt_forward_backward_sideview(landmarks)
        leg_status = judge_leg_cross(landmarks)

        print(f"头部姿态：{head_status}")
        print(f"倾斜姿态：{tilt_status}")
        print(f"二郎腿状态：{leg_status}")

        # 可视化并展示
        annotated_image = draw_landmarks(image, pose_landmarks)
        cv2.imshow("Pose Landmarks", annotated_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()