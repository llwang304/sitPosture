<template>
<div class="container">
  <div class="login-container">
    <!-- <img src="/images/bupt6.png" alt="BUPT Logo" class="logo" /> -->
    <div class="welcome-text">
      <h1>Hello!</h1>
      <p>Nice to see you again!</p>
    </div>
    <div class="input-container">
      <label ref="labelRef" for="phone-number" class="input-label">Phone Number</label>
      <input v-model="form.userName" ref="inputRef" type="text" id="phone-number" class="phone-input" placeholder="Enter your phone number" />
    </div>
    
    <div class="input-container">
      <label ref="labelRef2" for="password" class="input-label">Password</label>
      <input v-model="form.passWord" ref="inputRef2" type="password" id="password" class="phone-input" placeholder="Enter your password" />
    </div>
    
    <van-button type="primary" class="login-button" @click="onSubmit">Sign in</van-button>
    <!-- <img src="/images/login_pattern.jpg" alt="Plants Background" class="plants-bg" /> -->
  </div>
</div>
</template>
<script setup>
// 这里可以添加按钮点击事件的处理逻辑welcome
import {ref,onMounted,reactive,getCurrentInstance,nextTick} from 'vue';
const labelRef = ref(null);
const inputRef = ref(null);
const labelRef2 = ref(null);
const inputRef2 = ref(null);
onMounted(() => {
      nextTick(() => {
        if (labelRef.value && inputRef.value) {
          const labelRect = labelRef.value.getBoundingClientRect();
          const inputRect = inputRef.value.getBoundingClientRect();
          const labelRect2 = labelRef2.value.getBoundingClientRect();
          const inputRect2 = inputRef2.value.getBoundingClientRect();
          
           // 计算需要保留的区域
          const clipPathValue = `polygon(
            0% 0%, 0% 100%, 100% 100%, 100% 0%, 
            ${labelRect.right-inputRect.left}px 0%, ${labelRect.right-inputRect.left}px ${labelRect.bottom-inputRect.top}px, 
            ${labelRect.left-inputRect.left}px ${labelRect.bottom-inputRect.top}px, 
            ${labelRect.left-inputRect.left}px 0%, 0% 0%
          )`;
          
          const clipPathValue2 = `polygon(
            0% 0%, 0% 100%, 100% 100%, 100% 0%, 
            ${labelRect2.right-inputRect2.left}px 0%, ${labelRect2.right-inputRect2.left}px ${labelRect2.bottom-inputRect2.top}px, 
            ${labelRect2.left-inputRect2.left}px ${labelRect2.bottom-inputRect2.top}px, 
            ${labelRect2.left-inputRect2.left}px 0%, 0% 0%
          )`;
          inputRef.value.style.clipPath = clipPathValue;
          inputRef2.value.style.clipPath = clipPathValue2;
        }
      });
    });


//---------------------登录------------------------------
import { useRouter } from 'vue-router'

  //获取当前vue实例
  const { proxy } = getCurrentInstance()

  //获取路由对象
  const router = useRouter()
  //表单数据
  const form = reactive({
    userName: '',
    passWord: ''
  })
  //表单提交
  const onSubmit = async () => {
    const { data } = await proxy.$api.login(form) // {}把data解构出来
    //console.log('res',data)
    if (data.code === 10000) {
      localStorage.setItem('h5_token', data.data.token)
      localStorage.setItem('h5_userInfo', JSON.stringify(data.data.userInfo)) // 为什么要json.stringify?因为此时的后端发过来的数据中的userinfo是个object,而localstorage中智能存储字符串
      router.push('/homenew')
    } else {

    }
  }

</script>

<style scoped>
.container {
   /*  background-color: #f0f0f0; */
    min-height: 100vh;
    
  }
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  /*background: linear-gradient(180deg, #9dd9cb8d 0%, #a0e9ce89 50%, #ffffff 100%);  *//* 渐变背景 */
  background-image:url('/images/login_pattern.jpg');
/* background-color:rgba(255, 255, 255, 0.647); */
}
.logo {
  width: 150px;
  margin-top: 30px;
  position: fixed;
  top: 20px;
  right: 20px; 
}


.welcome-text {
  text-align: center;
  margin-top: 10px;
}

.welcome-text h1 {
  font-size: 2.2rem;
  margin-bottom: 10px;
  color: #02644e;
}

.welcome-text p {
  font-size: 1rem;
  color: #686868;
}

.input-container {
  position: relative;
  width: 70%;
  margin-top: 20px;
}

.input-label {
  position: absolute;
  top: -8px;
  left: 10px;
  /* background: linear-gradient(180deg, #ffffff8d 0%, #e0f2f7 100%); */
  padding: 0 5px;
  font-size: 14px;
  color: #008080;
  background-color: transparent;
    z-index: 1;
  
}

.phone-input {
  position:relative;
  width: 100%;
  padding: 15px 20px;
  border: 2px solid #008080;
  border-radius: 30px;
  font-size: 16px;
  outline: none;
  background-color: transparent;
  z-index: 2;
  box-sizing: border-box;
}

.phone-input::placeholder {
  color: #999;
}

.phone-input:focus {
  border-color: #00a0a0;
}


/**/

.login-button {
  width: 70%;
  margin-top: 30px;
  border-radius: 30px;
  background-color: #02644e;
  border: none;
}

.plants-bg {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  opacity: 0.4;
}
</style>