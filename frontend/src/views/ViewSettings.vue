<template>
  <div class="view is-active" data-view="系统设置">
    <div class="page-head">
      <span class="page-head__ico"><AppIcon name="settings" /></span>
      <div>
        <h1>系统设置</h1>
        <p>网络、语音、通知与账户，都可以在这里调整</p>
      </div>
    </div>

    <!-- 连接与网络 -->
    <div class="setting-group">
      <div class="setting-group__hd"><AppIcon name="wifi" /><h2>连接与网络</h2></div>

      <div class="setting-row" @click="openDrawer">
        <span class="setting-row__ico"><AppIcon name="device" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">当前连接设备</div>
          <div class="setting-row__sub">
            {{ store.activeDevice.name }} · 宠物 {{ store.activePet.name }}
          </div>
        </div>
        <span class="setting-row__val">切换 <AppIcon name="chevR" /></span>
      </div>

      <div class="setting-row" @click="toastRow('Wi-Fi 网络')">
        <span class="setting-row__ico"><AppIcon name="wifi" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">Wi-Fi 网络</div>
          <div class="setting-row__sub">当前连接的无线网络</div>
        </div>
        <span class="setting-row__val">{{ store.activeDevice.wifi }} <AppIcon name="chevR" /></span>
      </div>

      <div class="setting-row">
        <span class="setting-row__ico"><AppIcon name="link" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">蓝牙</div>
          <div class="setting-row__sub">用于配对周边智能设备</div>
        </div>
        <AppSwitch
          :model-value="store.network.bluetooth"
          label="蓝牙"
          @update:model-value="store.toggleOption('network', 'bluetooth')"
        />
      </div>

      <div class="setting-row" @click="toastRow('设备固件')">
        <span class="setting-row__ico"><AppIcon name="device" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">设备固件</div>
          <div class="setting-row__sub">
            当前版本 {{ store.activeDevice.fw }} ·
            {{ store.network.firmwareLatest ? '已是最新' : '有新版本可升级' }}
          </div>
        </div>
        <span class="setting-row__val">检查更新 <AppIcon name="chevR" /></span>
      </div>
    </div>

    <!-- 语音与交互 -->
    <div class="setting-group">
      <div class="setting-group__hd"><AppIcon name="mic" /><h2>语音与交互</h2></div>

      <div class="setting-row" @click="toastRow('语音唤醒词')">
        <span class="setting-row__ico"><AppIcon name="mic" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">语音唤醒词</div>
          <div class="setting-row__sub">叫一声就能唤醒小宠</div>
        </div>
        <span class="setting-row__val">{{ store.voice.wakeWord }} <AppIcon name="chevR" /></span>
      </div>

      <div class="setting-row">
        <span class="setting-row__ico"><AppIcon name="speaker" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">语音回复</div>
          <div class="setting-row__sub">用声音回答你的问题</div>
        </div>
        <AppSwitch
          :model-value="store.voice.tts"
          label="语音回复"
          @update:model-value="store.toggleTts"
        />
      </div>

      <div class="setting-row" @click="toastRow('交互语言')">
        <span class="setting-row__ico"><AppIcon name="robot" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">交互语言</div>
          <div class="setting-row__sub">语音识别与回复语言</div>
        </div>
        <span class="setting-row__val">{{ store.profile.language }} <AppIcon name="chevR" /></span>
      </div>
    </div>

    <!-- 通知与隐私 -->
    <div class="setting-group">
      <div class="setting-group__hd"><AppIcon name="bell" /><h2>通知与隐私</h2></div>

      <div class="setting-row">
        <span class="setting-row__ico"><AppIcon name="bell" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">消息通知</div>
          <div class="setting-row__sub">陪伴提醒与系统消息</div>
        </div>
        <AppSwitch
          :model-value="store.notify.message"
          label="消息通知"
          @update:model-value="store.toggleOption('notify', 'message')"
        />
      </div>

      <div class="setting-row">
        <span class="setting-row__ico"><AppIcon name="camera" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">移动侦测提醒</div>
          <div class="setting-row__sub">画面异常时推送通知</div>
        </div>
        <AppSwitch
          :model-value="store.notify.motion"
          label="移动侦测提醒"
          @update:model-value="store.toggleOption('notify', 'motion')"
        />
      </div>

      <div class="setting-row">
        <span class="setting-row__ico"><AppIcon name="memory" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">数据云端同步</div>
          <div class="setting-row__sub">自动备份成长记忆与设置</div>
        </div>
        <AppSwitch
          :model-value="store.notify.cloudSync"
          label="数据云端同步"
          @update:model-value="store.toggleOption('notify', 'cloudSync')"
        />
      </div>
    </div>

    <!-- 账户与关于 -->
    <div class="setting-group">
      <div class="setting-group__hd"><AppIcon name="user" /><h2>账户与关于</h2></div>

      <div class="setting-row" @click="toastRow('账户信息')">
        <span class="setting-row__ico"><AppIcon name="user" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">账户信息</div>
          <div class="setting-row__sub">当前登录：{{ store.profile.account }}</div>
        </div>
        <span class="setting-row__val">查看 <AppIcon name="chevR" /></span>
      </div>

      <div class="setting-row" @click="toastRow('关于 PetOS')">
        <span class="setting-row__ico"><AppIcon name="paw" /></span>
        <div class="setting-row__body">
          <div class="setting-row__title">关于 PetOS</div>
          <div class="setting-row__sub">AI Companion · v{{ store.profile.appVersion }}</div>
        </div>
        <span class="setting-row__val">详情 <AppIcon name="chevR" /></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCompanionStore } from '@/stores/companion'
import AppIcon from '@/components/AppIcon.vue'
import AppSwitch from '@/components/AppSwitch.vue'

const store = useCompanionStore()

function openDrawer() {
  store.ui.drawer = true
}

function toastRow(title) {
  store.pushToast(title)
}
</script>
