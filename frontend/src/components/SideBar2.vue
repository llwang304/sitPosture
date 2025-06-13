<template>
  <div class="custom-sidebar" :class="{ 'custom-sidebar--active': active }">
    <div class="custom-sidebar__content">
      <div class="custom-sidebar__header">
        <van-button plain type="primary" size="small" @click="createNewDialog">
          新建对话
        </van-button>
      </div>
      <van-divider />
      <div class="custom-sidebar__items">
        <div
          v-for="(item, index) in items"
          :key="index"
          class="custom-sidebar-item"
          :class="{ 'custom-sidebar-item--active': activeIndex === index }"
          @click.stop="selectItem(index)"
        >
          <van-icon name="bars"  size="18"/>
          <van-field
            v-if="isEditing[index]"
            :ref="(el) => editInput[index] = el"
            v-model="editText[index]"
            @keyup.enter="finishEdit(index)"
            autofocus
            class="edit-input"

          />
          <div v-if="!isEditing[index]" class="custom-sidebar-item__text">
            {{ item.title }}
          </div>
          
          <van-popover 
            v-model:show="popoverVisible[index]" 
            :actions="actions"
            @select="onSelectAction(index,$event)"
            >
            <template #reference>
              <van-icon
                  name="ellipsis"
                  size="16"
                  class="action-icon"
                />
            </template>
          </van-popover>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref,onMounted,onUnmounted,nextTick,watch,computed,watchEffect } from 'vue';

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  modelValue: {
    type: Number,
    default: 0,
  },
});

const emit = defineEmits(['update:modelValue', 'createNewDialog','deleteDialog','renameDialog']);

const activeIndex = ref(props.modelValue);
const showActions = ref(false);
const selectedDialogIndex = ref(-1);


const actions = [
      { text: '删除', icon: 'delete-o' },
      { text: '重命名', icon: 'edit' },
    ];
const popoverVisible = ref(props.items.map(() => false)); // 为每个对话项维护一个 popoverVisible 状态
const isEditing = ref(props.items.map(() => false));
const editText = ref(props.items.map((item) => item.title));
const editInput = ref([]);

const isRenaming = ref(false);

watch(
  () => props.items,
  (newItems) => {
    isEditing.value = newItems.map(() => false);
    editText.value = newItems.map((item) => item.title);
    popoverVisible.value = newItems.map(() => false);
    editInput.value = newItems.map(() => null); // 初始化 editInput 数组
  },
  { deep: true, immediate: true },
);
// 监听 modelValue（v-model 绑定）变化
watch(
  () => props.modelValue,
  (newVal) => {
    activeIndex.value = newVal;
  }
);

const selectItem = (index) => {
  activeIndex.value = index;
  emit('update:modelValue', index);
};

const createNewDialog = () => {
  emit('createNewDialog');
};
const showDialogActions = (index) => {
  showActions.value = true;
  selectedDialogIndex.value = index;
};

const onSelectAction = (index,action) => {
  popoverVisible.value[index] = false; // 关闭当前对话项的 popover
  if (action.text === '删除') {
    emit('deleteDialog', index);
  } else if (action.text === '重命名') {
    isEditing.value[index] = true;
    isRenaming.value = true; // 设置标志变量
    console.log('action.text === 重命名,isEditing.value[index]=',index,isEditing.value[index])
    nextTick(() => {
      console.log('editInput.value[index]=',editInput.value[index])
      if(editInput.value[index]){
        editInput.value[index].focus();
      }
      setTimeout(()=>{
        isRenaming.value = false;
      },500)
    });
  }
};

const finishEdit = (index) => {
  console.log('调用finishEdit')
  isEditing.value[index] = false;
  if (editText.value[index].trim() !== '') {
    emit('renameDialog', index, editText.value[index]);
  } else {
    editText.value[index] = props.items[index].title;
  }
};

/* const handleClickOutside = (event) => {
  props.items.forEach((_, index) => {
    // if (isEditing.value[index] && editInput.value[index] && !editInput.value[index].$el.contains(event.target)) {
    //  finishEdit(index);
    //} 
    if (isEditing.value[index] && editInput.value[index] && editInput.value[index].$el) {
      if (!editInput.value[index].$el.contains(event.target)) {
        finishEdit(index);
      }
    }
  });
};
 */
const getEditInputRef = computed(() => {
  return (index) => editInput.value[index];
});

const handleClickOutside = (event) => {
  if (isRenaming.value) { // 检查标志变量
    return;
  }
  const target = event.target;
  console.log('target',target)
  const isEditingAny = isEditing.value.some((item) => item);
  console.log('isEditingAny',isEditingAny)
  if (isEditingAny) {

    nextTick(()=>{
      props.items.forEach((_, index) => {
        console.log('index',index)
        console.log('editInput.value',editInput.value)
        const editInputRef = editInput.value[index];
        //const editInputRef = getEditInputRef.value(index);
        console.log('editInputRef',editInputRef)
        if (isEditing.value[index] && editInputRef && editInputRef.$el) {
          console.log('isEditing.value[index]',isEditing.value[index])
          console.log('editInputRef.$el',editInputRef.$el)
          if (!editInputRef.$el.contains(target)) {
            console.log('editInputRef.$el.contains(target)',editInputRef.$el.contains(target))
            console.log('index',index)
            finishEdit(index);
          }
        }
      });  
    })
    
  }
};

watchEffect(() => {
  console.log("editInput.value的变化：", editInput.value);
});

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  setTimeout(()=>{
    console.log("延迟后editInput.value:",editInput.value);
  },2000)
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});


defineExpose({
  activeIndex,
});

const active = ref(true); // 始终显示侧边栏
</script>

<style lang="less" scoped>
.custom-sidebar {
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 100vh;
  background-color: #fff;
  box-shadow: -2px 0 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  transform: translateX(0);
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.custom-sidebar--active {
  transform: translateX(0);
}

.custom-sidebar__content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.custom-sidebar__header {
  padding: 16px;
  display: flex; flex-direction: column;
  gap: 8px; /* 添加按钮之间的间距 */
}

.custom-sidebar__items {
  flex: 1;
  overflow-y: auto;
  display: flex; flex-direction: column;
}

.custom-sidebar-item {
  padding: 16px;
  font-size: 14px;
  color: #323233;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  display: flex; flex-direction: row;
}

.custom-sidebar-item--active {
  background-color: #f0f0f0;
  font-weight: 500;
}

.custom-sidebar-item__text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: inherit; // 继承父元素的行高
}

.action-icon {
  color: #999;
  cursor: pointer;
}

.edit-input {
  :deep(.van-field__control) {
    padding: 0; // 去除内边距
    height: 100%; // 设置高度为 100%
    font-size: inherit; // 继承父元素的字体大小
    line-height: inherit; // 继承父元素的行高
  }
  :deep(.van-field__body){
    height: auto;
  }
  :deep(.van-field__body--with-label){
    height: auto;
  } 
  :deep(.van-field__control:focus){
    border-bottom: 1px solid black;
  }
  :deep(.van-field__body--with-label .van-field__control){
    height: auto;
  }
} 

</style>