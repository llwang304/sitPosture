<template>
  <div class="monitor-page"> 
    <van-nav-bar
        title="实时监测"
        left-text="返回"
        left-arrow
        @click-left="onClickLeft"
    />
    <div class="monitor-container">
      <userBar/>
      <van-tabs v-model:active="active" class="monitor-tabs">
        <van-tab title="图片模式">
          <PoseComponentImg/>
        </van-tab>
        <van-tab title="视频模式">
          <PoseComponentVid/>
        </van-tab>
      </van-tabs>
      <!-- <PoseComponent/> -->
    </div>
  
  </div>
</template>

<script setup>

import PoseComponentImg from '../../components/PoseComponentImg.vue'
import PoseComponentVid from '../../components/PoseComponentVid.vue'
import userBar from '../../components/UserBar.vue'
import {ref,onMounted,reactive,getCurrentInstance,onUnmounted,computed} from 'vue';
import {useRouter} from 'vue-router'
import io from 'socket.io-client';
import socket from '../../utils/socketio.js'

const active=ref(0);
//-----------------navivBar返回上一页------------------
//获取router实例
  const router=useRouter()
const onClickLeft=()=>{
  history.back()
}
const userInfo=computed(()=>{
  return JSON.parse(localStorage.getItem('h5_userInfo'))||{}

})

//--------------------科大讯飞语音功能----------------
  const audioPlayer = ref(null);
  let audioContext;

  const getVoice = () => {
    console.log("调用getVoice")
    socket.emit('getVoice');
  };
  //audio标签+后端音频完整版
/*   socket.on('voiceData', (audioData) => {
    try{
      const blob = new Blob([audioData], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(blob);
      if (audioPlayer.value) {
        audioPlayer.value.src = audioUrl;
        audioPlayer.value.play();
      } else {
      console.error('audioPlayer is null');
      }
    }catch(error){
      console.error('播放音频时出错:', error);
    }
}); */


let isPlaying = false;  // 用于标识当前是否有音频在播放
let audioQueue = [];     // 存储待播放的音频片段

socket.on("voiceData", (audioData) => {
  // 将新的音频片段添加到队列中
  audioQueue.push(audioData);

  // 如果没有正在播放音频，开始播放队列中的音频
  if (!isPlaying) {
    playNextAudio();
  }
});

function playNextAudio() {
  if (audioQueue.length === 0) return; // 如果队列为空，停止播放

  // 获取队列中的下一个音频片段
  const audioData = audioQueue.shift();  // 取出队列中的第一个音频

  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const sampleRate = 16000;
  const numChannels = 1;

  // 将二进制 PCM 数据转换为 Float32 格式
  const pcmArray = new Int16Array(audioData);
  const audioBuffer = audioContext.createBuffer(numChannels, pcmArray.length, sampleRate);
  const floatArray = new Float32Array(pcmArray.length);
  for (let i = 0; i < pcmArray.length; i++) {
    floatArray[i] = pcmArray[i] / 32768;  // 归一化到 -1.0 ~ 1.0
  }

  audioBuffer.getChannelData(0).set(floatArray);

  // 播放音频
  const source = audioContext.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioContext.destination);

  // 音频播放完成后，开始播放下一个音频
  source.onended = () => {
    isPlaying = false;  // 标记当前音频播放完毕
    playNextAudio();    // 播放队列中的下一个音频
  };

  source.start();
  isPlaying = true;  // 标记当前有音频在播放
}


</script>

<style scoped>
body {
  margin: 0;
  height: 100%;
}
  .monitor-page{
    display: flex;
    flex-direction: column;
    height: 100vh; /* 直接设置为视口高度 */
    background-color: #f7f8fa; /* 浅灰色背景，与 VanUI 风格更搭 */
  }
  .monitor-container {
    display: flex;
    flex-direction: column;
    padding: 10px;
    flex-grow:1;
    overflow-y:auto;
   /* background: linear-gradient(180deg, rgb(211, 255, 236) 0%, 
   #a0e9ce89 50%, #ffffff 100%); */ /* 渐变背景 */
  }
  .monitor-tabs {
      margin-top: 0px; /* 与 userBar 拉开一些距离 */
      height: 100%;
    }
</style>