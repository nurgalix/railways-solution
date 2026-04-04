import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router/index.js';
import App from './App.vue';

import './assets/styles/main.css';

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount('#app');

// Start telemetry service after Pinia is ready
import { useTelemetryStore }  from './stores/telemetry.js';
import { telemetryService }   from './services/telemetryService.js';

const store = useTelemetryStore();
telemetryService.start(store);
