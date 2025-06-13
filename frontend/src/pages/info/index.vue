<template>
    <div class="container">

      <div class="header">
        <van-icon name="arrow-left" class="header-left" size="30px" @click=goBack />
        个人资料
      </div>
      <status-bar :item="statusBarProgress"/>

    <div v-if="statusBarProgress === 0">
    <van-cell class="cell" >
      <template #title>
       <!--  <van-image class="server-name" width="25" height="25" :src="orderData.service.serviceImg"></van-image> -->
        <span>基本信息</span>
      </template>
      <template #default>
        <div class="service-text" >服务内容</div>
      </template>
    </van-cell>
    <van-cell-group class="cell">
        <van-cell title="昵称" >
          <van-field 
            class="text"
            input-align="right"
            v-model="userInfo.name" 
            placeholder="请填写昵称" 
            >
          </van-field>
        </van-cell>

        <van-cell title="性别" :value="userInfo.gender || '请选择性别'" is-link @click="genderPopupVisible=true" />
        <van-cell title="出生日期" :value="currentDate|| '请选择出生日期'" is-link @click="agePopupVisible=true" />
        <!-- <van-cell >
        <template #title>出生日期</template>
        <template #default>
          <div  @click="agePopupVisible=true">{{currentDate||"请选择出生日期"}}
            <van-icon name="arrow" />
          </div>
        </template>
      </van-cell> -->
        <van-cell title="身高"  >
          <van-field 
            class="text"
            input-align="right"
            v-model="userInfo.height" 
            placeholder="请填写身高" 
            >
            <template #extra>
              <span style="color: #323233; margin-left: 5px;">cm</span>
            </template>
          </van-field>
        </van-cell>

        <van-cell title="体重" >
          <van-field 
            class="text"
            input-align="right"
            v-model="userInfo.weight" 
            placeholder="请填写体重" 
            >
            <template #extra>
              <span style="color: #323233; margin-left: 5px;">kg</span>
            </template>
          </van-field>
        </van-cell>
        

        <van-cell title="职业/日常活动" >
          <van-field 
            class="text"
            input-align="right"
            v-model="userInfo.occupation" 
            placeholder="工作环境（是否长时间坐着/从事体力劳动）" 
            rows="2"
            autosizes
            type="textarea"
            maxlength="50"
            show-word-limit
            >
          </van-field>
        </van-cell>
        
      </van-cell-group>
      <van-popup v-model:show="genderPopupVisible" position="bottom" :style="{ height: '30%' }">
         <van-picker
        :columns="genderOptions"
        @confirm="genderConfirm"
        @cancel="genderPopupVisible = false"
      />
      </van-popup>
      <van-popup v-model:show="agePopupVisible" position="bottom" :style="{ height: '30%' }">
        <van-date-picker
          title="选择日期"
          :min-date="minDate"
          :max-date="maxDate"
          @confirm="ageConfirm"
        @cancel="agePopupVisible = false"
        />
      </van-popup>
      <div class="nextbutton">
        <van-button  @click="saveBasicInfo" color="#0BAF94" style="width:80%">保存并进入下一页</van-button>
        
      </div>
    </div>
    <div v-if="statusBarProgress === 10">
      <van-cell-group class="cell">
         <van-field 
          class="text"
          style="height:350px"
          v-model="userInfo.spineHealth" 
          label-align="top"
          label="请简单描述您的健康情况，如是否有脊柱侧弯、颈椎病、腰椎病等问题，如有，请描述出现肩膀疼痛、背部疼痛、颈部僵硬等症状的频次。这些健康历史信息至关重要。谢谢" 
          placeholder="请简单描述您的健康情况"
          rows="8"
          autosizes
          type="textarea"
          maxlength="100"
          show-word-limit
        />
        <van-field 
          class="text"
          style="height:200px"
          v-model="userInfo.exerciseHabit" 
          label-align="top"
          label="请简单描述您的运动习惯" 
          placeholder="请简单描述您的运动习惯"
          rows="5"
          autosizes
          type="textarea"
          maxlength="80"
          show-word-limit
        />
        <div class="nextbutton">
          <van-button  @click="backpage" color="#0BAF94" style="width:45%">返回上一步</van-button>
          <van-button  @click="saveHealthInfo() " color="#0BAF94" style="width:45%">保存并进入下一页</van-button>
        </div>
      </van-cell-group>
    </div>
    <div v-if="statusBarProgress === 20">
      <van-cell-group class="cell">
        <van-cell title="连续久坐时间" :value="formattedTime|| '请选择连续久坐时间'" is-link @click="sittingTimePopupVisible=true" />
        <!-- <van-cell 
          title="是否开启语音提醒" 
          :value="userInfo.audioAlert === 1? '是' : '否' || '请选择是否开启语音'" is-link 
          @click="audioAlertPopupVisible=true" 
        /> -->
        <van-field 
          class="text"
          style="height:200px"
          v-model="userInfo.exerciseHabit" 
          label-align="top"
          label="请简单描述您的工作环境，是否有固定的办公环境，使用的座椅（高度，有无靠背）、办公桌等。" 
          placeholder="请简单描述您的工作环境"
          rows="5"
          autosizes
          type="textarea"
          maxlength="80"
          show-word-limit
        />
        
      </van-cell-group>
      
      <van-popup v-model:show="audioAlertPopupVisible" position="bottom" >
        <van-picker
        :columns="audioAlertOptions"
        @confirm="audioAlertConfirm"
        @cancel="audioAlertPopupVisible = false"
      />
      </van-popup>
      <van-popup v-model:show="sittingTimePopupVisible" position="bottom" >
        <van-time-picker 
          v-model="currentTime" 
          title="选择时间" 
          :filter="filter" 
          @confirm="timeConfirm"
          :formatter="formatter"
          @cancel="sittingTimePopupVisible = false"/>
      </van-popup>
      <div class="nextbutton">
          <van-button  @click="backpage" color="#0BAF94" style="width:45%">返回上一步</van-button>
          <van-button  @click="saveWorkInfo() " color="#0BAF94" style="width:45%">保存并进入下一步</van-button>
      </div>
    </div>
    <div v-if="statusBarProgress === 30">
      <van-cell-group class="cell">
         <van-field 
          class="text"
          style="height:200px"
          v-model="userInfo.otherInfo" 
          label-align="top"
          label="其他情况" 
          placeholder="如有上述问题未涵盖的问题，或感兴趣的内容，请注明。"
          rows="5"
          autosizes
          type="textarea"
          maxlength="100"
          show-word-limit
        />
      </van-cell-group>
      <div class="nextbutton">
          <van-button  @click="backpage" color="#0BAF94" style="width:45%">返回上一步</van-button>
          <van-button  @click="submitForm " color="#0BAF94" style="width:45%">确认修改</van-button>
      </div>
    </div>
    <!-- <div class="nextbutton">
        <van-button  v-if="statusBarProgress===10 || statusBarProgress===20 || statusBarProgress===30" @click="backpage" color="#0BAF94" style="width:45%">返回上一步</van-button>
        <van-button  v-if="statusBarProgress===20 || statusBarProgress===30 " @click="saveHealthInfo() " color="#0BAF94" style="width:45%">保存并进入下一页</van-button>
      </div> -->
  </div>
</template>

<script setup>
import {onMounted,ref,reactive,computed,getCurrentInstance} from 'vue'
import {useRouter} from 'vue-router'
import Statusbar from '../../components/statusBar.vue'



const router=useRouter()
const {proxy} =getCurrentInstance()//获取当前 Vue 组件实例的代理对象

/*--------------------header头部--------------------*/
/*返回上一页*/
//点击图标返回上一页
const goBack=()=>{
  //router.push('/home')//返回上一页和push是不一样的，push会在页面栈里新增一个url,而返回会清除掉当前的路径并返回到上一页
  router.go(-1)
}

/* //--------------------订单表格--------------------
//显示时表格内容
const orderData=reactive({
  companion:[],
  hospitals:[],
  service:{},
})

//提交时表格内容
const form =reactive(
  {
  hospital_id:'',
  hospital_name:'',
  demand:'',//备注
  companion_id:'',//陪护师id
  receiveAddress:'',//接送地址
  tel:'',//联系电话
  starttime:'',//服务开始时间
})

//就诊医院
const showHospital=ref(false)
const hospitalColumns=computed(()=>{//监听orderData变化，进行处理
  return orderData.hospitals.map(item=>{//computed要求的return 
    return {text:item.name,value:item.id}//map方法要求的return 
  })
})

const hospitalConfirm=(item)=>{//item是这个插件预设的一个关联值，不需要在调用confirm时传入参数
  console.log('item',item)
  form.hospital_id=item.selectedOptions[0].value
  form.hospital_name=item.selectedOptions[0].text
  showHospital.value = false
}
//就诊时间
const showStartTime=ref(false)
const currentDate = ref();
const minDate=ref(new Date())
const maxDate=ref(new Date())

const startTimeConfirm=(item)=>{
  console.log('item',item)
  const dateStr=item.selectedValues.join('-')
  currentDate.value=dateStr
  form.starttime=new Date(dateStr).getTime()
  showStartTime.value = false
}

//陪护师
const showCompanion=ref(false)
const companionName=ref('')
const companionColumns=computed(()=>{//监听orderData变化，进行处理
  return orderData.companion.map(item=>{//computed要求的return 
    return {text:item.name,value:item.id}//map方法要求的return 
  })
})
const companionConfirm=(item)=>{//item是这个插件预设的一个关联值，不需要在调用confirm时传入参数
  console.log('item',item)
  form.companion_id=item.selectedOptions[0].value
  companionName.value=item.selectedOptions[0].text
  showCompanion.value = false
}


//提交订单
const submit=async()=>{
  const params=[
    'hospital_id',
    'hospital_name',
    'demand',//备注
    'companion_id',//陪护师id
    'receiveAddress',//接送地址
    'tel',//联系电话
    'starttime',//服务开始时间
  ]
  for (const i of params){//是否可以在表单中加rules实现
    if((form[i]==='')){
      showNotify({ message: '请把每一项都填写' });
      return
    }
  }
  const {data:orderRes}=await proxy.$api.createOrder(form)
  console.log('orderRes',orderRes)
  Qrcode.toDataURL(orderRes.data.wx_code).then((url)=>{
    showCode.value=true
    codeImg.value=url
  })
}



//--------------------Onmounted--------------------
onMounted(async()=>{
  const {data}=await proxy.$api.h5Companion()
    Object.assign(orderData,data.data)
    console.log('OrderData=',orderData)

}) */

// 用于记录各部分的完成状态
const statusBarProgress = ref(0);


// 用户信息
const userInfo = reactive({
  name: "",
  gender: "",
  birthday:"",
  age: null,
  height: null,
  weight: null,
  occupation: "",
  spineHealth: "",
  exerciseHabit: "",
  sittingStyle: "",
  sittingTime: null,
  //audioAlert: null,
  healthGoal: "",
  reminderFrequency: "",
  otherInfo:"",
});

//选项options
//性别
const genderOptions = [
  {text:'男',value:'1'},
  {text:'女',value:'0'},
];
//出生日期
const today=new Date()
const currentDate = ref();
const minDate=new Date(today)
const maxDate=new Date(today)
maxDate.setFullYear(today.getFullYear() - 5); // 设置为 18 年前的日期
minDate.setFullYear(today.getFullYear() - 100); // 设置为 100 年前的日期
//久坐时间
const currentTime = ref(['00', '00']);
const filter = (type, options) => {
      if (type === 'minute') {
        return options.filter((option) => Number(option.value) % 5 === 0);
      }
      return options;
};
const formatter = (type, option) => {
      if (type === 'hour') {
        option.text += '时';
      }
      if (type === 'minute') {
        option.text += '分';
      }
      return option;
    };
// 计算属性，将时间格式化为更易读的样子
const formattedTime = computed(() => {
  const hour = currentTime.value[0];
  const minute = currentTime.value[1];
  return `${hour}时${minute}分`;
});
//语音提醒
/* const audioAlertOptions=[
  {text:'是',value:1},
  {text:'否',value:0},
] */


// 弹窗控制
//const namePopupVisible = ref(false);
const genderPopupVisible = ref(false);
const agePopupVisible = ref(false);
const heightPopupVisible = ref(false);
const weightPopupVisible = ref(false);
const occupationPopupVisible = ref(false);
const exerciseHabitPopupVisible = ref(false);
const sittingStylePopupVisible = ref(false);
const sittingTimePopupVisible = ref(false);
//const audioAlertPopupVisible = ref(false);
const healthGoalPopupVisible = ref(false);
const reminderFrequencyPopupVisible = ref(false);


const genderConfirm=(item)=>{
  console.log('item',item)
  userInfo.gender=item.selectedOptions[0].text
  genderPopupVisible.value=false
}
const ageConfirm=(item)=>{
  console.log('item',item)
  const dateStr=item.selectedValues.join('-')
  currentDate.value=dateStr
  console.log('currentDate',currentDate.value)
  const selectedDate=new Date(currentDate.value)
  const age=today.getFullYear()-selectedDate.getFullYear();
  console.log('age',age)
  userInfo.birthday=new Date(dateStr).getTime()
  agePopupVisible.value = false
}

/* const audioAlertConfirm=(item)=>{
  console.log('item',item)
  userInfo.audioAlert=item.selectedOptions[0].value
  audioAlertPopupVisible.value=false
} */
const timeConfirm=(item)=>{
  console.log('item',item)
  const hour = parseInt(currentTime.value[0], 10);
  const minute = parseInt(currentTime.value[1], 10);
  const totalMinutes = hour * 60 + minute;
  userInfo.sittingTime = totalMinutes;
  console.log('用户信息已更新：', userInfo.sittingTime);
  sittingTimePopupVisible.value=false
}

// 保存数据并进入下一步
const saveBasicInfo=()=>{
  // 保存基本信息
  statusBarProgress.value = 10; // 进入健康信息填写
  console.log('statusBarProgress',statusBarProgress)
}

const backpage=()=>{
  statusBarProgress.value = statusBarProgress.value-10;
}
function saveHealthInfo() {
  statusBarProgress.value = 20; // 进入工作环境信息填写
}

function saveWorkInfo() {
  statusBarProgress.value = 30; // 进入目标设定填写
}


// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await proxy.$api.getUserInfo();
    if (response.data.code === 10000) {
      Object.assign(userInfo, response.data.data);
    } else {
      showToast("获取用户信息失败");
    }
  } catch (error) {
    showToast("请求错误");
  }
};
const submitForm = async () => {
  try {
    const response = await proxy.$api.updateInfo(userInfo);
    if (response.data.code === 10000) {
      showToast("信息更新成功");
    } else {
      showToast("更新失败");
    }
  } catch (error) {
    showToast("请求错误");
  }
}
  
  onMounted(()=>{
    fetchUserInfo();
  });
</script>

<style lang="less" scoped>
  .container {
    background-color: #f0f0f0;
    height: 100vh;
  }
  .header {
    padding: 10px 0;
    text-align: center;
    line-height: 30px;
    font-size: 15px;
    .header-left {
      float: left;
    }
  }

  .cell {
    width: 95%;
    margin: 5px auto;
    background-color: #fff;
    ::v-deep(.van-field__control) {
      color: var(--van-cell-value-color);
    }
    ::v-deep(.van-cell__title) {
    display: flex;
    align-items: center;
    }
    .server-name {
      margin-left: 10px;
    }
  }
  .van-field__label {
  font-weight: bold;
  margin-bottom: 12px; /* 控制label和输入框之间的间距 */
  line-height: 1.5;
}

  .service-text {
    background: url(data:image/png;base64,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)
      no-repeat center center;
    background-size: 20px;
  }
  .submit {
    position: absolute;
    bottom: 0;
  }
  ::v-deep(.van-dialog__content) {
    text-align: center;
    padding: 20px;
    .close {
      position: absolute;
      left: 20px;
    }
  }
  .nextbutton {
  display: flex;
  justify-content: space-around; /* 水平居中 */
  width: 100%; /* 可选，确保父容器有足够的高度来垂直居中 */
  }
</style>