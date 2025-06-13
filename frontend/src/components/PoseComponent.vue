<template>
  <h1>Pose detection using the MediaPipe PoseLandmarker task</h1>

  <section id="demos" :class="{ invisible: !isModelLoaded }">
    <h2>Demo: Detecting Images</h2>
    <p><b>Click on an image below</b> to see the key landmarks of the body.</p>

    <div class="detectOnClick" v-for="(image, index) in imageList" :key="index">
      <img :src="image.src" width="100%" crossorigin="anonymous" :title="image.title" @click="detectPose(image.src, $event)" />
      <canvas :ref="'imageCanvas_' + index" class="canvas" :width="imageNaturalWidths[index]" :height="imageNaturalHeights[index]" :style="{ left: '0px', top: '0px', width: imageWidths[index] + 'px', height: imageHeights[index] + 'px' }"></canvas>
    </div>

    <h2>Demo: Webcam continuous pose landmarks detection</h2>
    <p>Stand in front of your webcam to get real-time pose landmarker detection.<br>Click <b>enable webcam</b> below and grant access to the webcam if prompted.</p>

    <div id="liveView" class="videoView">
      <button id="webcamButton" @click="toggleWebcam" :style="{ padding: '8px 16px', backgroundColor: '#007f8b', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }">
        {{ isWebcamRunning ? 'DISABLE WEBCAM' : 'ENABLE WEBCAM' }}
      </button>
      <div style="position: relative;">
        <video ref="webcamVideo" style="width: 640px; height: 360px; position: absolute; transform: rotateY(180deg); -webkit-transform: rotateY(180deg); -moz-transform: rotateY(180deg);" autoplay playsinline></video>
        <canvas ref="webcamCanvas" class="output_canvas" width="640" height="360" style="position: absolute; left: 0px; top: 0px; transform: rotateY(180deg); -webkit-transform: rotateY(180deg); -moz-transform: rotateY(180deg);"></canvas>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { PoseLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';
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

const detectPose = async (imageSrc: string, event: MouseEvent) => {
  if (!poseLandmarker.value) {
    console.log('Wait for poseLandmarker to load before clicking!');
    return;
  }

  if (runningMode.value === 'VIDEO') {
    runningMode.value = 'IMAGE';
    //await poseLandmarker.value.setOptions({ runningMode: 'IMAGE' });
  }

  const imgElement = event.target as HTMLImageElement;
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
    poseLandmarker.value.detect(imgElement, (result) => {
      if (result.landmarks && result.landmarks.length > 0) {
        for (const landmark of result.landmarks) {
          drawingUtils.value?.drawLandmarks(landmark, {
            radius: (data) => DrawingUtils.lerp(data.from!.z, -0.15, 0.1, 5, 1),
          });
          drawingUtils.value?.drawConnectors(landmark, PoseLandmarker.POSE_CONNECTIONS);
        }
      }
    });
  }
};

const hasGetUserMedia = () => !!navigator.mediaDevices?.getUserMedia;

const enableCam = async () => {
  if (!poseLandmarker.value) {
    console.log('Wait! poseLandmaker not loaded yet.');
    return;
  }
  runningMode.value = 'VIDEO'; // 确保在开启摄像头时设置 runningMode 为 VIDEO
  //await poseLandmarker.value.setOptions({ runningMode: 'VIDEO' }); // 提前设置 options
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
            canvasCtx.restore();
          }
          console.log(result)
        }); 
      }catch(error){
        console.error("Error during pose detection:", error);
      }
      
    }
    //requestAnimationFrame(predictWebcam);
    if (isWebcamRunning.value) {
    animationFrameId.value = requestAnimationFrame(predictWebcam);
  }
  }
};

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
});
</script>

<style scoped>
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