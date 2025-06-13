import { createWebHashHistory, createRouter,createWebHistory } from 'vue-router'

import Layout from '../pages/Main.vue'
import Home from '../pages/home/index.vue'
import User from '../pages/user/index.vue'
import Login from '../pages/login/index.vue'
import Stat from '../pages/statpage/index.vue'
import Chat from '../pages/chat/index.vue'
import Info from '../pages/info/index.vue'
import Welcome from '../pages/welcome/index.vue'
import Loginnew from '../pages/loginnew/index.vue'
import Homenew from '../pages/homenew/index.vue'
import Monitor from '../pages/monitor/index.vue'
import Monitornew from '../pages/monitorNew/index.vue'
import Register from '../pages/register/index.vue'
const routes = [
  { 
    path: '/',
    component: Layout,
    redirect: '/homenew',
    children: [
      {
        path: 'homenew',
        meta: { 
          icon: 'home-o',
          name: '首页'
        },
        component: Homenew
      },
      {
        path: 'stat',
        meta: { 
          icon: 'orders-o',
          name: '统计'
        },
        component: Stat
      },
      {
        path: 'user',
        meta: {
          icon: 'user-circle-o',
          name: '我的'
        },
        component: User
      }
    ]
  },
  {
    path: '/login',
    name:"login",
    component: Login
    
  },
  {
    path: '/loginnew',
    name:"loginnew",
    component: Loginnew
    
  },
  {
    path: '/register',
    name:"register",
    component: Register
    
  },
  {
    path: '/chat',
    name:"chat",
    component: Chat
    
  },
  {
    path: '/info',
    name:"info",
    component: Info
    
  },
  {
    path: '/welcome',
    name:"welcome",
    component: Welcome
    
  },
  {
    path: '/home',
    name:"home",
    component: Home
    
  },
  {
    path: '/monitor',
    name:"monitor",
    component: Monitor
    
  },
  {
    path: '/monitornew',
    name:"monitornew",
    component: Monitornew
    
  },
  
]
const router = createRouter({
  history: createWebHistory(),
  routes
})

// ✅ 登录守卫逻辑
router.beforeEach((to, from, next) => {
  const userInfoStr = localStorage.getItem("h5_userInfo")

  if (!userInfoStr && to.path !== '/welcome') {
    // 如果未登录，跳转登录页
    next('/welcome')
  } else if (userInfoStr && to.path === '/welcome') {
    // 已登录，访问 login 页面则跳转到主页
    next('/homenew')
  } else {
    next()  // 放行
  }
})


export default createRouter({
  history: createWebHashHistory(),
  routes
})