import { createRouter, createWebHashHistory } from 'vue-router';

/**
 * Routes for the Locomotive Digital Twin dashboard.
 *
 * Hash-mode routing is used so the app works without a server
 * rewrite rule (important for local/demo deployments).
 *
 * Adding a new route:
 *   1. Create a view in src/views/
 *   2. Add an entry below
 *   3. Add a <RouterLink> or nav-tab in TopBar.vue
 */
const routes = [
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
    meta: { label: 'Алерты', icon: '⚠' },
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
  // Catch-all — redirect unknown paths to dashboard
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
