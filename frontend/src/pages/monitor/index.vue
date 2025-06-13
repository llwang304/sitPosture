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
      <div class="camera-content">
        <div v-if="!isCameraOn" class="default-image-container">
          <img src="/images/defaultCamera.jpg" alt="Default Camera" class="default-image" />
        </div>
        <video ref="videoElement2" autoplay playsinline style="display: none;"></video>
        <canvas v-show="isCameraOn"  ref="videoCanvas" id="canvas" class="camera-canvas" ></canvas>
        <canvas v-show="!isCameraOn" ref="videoCanvas2" id="canvas2" class="camera-canvas" ></canvas>
        <van-button  type="primary"  @click="startCamera2" v-if="!isCameraOn" size="large" >开启摄像头2</van-button>
        <van-button  type="danger"  @click="stopCamera2" v-if="isCameraOn" size="large" >关闭摄像头2</van-button>
      </div>
      <div>
        <van-button  type="primary"  @click="getVoice" size="large" >获取语音</van-button>
       <!--  <audio ref="audioPlayer" controls></audio> -->
      </div>
    </div>
  </div>
</template>

<script setup>
  import userBar from '../../components/UserBar.vue'
  import {ref,onMounted,reactive,getCurrentInstance,onUnmounted,computed} from 'vue';
  import {useRouter} from 'vue-router'
  import io from 'socket.io-client';
  import socket from '../../utils/socketio.js'
  //获取当前vue实例
  const { proxy } = getCurrentInstance()
  //获取router实例
  const router=useRouter()
  //websocketio
  //const socket = io('http://localhost:5000'); 

  const userInfo=computed(()=>{
  return JSON.parse(localStorage.getItem('h5_userInfo'))||{}

})
  //-----------------navivBar返回上一页------------------
  const onClickLeft=()=>{
    history.back()
  }

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


  //---------------------摄像头--------------------------
  const videoElement = ref(null);
  const videoElement2 = ref(null);
  const videoCanvas=ref(null)
  const videoCanvas2=ref(null)
  const isCameraOn = ref(false);
  let stream =null;
  let frameRequestId = null; // 添加 frameRequestId 变量


  //-------------------发送帧并接收--------------------
  // 启动摄像头并接收视频帧
  const startCamera2 = async () => {
    console.log("启动摄像头");
    console.log(io.version);

    const confirmResult = await showConfirmDialog({
      title: '权限请求',
      message: '是否允许开启摄像头以进行运动识别？',
    });

    if (confirmResult) {
      try {
        // 启动视频流
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        //videoCanvas.value.srcObject = stream;
        //videoCanvas.value.style.display = 'block';
        isCameraOn.value = true;
        //创建一个隐藏的video元素，用于接受视频流
        const videoelement=document.createElement('video')
        videoelement.srcObject=stream
        videoelement.play();


        const sendFrame = () => { 
          if(!isCameraOn.value) return;
          const canvas = videoCanvas.value;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(videoelement, 0, 0, canvas.width, canvas.height);
          
          const dataURL = canvas.toDataURL('image/jpeg', 0.8);
          console.log(dataURL);
          const timestamp = performance.now();  // 当前时间戳
          //socket.emit('video_frame', dataURL);
          proxy.$api.sendVideoFrame({ frame: dataURL, timestamp: timestamp });
          frameRequestId=requestAnimationFrame(sendFrame);
        };
        // 启动帧捕获和发送
        sendFrame();
        console.log('sengframe被调用')
      } catch (error) {
        console.error('无法访问摄像头:', error);
      }
    }
  };

    // 停止摄像头并停止发送帧
  const stopCamera2 = () => {
    if (isCameraOn.value && stream) {
      // 停止摄像头视频流
      stream.getTracks().forEach(track => track.stop());
      isCameraOn.value = false;

      // 清除canvas上的内容
      const canvas = videoCanvas.value;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);  // 清空画布内容
      
      // 停止发送帧
      try{
        cancelAnimationFrame(frameRequestId);  // 取消帧捕获的动画帧请求
        console.log("摄像头已关闭，停止绘制");
      }catch(error){
        console.error("取消帧捕获失败",error)
      }  
    }
  };



  onMounted(()=>{
    socket.connect();
    // 监听后端返回的处理结果
    socket.on('enterFrame',(data)=>{
      console.log("enterFrame:",data.message)
    })
    socket.on('processed_frame', (data) => {
      const { frame, timestamp } = data;
      console.log("收到了processed_frame")
      console.log("timestamp",timestamp)
      const img = new Image();
      img.src = 'data:image/jpeg;base64,' + frame;  // 从后端返回的 base64 数据
      const canvas=videoCanvas2.value;
      const ctx = canvas.getContext('2d');
      img.onload = () => {
        // 创建一个canvas来显示处理后的图像
        //const canvas = document.createElement('canvas');
        ctx.clearRect(0,0,canvas.width,canvas.height);
        ctx.drawImage(img,0,0,canvas.width,canvas.height);
        console.log("画图")
        // 设置 canvas 大小与图像一致
        /* videoCanvas.value.width = img.width;
        videoCanvas.value.height = img.height;
        ctx.drawImage(img, 0, 0); */
        //document.body.appendChild(canvas);  // 或者将canvas添加到某个容器中显示
      };
      img.onerror = (error) => {
        console.error("图片加载失败:", error);
      };
    });

    //audioContext = new (window.AudioContext || window.webkitAudioContext)();
  })

  onUnmounted(() => {
  // 组件卸载时关闭 WebSocket 连接
  socket.disconnect();
});
</script>

<style scoped>
body {
  margin: 0;
  height: 100%;
}
  .monitor-page{
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  .monitor-container {
    display: flex;
    flex-direction: column;
    padding: 16px;
    flex-grow:1;
    overflow-y:auto;
   background: linear-gradient(180deg, #9dd9cb8d 0%, #a0e9ce89 50%, #ffffff 100%); /* 渐变背景 */
  }
  .camera-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  /* height: 100vh; */
}

.default-image-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  border-radius: 8px;
  margin:10px;
  /* margin-bottom: 16px; */
}
.default-image {
  width: 95%;
  height: 95%;
  object-fit: contain;
  /* margin-bottom: 8px; */
}

.default-text {
  font-size: 14px;
  color: #666;
  text-align: center;
}

.camera-canvas {
  border: 1px solid #ccc;
  border-radius: 8px;
  margin-bottom: 16px;
}

.camera-button {
  width: 200px;
}
</style>