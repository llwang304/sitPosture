<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="icon-container">
        <!-- 预留图标位置 -->
        <i class="icon"></i>
      </div>
      <h1 class="title">用户登录</h1>
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-field
            v-model="form.userName"
            name="用户名"
            label="用户名"
            placeholder="用户名"
            :rules="[{ required: true, message: '请填写用户名' }]"
          />
          <van-field
            v-model="form.passWord"
            type="password"
            name="密码"
            label="密码"
            placeholder="密码"
            :rules="[{ required: true, message: '请填写密码' }]"
          />
        </van-cell-group>
        <div style="margin: 16px;">
          <van-button round block type="primary" native-type="submit" class="submit-button">
            提交
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
  import { useRouter } from 'vue-router'
  import { reactive, getCurrentInstance } from 'vue'

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
    if (data.code === 10000) {
      localStorage.setItem('h5_token', data.data.token)
      localStorage.setItem('h5_userInfo', JSON.stringify(data.data.userInfo)) // 为什么要json.stringify?因为此时的后端发过来的数据中的userinfo是个object,而localstorage中智能存储字符串
      router.push('/homenew')
    } else {

    }
  }
</script>

<style lang="less" scoped>
  .login-container {
    background-color: #f4f4f4;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .login-wrapper {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    width: 300px;
  }

  .icon-container {
    text-align: center;
    margin-bottom: 20px;
  }

  .icon {
    font-size: 48px;
    color: #007aff;
  }

  .title {
    text-align: center;
    margin-bottom: 20px;
    transition: color 0.3s ease;
  }

  .title:hover {
    color: #007aff;
  }

  .submit-button {
    transition: background-color 0.3s ease;
  }

  .submit-button:hover {
    background-color: #0056b3;
  }
</style>