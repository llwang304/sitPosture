import { createApp } from 'vue'
//import './style.css'
import App from './App.vue'
import router from './router'//引入router
import api from './api'
//import cors from 'cors'

/* createApp(App).mount('#app') */
const app=createApp(App)
//路由挂载
app.use(router)
app.mount('#app')
//在实例上绑定属性
app.config.globalProperties.$api=api

