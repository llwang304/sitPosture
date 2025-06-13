<template>
  <div>
    <router-view />
    <div style="height: 5rem;"></div>
    <van-tabbar v-model="active">
      <van-tabbar-item placeholder  v-for="(item) in router.options.routes[0].children" :key="item.path" :icon="item.meta.icon" :url="`#/${item.path}`">{{item.meta.name}}</van-tabbar-item>
    </van-tabbar>

  </div>
</template>
<script setup>
  import { ref,onMounted } from 'vue';
  import {useRouter,useRoute} from 'vue-router' //组装时间：onMounted,//我其实还不太理解router和route
  

  /*--------------------tabbar--------------------*/
  const active = ref(0);
      

  /*--------------------生命周期--------------------*/
  const router=useRouter()
  const route=useRoute()
  onMounted(()=>{
    console.log(router,'router')
    //匹配tabbar跳转
    const data=router.options.routes[0]
    active.value=data.children.findIndex(item=> '/'+item.path===route.path)
  });
</script>

<style scoped>

</style>
