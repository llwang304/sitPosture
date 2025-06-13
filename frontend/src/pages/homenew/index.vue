<template>
<div >
  <van-nav-bar title="智能坐姿识别和健康建议系统" >
    <template #title>
      <div class="nav-title">
        <img src="/icons/logo.png" alt="Icon" class="nav-icon" />
        智能坐姿识别&健康建议
      </div>
    </template>
  </van-nav-bar>
  <div class="home-container">
  <div class="app-text">
    <p>从这里开始</p>
    <p>守护你的坐姿健康</p>
  </div>
    <div class="start-card">
      <div class="card-title">
        <p>实时监测</p>
      </div>

      <div class="posture-images">
        <img src="/images/postureCompare.jpg" alt="Posture Comparison" class="posture-comparison" />
      </div>
      <van-button type="warning" class="start-button" @click="OnClickMonitor">
        进入坐姿监督模式
        <van-icon name="arrow" size="16" />
      </van-button>
    </div>

    <div class="start-card">
      <div class="card-title">
        <p>健康助手</p>
      </div>
      <div class="posture-images">
        <img src="/images/assistant.jpg" alt="Daily Goal" class="daily-goal" />
      </div>
      <van-button type="warning" class="start-button" @click="OnClickStatic">为您的健康问题答疑解惑
        <van-icon name="arrow" size="16" />
      </van-button>
    </div>

  </div>
</div>
</template>

<script setup>
import userBar from '../../components/UserBar.vue'
import {ref,computed} from "vue"
import {useRouter} from 'vue-router'

const router=useRouter()


//-------------按钮路由跳转-----------------
const OnClickMonitor=()=>{
  router.push('/monitornew')
}
const OnClickStatic=()=>{
  router.push('/chat')
}
</script>

<style scoped lang="less" >
.nav-title {
  display: flex;
  align-items: center;
}

.nav-icon {
  width: 24px; /* 调整图标宽度 */
  height: 24px; /* 调整图标高度 */
  margin-right: 8px; /* 调整图标与文字的间距 */
}

.home-container {
  padding: 16px;
   background: linear-gradient(180deg, #9dd9cb8d 0%, #a0e9ce89 50%, #ffffff 100%); /* 渐变背景 */
}
.app-text {
  text-align: left;
  margin-left: 16px;
  margin-bottom: 1rem;
}

.app-text p:first-child {
  font-size: 25px;
  font-weight: bold;
  color: #ffa600;
  margin: 0;
}

.app-text p:last-child {
  font-size: 35px;
  font-weight: bold;
  color: #02644e;
  margin: 0;
}
//userbar相关
.user-info-card {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 24px;
  margin-right: 16px;
}

.user-details {
  flex: 1;
}

.greeting {
  font-size: 16px;
  margin: 0;
}

.username {
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.user-actions {
  display: flex;
  gap: 16px;
}
.icon-button {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  .icon{
    width:75%;
    height: 75%;
  }
}
//功能卡片相关
.start-card {
  background-color: #fff;
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
}

.card-title {
  text-align: center;
  margin-bottom: 5px;
}

.card-title p {
  margin: 4px 0;
  font-size: 18px;
  font-weight: bold;
}

.card-icons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
}

.posture-images {
  text-align: center;
  margin-bottom: 16px;
}

.posture-comparison {
  width: 100%;
  max-width: 300px;
  border-radius: 8px;
}

.start-button {
  width: 100%;
}

.daily-goal {
  width: 100%;
  max-width: 200px;
  border-radius: 8px;
}



/*---------------*/
.start-card2 {
  position: relative;
  background-color: #ffc65c;
  /* width: 80%;
  height: 130px; */
  border-radius: 12px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.posture-container2 {
  /* width: 200px;
  height: 150px; */
  overflow: hidden;
  position: absolute;
  top: -10px; /* 调整偏移量 */
  left: 16px; /* 调整偏移量 */
}

.posture-comparison2 {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.start-info2 {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  padding: 16px;
}

.start-text2 {
  font-size: 16px;
  color: #fff;
  margin-bottom: 8px;
  white-space: nowrap; /* 防止文本换行 */
}

.start-button2 {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>