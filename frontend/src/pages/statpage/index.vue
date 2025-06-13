<template>
<div>
  <van-nav-bar title="健康记录" />
  <div class="stat-page">
    <!-- 卡片 1：选择日期 -->
    <div class="date-picker-card">
      <van-cell-group>
        <van-cell title="选择日期区间" :value="date" @click="showCalender= true" >
          <template #default>
            <div>{{date||"请选择结束时间"}}
              <van-icon name="arrow" />
            </div>
          </template>
        </van-cell>
        <van-calendar v-model:show="showCalender" type="range" @confirm="onConfirm" allow-same-day :min-date="minDateC" :max-date="maxDateC" />

      </van-cell-group>
    </div>
    <!-- 卡片 2：坐姿时长分布 -->
    <!-- <div class="duration-distribution-card">
        <div class="chart-container">
          <v-chart class="chart" :option="postureDurationOptions" autoresize />
        </div>
    </div> -->
    <van-swipe class="my-swipe" :autoplay="5000" indicator-color="white">
      <van-swipe-item>
        <!-- 卡片 3：前后倾分布 -->
        <div class="duration-distribution-card">
            <div class="chart-container">
              <v-chart class="chart" :option=" headOptions " autoresize />
            </div>
        </div>
      </van-swipe-item>
      <van-swipe-item>
        <!-- 卡片 3：左右倾分布 -->
        <div class="duration-distribution-card">
            <div class="chart-container">
              <v-chart class="chart" :option="torsoOptions" autoresize />
            </div>
        </div>
      </van-swipe-item>
      <van-swipe-item>
        <!-- 卡片 4：驼背分布 -->
        <div class="duration-distribution-card">
            <div class="chart-container">
              <v-chart class="chart" :option="legOptions" autoresize />
            </div>
        </div>
      </van-swipe-item>
      <van-swipe-item>
        <!-- 卡片 5：翘腿分布 -->
        <div class="duration-distribution-card">
            <div class="chart-container">
              <v-chart class="chart" :option="overallOptions" autoresize />
            </div>
        </div>
      </van-swipe-item>
    </van-swipe>
    
    <!-- 卡片 6：用眼距离统计 -->
    <!-- <div class="eye-distance-stat-card">
      <div class="chart-container">
        <v-chart class="chart" :option="eyeDistanceOptions" autoresize />
      </div>
    </div> -->
  </div>
</div>
</template>

<script setup>
import { ref,onMounted,provide,getCurrentInstance } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, PieChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';

const {proxy} =getCurrentInstance()

//-------------calander------------
const date = ref('');
const showCalender = ref(false);
const currentDate = new Date();
const minDateC = new Date(2024, 11, 1);
const maxDateC = currentDate;
const formatDate = (date) => `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;//用于前端显示
const formatDate2 = (date) => {//用于后端解析日期
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const sendDateRange = async (startDate, endDate) => {
  try {
    console.log("startDate",startDate);
    console.log("endDate",endDate);
    const response = await proxy.$api.sendDateRange({
      phone:JSON.parse(localStorage.getItem("h5_userInfo")).phone,
      startDate: formatDate2(startDate),
      endDate: formatDate2(endDate),
    });
    const stats = response.data.data.stats
    headOptions.value = generatePieOptions('头部状态', stats.head ?? {}, defaultCategories.head)
    torsoOptions.value = generatePieOptions('躯干前后倾', stats.torso ?? {}, defaultCategories.torso)
    legOptions.value = generatePieOptions('腿部翘腿情况', stats.leg ?? {}, defaultCategories.leg)
    overallOptions.value = generatePieOptions('整体坐姿评估', stats.overall ?? {}, defaultCategories.overall)

    console.log("startDate",startDate);
    console.log("endDate",endDate);
    console.log('后端响应:', response.data);
    // 处理后端响应
  } catch (error) {
    console.error('发送日期范围失败:', error);
    // 处理错误
  }
};

function formatPostureTime(seconds) {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  return `${hrs} 时 ${mins} 分 ${secs} 秒`;
}



// 工具函数：生成完整的图表数据（补全缺失类别）
function generatePieOptions(title, dataMap, categories) {
  const fullData = categories.map(cat => ({
    name: cat,
    value: dataMap[cat] ?? 0
  }))
  
  return {
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter:// '{b}：{c} 分钟 ({d}%)'
      function (params) {
    const formattedTime = formatPostureTime(params.value);
    return `${params.name}：${formattedTime} (${params.percent}%)`;
  }
    },
    legend:{
      orient:'horizontal',
      bottom:'0%',
      data:categories,
    },
    series: [
      {
        name:"时长分布",
        type: 'pie',
        radius: '50%',
        data: fullData,
        label:{
          formatter://'{b}\n{c} 分钟\n({d}%)'
          function (params) {
    const formattedTime = formatPostureTime(params.value);
    return `${params.name}\n${formattedTime}\n(${params.percent}%)`;
  },
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
}



const onConfirm = (values) => {
  const [start, end] = values;
  showCalender.value = false;
  date.value = `${formatDate(start)} - ${formatDate(end)}`;
  sendDateRange(start, end);// 发送日期范围到后端
};

//--------------------pie chart-----------------
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

provide(THEME_KEY, 'light');

// 算法的标准
const tiltFBOptions = ref({})
const tiltLROptions = ref({})
const hunchbackOptions = ref({})
const legCrossOptions = ref({})

// 关键点的算法：ECharts 变量
const headOptions = ref({})
const torsoOptions = ref({})
const legOptions = ref({})
const overallOptions = ref({})

// 默认类别（确保缺失的类别也显示）
const defaultCategories = {
  head: ['upright', 'forward', 'backward'],
  torso: ['upright', 'forward', 'backward'],
  leg: ['none', 'left', 'right'],
  overall: ['good', 'bad']
}




// 选择开始日期后的回调
const onStartDateConfirm = (value) => {
  startDate.value = value;
  showStartPicker.value = false;
};

// 选择结束日期后的回调
const onEndDateConfirm = (value) => {
  endDate.value = value;
  showEndPicker.value = false;
};


//-------------------生命周期---------------
onMounted(() => {

});

/* //-------------没用的演示代码---------------
const postureDurationOptions = ref({
  title: {
    text: '坐姿时长分布',
    left:'center',
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b} : {c} ({d}%)',
  },
  legend: {
    orient: 'vertical',
    left: 'right',
    data: ['良好坐姿', '不良坐姿（左倾）', '不良坐姿（右倾）','不良坐姿（前倾）',
    '不良坐姿（后倾）','不良坐姿（左腿放于右腿上）','不良坐姿（右腿放于左腿上）'],
  },
  series: [
    {
      name: '坐姿时长分布',
      type: 'pie',
      radius: '55%',
      center: ['50%', '60%'],
      data: [
        { value: 40, name: '良好坐姿' },
        { value: 7, name: '不良坐姿（左倾）' },
        { value: 4, name: '不良坐姿（右倾）' },
        { value: 23, name: '不良坐姿（前倾）' },
        { value: 10, name: '不良坐姿（后倾）' },
        { value: 13, name: '不良坐姿（左腿放于右腿上）' }, 
        { value: 4, name: '不良坐姿（右腿放于左腿上）' }, 
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)',
        },
      },
    },
  ],
});
const eyeDistanceOptions = ref({
  title: {
    text: '用眼距离统计',
    left:'center',
  },
  xAxis: {
    type: 'category',
    data: ['10-20cm','20-30cm','30-40cm', '40-50cm', '50-60cm', '60-70cm', '70-80cm'],
    axisLabel: {
      rotate: 45,  // 旋转 45 度
      fontSize: 12, // 缩小字体
    },
  },
  yAxis: {
    type: 'value',
  },
  series: [
    {
      data: [20, 60, 10, 20, 30, 40, 50],
      type: 'bar',
    },
  ],
}); */


</script>

<style lang="less" scoped>
.stat-page {
  padding: 16px;
  background: linear-gradient(180deg, #9dd9cb8d 0%, #a0e9ce89 50%, #ffffff 100%);
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

.date-picker-card {
  background-color: white;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.duration-distribution-card, .eye-distance-stat-card {
  background-color: white;
  padding: 15px;
  margin-bottom: 25px;
  //margin: 3px;   /* 给卡片外边距，产生间隔 */
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-height: 360px;
}

.chart-container {
  height: 350px;
}
.chart {
  height: 100%;
}

.my-swipe .van-swipe-item {
  color: #fff;
  font-size: 20px;
  line-height: 100px;
  text-align: center;
  background-color: #007f8b;
  border-radius: 8px;
}

</style>
