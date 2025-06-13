<template>
  <div class="chat-page">
    <van-nav-bar title="健康助手" left-arrow @click-left="onClickLeft" >
      <template #right>
        <van-icon name="bars"  size="18" @click="toggleSidebar"/>
      </template>
    </van-nav-bar>

    <!-- <van-sidebar  v-show="isSidebarOpen" v-model=" isSidebarOpen ">
      <template #title> 
        <van-button type="primary"> 新建新对话</van-button>
      </template>
      <van-sidebar-item title="标签名称" />
      <van-sidebar-item title="标签名称" />
      <van-sidebar-item title="标签名称" />
    </van-sidebar> -->
    <!-- <div class="sidebar" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="search-bar">
        <input type="text" v-model="summary" placeholder="总结" readonly />
      </div>
      <div class="dialog-list">
        <div v-for="(dialog, index) in dialogs" :key="index" class="dialog-item">
          {{ dialog.title }}
          <button @click="deleteDialog(index)">删除</button>
        </div>
      </div>
      <button @click="newDialog">新建对话</button>
    </div> -->

    <div class="chat-content">
      <div v-for="(message, index) in messages" :key="index" :class="message.role === 'user' ? 'user' : 'assistant'">
        <van-image v-if="message.role === 'assistant'" round width="30" height="30" :src="assistantAvatar" />
        <div class="message-bubble" :style="{ backgroundColor: message.role === 'user' ? '#333' : '#f0f0f0', color: message.role === 'user' ? 'white' : 'black' }">
          <div v-if="message.role === 'assistant'" v-html="renderedMarkdown(message.content)"></div>
          <div v-else>{{ message.content}}</div>
          <div class="message-time" v-if="message.time">{{ message.time }}</div>
        </div>
      </div>
      <div v-if="loading" class="loading-container">
        <van-loading type="spinner" />
        <span style="margin-left: 8px;">正在思考中...</span>
      </div>
    </div>
    <div class="chat-input">
      <van-field v-model="message" placeholder="Message..." />
      <!-- <van-icon name="send-o" @click="sendMessage"/> -->
      <van-button plain type="primary" @click="sendMessage">发送</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref,onMounted,onUnmounted,reactive,getCurrentInstance} from 'vue';
import { useRouter } from 'vue-router';
import socket from '../utils/socketio.js'
//import { initializeApp } from 'firebase/app';
//import { getDatabase, ref as dbRef, onValue, push, set } from 'firebase/database';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const firebaseConfig = {
  // 替换为您的 Firebase 配置
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  databaseURL: "YOUR_DATABASE_URL",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const { proxy } = getCurrentInstance()
const router = useRouter();
const message = ref('');
const messages = ref([]);
const loading = ref(false); // 新增 loading 状态

const assistantAvatar='/images/ai_avatar.png'

const loadHistory=async()=>{
  try {
    //const response = await axios.get('/api/history');
    const response = await api.loadHistory();
    messages.value = response.data.history;
  } catch (error) {
    console.error('Error fetching history:', error);
  }
}


onMounted(() => {
  socket.connect(); 
  socket.on('chat_response', (data) => {
    console.log('收到回复：', data);
    messages.value.push({ role: 'assistant', content: data.content });
    loading.value = false;
  });
});
/* //http版本
const sendMessage = async() => {
  if (message.value.trim() !== '') {
    messages.value.push({ role: 'user', content: message.value });
    const response =await proxy.$api.chat({ role: 'user', content: message.value });
    //const responseData=response.json()
    console.log('response',response)
    messages.value.push({ role: 'assistant', content: response.data.content});
    //socket.emit('chat', { message: message.value });
    console.log('sendmessage success, messages are ',messages)
    message.value = '';
  }
}; */
//socketio版本
const sendMessage = async() => {
  if (message.value.trim() !== '') {
    messages.value.push({ role: 'user', content: message.value });
    proxy.$api.sendUserMessage({ role: 'user', content: message.value });
    console.log({ role: 'user', content: message.value });//添加调试代码
    message.value = '';
    loading.value = true;

    //const response =await proxy.$api.chat({ role: 'user', content: message.value });
    //const responseData=response.json()
    /* console.log('response',response)
    messages.value.push({ role: 'assistant', content: response.data.content});
    //socket.emit('chat', { message: message.value });
    console.log('sendmessage success, messages are ',messages)
    message.value = ''; */
  }
};

onUnmounted(() => {
  // 组件卸载时关闭 WebSocket 连接
  socket.disconnect();
});

const renderedMarkdown = (markdown) => {
  const html = marked(markdown);
  return DOMPurify.sanitize(html);
};


//----------------------页头和侧边栏----------------------------
const isSidebarOpen = ref(false);
const onClickLeft = () => {
  router.back();
};

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

</script>

<style lang="less" scoped>
  .chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.sidebar-button {
  position: absolute;
  top: 10px;
  right: 10px;
  cursor: pointer;
  font-size: 20px;
}
//---------------------侧边栏-------------------------
.sidebar {
  position: absolute;
  top: 0;
  right: -300px;
  width: 300px;
  height: 100vh;
  background-color: #f0f0f0;
  transition: right 0.3s ease;
  padding: 20px;
}

.sidebar-open {
  right: 0;
}

.search-bar {
  margin-bottom: 20px;
}

.search-bar input {
  width: 100%;
  padding: 10px;
}

.dialog-list {
  margin-bottom: 20px;
}

.dialog-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border-bottom: 1px solid #ccc;
}


//----------------------对话内容相关--------------------
.chat-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.user,
.assistant {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
}

.user {
  justify-content: flex-end;
}

.assistant {
  justify-content: flex-start;
}

.message-bubble {
  padding: 8px 12px;
  border-radius: 16px;
  max-width: 70%;
  word-wrap: break-word;
  margin: 0 8px;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.chat-input {
  display: flex;
  align-items: center;
  padding: 8px;
  border-top: 1px solid #eee;
}

.chat-input .van-field {
  flex: 1;
  margin-right: 8px;
}

/* 加载提示样式 */
.loading-container {
  position: absolute; /* 绝对定位 */
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* 居中显示 */
  display: flex;
  align-items: center;
  color: #999;
}
</style>