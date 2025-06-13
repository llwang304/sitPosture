<template>
<div class="pose-component-img-container">
  <h1>坐姿识别</h1>
  <div id="demos" :class="{ invisible: !isModelLoaded }">
    <p><b>请上传一张单人图片，点击按钮开始识别</b> </p>
    <!-- <p><b>点击 <span class="add-icon">+</span>添加图片</b> </p> -->
    <div style="margin-bottom: 16px">
      <button type="primary" @click="handleDetect" 
        :style="{ padding: '8px 16px', backgroundColor: '#007f8b', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }">识别坐姿</button>
    </div>
    <div>
      
      <van-uploader 
        :after-read="afterRead" 
        :max-count="1" 
        :disabled="uploaderDisabled"
        v-model="fileList"
        :before-delete="beforeDelete"
      />
    </div>
    <div class="detectOnClick" v-for="(image, index) in imageList" :key="index" style="text-align: center;">
      <div class="image-wrapper">
      <img :src="image.src" width="100%" 
      crossorigin="anonymous" :title="image.title" id="uploadedImg"
        />
      <canvas :ref="'imageCanvas_' + index" class="canvas" 
      :width="imageNaturalWidths[index]" :height="imageNaturalHeights[index]" 
      :style="{ left: '0px', top: '0px', width: imageWidths[index] + 'px', 
      height: imageHeights[index] + 'px' }"></canvas>
      </div>
      
    </div>
  </div>
  <div v-if="currentPostureResult" class="recognition-results">
    <h3>识别结果:</h3>
    <p>头部: {{ currentPostureResult.head || 'N/A' }}</p>
    <p>躯干: {{ currentPostureResult.torso || 'N/A' }}</p>
    <p>腿部: {{ currentPostureResult.leg || 'N/A' }}</p>
    <p>整体: {{ currentPostureResult.overall || 'N/A' }}</p>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { PoseLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';
/* import pose1 from '../assets/pose1.jpg';
import pose2 from '../assets/pose2.jpg'; */
import type { UploaderInstance} from 'vant';
import socket from '../utils/socketio.js'

//生成关键点绘制关键点相关
const isModelLoaded = ref(false);
const poseLandmarker = ref<PoseLandmarker>();
const runningMode = ref<'IMAGE' | 'VIDEO'>('IMAGE');
const drawingUtils = ref<DrawingUtils>();
const imageNaturalWidths = reactive<number[]>([]);
const imageNaturalHeights = reactive<number[]>([]);
const imageWidths = reactive<number[]>([]);
const imageHeights = reactive<number[]>([]);
const imageCanvases = ref<HTMLCanvasElement[]>([]);

// 姿态识别结果的响应式变量
const currentPostureResult = ref<any>(null)

//上传图片相关
const uploadedImage = ref<{ url: string; file?: File; canvasRef?: string } | null>(null);
const uploadedImg = ref<HTMLImageElement | null>(null);
const imageNaturalWidth = ref(0);
const imageNaturalHeight = ref(0);
const uploaderRef = ref<UploaderInstance>();
const uploaderDisabled=ref(false)
const imageList = ref([
  /* { src: pose1, title: 'Click to get detection!' },
  { src: pose2, title: 'Click to get detection!' }, */
]);
const fileList=ref([

])

//-----------------------上传图片方法-----------------------

const afterRead = (file) => {
  if (file && typeof file === 'object' && 'content' in file) {
    const newImg = {
      src: file.content as string,
      title: '点击查看检测结果',
    };
    imageList.value.push(newImg);
    uploaderDisabled.value=true;

  }
};
const beforeDelete = (file, details) => {  
      // 删除 imageList 中对应项
      const index = fileList.value.findIndex(f => f.content === file.content)
      if (index !== -1) {
        imageList.value.splice(index, 1)
        fileList.value.splice(index, 1)
      }
      uploaderDisabled.value=false;  
  }


//-----------------------绘制图片方法-----------------------
const createPoseLandmarker = async () => {
  try {
    const vision = await FilesetResolver.forVisionTasks(
      'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm'
    );
    poseLandmarker.value = await PoseLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath: 
        `/models/pose_landmarker_full.task`,
        delegate: 'GPU',
      },
      runningMode: 'IMAGE',
      numPoses: 1, // 根据你的需求调整
    });
    isModelLoaded.value = true;
    console.log('已调用createLandmarker')
  } catch (error) {
    console.error('Failed to load pose landmarker:', error);
  }
};

const handleDetect = () => {
  const image = imageList.value[0];
  if (!image) return;
  const imgEl = document.getElementById('uploadedImg') as HTMLImageElement | null;
  if (!imgEl) return;

  detectPose(image.src, imgEl); // 手动构造 event
};


const detectPose = async (imageSrc: string, imgElement: HTMLImageElement) => {
  if (!poseLandmarker.value) {
    console.log('Wait for poseLandmarker to load before clicking!');
    return;
  }

  if (runningMode.value === 'VIDEO') {
    runningMode.value = 'IMAGE';
    await poseLandmarker.value.setOptions({ runningMode: 'IMAGE' });
  }

  //const imgElement = event.target as HTMLImageElement;
  const index = imageList.value.findIndex(img => img.src === imageSrc);
  if (index === -1) return;

  imageNaturalWidths[index] = imgElement.naturalWidth;
  imageNaturalHeights[index] = imgElement.naturalHeight;
  imageWidths[index] = imgElement.width;
  imageHeights[index] = imgElement.height;
  const boundingRect = imgElement.getBoundingClientRect();
  const canvas = (imageCanvases.value[index] = imageCanvases.value[index] || document.createElement('canvas')) as HTMLCanvasElement;
  const parent = imgElement.parentNode as HTMLDivElement;
  const existingCanvas = parent.querySelector('.canvas');
  if (existingCanvas) {
    parent.removeChild(existingCanvas);
  }
  canvas.classList.add('canvas');
  canvas.width = imgElement.naturalWidth;
  canvas.height = imgElement.naturalHeight;
  canvas.style.position='absolute';
  canvas.style.left = '0px';
  canvas.style.top = '0px';
  canvas.style.width = `${boundingRect.width}px`;
  canvas.style.height = `${boundingRect.height}px`;
  parent.style.position='relative';
  parent.appendChild(canvas);
  const canvasCtx = canvas.getContext('2d');
  if (canvasCtx) {
    drawingUtils.value = new DrawingUtils(canvasCtx);
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    poseLandmarker.value.detect(imgElement, (result) => {
      handlePoseResult(result);
      if (result.landmarks && result.landmarks.length > 0) {
        for (const landmark of result.landmarks) {
          drawingUtils.value?.drawLandmarks(landmark, {
            radius: (data) => DrawingUtils.lerp(data.from!.z, -0.15, 0.1, 5, 1),
          });
          drawingUtils.value?.drawConnectors(landmark, PoseLandmarker.POSE_CONNECTIONS);
        }
        console.log('landmarks',result)
      }
    });
  }
};

const hasGetUserMedia = () => !!navigator.mediaDevices?.getUserMedia;

// 发送landmark
function handlePoseResult(result: any) {
  console.log('handleposeresult',result)
  const rawLandmarks = result?.landmarks?.[0]

  const landmarks = rawLandmarks.map((pt: any) => ({
    x: pt.x,
    y: pt.y,
    z: pt.z,
    visibility: pt.visibility
  }))

  socket.emit('pose_landmarks',{
      phone:JSON.parse(localStorage.getItem("h5_userInfo")).phone,
      landmarks:landmarks,
      mode: 'image',
      });

  }

// 绘制result
function drawPostureResult(ctx: CanvasRenderingContext2D, result: any) {
  ctx.font = '20px Arial'
  const isNormal = result.overall === 'good' // 根据你具体定义调整
  // const isNormal = result.overall === 'good' || result.overall === 'normal' || result.overall === 'upright'  // 根据你具体定义调整
  ctx.fillStyle = isNormal ? 'limegreen' : 'red'
  ctx.fillStyle = 'red'
  ctx.fillText(`Head: ${result.head}`, 10, 30)
  ctx.fillText(`Torso: ${result.torso}`, 10, 60)
  ctx.fillText(`Leg: ${result.leg}`, 10, 90)
  ctx.fillText(`Overall: ${result.overall}`, 10, 120)
}

//--------------------------语音相关----------------------------------------
//--------------------科大讯飞语音功能----------------
  const audioPlayer = ref(null);
  let audioContext;

  const g0etVoice = () => {
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

/* function playNextAudio() {
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
 */




onMounted(() => {
  createPoseLandmarker();
  if (!hasGetUserMedia()) {
    console.warn('getUserMedia() is not supported by your browser');
  }
  socket.on('posture_result_image', (data:any) => {
    console.log("收到姿态识别结果：", data)
    currentPostureResult.value = data
  })
});
</script>

<style scoped>
.pose-component-img-container{
  padding:10px;
  background-color: #fff;
  height: 100vh;
  display: flex;
  flex-direction: column; /* 垂直排列子元素 */
}
body {
  font-family: roboto;
  margin: 2em;
  color: #3d3d3d;
}

h1 {
  color: #007f8b;
}

h2 {
  clear: both;
}

em {
  font-weight: bold;
}

video {
  clear: both;
  display: block;
}

section {
  /* opacity: 1; */
  transition: opacity 500ms ease-in-out;
}

header,
footer {
  clear: both;
}

.removed {
  display: none;
}

.invisible {
  opacity: 0.2;
}

.note {
  font-style: italic;
  font-size: 130%;
}

.videoView,
.detectOnClick {
  position: relative;
  /* float: left; */
  width: 48%;
  margin: 2% 1%;
  cursor: pointer;
  background-color: white; /* ✅ 添加这一行 */
}

.videoView p,
.detectOnClick p {
  /* position: absolute; */
  padding: 5px;
  background-color: #007f8b;
  color: #fff;
  border: 1px dashed rgba(255, 255, 255, 0.7);
  z-index: 2;
  font-size: 12px;
  margin: 0;
}

.highlighter {
  background: rgba(0, 255, 0, 0.25);
  border: 1px dashed #fff;
  z-index: 1;
  position: absolute;
}

.canvas {
  z-index: 2;
  position: absolute;
  pointer-events: none;
}


.detectOnClick {
  z-index: 0;
}

.detectOnClick img {
  width: 100%;
}


/*调整*/
.image-wrapper {
  position: relative;
  width: 100%;
}

.canvas uploaded-image-container {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}



/*currentresult显示*/
/* ----------------------- 姿态识别结果的样式 ----------------------- */
.recognition-results {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid #007f8b;
  border-radius: 8px;
  background-color: #e0f7fa;
  color: #004d40;
  text-align: left; /* 结果文本左对齐 */
  width: 90%; /* 与图片区域保持一致的宽度 */
  max-width: 400px; /* 与图片区域保持一致的最大宽度 */
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  /* ✅ 让结果区域自身也居中 */
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 20px; /* 底部间距 */
  z-index: 5;
  
}

.recognition-results h3 {
  margin-top: 0;
  color: #007f8b;
  border-bottom: 1px dashed #007f8b;
  padding-bottom: 5px;
}

.recognition-results p {
  margin: 8px 0;
  line-height: 1.5;
}
</style>