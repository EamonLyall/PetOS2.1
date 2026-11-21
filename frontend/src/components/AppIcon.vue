<template>
  <svg class="ic" :class="iconClass">
    <use :href="'#i-' + name" />
  </svg>
</template>

<script setup>
// 通用图标组件：通过 name 引用 IconSymbols 里定义的 symbol
// 用法：<AppIcon name="home" />；需要额外样式类时传 icon-class
defineProps({
  name: {
    type: String,
    required: true
  },
  iconClass: {
    type: String,
    default: ''
  }
})
</script>
