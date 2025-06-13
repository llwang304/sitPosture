<template>
<div>
  <!-- <div class="user-account-page"> -->
    <van-nav-bar title="个人中心" />
    <div class="user-container">
      <div class="user">
        <van-image  class="img" width="100" height="100" :src="userInfo.avatar"></van-image>
        <div class="text">{{userInfo.username}}</div>
        <div class="account-info">
          <van-icon name="user-o" class="icon" />
          <span class="label">账户</span>
          <span>{{ userInfo.phone }}</span>
        </div>
      </div>
       <!-- 栏目部分 -->
      <div class="user-menu">
        <van-cell-group>
          <!-- <van-cell title="我的订单" is-link /> -->
          <van-cell title="个人资料" is-link @click="goInfoPage"/>
          <van-cell title="设置" is-link />
          <van-cell title="帮助与支持" is-link />
        </van-cell-group>
      </div>
    </div>
</div>
</template>

<script setup>
import { ref,onMounted ,computed} from 'vue';
import {useRouter} from 'vue-router'
const router=useRouter()

const userInfo=computed(()=>{
  return JSON.parse(localStorage.getItem('h5_userInfo'))||{}

})


//---------------------跳转资料页---------------------
const goInfoPage=()=>{
  router.push(`/info`)
}
// 在这里不需要处理通信，只是展示页面结构
</script>

<style lang="less" scoped>
  
.user-account-page {
  padding: 20px;
  background-color: #f9f9f9;
  height: 100vh;
}

.user-menu {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}


.user-container {
    background: linear-gradient(180deg, #9dd9cb8d 0%, #a0e9ce89 50%, #ffffff 100%); /* 渐变背景 */
    height: 100vh;
    padding:16px;
    overflow: hidden;
    .user {
      
      //height: 200px;
      background-color: #fff;
      text-align: center;
      border-radius: 10px;
      margin: 10px;
      .img {
        margin-top: 30px;
      }
      .text {
        line-height: 30px;
        font-weight: bold;
      }
      /* 新增账户信息样式 */
      .account-info {
          color: #999; /* 灰色字体 */
          font-size: 14px; /* 字号比用户名小，假设用户名是默认16px，这里可以根据实际调整 */
          margin-top: 10px;
          display: flex;
          justify-content: center;
          align-items: center;
        }
      .account-info.icon {
          margin-right: 5px;
        }
      .account-info.label {
          margin-right: 10px;
        }
      .account-info span {
        margin-right: 10px; /* 给span标签添加间隔，使账户和数据之间有间隔 */
      }
    }
    
    .foot {
      margin: 0 10px;
      padding: 10px;
      line-height: 50px;
      background-color: #fff;
      .foot1,
      .foot2 {
        display: flex;
        justify-content: space-between;
        color: #555;
      }
      .foot1 {
        border-bottom: 0.5px solid #f5f5f5;
      }
    }
    .quit {
      width: 90%;
      margin: 20px;
    }
    .quit_text {
      margin: 20px 0;
      text-align: center;
    }
  }
</style>
