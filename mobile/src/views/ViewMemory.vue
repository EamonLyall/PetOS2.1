<template>
  <div class="view is-active" data-view="成长记忆">
    <div class="page-head">
      <span class="page-head__ico"><AppIcon name="memory" /></span>
      <div>
        <h1>成长记忆</h1>
        <p>和{{ p.name }}一起走过的每一天，都值得被记住</p>
      </div>
    </div>

    <div class="stat-row">
      <div class="stat"><b>{{ p.days }}</b><span>相伴天数</span></div>
      <div class="stat"><b>{{ p.moments }}</b><span>珍藏瞬间</span></div>
      <div class="stat"><b>{{ milestones.length }}</b><span>成长里程碑</span></div>
    </div>

    <div class="info-grid info-grid--2">
      <!-- 成长时间线（数据来自后端） -->
      <article class="card">
        <div class="card__hd">
          <span class="card__badge card__badge--violet"><AppIcon name="memory" /></span>
          <h2 class="card__title">成长时间线</h2>
        </div>
        <ul class="timeline">
          <li v-for="(t, i) in timeline" :key="i" class="tl-item">
            <div class="tl-item__date">{{ t.date }}</div>
            <div class="tl-item__title">{{ t.title }}</div>
            <div class="tl-item__desc">{{ t.desc }}</div>
          </li>
        </ul>
      </article>

      <!-- 里程碑（数据来自后端；图标按顺序沿用原型配色） -->
      <article class="card">
        <div class="card__hd">
          <span class="card__badge card__badge--pink"><AppIcon name="heart" /></span>
          <h2 class="card__title">里程碑</h2>
        </div>
        <ul class="kv-list">
          <li v-for="(m, i) in milestones" :key="i" class="kv">
            <span class="kv__ico" :class="milestoneIconClass(i)"><AppIcon :name="milestoneIcon(i)" /></span>
            <div class="kv__body">
              <span class="kv__label">{{ m.label }}</span>
              <span class="kv__value">{{ m.value }}</span>
            </div>
            <span class="kv__tail">{{ m.tail }}</span>
          </li>
        </ul>
      </article>
    </div>

    <!-- 照片墙（数据来自后端；imageKey 映射到前端打包图片，imageUrl 优先） -->
    <section class="grid">
      <article class="card">
        <div class="card__hd">
          <span class="card__badge"><AppIcon name="camera" /></span>
          <h2 class="card__title">照片墙</h2>
          <div class="card__aside">
            <button class="link" type="button" @click="store.pushToast('已打开全部 ' + p.moments + ' 张照片')">
              查看全部<AppIcon name="chevR" />
            </button>
          </div>
        </div>
        <div class="gallery">
          <div v-for="(g, i) in gallery" :key="i" class="gallery__item">
            <img :src="galleryImage(g)" :alt="g.caption" />
            <span class="gallery__cap">{{ g.caption }}</span>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from '@/components/AppIcon.vue'

const store = useCompanionStore()
const p = computed(() => store.activePet)

const timeline = computed(() => store.timeline)
const milestones = computed(() => store.milestones)
const gallery = computed(() => store.gallery)

// 里程碑图标与配色（与原型顺序一致，纯展示装饰）
const MILESTONE_ICONS = ['bolt', 'music', 'game', 'smile']
const MILESTONE_ICON_CLASS = ['', 'kv__ico--mint', '', 'kv__ico--violet']

function milestoneIcon(i) {
  return MILESTONE_ICONS[i] || 'heart'
}

function milestoneIconClass(i) {
  return MILESTONE_ICON_CLASS[i] || ''
}

// 照片：后端有 imageUrl 用后端图片，否则按 imageKey 取本地打包图
function galleryImage(g) {
  if (g.imageUrl) return g.imageUrl
  return store.IMG[g.imageKey] || store.IMG.kitten
}
</script>
