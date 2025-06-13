<template>
<div class="container">
  <div class="welcome-container">
    <div class="circle-image-container">
      <img src="/images/welcome1.jpg" alt="Sitting" class="sitting-image" />
    </div>
    <div class="text-container">
      <p class="multi-line-text">
        Shape<br />
        Your Posture, <br />
        Shape<br />
        Your Life
      </p>
    </div>
    <div class="button-container">
      <van-button  class="create-account-button" @click="OnclickRegister" >Create an account</van-button>
      <p class="question-text">Already have an account?
      </p>
      <van-button   class="sign-in-button" @click="OnclickLoginIn">Sign in</van-button>
    </div>
  </div>
</div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
const OnclickLoginIn=()=>{
  router.push('/loginnew')
}
const OnclickRegister=()=>{
  router.push('/register')
}
</script>

<style scoped>
.container {
    background-color: #f0f0f0;
    /* min-height: 100vh; */
    
  }
.welcome-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  overflow: hidden; /* 关键：隐藏超出的部分 */
  background: linear-gradient(180deg, #9dd9cb8d 0%, #a0e9ce89 50%, #ffffff 100%); /* 渐变背景 */
}

.circle-image-container {
  position:absolute;
  top:0;
  left:50%;
  transform: translateX(-50%) translateY(-45%); /* 将图片的水平中心和垂直中心向上移动，使底部40%在页面顶部 */
  -webkit-mask-image: radial-gradient(circle, rgba(0, 0, 0, 1) 60%, rgba(0, 0, 0, 0));
  mask-image: radial-gradient(circle, rgba(0, 0, 0, 1) 60%, rgba(0, 0, 0, 0));
  width: 500px; /* 圆形容器的宽度 */
  height: 500px; /* 圆形容器的高度 */
  border-radius: 50%;
  overflow: hidden;
  /* margin-bottom: 20px; */
  /* filter: blur(2px); */
}

.sitting-image {
  width: 100%;
  height: 100%;
  transform: translateY(15%) scale(0.8);
  /* transform:  */ 
  object-fit: cover;
   /* 添加羽化效果，数值可以调整 */
}

h1 {
  font-size: 2rem;
  margin-bottom: 30px;
  text-align: center;
}
.text-container {
  position: absolute; /* 使用绝对定位，以便相对于页面定位 */
  top: 53%; /* 将容器的顶部放置在页面纵向的 50% 位置 */
  left: 50%; /* 将容器的左边放置在页面横向的 50% 位置 */
  transform: translate(-50%, -50%); /* 将容器的中心移动到页面的中心 */
  text-align: center; /* 让文字在其容器内居中 */
   width: 95%; /* 根据实际情况调整 */
   justify-content: center;
}

.multi-line-text {
  font-family: Arial, sans-serif;
  font-size: 2.1rem; /* 设置字体大小，根据需要调整 */
  line-height: 1.0; /* 设置行高，根据需要调整 */
  margin: 0; /* 移除默认的段落外边距 */
  white-space: pre-line; /* 保留换行符和空格 */
  color:#02644e;
  letter-spacing: 0.7rem; /* 增加字符间隔 */
}
.button-container {
  display: flex;
  position: absolute;
  top: 90%;
  left: 50%;
  transform: translateX(-50%) translateY(-50%);
  flex-direction: column; /* 将主轴改为垂直方向 */
  align-items: center;
  width:100%;
  height:50%;
}
.create-account-button{
  width: 75%; /* 设置按钮宽度 */
  height: 18%; /* 设置按钮高度 */
  border-radius: 30px; /* 设置圆角 */
  font-size: 1.2rem; /* 设置字体大小，可以根据需要调整 */
  color:#ffffff;
  background:#02644e;
}
.sign-in-button {
  /* padding: 10px 20px;
  margin: 0 10px;
  cursor: pointer; */

  width: 75%; /* 设置按钮宽度 */
  height: 18%; /* 设置按钮高度 */
  border-radius: 30px;
  font-size: 1.2rem;
  color:#02644e;
  border: 1px solid #02644e;
  background-color:#ffffff;
}

.question-text{
  color:#686868;
}
</style>