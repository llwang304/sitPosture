<template>
  <div class="custom-sidebar" :class="{ 'custom-sidebar--active': active }">
    <div class="custom-sidebar__content">
      <div class="custom-sidebar__header">
        <van-button plain type="primary" size="small" @click="createNewDialog">
          新建对话
        </van-button>
        <van-button plain type="danger" size="small" @click="toggleDeleteMode">
          {{ isDeleting ? '取消删除' : '删除对话' }}
        </van-button>
      </div>
      <van-divider />
      <div class="custom-sidebar__items">
        <div
          v-for="(item, index) in items"
          :key="index"
          class="custom-sidebar-item"
          :class="{ 'custom-sidebar-item--active': activeIndex === index }"
          @click="selectItem(index)"
        >
          <van-icon name="bars"  size="18"/>
          <div class="custom-sidebar-item__text">{{ item.title }}</div>
          <van-icon
            v-if="isDeleting"
            name="delete"
            size="16"
            class="delete-icon"
            @click.stop="deleteItem(index)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

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

const emit = defineEmits(['update:modelValue', 'createNewDialog','deleteDialog']);

const activeIndex = ref(props.modelValue);
const isDeleting = ref(false);//1表示可删除状态 0表示不可删除状态

const selectItem = (index) => {
  activeIndex.value = index;
  emit('update:modelValue', index);
};

const createNewDialog = () => {
  emit('createNewDialog');
};

const toggleDeleteMode = () => {
  isDeleting.value = !isDeleting.value;
};

const deleteItem = (index) => {
  emit('deleteDialog', index);
};

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
}

.delete-icon {
  color: #f00;
  cursor: pointer;
  vertical-align: middle; /* 垂直居中对齐 */
  right: 0; /* 放置在右侧边缘 */
  font-size: 14px; /* 调整图标大小 */
}
</style>