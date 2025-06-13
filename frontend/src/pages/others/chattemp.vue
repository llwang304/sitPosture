<template>
  <div class="chat-container">
    <!-- 对话展示区域 -->
    <div class="message-area">
      <div 
        v-for="(msg, index) in messages" 
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="content">{{ msg.content }}</div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <input 
        v-model="inputMessage"
        @keyup.enter="sendMessage"
        :disabled="isLoading"
      />
      <button 
        @click="sendMessage"
        :disabled="isLoading"
      >
        {{ isLoading ? '发送中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import {onMounted,ref,reactive,computed,getCurrentInstance} from 'vue'
const {proxy} =getCurrentInstance()//获取当前 Vue 组件实例的代理对象

// 输入框输入值
const inputMessage = ref('');
// 消息列表
const messages = ref([]);
// 加载状态
const isLoading = ref(false);
// API 请求地址
const apiUrl = ref('http://localhost:5000/chat');

// 发送消息方法
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return;

  isLoading.value = true;

  // 添加用户消息到消息列表
  messages.value.push({
    role: 'user',
    content: inputMessage.value
  });

  try {
    /* const response = await axios.post(apiUrl.value, {
      message: inputMessage.value
    }); */
    const response=await proxy.$api.chat({
      message: inputMessage.value
    })
    if (response.data.status === 'success') {
      // 添加助手消息到消息列表
      messages.value.push({
        role: 'assistant',
        content: response.data.message
      });
      console.log('success')
    }
  } finally {
    inputMessage.value = '';
    isLoading.value = false;
    scrollToBottom();
  }
};

// 滚动到消息区域底部方法
const scrollToBottom = () => {
  setTimeout(() => {
    const container = document.querySelector('.message-area');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, 0);
};
</script>

<style lang="less" scoped>
.chat-container {
  max-width: 600px;
  margin: 20px auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
}

.message-area {
  height: 400px;
  overflow-y: auto;
  margin-bottom: 15px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 5px;
}

.message {
  margin: 10px 0;
  padding: 8px 12px;
  border-radius: 15px;
  max-width: 80%;
}

.message.user {
  background: #e3f2fd;
  margin-left: auto;
}

.message.assistant {
  background: #fff;
  border: 1px solid #eee;
}

.input-area {
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 8px 15px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}
</style>