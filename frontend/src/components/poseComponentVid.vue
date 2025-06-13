<template>
<div class="pose-component-vid-container">
  <h1>坐姿识别</h1>

  <section id="demos" :class="{ invisible: !isModelLoaded }">
    <p><b>请开启摄像头，待出现画面后，将手机置于身体侧面，直至人体全部在画面中。</b> </p>
    <div id="liveView" class="videoView">
      <button id="webcamButton" @click="toggleWebcam" :style="{ padding: '8px 16px', backgroundColor: '#007f8b', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }">
        {{ isWebcamRunning ? '关闭摄像头' : '开启摄像头' }}
      </button>
      <div style="position: relative;">
        <video ref="webcamVideo" style="width: 640px; height: 360px; position: absolute; transform: rotateY(180deg); -webkit-transform: rotateY(180deg); -moz-transform: rotateY(180deg);" autoplay playsinline></video>
        <canvas ref="webcamCanvas" class="output_canvas" width="640" height="360" style="position: absolute; left: 0px; top: 0px; transform: rotateY(180deg); -webkit-transform: rotateY(180deg); -moz-transform: rotateY(180deg);"></canvas>
      </div>
    </div>
  </section>
</div>
</template>

<script setup lang="ts">
import { showNotify } from 'vant';
import { ref, onMounted, reactive, onBeforeUnmount } from 'vue';
import { PoseLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';
import socket from '../utils/socketio.js'
const animationFrameId = ref<number | null>(null);
const isModelLoaded = ref(false);
const poseLandmarker = ref<PoseLandmarker>();
//const runningMode = ref<'IMAGE' | 'VIDEO' | 'LIVE_STREAM'>('LIVE_STREAM');
const runningMode = ref<'IMAGE' | 'VIDEO'>('VIDEO');
const webcamVideo = ref<HTMLVideoElement>();
const webcamCanvas = ref<HTMLCanvasElement>();
const isWebcamRunning = ref(false);
const lastVideoTime = ref(-1);
const drawingUtils = ref<DrawingUtils>();
const imageNaturalWidths = reactive<number[]>([]);
const imageNaturalHeights = reactive<number[]>([]);
const imageWidths = reactive<number[]>([]);
const imageHeights = reactive<number[]>([]);
const imageCanvases = ref<HTMLCanvasElement[]>([]);




// 发送功能
// 发送时间控制
const lastSentTime = ref(0)
const SEND_INTERVAL = 1000 // 每 2 秒发送一次
let lastLandmarks: { x: number; y: number; z: number; visibility: number }[] | null = null

// 姿态识别结果的响应式变量
const currentPostureResult = ref<any>(null)

// 判断两个 landmark 序列是否有显著变化
function hasSignificantChange(
  current: { x: number; y: number; z: number; visibility: number }[],
  previous: typeof current | null
): boolean {
  if (!previous) return true
  let totalDiff = 0
  for (let i = 0; i < current.length; i++) {
    const dx = current[i].x - previous[i].x
    const dy = current[i].y - previous[i].y
    totalDiff += Math.sqrt(dx * dx + dy * dy)
  }
  return totalDiff > 0.1 // 可调阈值
}

// 主处理函数，在 Mediapipe 调用回调中触发
function handlePoseResult(result: any) {
  console.log('handleposeresult',result)
  const now = Date.now()
  const rawLandmarks = result?.landmarks?.[0]
  if (!rawLandmarks || now - lastSentTime.value < SEND_INTERVAL) return

  const landmarks = rawLandmarks.map((pt: any) => ({
    x: pt.x,
    y: pt.y,
    z: pt.z,
    visibility: pt.visibility
  }))

    socket.emit('pose_landmarks',{
        phone:JSON.parse(localStorage.getItem("h5_userInfo")).phone,
        landmarks:landmarks,
        mode: 'video',
        });
    lastLandmarks = landmarks
    lastSentTime.value = now
  }





//识别姿势逻辑
const imageList = ref([
  { src: 'https://assets.codepen.io/9177687/woman-ge0f199f92_640.jpg', title: 'Click to get detection!' },
  { src: 'https://assets.codepen.io/9177687/woman-g1af8d3deb_640.jpg', title: 'Click to get detection!' },
]);

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
      runningMode: 'VIDEO',
      numPoses: 1, // 根据你的需求调整
    });
    isModelLoaded.value = true;
    console.log('已调用createLandmarker')
  } catch (error) {
    console.error('Failed to load pose landmarker:', error);
  }
};

const hasGetUserMedia = () => !!navigator.mediaDevices?.getUserMedia;

const enableCam = async () => {
  if (!poseLandmarker.value) {
    console.log('Wait! poseLandmaker not loaded yet.');
    return;
  }
  runningMode.value = 'VIDEO'; // 确保在开启摄像头时设置 runningMode 为 VIDEO
  if (isWebcamRunning.value) {
    isWebcamRunning.value = false;
  } else {
    isWebcamRunning.value = true;
  }

  const constraints = {
    video: true,
  };

  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    if (webcamVideo.value) {
      webcamVideo.value.srcObject = stream;
      webcamVideo.value.addEventListener('loadeddata', predictWebcam);
    }
  } catch (error) {
    console.error('Error accessing webcam:', error);
    isWebcamRunning.value = false;
  }
};

const predictWebcam = async () => {
   if (!isModelLoaded.value||!poseLandmarker.value || !webcamVideo.value || !webcamCanvas.value || !isWebcamRunning.value) {
    return;
  }
  if (webcamVideo.value && webcamCanvas.value && poseLandmarker.value && isWebcamRunning.value) {
    webcamCanvas.value.style.height = webcamVideo.value.videoHeight + 'px';
    webcamVideo.value.style.height = webcamVideo.value.videoHeight + 'px';
    webcamCanvas.value.style.width = webcamVideo.value.videoWidth + 'px';
    webcamVideo.value.style.width = webcamVideo.value.videoWidth + 'px';

    if (runningMode.value === 'IMAGE') {
      runningMode.value = 'VIDEO';
      await poseLandmarker.value.setOptions({ runningMode: 'VIDEO' });
    }

    let startTimeMs = performance.now();
    if (lastVideoTime.value !== webcamVideo.value.currentTime) {
      lastVideoTime.value = webcamVideo.value.currentTime;
      try{
        poseLandmarker.value.detectForVideo(webcamVideo.value, startTimeMs, (result) => {
          // 调用 handlePoseResult 
          handlePoseResult(result);

          const canvasCtx = webcamCanvas.value?.getContext('2d');
          if (canvasCtx) {
            canvasCtx.save();
            canvasCtx.clearRect(0, 0, webcamCanvas.value.width, webcamCanvas.value.height);
            if (result.landmarks && result.landmarks.length > 0) {
              drawingUtils.value = new DrawingUtils(canvasCtx);
              for (const landmark of result.landmarks) {
                drawingUtils.value.drawLandmarks(landmark, {
                  radius: (data) => DrawingUtils.lerp(data.from!.z, -0.15, 0.1, 5, 1),
                });
                drawingUtils.value.drawConnectors(landmark, PoseLandmarker.POSE_CONNECTIONS);
              }
            }
            // 加上姿态识别的结果
            if (currentPostureResult.value) {
              canvasCtx.save()
              // 水平镜像
              canvasCtx.translate(webcamCanvas.value.width, 0)
              canvasCtx.scale(-1, 1)
              drawPostureResult(canvasCtx, currentPostureResult.value)
            }
            canvasCtx.restore();
          }
          console.log(result)
        }); 
        
      }catch(error){
        console.error("Error during pose detection:", error);
      }
      
    }
    if (isWebcamRunning.value) {
      animationFrameId.value = requestAnimationFrame(predictWebcam);
    }
  }
};

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


const toggleWebcam = () => {
  if (isWebcamRunning.value) {
    // 关闭摄像头
    if (webcamVideo.value && webcamVideo.value.srcObject) {
      const stream = webcamVideo.value.srcObject as MediaStream;
      stream.getTracks().forEach(track => {
        track.stop();
      });
      webcamVideo.value.srcObject = null;
    }
    isWebcamRunning.value = false;
    // 取消动画帧
    if (animationFrameId.value !== null) {
      cancelAnimationFrame(animationFrameId.value);
      animationFrameId.value = null;
    }
     // 添加清除画布的操作
    if (webcamCanvas.value) {
      const canvasCtx = webcamCanvas.value.getContext('2d');
      if (canvasCtx) {
        canvasCtx.clearRect(0, 0, webcamCanvas.value.width, webcamCanvas.value.height);
      }
    }
  } else {
    // 开启摄像头
    enableCam();
  }
};

onMounted(() => {
  createPoseLandmarker();
  if (!hasGetUserMedia()) {
    console.warn('getUserMedia() is not supported by your browser');
  }
  socket.on('posture_result_video', (data:any) => {
    console.log("收到姿态识别结果：", data)
    currentPostureResult.value = data
    if (data.overall === 'bad') {
    // 调用 Vant 的危险通知
    showNotify({ type: 'danger', message: '请注意，您的坐姿不正确！' });
  }
  })
});
onBeforeUnmount(()=>{
  socket.off('posture_result_video')
})

</script>

<style scoped>
.pose-component-vid-container{
  padding:10px;
  background-color: #fff;
  height: 100vh;
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
  opacity: 1;
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
  float: left;
  width: 48%;
  margin: 2% 1%;
  cursor: pointer;
}

.videoView p,
.detectOnClick p {
  position: absolute;
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

.output_canvas {
  /* transform: rotateY(180deg);
  -webkit-transform: rotateY(180deg);
  -moz-transform: rotateY(180deg); */
}

.detectOnClick {
  z-index: 0;
}

.detectOnClick img {
  width: 100%;
}
</style>