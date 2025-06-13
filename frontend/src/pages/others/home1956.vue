<template>
  <div class="containter">
    <div class="header">
      <div class="header-left">
        智能坐姿识别与健康建议
        <van-icon name="arrow" />
      </div>
      <div class="header-right">
        <van-icon name="chat-o"  size="30" @click="goToChat" />
      </div>
    </div>

    <div class="upload-container">
      <span class="title">功能一：上传图片获取姿态三维数据</span>
      <van-uploader class="uploader" :after-read="afterRead"  v-model="fileList" multiple :max-count="1"/>
      <span class="result-title">结果如下：</span>
      <span class="result-subtitle">人体关键点三维可视化：</span>
      <van-image
        width="150"
        height="150"
        src="/singlePicResult092.jpg"
      />
      <van-image
        width="150"
        height="150"
        src="/singlePicResult3D092.jpg"
      />
      <div class="result">
        <van-cell-group>
          <van-cell v-for="(value, key) in postureData" :key="key" :title="key" :value="postureData[key]" />
        </van-cell-group>
      <!-- <van-cell v-if="hasDesk" title="眼镜距离书本屏幕距离" v-model="postureData.glassesDistance" /> -->
      </div>
        
    </div>
    <div>
      <video ref="videoElement" autoplay playsinline style="display: none;"></video>
      <van-button  type="primary"  @click="startCamera" v-if="!isCameraOn" size="large" >开启摄像头</van-button>
      
      <van-button  type="danger"  @click="stopCamera" v-if="isCameraOn" size="large" >关闭摄像头</van-button>
      <video ref="videoElement2" autoplay playsinline style="display: none;"></video>
       <canvas ref="videoCanvas"></canvas>
      <van-button  type="primary"  @click="startCamera2" v-if="!isCameraOn" size="large" >开启摄像头2</van-button>
      <van-button  type="danger"  @click="stopCamera2" v-if="isCameraOn" size="large" >关闭摄像头2</van-button>
    </div>
    
    <!-- <div>
      <video ref="videoElement" autoplay playsinline style="display: none;"></video>
    <van-button  type="primary" size="large"  @click="startCameras1" v-if="!isCameraOn">开启摄像头1</van-button>
    </div> -->
    
    
    <!-- <div class="upload-container">
        <span class="title">功能二：上传视频获取姿态三维数据</span>
        <van-uploader class="uploader" :after-read="afterRead2"  v-model="fileList2" multiple :max-count="1"/>
        <video ref="videoElement" autoplay playsinline></video>
        <span >结果如下：</span>
    </div> -->
    <van-dialog>

    </van-dialog>
  </div>
</template>
 
<script setup>
  import {ref,onMounted,reactive,getCurrentInstance} from 'vue';
  import {useRouter} from 'vue-router'
  import io from 'socket.io-client';

  //获取当前vue实例
  const { proxy } = getCurrentInstance()

  //获取router实例
  const router=useRouter()

  //websocketio
  const socket = io('http://localhost:5000'); 
  //-------------------对话功能-------------------------
  const goToChat = () => {
  router.push(`/chat`)
};
  //-------------------上传图片功能----------------------
  const fileList=ref([])
  const fileList2=ref([])
  const afterRead = (file) => {
      // 此时可以自行将文件上传至服务器
      console.log(file);
    };
  const afterRead2 = (file) => {
      // 此时可以自行将文件上传至服务器
      console.log(file);
    };


  //-----------------返回结果--------------------------
  // 定义一个对象来封装所有姿态数据
  const postureData = ref({
    postureType: "不良坐姿（含胸驼背）",
    spineState: "背部弯曲，脊柱未保持正常生理弯曲，呈驼背状",
    headShoulderPosition: "头部前倾，与脊柱未对齐，肩膀耸起且紧张",
    legPosition: "双腿平放在地面",
    armPosition: "手臂前伸",
    Distance: "40 cm" // 这里你可以根据实际情况调整
  });

  // 模拟调用后端接口的函数（以后可以替换成实际的接口调用）
  const fetchPostureData = async () => {
    // 这里可以调用后端接口获取数据并更新对象的字段
    // 比如：
    // const response = await api.getPostureData();
    // postureData.value = response.data; // 通过响应数据来更新 postureData
  };


  //--------------------开始录像------------------------------
  const videoElement = ref(null);
  const videoElement2 = ref(null);
  const videoCanvas=ref(null)
  const isCameraOn = ref(false);
  let stream =null;
  
  

  const startCamera = async () => {
    console.log("调用startcamera函数")
    const confirmResult=await showConfirmDialog({
    title: '权限请求',
    message:
      '是否允许开启摄像头以进行运动识别？',
  });
    /* .then(() => {
      // on confirm
      confirmResult=true
    })
    .catch(() => {
      // on cancel
      
    } );*/
    if (confirmResult) {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElement.value.srcObject = stream;
        videoElement.value.style.display = 'block';
        isCameraOn.value = true;

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const video = videoElement.value;

        const sendFrame = () => {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          const dataURL = canvas.toDataURL('image/jpeg', 0.8);
          //socket.emit('video_frame', dataURL);
          proxy.$api.sendVideoFrame(dataURL);
          requestAnimationFrame(sendFrame);
        };

        sendFrame();
      } catch (error) {
        console.error('无法访问摄像头:', error);
      }
    }
  };

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
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElement.value.srcObject = stream;
        //videoElement.value.style.display = 'block';
        isCameraOn.value = true;
        //创建一个canvas用于捕捉视频帧 
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const video = videoElement.value;
        const sendFrame = () => {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height); 
          const dataURL = canvas.toDataURL('image/jpeg', 0.8);
          const timestamp = performance.now();  // 当前时间戳
          //socket.emit('video_frame', dataURL);
          proxy.$api.sendVideoFrame({ frame: dataURL, timestamp: timestamp });
          requestAnimationFrame(sendFrame);
        };
        // 启动帧捕获和发送
        sendFrame();
      } catch (error) {
        console.error('无法访问摄像头:', error);
      }
    }
  };

/* // 监听后端传送的视频帧
    socket.on('video_frame', (frameData) => {
      const img = new Image();
      img.src = `data:image/jpeg;base64,${frameData.toString('base64')}`;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        videoElement.value.srcObject = canvas.toDataURL();
      };
    }); */

  // 停止摄像头
const stopCamera = () => {
  if (stream) {
    const tracks = stream.getTracks();
    tracks.forEach((track) => {
      track.stop(); // 停止所有摄像头和麦克风轨道
    });
    videoElement.value.style.display = 'none'; // 隐藏视频元素
    isCameraOn.value = false; // 更新摄像头状态
  }
};


/*  // 停止摄像头
  const stopCamera2 = () => {
    if (videoElement.value.srcObject) {
      const tracks = videoElement.value.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      videoElement.value.style.display = 'none';
      isCameraOn.value = false;
    }
  }; */

// 停止摄像头并停止发送帧
const stopCamera2 = () => {
  if (isCameraOn.value) {
    // 停止摄像头视频流
    const stream = videoElement.value.stream;
    if (stream) {
      stream.getTracks().forEach(track => track.stop()); // 停止所有轨道
    }

    // 停止帧的发送
    if (typeof animationFrameId !== 'undefined') {
      cancelAnimationFrame(animationFrameId); // 取消帧发送的循环
    }

    // 设置摄像头状态为关闭
    isCameraOn.value = false;
  }
};

/* onMounted(()=>{
  // 监听后端返回的处理结果
  socket.on('processed_frame', (data) => {
    const img = new Image();
    img.src = 'data:image/jpeg;base64,' + data.frame;  // 从后端返回的 base64 数据
    img.onload = () => {
      // 创建一个canvas来显示处理后的图像
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      //document.body.appendChild(canvas);  // 或者将canvas添加到某个容器中显示
    };
  });
}) */

onMounted(()=>{
  // 监听后端返回的处理结果
  
  socket.on('processed_frame', (data) => {
    const { frame, timestamp } = data;
    const img = new Image();
    img.src = 'data:image/jpeg;base64,' + frame;  // 从后端返回的 base64 数据
    const canvas=videoCanvas.value;
    const ctx = canvas.getContext('2d');
    img.onload = () => {
      // 创建一个canvas来显示处理后的图像
      //const canvas = document.createElement('canvas');
      ctx.clearRect(0,0,canvas.width,canvas.height);
      ctx.drawImage(img,0,0,canvas.width,canvas.height)
      // 设置 canvas 大小与图像一致
      /* videoCanvas.value.width = img.width;
      videoCanvas.value.height = img.height;
      ctx.drawImage(img, 0, 0); */
      //document.body.appendChild(canvas);  // 或者将canvas添加到某个容器中显示
    };
  });
})
  
</script>

<style lang="less" scoped>
.container {
    background-color: #f0f0f0;
    height: 100vh;
  }
  .header {
    display: flex;
    justify-content: space-between;
    margin: 5px;
    line-height: 54px;
    .header-left {
      padding-left: 22px;
      background: url(data:image/png;base64,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)
        no-repeat left center;
      background-size: 20px;
      font-size: 20px;
      font-weight: bold;
      color: #666666;
    }
    .header-right{
      background-size: 20px;
      font-size: 20px;
      font-weight: bold;
      color: #666666;
    }
  }

  .upload-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin: 20px;
  .title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px; /* 给标题和上传按钮之间留点空隙 */
  color: #666666; /* 设置标题颜色 */
  }
  .uploader {
    width: 100%;
    font-size: 16px; /* 调整上传按钮文字大小 */
    height: 100px; /* 增加上传按钮的高度，使其更大 */
    //background-color: #007bff; /* 上传按钮背景色 */
    border-radius: 8px; /* 给上传按钮加圆角 */
    color: white; /* 设置上传按钮字体颜色 */

    .van-uploader__input {
      font-size: 18px; /* 增加上传按钮文字的大小 */
    }
  }
  .result-title {
    display: block;
    font-size: 16px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 10px;
    color: #555;
  }
  .result-subtitle {
    display: block;
    font-size: 10px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 10px;
    color: #555;
  }

  .result {
    margin-top: 10px;
    background-color: white;
    padding: 10px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }



  //按钮
  .flex {
    display: flex;
  }

  .items-center {
    align-items: center;
  }

  .justify-center {
    justify-content: center;
  }

  .h-screen {
    height: 100vh;
  }
}




</style>


