<template>
  <!-- 通用开关：
       - 传 modelValue 时为受控模式（状态由父组件 / 数据库驱动，点击只发事件）；
       - 不传 modelValue 时为自包含本地状态，点击切换并弹 Toast。 -->
  <button
    class="switch"
    :class="{ 'is-on': isOn }"
    type="button"
    :aria-label="label"
    :aria-pressed="isOn"
    @click.stop="toggle"
  ></button>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCompanionStore } from '@/stores/companion'

const props = defineProps({
  initial: { type: Boolean, default: false }, // 非受控模式的初始状态
  modelValue: { type: Boolean, default: undefined }, // 受控模式状态（由后端设置驱动）
  label: { type: String, default: '开关' }    // 无障碍标签 / Toast 文案
})

const emit = defineEmits(['update:modelValue'])

const store = useCompanionStore()
const localOn = ref(props.initial)

// 受控模式优先使用 modelValue，否则使用本地状态
const isOn = computed(() => (props.modelValue !== undefined ? props.modelValue : localOn.value))

function toggle() {
  if (props.modelValue !== undefined) {
    // 受控模式：交给父组件调用后端接口，成功后由 props 回传最新值
    emit('update:modelValue', !props.modelValue)
    return
  }
  localOn.value = !localOn.value
  store.pushToast(props.label + (localOn.value ? ' · 已开启' : ' · 已关闭'))
}
</script>
