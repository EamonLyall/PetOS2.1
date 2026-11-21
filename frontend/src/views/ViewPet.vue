<template>
  <div class="view is-active" data-view="我的宠物">
    <div class="page-head">
      <span class="page-head__ico"><AppIcon name="pet" /></span>
      <div>
        <h1>我的宠物</h1>
        <p>{{ p.name }}的一切，都在这里～</p>
      </div>
    </div>

    <!-- 宠物简介 -->
    <section class="profile">
      <img class="profile__avatar" :src="store.IMG.kitten" :alt="p.name + '头像'" />
      <div class="profile__main">
        <div class="profile__name">
          {{ p.name }} <span class="lv">LV.{{ p.level }}</span>
        </div>
        <p class="profile__desc">{{ p.desc }} · 已陪伴你 {{ p.days }} 天</p>
        <div class="profile__bar">
          <div class="profile__bar-row">
            <span>成长值</span>
            <b>{{ p.growth }} / 100 · 距 LV.{{ p.level + 1 }} 还需 {{ 100 - p.growth }}</b>
          </div>
          <div class="bar"><i :style="{ width: p.growth + '%' }"></i></div>
        </div>
      </div>
      <div class="profile__meta">
        <span>品种 · {{ p.breed }}</span>
        <span>年龄 · {{ p.age }}</span>
        <span>体重 · {{ p.weight }}</span>
      </div>
    </section>

    <!-- 数据统计 -->
    <div class="stat-row">
      <div class="stat"><b>{{ p.days }}</b><span>陪伴天数</span></div>
      <div class="stat"><b>{{ p.moments }}</b><span>精彩瞬间</span></div>
      <div class="stat"><b>{{ p.growth }}</b><span>成长值</span></div>
    </div>

    <div class="info-grid">
      <!-- 状态总览 -->
      <article class="card">
        <div class="card__hd">
          <span class="card__badge card__badge--pink"><AppIcon name="heart" /></span>
          <h2 class="card__title">宠物状态总览</h2>
        </div>
        <ul class="kv-list" style="margin-top:16px">
          <li class="kv">
            <span class="kv__ico kv__ico--mint"><AppIcon name="smile" /></span>
            <div class="kv__body">
              <span class="kv__label">情绪状态</span>
              <span class="kv__value">{{ p.mood }} <span class="tag">{{ p.moodTag }}</span></span>
            </div>
          </li>
          <li class="kv">
            <span class="kv__ico"><AppIcon name="health" /></span>
            <div class="kv__body">
              <span class="kv__label">健康状态</span>
              <span class="kv__value">{{ p.healthStatus }}</span>
            </div>
          </li>
          <li class="kv">
            <span class="kv__ico kv__ico--amber"><AppIcon name="bolt" /></span>
            <div class="kv__body">
              <span class="kv__label">活跃度 / 能量值</span>
              <span class="kv__value">{{ p.active }}% · {{ p.energy }}%</span>
            </div>
          </li>
        </ul>
      </article>

      <!-- 健康档案 -->
      <article class="card">
        <div class="card__hd">
          <span class="card__badge"><AppIcon name="health" /></span>
          <h2 class="card__title">健康档案</h2>
        </div>
        <ul class="kv-list">
          <li class="kv">
            <span class="kv__ico kv__ico--mint"><AppIcon name="heart" /></span>
            <div class="kv__body">
              <span class="kv__label">心率</span>
              <span class="kv__value">{{ p.heartRate }} 次 / 分</span>
            </div>
            <span class="kv__tail">{{ heartRateTag }}</span>
          </li>
          <li class="kv">
            <span class="kv__ico kv__ico--amber"><AppIcon name="bolt" /></span>
            <div class="kv__body">
              <span class="kv__label">今日活动</span>
              <span class="kv__value">{{ p.activeMinutes }} 分钟</span>
            </div>
            <span class="kv__tail">{{ activeTag }}</span>
          </li>
          <li class="kv">
            <span class="kv__ico"><AppIcon name="moon" /></span>
            <div class="kv__body">
              <span class="kv__label">睡眠时长</span>
              <span class="kv__value">{{ p.sleepHours }} 小时</span>
            </div>
            <span class="kv__tail">{{ sleepTag }}</span>
          </li>
          <li class="kv">
            <span class="kv__ico kv__ico--violet"><AppIcon name="memory" /></span>
            <div class="kv__body">
              <span class="kv__label">最近体检</span>
              <span class="kv__value">{{ p.lastCheckup }}</span>
            </div>
            <span class="kv__tail">{{ p.healthStatus }}</span>
          </li>
        </ul>
      </article>

      <!-- 今日小确幸 -->
      <article class="card card--bless">
        <div class="card__hd">
          <span class="card__badge card__badge--violet"><AppIcon name="spark" /></span>
          <h2 class="card__title">今日小确幸</h2>
          <div class="card__aside">
            <span class="chip" style="height:24px;font-size:13px">{{ doneCount }}/3</span>
          </div>
        </div>
        <ul class="bless-list">
          <li v-for="(b, i) in store.blessList" :key="i">
            <button
              class="bless"
              :class="{ 'is-done': b.done }"
              type="button"
              :aria-pressed="b.done"
              @click="store.toggleBless(i)"
            >
              <span class="bless__box"><AppIcon name="check" /></span>
              <span>{{ b.text }}</span>
            </button>
          </li>
        </ul>
        <div style="margin-top:auto;padding-top:16px;font-size:14px;color:var(--c-ink-3)">
          “主人，别忘了陪我哦～”
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from '@/components/AppIcon.vue'

const store = useCompanionStore()
const p = computed(() => store.activePet)
const doneCount = computed(() => store.blessList.filter(b => b.done).length)

// 健康指标判定：由数据库数值实时计算，不再写死“正常/达标/充足”等文案
const heartRateTag = computed(() => {
  const v = p.value.heartRate
  if (!v) return '-'
  return v >= 120 && v <= 160 ? '正常' : '需关注'
})
const activeTag = computed(() => (p.value.activeMinutes >= 30 ? '达标' : '待加强'))
const sleepTag = computed(() => (p.value.sleepHours >= 10 ? '充足' : '偏少'))
</script>
