# @app.route('/chat', methods=['GET','POST'])
# # @socketio.on('chat')
# @token_required
# def chat():
#     print('进入chat函数')
#     try:
#         data = request.json
#         print(data)
#         user_message = data.get('content')
#         description=describe_user_info(users)
#         response=asyncio.run(llm.get_gemini_response(user_message,description))
#         if response["success"]:
#             # 操作成功，获取回复内容
#             reply = response["content"]
#             print("回复：", reply)
#             # 将 reply 发送给用户
#             return jsonify({
#                     "success": True,
#                     "content": reply,
#                     # "history": messages + [{"role": "assistant", "content": ai_response}]
#             })
#         else:
#             # 操作失败，获取错误信息
#             error_message = response["content"]
#             print("错误：", error_message)
#             # 处理错误信息
#             return jsonify({
#                 "success": False,
#                 "content": error_message,
#                 # "history": messages + [{"role": "assistant", "content": ai_response}]
#             })
#
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "content": f"请求失败：{str(e)}"
#         }), 500


# # 启动摄像头并发送视频帧
# @socketio.on('connect')
# def handle_connect():
#     print('客户端已连接')
#
#     # 启动摄像头
#     cap = cv2.VideoCapture(0)
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         # 处理每一帧
#         frame = process_frame(frame)
#
#         # 将图像转为字节流并发送给前端
#         _, buffer = cv2.imencode('.jpg', frame)
#         frame_data = buffer.tobytes()
#         emit('video_frame', frame_data)
#
#         time.sleep(0.03)  # 30 FPS
#
#     cap.release()


# 版本1
# # 处理视频帧并发送回前端
# @socketio.on('video_frame')
# def handle_video_frame(data):
#     # 将前端发送的 base64 编码的图像解码
#     img_data = base64.b64decode(data.split('data:image/jpeg;base64,')[1])
#     np_img = np.frombuffer(img_data, np.uint8)
#     frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
#
#     # 使用 MediaPipe 进行人体姿态检测
#     # 处理每一帧
#     processed_frame = process_frame(frame)
#
#     # 将处理后的图像编码为 JPEG
#     _, buffer = cv2.imencode('.jpg', processed_frame)
#     frame_bytes = buffer.tobytes()
#
#     # 将图像转换为 base64 字符串
#     frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
#
#     # 将处理后的图像返回给前端
#     emit('processed_frame', {'frame': frame_base64})


# return jsonify({
#     "username": user.username,
#     "avatar": user.avatar,
#     "health_info": {
#         "name": health_info.name,
#         "gender": health_info.gender,
#         "birthday": health_info.birthday,
#         "age": health_info.age,
#         "height": health_info.height,
#         "weight": health_info.weight,
#         "occupation": health_info.occupation,
#         "spineHealth": health_info.spineHealth,
#         "exerciseHabit": health_info.exerciseHabit,
#         "sittingStyle": health_info.sittingStyle,
#         "sittingTime": health_info.sittingTime,
#         "healthGoal": health_info.healthGoal,
#         "reminderFrequency": health_info.reminderFrequency,
#         "otherInfo": health_info.otherInfo
#     }
# })


# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.get_json()
#     return jsonify({
#         "status": "success",
#         "message": "好的，我将作为您的健康助理，请您将想咨询的问题告诉我，我将为您解决",
#
#     }), 200
