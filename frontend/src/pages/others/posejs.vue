<template>
  <div>
    <h1>Pose detection using the MediaPipe PoseLandmarker task</h1>

    <section id="demos" v-if="poseLandmarker">
      <h2>Demo: Detecting Images</h2>
      <p><b>Click on an image below</b> to see the key landmarks of the body.</p>

      <div class="detectOnClick" v-for="(img, index) in images" :key="index">
        <img
          :src="img.src"
          alt="Pose Detection"
          @click="handleClick"
          crossorigin="anonymous"
        />
      </div>

      <h2>Demo: Webcam continuous pose landmarks detection</h2>
      <p>Click to enable webcam and get real-time pose landmarker detection.</p>

      <div id="liveView" class="videoView">
        <button id="webcamButton" @click="toggleWebcam">
          {{ buttonText }}
        </button>
        <div style="position: relative;">
          <video id="webcam" ref="video" autoplay playsinline></video>
          <canvas id="output_canvas" ref="canvas" :width="videoWidth" :height="videoHeight"></canvas>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
// 使用 npm 安装的 mediapipe 依赖
import {
  PoseLandmarker,
  FilesetResolver,
  DrawingUtils
} from '@mediapipe/tasks-vision';

const poseLandmarker = ref(null);
const webcamRunning = ref(false);
const videoHeight = ref(360);
const videoWidth = ref(480);
const video = ref(null);
const canvas = ref(null);
const canvasCtx = ref(null);
const buttonText = ref('ENABLE WEBCAM');
const runningMode=ref("VIDEO");
let lastVideoTime = -1; // 用于避免重复视频时间处理
let animationFrameId = null; //用于管理帧，创建资源，释放资源
const hasGetUserMedia = () => !!navigator.mediaDevices?.getUserMedia;// 检查是否支持获取摄像头
const images = [
  { src: new URL('../assets/pose1.jpg', import.meta.url).href },
  { src: new URL('../assets/pose2.jpg', import.meta.url).href },
];

// Create pose landmarker instance
const createPoseLandmarker = async () => {
  const vision = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm'
  );
  poseLandmarker.value = await PoseLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath:
        `/models/pose_landmarker_full.task`,
      delegate: 'GPU',
    },
    runningMode: "VIDEO",
    numPoses: 2,
  });
};

// Handle image click
const handleClick = async (event) => {
  if (!poseLandmarker.value) {
    console.log("Wait for poseLandmarker to load before clicking!");
    return;
  }
  if (runningMode.value === 'VIDEO') {
    runningMode.value = 'IMAGE';
    await poseLandmarker.value.setOptions({ runningMode: 'IMAGE' });
  }

  // Remove previous canvas
  const allCanvas = event.target.parentNode.getElementsByClassName('canvas');
  for (let i = allCanvas.length - 1; i >= 0; i--) {
    const n = allCanvas[i];
    n.parentNode.removeChild(n);
  }

  // Perform pose detection
  poseLandmarker.value.detect(event.target, (result) => {
    const canvasElement = document.createElement('canvas');
    canvasElement.setAttribute('class', 'canvas');
    canvasElement.setAttribute('width', event.target.naturalWidth + 'px');
    canvasElement.setAttribute('height', event.target.naturalHeight + 'px');
    canvasElement.style.position = 'absolute';
    canvasElement.style.top = '0';
    canvasElement.style.left = '0';
    canvasElement.style.width = event.target.getBoundingClientRect().width + 'px';
    canvasElement.style.height = event.target.getBoundingClientRect().height + 'px'
    event.target.parentNode.appendChild(canvasElement);
    const ctx = canvasElement.getContext('2d');
    const drawingUtils = new DrawingUtils(ctx);

    // Draw landmarks
    for (const landmark of result.landmarks) {
      drawingUtils.drawLandmarks(landmark, {
        radius: (data) =>
          DrawingUtils.lerp(data.from.z, -0.15, 0.1, 5, 1),
      });
      drawingUtils.drawConnectors(landmark, PoseLandmarker.POSE_CONNECTIONS);
    }
  });
};

// Enable webcam and start pose detection
const enableCam = async () => {
  if (!hasGetUserMedia()) {
    alert('Your browser does not support webcam access.');
    return;
  }
  console.log('调用enableCam');
  if (!poseLandmarker.value) {
    console.log("Wait! poseLandmaker not loaded yet.");
    return;
  }
  // 切换按钮文本
  webcamRunning.value = true;
  buttonText.value = 'DISABLE WEBCAM';

  // getUsermedia parameters.
  const constraints = { video: true };
  // Activate the webcam stream.
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    video.value.srcObject = stream;
    video.value.addEventListener("loadeddata", predictWebcam);
  } catch (error) {
    console.error('Error accessing webcam:', error);
    webcamRunning.value = false;
    buttonText.value = 'ENABLE WEBCAM';
  }
};

// Perform webcam pose detection
const predictWebcam = async() => {
  if (!poseLandmarker.value || !video.value || !canvas.value || !webcamRunning.value) {
    return;
  }
  if (runningMode.value === 'IMAGE') {
    runningMode.value = 'VIDEO';
    await poseLandmarker.value.setOptions({ runningMode: 'VIDEO' });
  }
  canvas.value.style.height = video.value.videoHeight + 'px';
  video.value.style.height = video.value.videoHeight + 'px';
  canvas.value.style.width = video.value.videoWidth + 'px';
  video.value.style.width = video.value.videoWidth + 'px';

  const nowInMs = Date.now();
  if (lastVideoTime !== video.value.currentTime) {
    lastVideoTime = video.value.currentTime;
    poseLandmarker.value.detectForVideo(video.value, nowInMs, (result) => {
      canvasCtx.value = canvas.value.getContext('2d');
      const drawingUtils = new DrawingUtils(canvasCtx.value);
      canvasCtx.value.save();
      canvasCtx.value.clearRect(0, 0, canvas.value.width, canvas.value.height);

      for (const landmark of result.landmarks) {
        drawingUtils.drawLandmarks(landmark, {
          radius: (data) =>
            DrawingUtils.lerp(data.from.z, -0.15, 0.1, 5, 1),
        });
        drawingUtils.drawConnectors(landmark, PoseLandmarker.POSE_CONNECTIONS);
      }
      canvasCtx.value.restore();
    });
  }

  if (webcamRunning.value) {
    animationFrameId = requestAnimationFrame(predictWebcam);
  }
};

const toggleWebcam = () => {
  if (webcamRunning.value) {
    // 关闭摄像头
    if (video.value && video.value.srcObject) {
      const stream = video.value.srcObject;
      const tracks = stream.getTracks();
      tracks.forEach((track) => track.stop());
      video.value.srcObject = null;
    }
    webcamRunning.value = false;
    buttonText.value = 'ENABLE WEBCAM';
    // 取消动画帧
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
  } else {
    // 开启摄像头
    enableCam();
  }
};

// Mount and unmount lifecycle hooks
onMounted(() => {
  createPoseLandmarker();
});

onBeforeUnmount(() => {
  if (animationFrameId) {
    window.cancelAnimationFrame(animationFrameId);
  }
  if (video.value && video.value.srcObject) {
    const stream = video.value.srcObject;
    const tracks = stream.getTracks();
    tracks.forEach((track) => track.stop());
    video.value.srcObject = null;
  }
});
</script>

<style scoped>
/* 样式保持不变 */
</style>