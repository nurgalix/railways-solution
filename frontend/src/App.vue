<template>
  <div class="app-root">
    <TopBar v-if="!isLoginPage" />
    <RouterView />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import TopBar from '@/components/layout/TopBar.vue';

const route = useRoute();
const isLoginPage = computed(() => route.name === 'login');
</script>
