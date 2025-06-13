import io from 'socket.io-client';
const userInfoStr = localStorage.getItem("h5_userInfo");
const socket= io("http://localhost:5000");
/* const phone= JSON.parse(localStorage.getItem("h5_userInfo")).phone
const token = localStorage.getItem('h5_token'); */
/* if (phone) {
  const socket = io("http://localhost:5000", {
    query: { token: phone}
  });
  } */
//const socket = io('http://localhost:5000',/* {query: { token: phone}} */); // 替换为你的后端 URL
if (userInfoStr) {
  const phone = JSON.parse(userInfoStr).phone;
  const socket = io("http://localhost:5000", {
    query: { token: phone }
  });
} else {
  console.warn("用户信息未初始化，暂不建立 Socket 连接");
}


// 可以在这里添加其他 Socket.IO 事件监听和处理逻辑
socket.on('connect', () => {
  console.log('Connected to server');
});

socket.on('disconnect', () => {
  console.log('Disconnected from server');
});

export default  socket;