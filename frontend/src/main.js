import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router/index.js';
import App from './App.vue';

import './assets/styles/main.css';

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);
app.use(router);
app.mount('#app');

// Verify stored token on startup, then start telemetry
import { useAuthStore }       from './stores/auth.js';
import { useTelemetryStore }  from './stores/telemetry.js';
import { telemetryService }   from './services/telemetryService.js';

const auth = useAuthStore();

// If a token exists in localStorage, confirm it is still valid with the server
if (auth.token) {
  auth.fetchMe();
}

const store = useTelemetryStore();
telemetryService.start(store);
