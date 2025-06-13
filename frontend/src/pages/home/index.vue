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
    
      <!-- <van-swipe class="my-swiper" height="170" :autoplay="3000" lazy-render>
        <van-swipe-item v-for="item in homeData.slides" :key="item.id">
          <van-image :src="item.pic_image_url"  radius="5"/>
        </van-swipe-item>
    </van-swipe> -->
    <div class="upload-welcomecontainer">
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
       <canvas ref="videoCanvas" id="canvas"  ></canvas>
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
          requestAnimationFrame(sendFrame);
        };
        // 启动帧捕获和发送
        sendFrame();
        console.log('sengframe被调用')
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
  /* if (isCameraOn.value) {
    // 停止摄像头视频流
    //const stream = videoElement.value.stream;
    if (stream) {
      stream.getTracks().forEach(track => track.stop()); // 停止所有轨道
    }
    // 停止帧的发送
    if (typeof animationFrameId !== 'undefined') {
      cancelAnimationFrame(animationFrameId); // 取消帧发送的循环
    }
    // videoCanvas.value.style.display = 'none' 
    // 设置摄像头状态为关闭
    isCameraOn.value = false;
  } */
  if (isCameraOn.value && stream) {
    // 停止摄像头视频流
    stream.getTracks().forEach(track => track.stop());
    isCameraOn.value = false;

    // 清除canvas上的内容
    const canvas = videoCanvas.value;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);  // 清空画布内容
    
    // 停止发送帧
    cancelAnimationFrame(frameRequestId);  // 取消帧捕获的动画帧请求
    console.log("摄像头已关闭，停止绘制");
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
  socket.on('enterFrame',(data)=>{
    console.log(data.message)
  })
  socket.on('processed_frame', (data) => {
    const { frame, timestamp } = data;
    console.log("收到了processed_frame")
    console.log("timestamp",timestamp)
    const img = new Image();
    img.src = 'data:image/jpeg;base64,' + frame;  // 从后端返回的 base64 数据
    const canvas=videoCanvas.value;
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
      padding-left: 30px;
      background: url('/images/bupt2.png')
        no-repeat left center;
      background-size: 30px;
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