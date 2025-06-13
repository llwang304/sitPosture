import axios from 'axios'

const http=axios.create({
    baseURL: 'http://localhost:5000/',
    timeout: 10000,
    headers:{"terminal":"h5"}
})

//添加拦截器：在请求或响应被 then 或 catch 处理前拦截它们。
http.interceptors.request.use(function (config) {
    // 在发送请求之前做些什么
    // 添加token,用于用户鉴权
    const token=localStorage.getItem('h5_token')
    // 不需要添加token的白名单,这样做是为了避免在不需要身份验证的请求中添加 token。
    const whiteUrl=[
        //'/get/code',
        //'/user/authentication',
        '/login',
    ]
    if(token&&!whiteUrl.includes(config.url)){
        config.headers['h-token'] = token
    }
    return config;
  }, function (error) {
    // 对请求错误做些什么
    return Promise.reject(error);
  });

// 添加响应拦截器
http.interceptors.response.use(function (response) {
    // 2xx 范围内的状态码都会触发该函数。
    // 对响应数据做点什么
    //对接口异常的数据需要给用户提示
    if(response.data.code===-1){
        //ElMessage.warning(response.data.message)
    }
    if(response.data.code===-2){//如admin页面中的token  过期等问题
      //清除缓存记录
      localStorage.removeItem('h5_token')
      localStorage.removeItem('h5_userInfo')
      //localStorage.removeItem('pz_v3pz')
      //跳转回登陆页面
      window.location.href=window.location.origin
    }

    return response;
  }, function (error) {
    // 超出 2xx 范围的状态码都会触发该函数。
    // 对响应错误做点什么
    return Promise.reject(error);
  });

  //向外部暴露
  export default http;
  

