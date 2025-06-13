<template>
  <div class="chat-page">
    <van-nav-bar title="健康助手" left-arrow @click-left="onClickLeft" >
      <template #right>
        <van-icon name="bars"  size="18" @click="toggleSidebar"/>
      </template>
    </van-nav-bar>

    <Sidebar2
        :key="dialogs.length"
        :items="conversations"
        v-model="activeDialogIndex"
        @createNewDialog="newConversation"
        @deleteDialog="handleDeleteConversation"
        @renameDialog="handleRenameConversation"
        v-show="isSidebarOpen"
        :style="{
        position: 'fixed',
        top: '46px', // 导航栏高度
        right: 0,
        height: 'calc(100vh - 46px)', // 剩余高度
        transform: isSidebarOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.3s ease',
      }"
      />

    <div class="chat-content">
      <div v-for="(message, index) in currentDialogMessages" :key="index" :class="message.role === 'user' ? 'user' : 'assistant'">
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
   <!--  <van-popup v-model:show="showRenameDialog" position="center">
      <van-field v-model="renameDialogTitle" label="对话标题" placeholder="请输入新的对话标题" />
      <div style="padding: 16px;">
        <van-button type="primary" block @click="confirmRenameDialog">确认</van-button>
      </div>
    </van-popup> -->
  </div>
</template>

<script setup>
import { ref,onMounted,onUnmounted,reactive,getCurrentInstance,computed} from 'vue';
import { useRouter } from 'vue-router';
import io from 'socket.io-client';
import socket from '../utils/socketio.js'
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { showConfirmDialog } from 'vant';

const { proxy } = getCurrentInstance()
const router = useRouter();
const message = ref('');
const messages = ref([]);
const loading = ref(false); // 新增 loading 状态
//const socket = io('http://localhost:5000');
const assistantAvatar='/images/ai_avatar.png'

const loadHistory=async()=>{
  try {
    //const response = await axios.get('/api/history');
    const response = await api.loadHistory();
    messages.value = response.data.history;
  } catch (error) { 你
    console.error('Error fetching history:', error);
  }
}


onMounted(() => {
  socket.connect();
  socket.on('chat_response', (data) => {
    console.log('收到回复：', data);
    dialogs.value[activeDialogIndex.value].messages.push({ role: 'user', content: message.value });
    //messages.value.push({ role: 'assistant', content: data.content });
    loading.value = false;
  });
  fetchConversations ();
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
    //messages.value.push({ role: 'user', content: message.value });
    dialogs.value[activeDialogIndex.value].messages.push({ role: 'user', content: message.value });
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
import Sidebar from './SideBar.vue'; // 导入侧边栏组件
import Sidebar2 from './SideBar2.vue'; // 导入侧边栏组件
//侧边栏开闭
const isSidebarOpen = ref(false);
const onClickLeft = () => {
  router.back();
};
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

//侧边栏功能
const activeDialogIndex = ref(0);
const conversations=ref([])
const dialogs = ref([
  { 
    title: '对话 1', messages: [
      { role: 'user', content: '我的工作需要长时间坐着，如何保持正确的坐姿？' },
      { role: 'assistant', content: '请保持背部挺直，避免长时间低头，并定期起身活动。' }
    ] 
  },
  { 
    title: '对话 2', messages: [
      { role: 'user', content: '翘二郎腿有什么危害？' },
      { role: 'assistant', content: '翘二郎腿可能会导致脊柱侧弯' }
    ] 
  }
  ]);
const currentDialogMessages = computed(() => {
  if (dialogs.value[activeDialogIndex.value]) {
    return dialogs.value[activeDialogIndex.value].messages;
  }else{
    return [];
  }
});
/* const newDialog = () => {
  dialogs.value.push({ title: `对话 ${dialogs.value.length + 1}`, messages: [] });
  console.log('newdialog后activeDialogIndex:', activeDialogIndex.value); // 添加调试代码
}; */
const newDialog = () => {
  conversations.value.push({ title: `对话 ${conversations.value.length + 1}`, messages: [] });
  console.log('newdialog后activeDialogIndex:', activeDialogIndex.value); // 添加调试代码
};
const newConversation = async() => {
  const phone = JSON.parse(localStorage.getItem("h5_userInfo")).phone;
  const newTitle = `对话 ${conversations.value.length + 1}`;
  try {
    const res = await proxy.$api.createConversation({ phone, title: newTitle });
    conversations.value.push({
      conversation_id: res.data.conversation_id,
      title: newTitle,
      updated_at: new Date().toISOString(),
    });
    activeDialogIndex.value = conversations.value.length - 1;
    console.log('newdialog后activeDialogIndex:', activeDialogIndex.value); // 添加调试代码
  } catch (error) {
    console.error('新建对话失败', error);
  }
  //conversations.value.push({ title: `对话 ${conversations.value.length + 1}`, messages: [] }); 
};

/* const handleDeleteDialog = (index) => {
  const result=showConfirmDialog({
    title: '删除对话',
    message: '确定要删除该对话吗？',
  })
    .then(() => {
      // 用户点击确认，删除对话
      dialogs.value.splice(index, 1);
      // 如果删除的是当前选中的对话，则更新 activeDialogIndex
      if (activeDialogIndex.value === index) {
        activeDialogIndex.value = 0;
      } else if (activeDialogIndex.value > index) {
            // 如果删除的是当前选中对话之前的对话，则需要将 activeDialogIndex 减 1
            activeDialogIndex.value--;
        }
      console.log('dialogs after rename',dialogs)
      console.log('删除后activeDialogIndex:', activeDialogIndex.value); // 添加调试代码
    })
    .catch((action)=>{
      console.log('action',action)
    });
}; */

//16:45版本
const handleDeleteDialog = (index) => {
  showConfirmDialog({
    title: '删除对话',
    message: '确定要删除该对话吗？',
  })
    .then(() => {
      dialogs.value.splice(index, 1);

      if (activeDialogIndex.value === index) {
        activeDialogIndex.value = Math.max(0, dialogs.value.length - 1);
      } else if (activeDialogIndex.value > index) {
        activeDialogIndex.value--;
      }
      console.log('dialogs after delete', dialogs.value);
      console.log('删除后activeDialogIndex:', activeDialogIndex.value);
    })
    .catch((action) => {
      console.log('action', action);
    });
};

const handleDeleteConversation = async (index) => {
  const conversationId = conversations.value[index].conversation_id;

  showConfirmDialog({
    title: '删除对话',
    message: '确定要删除该对话吗？',
  })
    .then(async () => {
      try {
        const phone = JSON.parse(localStorage.getItem("h5_userInfo")).phone;
        await proxy.$api.deleteConversation({ phone, conversation_id: conversationId });
        conversations.value.splice(index, 1);

        if (activeDialogIndex.value === index) {
          activeDialogIndex.value = Math.max(0, conversations.value.length - 1);
        } else if (activeDialogIndex.value > index) {
          activeDialogIndex.value--;
        }
      } catch (err) {
        console.error('删除对话失败', err);
      }
    })
    .catch((action) => {
      console.log('action', action);
    });
};

//重命名对话功能
const showRenameDialog = ref(false);
const renameDialogTitle = ref('');
const renameDialogIndex = ref(-1);


const handleRenameDialog = (index, newTitle) => {
  dialogs.value[index].title = newTitle;
  console.log('重命名后activeDialogIndex:', activeDialogIndex.value);
  console.log('重命名后dialogs:', dialogs.value);
};

const confirmRenameDialog = () => {
  if (renameDialogTitle.value.trim() !== '') {
    dialogs.value[renameDialogIndex.value].title = renameDialogTitle.value;
    showRenameDialog.value = false;
  } else {
    Toast('对话标题不能为空');
  }
};
 
const handleRenameConversation = async (index, newTitle) => {
  const conversationId = conversations.value[index].conversation_id;
  const phone = JSON.parse(localStorage.getItem("h5_userInfo")).phone;
  try {
    await proxy.$api.renameConversation({ phone,conversation_id: conversationId, title: newTitle });
    conversations.value[index].title = newTitle;
    console.log("conversation=",conversations)
  } catch (err) {
    console.error('重命名对话失败', err);
  }
};






//------------------与后端接口--------------------------
// edit: 加载对话列表
const fetchConversations = async () => {
  try {
    const phone= JSON.parse(localStorage.getItem("h5_userInfo")).phone
    const res = await proxy.$api.getconversations({ phone });

    //const res = await axios.get(`/api/conversations?phone=${phone}`);
    conversations.value = res.data;
    console.log("conversations",conversations.value)
    // 默认加载第一个会话的 message
    /* if (conversations.value.length > 0) {
      activeConversationId.value = conversations.value[0].conversation_id;
      loadMessagesForConversation(activeConversationId.value);
    } */
  } catch (err) {
    console.error("加载会话失败", err);
  }
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