<template>
<div class="container">
    <van-nav-bar
      title="注册"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
    />
  <div class="login-container">
    <!-- <img src="/images/bupt6.png" alt="BUPT Logo" class="logo" /> -->
    <!-- 自定义的绿色返回按钮 -->
    
    <div class="welcome-text">
      <h1>欢迎!</h1>
      <p>从这里开始!</p>
    </div>
    <div class="input-container">
      <label ref="labelRef" for="phone-number" class="input-label">电话号码</label>
      <input 
        v-model="form.phone" 
        ref="inputRef" 
        type="text" 
        id="phone-number" 
        class="phone-input" 
        placeholder="请输入电话号码" 
        @blur="validateField('phone')"
        />
      <span v-if="errors.phone" class="error-message">{{ errors.phone }}</span>
    </div>
    <div class="input-container">
      <label ref="labelRef4" for="name" class="input-label">用户昵称</label>
      <input 
        v-model="form.username" 
        ref="inputRef4" 
        type="text" 
        id="name" 
        class="phone-input" 
        placeholder="请输入用户昵称"
        @blur="validateField('username')" 
      />
      <span v-if="errors.username" class="error-message">{{ errors.username}}</span>
    </div>
    <div class="input-container">
      <label ref="labelRef2" for="password" class="input-label">密码</label>
      <input 
        v-model="form.password" 
        ref="inputRef2" 
        type="password" 
        id="password" 
        class="phone-input" 
        placeholder="请输入密码" 
        @blur="validateField('password')"
      />
      <span v-if="errors.password" class="error-message">{{ errors.password}}</span>
    </div>
    <div class="input-container">
      <label ref="labelRef3" for="password" class="input-label">密码验证</label>
      <input 
      v-model="form.confirmPassword" 
      ref="inputRef3" 
      type="password" 
      id="password2" 
      class="phone-input" 
      placeholder="请再次输入密码" 
      @blur="validateField('confirmPassword')"
      />
      <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword}}</span>
      <p v-if="passwordMismatch" class="error-message">两次输入的密码不匹配!</p>
    </div>
    
    <van-button type="primary" class="login-button" @click="onSubmit">注册</van-button>
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
const labelRef3 = ref(null);
const inputRef3 = ref(null);
const labelRef4 = ref(null);
const inputRef4 = ref(null);
onMounted(() => {
      nextTick(() => {
        if (labelRef.value && inputRef.value) {
          const labelRect = labelRef.value.getBoundingClientRect();
          const inputRect = inputRef.value.getBoundingClientRect();
          const labelRect2 = labelRef2.value.getBoundingClientRect();
          const inputRect2 = inputRef2.value.getBoundingClientRect();
          const labelRect3 = labelRef3.value.getBoundingClientRect();
          const inputRect3 = inputRef3.value.getBoundingClientRect();
          const labelRect4 = labelRef3.value.getBoundingClientRect();
          const inputRect4 = inputRef3.value.getBoundingClientRect();

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
          const clipPathValue3 = `polygon(
            0% 0%, 0% 100%, 100% 100%, 100% 0%, 
            ${labelRect3.right-inputRect3.left}px 0%, ${labelRect3.right-inputRect3.left}px ${labelRect3.bottom-inputRect3.top}px, 
            ${labelRect3.left-inputRect3.left}px ${labelRect3.bottom-inputRect3.top}px, 
            ${labelRect3.left-inputRect3.left}px 0%, 0% 0%
          )`;
          const clipPathValue4 = `polygon(
            0% 0%, 0% 100%, 100% 100%, 100% 0%, 
            ${labelRect4.right-inputRect4.left}px 0%, ${labelRect4.right-inputRect4.left}px ${labelRect4.bottom-inputRect4.top}px, 
            ${labelRect4.left-inputRect4.left}px ${labelRect4.bottom-inputRect4.top}px, 
            ${labelRect4.left-inputRect4.left}px 0%, 0% 0%
          )`;
          inputRef.value.style.clipPath = clipPathValue;
          inputRef2.value.style.clipPath = clipPathValue2;
          inputRef3.value.style.clipPath = clipPathValue3;
          inputRef4.value.style.clipPath = clipPathValue4;
        }
      });
    });
  

//---------------------登录------------------------------
import {computed} from 'vue'
import { useRouter } from 'vue-router'

  //获取当前vue实例
  const { proxy } = getCurrentInstance()

  //获取路由对象
  const router = useRouter()
  //表单数据
  const form = reactive({
    phone:'',
    username: '',
    password: '',
    confirmPassword: ''
  })
  //错误信息
  const errors = reactive({
    phone: '',
    username: '',
    password: '',
    confirmPassword: '',
    
  })
  //返回上一页
  const onClickLeft = () => {
    router.back();
  };

  //表单校验
  const passwordMismatch = computed(() => {
    return form.password !== form.confirmPassword && form.confirmPassword !== '';
  });

  const validateField = (fieldName) => {
  if (!form[fieldName]) {
    errors[fieldName] = '该字段不能为空';
  } else {
    errors[fieldName] = '';
  }
};
  //表单提交
  const onSubmit = async () => {
    validateField('phone');
    validateField('username');
    validateField('password');
    validateField('confirmPassword');
    try{
      const { data } = await proxy.$api.register(form) // {}把data解构出来
      //console.log('res',data)
      if (data.code === 10000) {
        localStorage.setItem('h5_token', data.data.token)
        localStorage.setItem('h5_userInfo', JSON.stringify(data.data.userInfo)) // 后端发过来的数据中的userinfo是个object,而localstorage中存储字符串
        // 提示 & 跳转到主页
        showToast('注册成功，欢迎加入,即将跳转到主页！')
        router.push('/homenew')
      } else {
        showDialog({ message: '注册失败，用户已注册' });
      }
    }catch(err){
      showToast('注册失败，用户已注册')
      form.username = ''; // 清空用户名字段
      form.password = ''; // 清空密码字段
      form.confirmPassword = ''; // 清空确认密码字段
      form.phone = ''; // 清空手机号字段
      console.error(err);
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
  height: 95vh;
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


/*欢迎*/

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

/* .phone-input::placeholder {
  color: #999;
} */

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

.error-message {
  color: red;
  font-size: 12px;
  margin-top: 5px;
}
</style>