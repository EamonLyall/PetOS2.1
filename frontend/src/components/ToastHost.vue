<template>
  <div class="toasts" role="status" aria-live="polite">
    <div v-for="t in store.toasts" :key="t.id" class="toast show">
      <span class="toast__dot"></span>
      <span>{{ t.msg }}</span>
    </div>
  </div>
</template>

<script setup>
import { useCompanionStore } from '@/stores/companion'

const store = useCompanionStore()
</script>
