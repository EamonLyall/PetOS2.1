<template>
  <aside class="drawer" :class="{ 'is-open': store.ui.drawer }" aria-label="设备中心">
    <div class="drawer__hd">
      <span class="card__badge"><AppIcon name="device" /></span>
      <div>
        <h2>设备中心</h2>
        <p>连接、切换与管理你的 PetOS 设备</p>
      </div>
      <button class="drawer__close" type="button" aria-label="关闭" @click="store.ui.drawer = false">
        <AppIcon name="close" />
      </button>
    </div>

    <div class="drawer__body">
      <!-- 当前设备 -->
      <div class="dev-current">
        <span class="dev-current__ico"><AppIcon name="paw" /></span>
        <div class="dev-current__main">
          <div class="dev-current__name">{{ store.activeDevice.name }}</div>
          <div class="dev-current__sub">
            <i class="dot" :class="store.connected ? 'dot--on' : 'dot--off'"></i>
            <template v-if="store.connected">
              {{ store.activePet.name }} · {{ store.activeDevice.place }}
              · 信号 {{ store.activeDevice.signal }}%
              · 电量 {{ store.activeDevice.battery }}%
            </template>
            <template v-else>当前未连接任何设备</template>
          </div>
        </div>
        <button v-if="store.connected" class="btn-ghost" type="button" @click="store.disconnect">
          <AppIcon name="power" />断开
        </button>
        <span v-else class="tag tag--mute">离线</span>
      </div>

      <!-- 已保存的设备 -->
      <div class="drawer__section">
        <div class="drawer__sec-hd"><AppIcon name="wifi" />已保存的设备</div>
        <ul class="dev-list">
          <li
            v-for="d in store.devices"
            :key="d.id"
            class="dev-list__item"
            :class="{ 'is-active': isCurrent(d) }"
          >
            <span class="dev-list__ico"><AppIcon name="device" /></span>
            <div class="dev-list__body">
              <div class="dev-list__name">
                {{ d.name }}
                <span v-if="isCurrent(d)" class="tag">当前</span>
              </div>
              <div class="dev-list__sub">
                {{ store.pets[d.petKey].name }} · {{ d.place }}
                · {{ d.online ? '在线' : '离线' }} · {{ d.last }}
              </div>
            </div>
            <button
              class="dev-list__btn"
              :class="{ 'is-off': !isCurrent(d) }"
              type="button"
              @click="isCurrent(d) ? store.disconnect() : store.connectDevice(d.id)"
            >
              {{ isCurrent(d) ? '断开' : '连接' }}
            </button>
          </li>
        </ul>
      </div>

      <!-- 附近发现的设备 -->
      <div class="drawer__section">
        <div class="drawer__sec-hd">
          <AppIcon name="signal" />附近发现的设备
          <button class="link" type="button" @click="store.rescan">
            <AppIcon name="refresh" />重新扫描
          </button>
        </div>
        <div class="scan-line"></div>
        <ul class="dev-list">
          <li v-for="d in store.nearby" :key="d.id" class="dev-list__item">
            <span class="dev-list__ico"><AppIcon name="plus" /></span>
            <div class="dev-list__body">
              <div class="dev-list__name">{{ d.name }}</div>
              <div class="dev-list__sub">
                {{ store.pets[d.petKey].name }} · {{ d.place }} · 信号 {{ d.signal }}%
              </div>
            </div>
            <button class="dev-list__btn" type="button" @click="store.connectDevice(d.id)">
              连接
            </button>
          </li>
        </ul>
      </div>

      <div class="drawer-tip">
        <AppIcon name="info" />
        <span>连接新设备后，首页问候、宠物档案、成长值与陪伴数据会自动切换为该设备对应的宠物。断开后可随时从「已保存的设备」重新连接，或选择附近设备配对。</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useCompanionStore } from '@/stores/companion'
import AppIcon from './AppIcon.vue'

const store = useCompanionStore()

function isCurrent(d) {
  return d.id === store.activeDeviceId && store.connected
}
</script>
