<template>
  <div class="app-root">
    <TopBar />

    <main class="cabin-layout">
      <!-- LEFT: Health + Alerts -->
      <aside class="col col-left">
        <HealthIndexCard />
        <AlertsPanel />
      </aside>

      <!-- CENTER: Speed + Trends -->
      <section class="col col-center">
        <SpeedPanel />
        <TrendsPanel />
      </section>

      <!-- RIGHT: Fuel + Pressure/Temp + Electrical + Map -->
      <aside class="col col-right">
        <FuelEnergyPanel />
        <PressureTempPanel />
        <ElectricalPanel />
        <RouteMapPanel />
      </aside>
    </main>
  </div>
</template>

<script setup>
import TopBar           from './components/layout/TopBar.vue';
import HealthIndexCard  from './components/cabin/HealthIndexCard.vue';
import AlertsPanel      from './components/cabin/AlertsPanel.vue';
import SpeedPanel       from './components/cabin/SpeedPanel.vue';
import TrendsPanel      from './components/cabin/TrendsPanel.vue';
import FuelEnergyPanel  from './components/cabin/FuelEnergyPanel.vue';
import PressureTempPanel from './components/cabin/PressureTempPanel.vue';
import ElectricalPanel  from './components/cabin/ElectricalPanel.vue';
import RouteMapPanel    from './components/cabin/RouteMapPanel.vue';
</script>

<style>
/* ── Global layout resets ──────────────────────────────────────── */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}

.app-root {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--color-bg);
}

/* ── 3-column cabin grid ───────────────────────────────────────── */
.cabin-layout {
  display: grid;
  grid-template-columns: 300px 1fr 300px;
  grid-template-rows: 1fr;
  gap: 0.75rem;
  padding: 0.75rem;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  align-items: start;
}

/* ── Columns ───────────────────────────────────────────────────── */
.col {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* Center column is scrollable if content overflows */
.col-center {
  min-width: 0;
}

/* ── Responsive: laptop (< 1280px) ────────────────────────────── */
@media (max-width: 1280px) {
  .cabin-layout {
    grid-template-columns: 260px 1fr 260px;
  }
}

/* ── Responsive: tablet / small screen ────────────────────────── */
@media (max-width: 900px) {
  .cabin-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }
  .col-left, .col-right, .col-center {
    display: contents; /* flatten — each card goes into a single-column flow */
  }
  .cabin-layout {
    display: flex;
    flex-direction: column;
  }
}
</style>
