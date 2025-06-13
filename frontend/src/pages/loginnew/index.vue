<template>
<div class="container">
  <van-nav-bar
      title="登录"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
    />
  <div class="login-container">
    <div class="welcome-text">
      <h1>你好!</h1>
      <p>很高兴见到你!</p>
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
        @blur="validatePhone"
      />
      <div class="error-container">
        <span v-if="errors.phone" class="error-message">{{ errors.phone }}</span>
      </div>
      
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
        @blur="validatePassword"
        />
      <div class="error-container">
        <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
      </div>
        
    </div>
    
    <van-button type="primary" class="login-button" @click="onSubmit">登录</van-button>
    <p class="link-text" @click="showReset = true" >忘记密码？</p>
    <van-dialog
      v-model:show="showReset"
      title="重置密码"
      show-cancel-button
      @confirm="onConfirmReset"
      @cancel="onCancelReset"
    >
    <div class="reset-form">
      <van-field v-model="resetForm.phone" label="手机号" placeholder="请输入手机号" required />
      <van-field v-model="resetForm.username" label="昵称" placeholder="请输入昵称"  required/>
      <van-field v-model="resetForm.newPassword" label="新密码" type="password" placeholder="请输入新密码" required/>
    </div>
</van-dialog>
  </div>
</div>
</template>
<script setup>
// 这里可以添加按钮点击事件的处理逻辑welcome
import {ref,onMounted,reactive,getCurrentInstance,nextTick} from 'vue';
import { ERROR_CODES } from '../../utils/errorCode';
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
    phone: '',
    password: ''
  })
  // 错误提示
  const errors = reactive({
    phone: '',
    password: ''
});
  //返回上一页
  const onClickLeft = () => {
      router.back();
  };

  //表单提交
  const onSubmit = async () => {
    // 验证字段
    validatePhone();
    validatePassword();
    //如果有错误，停止提交
    if (errors.phone || errors.password) {
      return;
    }

    const { data } = await proxy.$api.login(form) // {}把data解构出来
    //console.log('res',data)
    if (data.code === 10000) {
      localStorage.setItem('h5_token', data.data.token)
      localStorage.setItem('h5_userInfo', JSON.stringify(data.data.userInfo)) // 为什么要json.stringify?因为此时的后端发过来的数据中的userinfo是个object,而localstorage中智能存储字符串
      router.push('/homenew')
    } else {
    }
  }
  //校验
  // Validation functions
const validatePhone = () => {
  if (!form.phone) {
    errors.phone = '  该项不能为空';
  } else {
    errors.phone = '';
  }
};

const validatePassword = () => {
  if (!form.password) {
    errors.password = '  该项不能为空';
  } else {
    errors.password = '';
  }
};



//-----------------------找回密码---------------------
const showReset = ref(false)
const resetForm = reactive({
  phone: '',
  username: '',
  newPassword: ''
})
const clearResetForm = () => {
  resetForm.phone = ''
  resetForm.username = ''
  resetForm.newPassword = ''
}

const onConfirmReset=async()=>{
  await onResetPassword();
  clearResetForm();
}
const onCancelReset=()=>{
  clearResetForm();

}
const onResetPassword = async () => {
  try {
    const res = await proxy.$api.resetPassword(resetForm)
    if (res.data.code === 10000) {
      showToast('密码重置成功，请重新登录')
    } else {
      showToast(res.data.message || '重置失败')
    }
  } catch (err) {
    console.error(err)
    showToast('网络错误，请稍后再试')
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
/*报错信息*/
.error-container {
  min-height: 15px; /* 你可以根据字体大小微调，比如18px或20px */
  margin-top: 5px;
}
.error-message {
  color: red;
  font-size: 12px;
  margin-top: 5px;
}


/*登录按钮*/

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

.link-text {
  color: #1989fa;         /* 蓝色文本 */
  text-decoration: underline; /* 下划线 */
  cursor: pointer;        /* 鼠标悬浮变成手型 */
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
}
</style>