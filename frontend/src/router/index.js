import { createRouter, createWebHashHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth.js';

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { label: 'Кабина', icon: '🖥' },
  },
  {
    path: '/alerts',
    name: 'alerts',
    component: () => import('@/views/AlertsView.vue'),
    meta: { label: 'Сообщения', icon: '⚠' },
  },
  {
    path: '/trends',
    name: 'trends',
    component: () => import('@/views/TrendsView.vue'),
    meta: { label: 'Тренды', icon: '📈' },
  },
  {
    path: '/route',
    name: 'route',
    component: () => import('@/views/RouteView.vue'),
    meta: { label: 'Маршрут', icon: '🗺' },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { label: 'Настройки', icon: '⚙' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// Navigation guard — redirect to /login if not authenticated
router.beforeEach((to) => {
  if (to.meta.public) return true;
  const auth = useAuthStore();
  if (!auth.isAuthenticated) return { name: 'login' };
});

export default router;
