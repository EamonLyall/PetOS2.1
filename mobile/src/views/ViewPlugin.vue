<template>
  <div class="view is-active" data-view="插件中心">
    <div class="page-head">
      <span class="page-head__ico"><AppIcon name="plugin" /></span>
      <div>
        <h1>插件中心</h1>
        <p>给小宠装上更多本领，持续解锁新玩法</p>
      </div>
    </div>

    <!-- 已启用分组 -->
    <div v-if="enabledPlugins.length" class="plugin-group">
      <div class="plugin-group__hd">
        已启用<span>{{ enabledPlugins.length }} 项</span>
      </div>
      <div class="plugin-grid">
        <article
          v-for="p in enabledPlugins"
          :key="p.n"
          class="plugin"
          @click="onCardClick(p)"
        >
          <span class="plugin__ico" :class="p.c"><AppIcon :name="p.i" /></span>
          <div class="plugin__name">{{ p.n }}</div>
          <p class="plugin__desc">{{ p.d }}</p>
          <div class="plugin__foot">
            <span class="plugin__status">● 已启用</span>
            <button
              class="switch is-on"
              type="button"
              :aria-label="'切换' + p.n"
              aria-pressed="true"
              @click.stop="togglePlugin(p)"
            ></button>
          </div>
        </article>
      </div>
    </div>

    <!-- 未启用 / 可安装分组 -->
    <div v-if="disabledPlugins.length" class="plugin-group">
      <div class="plugin-group__hd">
        未启用 / 可安装<span>{{ disabledPlugins.length }} 项</span>
      </div>
      <div class="plugin-grid">
        <article
          v-for="p in disabledPlugins"
          :key="p.n"
          class="plugin"
          @click="onCardClick(p)"
        >
          <span class="plugin__ico" :class="p.c"><AppIcon :name="p.i" /></span>
          <div class="plugin__name">{{ p.n }}</div>
          <p class="plugin__desc">{{ p.d }}</p>
          <div class="plugin__foot">
            <span class="plugin__status plugin__status--off">○ 未启用</span>
            <button
              class="switch"
              type="button"
              :aria-label="'切换' + p.n"
              aria-pressed="false"
              @click.stop="togglePlugin(p)"
            ></button>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from '@/components/AppIcon.vue'

const store = useCompanionStore()

// 插件清单来自后端（store.plugins），on 为后端返回的启用状态
const plugins = computed(() => store.plugins)

const enabledPlugins = computed(() => plugins.value.filter(p => p.on))
const disabledPlugins = computed(() => plugins.value.filter(p => !p.on))

// 卡片整体点击：提示启用 / 安装状态
function onCardClick(p) {
  store.pushToast(p.n + (p.on ? '已启用' : '正在安装中，请稍候'))
}

// 开关：调用后端接口切换，成功后由 store 更新本地状态
function togglePlugin(p) {
  store.togglePlugin(p)
}
</script>
