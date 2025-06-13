import request from '../utils/request'
import socket from '../utils/socketio'

export default{
  //用户登录
  login(data){
    return request.post('/login',data)
  },
  //重置密码
  resetPassword(data){
    return request.post('/resetPassword',data)
  },
  //用户注册
  register(data){
    return request.post('/register',data)
  },
  //首页数据
  index(){
    return request.get('/Index/index')
  },
  //聊天功能
  chat(data){
    return request.post('/chat',data)
  },

  //-----------monitor.vue--------------

  //发送视频，(弃用)
  sendVideoFrame(dataURL) {
    socket.emit('video_frame', dataURL);
  },
  updateVolumn(data){
    return request.post('/update_settings',data);
  },
  //获取个人资料信息
  getUserInfo(){
    return request.get('/getUserInfo');
  },
  //更新个人资料信息
  updateInfo(data){
    return request.post('/updateUserInfo',data);
  },
  //获取历史聊天记录（弃用）
  LoadHistory(){
    return request.get('/loadHistory');
  },

  //发送信息
  sendUserMessage(data){
    console.log('发送消息：', data); // 添加这行
    socket.emit('receiveUserMessage', data);
  },

  //获取会话
  getconversations(params){
    return request.get('/api/conversations', { params });
  },
  // 创建对话
  createConversation(data){
    return request.post('/api/conversations/create', data);
  },

  // 删除对话
  deleteConversation(data){
    return request.post('/api/conversations/delete', data);
  },

  // 重命名对话
  renameConversation(data){
    return request.post('/api/conversations/rename', data);
  },
  getMessagesHistory(params){
    return request.get('/api/messages/history', {params});
  },
  //stat
  sendDateRange(data){
    return request.post('/dateRange',data);
  }
  //
} 