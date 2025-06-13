<template>
  <div class="user-info-card">
      <img src="/images/user1.jpg" alt="User Avatar" class="avatar" />
      <div class="user-details">
        <p class="greeting">你好！</p>
        <p class="username">张三</p>
      </div>
      <div class="user-actions">
        <div class="icon-button" @click="toggleMic">
          <img :src="micIcon" class="icon" />
        </div>
        <div class="icon-button" @click="toggleVolume">
          <img :src="volumeIcon" class="icon" />
        </div>
        <div class="icon-button" @click="showPopup = true">
          <img :src="timeIcon" class="icon" />
        </div>

         <van-popup v-model:show="showPopup" position="top" round>
            <div class="popup-content">
              <h3>提醒设置</h3>
              <label>提醒间隔：</label>
              <select v-model="reminderFrequency" @change="updateSettings">
                <option :value="5">每5分钟</option>
                <option :value="10">每10分钟</option>
                <option :value="15">每15分钟</option>
              </select>
            </div>
          </van-popup>
      </div>
      
    </div>
</template>

<script setup>
import {ref,computed, onMounted} from "vue"
/* import io from 'socket.io-client';
const socket = io('http://localhost:5000');  */
import socket from '../utils/socketio.js'
const isMicMuted = ref(false);
const isVolumeMuted = ref(false);
const reminderFrequency = ref(10)  // 默认值为10分钟
const showPopup=ref(false)
const toggleMic = () => {
  const newState = !isMicMuted.value;
  isMicMuted.value = newState; 
  // 发送 WebSocket 消息
  socket.emit('update_settings', {
    phone: JSON.parse(localStorage.getItem("h5_userInfo")).phone,
    isMicMuted: newState,
    isVolumeMuted: isVolumeMuted.value
  });
  /* try {
    // 发送 WebSocket 消息
    socket.emit('update_settings', {
      phone: JSON.parse(localStorage.getItem("h5_userInfo")).phone,
      isMicOn: newState,
      isVolumeOn: isVolumeMuted.value
    });

    // 监听后端的响应
    socket.once('update_response', (response) => {
      if (response.status !== 'success') {
        // 如果后端返回失败，抛出异常并回滚
        throw new Error(response.message || '更新失败');
      }
      showToast({ message: '麦克风状态已更新', type: 'success' });
    });
  } catch (error) {
    // 回滚操作并显示失败提示
    isMicMuted.value = !newState;
    showToast({ message: error.message || '请求失败', type: 'fail' });
  } */

};
const toggleVolume = () => {
  const newState = !isVolumeMuted.value;
  isVolumeMuted.value = newState;
  // 发送 WebSocket 消息
  socket.emit('update_settings', {
    phone: JSON.parse(localStorage.getItem("h5_userInfo")).phone,
    isMicMuted: isMicMuted.value,
    isVolumeMuted: newState
  });
};
const micIcon = computed(() => {
  return isMicMuted.value ? '/icons/microphone-off.svg' : '/icons/microphone.svg';
});
const volumeIcon = computed(() => {
  return isVolumeMuted.value ? '/icons/bell-off.svg' : '/icons/bell.svg';
});
const timeIcon='/icons/time.svg';
onMounted(()=>{
  socket.on('init_setting',(data)=>{
      console.log("init_setting:",data)
      isMicMuted.value=data.isMicMuted
      isVolumeMuted.value=data.isVolumeMuted
    })
})
</script>

<style scoped lang="less">
  .user-info-card {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 24px;
  margin-right: 16px;
}

.user-details {
  flex: 1;
}

.greeting {
  font-size: 16px;
  margin: 0;
}

.username {
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.user-actions {
  display: flex;
  gap: 16px;
}
.icon-button {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  .icon{
    width:75%;
    height: 75%;
  }
}

</style>